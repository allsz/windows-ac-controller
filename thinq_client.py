"""
thinq_client.py - Cliente assincrono persistente para a LG ThinQ Connect API.

Uma unica thread de rede com event loop proprio e uma unica ClientSession (conexao HTTPS
reaproveitada) atendem todas as chamadas. Isso substitui o modelo anterior de "uma QThread +
event loop + sessao + leitura do cofre DPAPI por clique".

As chamadas sao serializadas por um asyncio.Lock, entao comandos rapidos chegam ao aparelho na
mesma ordem em que foram disparados e uma consulta de status nunca corre contra um comando.
Os resultados voltam a thread da interface por sinais Qt (conexao enfileirada automatica).
"""

import asyncio
import threading
from typing import Optional

from PySide6 import QtCore

import credentials_backend

REQUEST_TIMEOUT_SECONDS = 15


class NotConfiguredError(Exception):
    """Nao ha token PAT / device_id configurados."""


class ThinQClient(QtCore.QObject):
    status_updated = QtCore.Signal(dict)
    status_failed = QtCore.Signal()
    command_finished = QtCore.Signal(bool, str)

    def __init__(self, env_dir: Optional[str] = None, parent=None):
        super().__init__(parent)
        self._env_dir = env_dir
        self._start_lock = threading.Lock()
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._lock: Optional[asyncio.Lock] = None
        self._session = None
        self._api = None
        self._api_key = None
        self._closed = False

    # ------------------------------------------------------------------
    # API publica (chamada da thread da interface)
    # ------------------------------------------------------------------
    def get_status(self) -> None:
        self._submit(self._fetch_status(), self._on_status_done)

    def send_command(self, payload: dict) -> None:
        self._submit(self._post_command(payload), self._on_command_done)

    def close(self) -> None:
        """Encerra a thread de rede e fecha a sessao HTTP."""
        with self._start_lock:
            self._closed = True
            loop, thread = self._loop, self._thread
        if loop is None:
            return
        loop.call_soon_threadsafe(loop.stop)
        if thread is not None:
            thread.join(timeout=1.0)

    # ------------------------------------------------------------------
    # Infraestrutura do event loop
    # ------------------------------------------------------------------
    def _ensure_loop(self) -> Optional[asyncio.AbstractEventLoop]:
        with self._start_lock:
            if self._closed:
                return None
            if self._loop is not None:
                return self._loop

            loop = asyncio.new_event_loop()
            self._lock = asyncio.Lock()

            def runner():
                asyncio.set_event_loop(loop)
                try:
                    loop.run_forever()
                    pending = asyncio.all_tasks(loop)
                    for task in pending:
                        task.cancel()
                    loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                    loop.run_until_complete(self._drop_api())
                finally:
                    loop.close()

            self._loop = loop
            self._thread = threading.Thread(target=runner, name="thinq-client", daemon=True)
            self._thread.start()
            return loop

    def _submit(self, coro, callback) -> None:
        loop = self._ensure_loop()
        if loop is None:
            coro.close()
            return
        fut = asyncio.run_coroutine_threadsafe(coro, loop)
        fut.add_done_callback(callback)

    async def _drop_api(self) -> None:
        session, self._session, self._api, self._api_key = self._session, None, None, None
        if session is not None:
            await session.close()

    async def _get_api(self):
        """Retorna (api, device_id), recriando a sessao apenas quando as credenciais mudam."""
        creds = credentials_backend.resolve_credentials(self._env_dir)
        if not creds:
            raise NotConfiguredError("Credenciais LG ThinQ nao configuradas")

        key = (creds["pat"], creds.get("country", "BR"), creds.get("client_id", "windows_ac_tray_app"))
        if self._api is None or key != self._api_key:
            from aiohttp import ClientSession, ClientTimeout
            from thinqconnect import ThinQApi

            await self._drop_api()
            self._session = ClientSession(timeout=ClientTimeout(total=REQUEST_TIMEOUT_SECONDS))
            self._api = ThinQApi(
                session=self._session,
                access_token=key[0],
                country_code=key[1],
                client_id=key[2],
            )
            self._api_key = key
        return self._api, creds["device_id"]

    # ------------------------------------------------------------------
    # Operacoes (executam no event loop de rede)
    # ------------------------------------------------------------------
    async def _fetch_status(self):
        async with self._lock:
            api, device_id = await self._get_api()
            res = await api.async_get_device_status(device_id)
            return res.body if hasattr(res, "body") else res

    async def _post_command(self, payload: dict):
        async with self._lock:
            api, device_id = await self._get_api()
            print(f"[ThinQ] >> Enviando comando: {payload}", flush=True)
            res = await api.async_post_device_control(device_id, payload)
            print(f"[ThinQ] << Comando executado com sucesso: {res}", flush=True)
            return res

    # ------------------------------------------------------------------
    # Retorno para a thread da interface (emite sinais; Qt enfileira)
    # ------------------------------------------------------------------
    def _on_status_done(self, fut) -> None:
        try:
            data = fut.result()
        except NotConfiguredError:
            self.status_failed.emit()
            return
        except BaseException as e:  # inclui CancelledError no encerramento
            print("[ThinQ Status Error]:", repr(e), flush=True)
            self.status_failed.emit()
            return
        if data and isinstance(data, dict):
            print("[ThinQ] Status atualizado com sucesso do aparelho.", flush=True)
            self.status_updated.emit(data)
        else:
            self.status_failed.emit()

    def _on_command_done(self, fut) -> None:
        try:
            res = fut.result()
        except NotConfiguredError:
            return
        except BaseException as e:
            print(f"[ThinQ Command Error]: {e!r}", flush=True)
            self.command_finished.emit(False, str(e))
            return
        self.command_finished.emit(True, str(res))
