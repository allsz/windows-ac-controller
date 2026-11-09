"""
credentials_backend.py - Gerenciamento Seguro de Credenciais Locais (Windows DPAPI)

Utiliza a API nativa de proteção de dados do Windows (CryptProtectData / CryptUnprotectData).
Os dados são criptografados com a chave criptográfica mestre do usuário logado no Windows.
Nenhum outro usuário ou máquina consegue descriptografar os dados.
Zero dependências externas além do Python padrão (ctypes).
"""

import os
import sys
import json
import base64
import ctypes
from ctypes import wintypes
from typing import Optional, Dict, Any

# Estruturas do Windows DPAPI
class DATA_BLOB(ctypes.Structure):
    _fields_ = [
        ("cbData", wintypes.DWORD),
        ("pbData", ctypes.POINTER(ctypes.c_byte))
    ]

_crypt32 = ctypes.windll.crypt32
_kernel32 = ctypes.windll.kernel32

def _get_app_data_dir() -> str:
    """Retorna o diretório %APPDATA%/LG-DualInverter-Controller seguro."""
    appdata = os.getenv("APPDATA") or os.path.expanduser("~")
    target_dir = os.path.join(appdata, "LG-DualInverter-Controller")
    os.makedirs(target_dir, exist_ok=True)
    return target_dir

def _get_vault_file_path() -> str:
    return os.path.join(_get_app_data_dir(), "credentials.vault")

def dpapi_encrypt(plaintext: str) -> str:
    """Criptografa uma string usando a DPAPI do Windows e retorna base64."""
    data_bytes = plaintext.encode("utf-8")
    blob_in = DATA_BLOB()
    blob_in.cbData = len(data_bytes)
    blob_in.pbData = ctypes.cast(ctypes.create_string_buffer(data_bytes), ctypes.POINTER(ctypes.c_byte))

    blob_out = DATA_BLOB()

    # CRYPTPROTECT_UI_FORBIDDEN = 0x1 (não exibe prompts de UI do Windows)
    success = _crypt32.CryptProtectData(
        ctypes.byref(blob_in),
        "LGThinQCredentials",
        None,
        None,
        None,
        0x1,
        ctypes.byref(blob_out)
    )

    if not success:
        raise OSError("Falha ao criptografar dados via Windows DPAPI")

    try:
        encrypted_bytes = ctypes.string_at(blob_out.pbData, blob_out.cbData)
        return base64.b64encode(encrypted_bytes).decode("ascii")
    finally:
        _kernel32.LocalFree(blob_out.pbData)

def dpapi_decrypt(cipher_base64: str) -> str:
    """Descriptografa uma string base64 criptografada via DPAPI do Windows."""
    encrypted_bytes = base64.b64decode(cipher_base64.encode("ascii"))
    blob_in = DATA_BLOB()
    blob_in.cbData = len(encrypted_bytes)
    blob_in.pbData = ctypes.cast(ctypes.create_string_buffer(encrypted_bytes), ctypes.POINTER(ctypes.c_byte))

    blob_out = DATA_BLOB()

    success = _crypt32.CryptUnprotectData(
        ctypes.byref(blob_in),
        None,
        None,
        None,
        None,
        0x1,
        ctypes.byref(blob_out)
    )

    if not success:
        raise OSError("Falha ao descriptografar dados via Windows DPAPI")

    try:
        decrypted_bytes = ctypes.string_at(blob_out.pbData, blob_out.cbData)
        return decrypted_bytes.decode("utf-8")
    finally:
        _kernel32.LocalFree(blob_out.pbData)

def save_credentials(pat: str, country: str = "BR", client_id: str = "windows_ac_tray_app", device_id: str = "") -> None:
    """Salva as credenciais do usuário criptografadas no cofre seguro local."""
    payload = {
        "pat": pat.strip(),
        "country": country.strip().upper(),
        "client_id": client_id.strip(),
        "device_id": device_id.strip()
    }
    raw_json = json.dumps(payload, ensure_ascii=False)
    encrypted_data = dpapi_encrypt(raw_json)

    with open(_get_vault_file_path(), "w", encoding="ascii") as f:
        f.write(encrypted_data)

def load_credentials() -> Optional[Dict[str, str]]:
    """Carrega as credenciais se existirem; caso contrário verifica fallback do .env se presente."""
    vault_path = _get_vault_file_path()
    if os.path.exists(vault_path):
        try:
            with open(vault_path, "r", encoding="ascii") as f:
                encrypted_data = f.read().strip()
            if encrypted_data:
                decrypted_json = dpapi_decrypt(encrypted_data)
                return json.loads(decrypted_json)
        except Exception as e:
            print(f"[Aviso] Erro ao ler cofre seguro DPAPI: {e}", file=sys.stderr)

    # Fallback transparente para o arquivo .env se estiver em modo desenvolvimento
    pat = os.getenv("THINQ_PAT")
    if pat:
        return {
            "pat": pat,
            "country": os.getenv("THINQ_COUNTRY", "BR"),
            "client_id": os.getenv("THINQ_CLIENT_ID", "windows_ac_tray_app"),
            "device_id": os.getenv("THINQ_DEVICE_ID", "")
        }

    return None

def clear_credentials() -> None:
    """Remove as credenciais salvas do cofre local."""
    vault_path = _get_vault_file_path()
    if os.path.exists(vault_path):
        try:
            os.remove(vault_path)
        except OSError:
            pass

