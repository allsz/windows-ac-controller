"""
updater.py - Verificacao e instalacao de atualizacoes via GitHub Releases.

Fluxo: consulta a ultima release publicada -> compara com a versao atual -> baixa o instalador
(WTC-LG-Setup-X.Y.Z.exe) -> confere o SHA-256 contra o SHA256SUMS.txt da mesma release -> executa o
instalador em modo silencioso e encerra o app. Sem dependencias extras (urllib da biblioteca padrao).

Na versao portatil (sem desinstalador ao lado do exe) nao ha instalacao automatica: o app apenas
avisa e abre a pagina da release.
"""

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import urllib.error
import urllib.request
from typing import Optional

from PySide6 import QtCore

REPO = "allsz/windows-ac-controller"
LATEST_URL = f"https://api.github.com/repos/{REPO}/releases/latest"
RELEASES_PAGE = f"https://github.com/{REPO}/releases/latest"
ALLOWED_DOWNLOAD_PREFIX = f"https://github.com/{REPO}/releases/download/"
USER_AGENT = "WTC-LG-updater"
TIMEOUT_SECONDS = 15
SETUP_NAME = re.compile(r"^WTC-LG-Setup-.+\.exe$")


def parse_version(text: str) -> tuple:
    """'v1.2.3' -> (1, 2, 3). Sufixos como '-beta' sao ignorados; texto invalido vira ()."""
    m = re.match(r"^v?(\d+(?:\.\d+)*)", (text or "").strip())
    return tuple(int(p) for p in m.group(1).split(".")) if m else ()


def is_newer(latest: str, current: str) -> bool:
    a, b = parse_version(latest), parse_version(current)
    return bool(a) and bool(b) and a > b


def is_installed_build() -> bool:
    """True quando rodando do instalador (o Inno grava unins000.exe ao lado do exe)."""
    if not getattr(sys, "frozen", False):
        return False
    return os.path.exists(os.path.join(os.path.dirname(sys.executable), "unins000.exe"))


def _open(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"})
    return urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS)


def fetch_latest_release(current_version: str) -> Optional[dict]:
    """Retorna dict(version, notes, page, setup_url, setup_name, sums_url) se ha versao mais nova, senao None.
    Levanta excecao em falha de rede/parse (o chamador decide como avisar)."""
    try:
        with _open(LATEST_URL) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:  # repositorio ainda sem nenhuma release publicada
            return None
        raise
    tag = data.get("tag_name", "")
    if not is_newer(tag, current_version):
        return None
    setup = sums = None
    for asset in data.get("assets", []):
        name, url = asset.get("name", ""), asset.get("browser_download_url", "")
        if SETUP_NAME.match(name):
            setup = (name, url)
        elif name == "SHA256SUMS.txt":
            sums = url
    return {
        "version": tag.lstrip("v"),
        "notes": data.get("body") or "",
        "page": data.get("html_url") or RELEASES_PAGE,
        "setup_name": setup[0] if setup else None,
        "setup_url": setup[1] if setup else None,
        "sums_url": sums,
    }


def _parse_sums(raw: bytes) -> dict:
    # Releases antigas podem ter sido geradas em UTF-16 pelo PowerShell 5.1
    text = raw.decode("utf-16") if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else raw.decode("utf-8", "replace")
    out = {}
    for line in text.splitlines():
        parts = line.strip().split(None, 1)
        if len(parts) == 2 and re.fullmatch(r"[0-9a-fA-F]{64}", parts[0]):
            out[parts[1].strip().lstrip("*")] = parts[0].lower()
    return out


def download_installer(info: dict, progress=None) -> str:
    """Baixa o instalador para uma pasta temporaria e valida o SHA-256. Retorna o caminho."""
    for url in (info.get("setup_url"), info.get("sums_url")):
        if not url or not url.startswith(ALLOWED_DOWNLOAD_PREFIX):
            raise RuntimeError("A release nao contem o instalador/checksum esperados.")

    with _open(info["sums_url"]) as resp:
        expected = _parse_sums(resp.read()).get(info["setup_name"])
    if not expected:
        raise RuntimeError("Checksum do instalador ausente em SHA256SUMS.txt.")

    dest_dir = tempfile.mkdtemp(prefix="wtc-lg-update-")
    dest = os.path.join(dest_dir, info["setup_name"])
    sha = hashlib.sha256()
    with _open(info["setup_url"]) as resp, open(dest, "wb") as f:
        total = int(resp.headers.get("Content-Length") or 0)
        done = 0
        while True:
            chunk = resp.read(64 * 1024)
            if not chunk:
                break
            f.write(chunk)
            sha.update(chunk)
            done += len(chunk)
            if progress and total:
                progress(int(done * 100 / total))
    if sha.hexdigest() != expected:
        os.remove(dest)
        raise RuntimeError("Checksum invalido: o download foi descartado.")
    return dest


def launch_installer(path: str) -> None:
    """Inicia o instalador silencioso, desacoplado do app (que deve encerrar logo em seguida)."""
    flags = getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    subprocess.Popen(
        [path, "/SILENT", "/SUPPRESSMSGBOXES", "/NORESTART", "/CLOSEAPPLICATIONS"],
        creationflags=flags,
        close_fds=True,
    )


class Updater(QtCore.QObject):
    """Executa verificacao/download em thread propria e devolve o resultado por sinais."""

    check_finished = QtCore.Signal(object, str)    # (info | None, erro | "")
    download_progress = QtCore.Signal(int)
    download_finished = QtCore.Signal(str, str)    # (caminho | "", erro | "")

    def __init__(self, current_version: str, parent=None):
        super().__init__(parent)
        self._current = current_version

    def check(self) -> None:
        def work():
            try:
                self.check_finished.emit(fetch_latest_release(self._current), "")
            except Exception as e:
                self.check_finished.emit(None, str(e))
        threading.Thread(target=work, name="updater-check", daemon=True).start()

    def download(self, info: dict) -> None:
        def work():
            try:
                path = download_installer(info, self.download_progress.emit)
                self.download_finished.emit(path, "")
            except Exception as e:
                self.download_finished.emit("", str(e))
        threading.Thread(target=work, name="updater-download", daemon=True).start()
