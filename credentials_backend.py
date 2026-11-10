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

def _get_app_data_dir(create: bool = False) -> str:
    """Retorna o diretório %APPDATA%/WTC LG. So cria a pasta quando create=True (gravacao),
    para que ler/consultar o cofre nunca recrie a pasta apos uma exclusao de dados."""
    appdata = os.getenv("APPDATA") or os.path.expanduser("~")
    target_dir = os.path.join(appdata, "WTC LG")
    if create:
        os.makedirs(target_dir, exist_ok=True)
    return target_dir

_legacy_migration_done = False


def _migrate_legacy_data_dir() -> None:
    """Migra dados da pasta legada LG-DualInverter-Controller para WTC LG (uma vez por execucao)."""
    global _legacy_migration_done
    if _legacy_migration_done:
        return
    _legacy_migration_done = True
    try:
        appdata = os.getenv("APPDATA") or os.path.expanduser("~")
        legacy_dir = os.path.join(appdata, "LG-DualInverter-Controller")
        target_dir = os.path.join(appdata, "WTC LG")
        if os.path.isdir(legacy_dir):
            legacy_vault = os.path.join(legacy_dir, "credentials.vault")
            target_vault = os.path.join(target_dir, "credentials.vault")
            if os.path.exists(legacy_vault) and not os.path.exists(target_vault):
                import shutil
                os.makedirs(target_dir, exist_ok=True)
                shutil.copy2(legacy_vault, target_vault)
            # Remove arquivos e diretório legado após migração
            import shutil
            shutil.rmtree(legacy_dir, ignore_errors=True)
    except Exception:
        pass

def _get_vault_file_path(create_dir: bool = False) -> str:
    return os.path.join(_get_app_data_dir(create_dir), "credentials.vault")

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

    # Gravacao atomica: escreve em arquivo temporario na mesma pasta e troca com os.replace,
    # assim um crash no meio da escrita nunca deixa o cofre truncado.
    vault_path = _get_vault_file_path(create_dir=True)
    tmp_path = vault_path + ".tmp"
    try:
        with open(tmp_path, "w", encoding="ascii") as f:
            f.write(encrypted_data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, vault_path)
    except Exception:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        raise

def load_credentials() -> Optional[Dict[str, str]]:
    """Carrega as credenciais se existirem; caso contrário verifica fallback do .env se presente."""
    _migrate_legacy_data_dir()
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

_resolved_cache = None


def resolve_credentials(env_dir: Optional[str] = None) -> Optional[Dict[str, str]]:
    """Retorna credenciais completas (PAT + device_id) do cofre DPAPI ou, em modo dev, do .env.

    Nao ha valor padrao para device_id: se faltar, retorna None.
    O resultado e reaproveitado enquanto o arquivo do cofre nao mudar (evita ler e
    descriptografar o DPAPI a cada chamada a API); salvar/limpar credenciais invalida sozinho.
    """
    global _resolved_cache
    stamp = _vault_stamp()
    if _resolved_cache is not None and _resolved_cache[0] == stamp and _resolved_cache[1] == env_dir:
        return _resolved_cache[2]
    result = _resolve_credentials_uncached(env_dir)
    _resolved_cache = (stamp, env_dir, result)
    return result


def _vault_stamp():
    try:
        st = os.stat(_get_vault_file_path())
        return (st.st_mtime_ns, st.st_size)
    except OSError:
        return None


def _resolve_credentials_uncached(env_dir: Optional[str]) -> Optional[Dict[str, str]]:
    creds = load_credentials()
    if creds and creds.get("pat") and creds.get("device_id"):
        return creds

    try:
        from dotenv import load_dotenv
        env_file = os.path.join(env_dir, ".env") if env_dir else None
        if env_file and os.path.exists(env_file):
            load_dotenv(env_file)
        else:
            load_dotenv()
    except ImportError:
        pass

    pat = os.getenv("THINQ_PAT")
    device_id = os.getenv("THINQ_DEVICE_ID")
    if not pat or not device_id:
        return None
    return {
        "pat": pat,
        "country": os.getenv("THINQ_COUNTRY", "BR"),
        "client_id": os.getenv("THINQ_CLIENT_ID", "windows_ac_tray_app"),
        "device_id": device_id,
    }

def clear_credentials() -> None:
    """Remove as credenciais salvas do cofre local."""
    vault_path = _get_vault_file_path()
    if os.path.exists(vault_path):
        try:
            os.remove(vault_path)
        except OSError:
            pass

def purge_all_app_data() -> None:
    """Exclui permanentemente todos os dados do aplicativo do computador (LGPD/GDPR):
    - Cofre DPAPI de credenciais (%APPDATA%/WTC LG e legado %APPDATA%/LG-DualInverter-Controller)
    - Preferências salvas no Registro do Windows (HKCU/Software/WTC LG e HKCU/Software/LGAirConditioner)
    - Inicialização automática com o Windows (HKCU/Software/Microsoft/Windows/CurrentVersion/Run)
    """
    import shutil
    import winreg
    from PySide6 import QtCore

    # 1. Limpa cofre de credenciais e diretórios no %APPDATA%
    appdata = os.getenv("APPDATA") or os.path.expanduser("~")
    for folder_name in ["WTC LG", "LG-DualInverter-Controller"]:
        dir_path = os.path.join(appdata, folder_name)
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path, ignore_errors=True)
            except Exception:
                pass

    # 2. Limpa QSettings
    try:
        prefs_wtc = QtCore.QSettings("WTC LG", "Preferences")
        prefs_wtc.clear()
        prefs_wtc.sync()
    except Exception:
        pass

    try:
        prefs_legacy = QtCore.QSettings("LGAirConditioner", "Preferences")
        prefs_legacy.clear()
        prefs_legacy.sync()
    except Exception:
        pass

    # 3. Limpa chaves do Registro para garantir remoção completa das árvores de software
    for reg_path in [r"Software\WTC LG", r"Software\LGAirConditioner"]:
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, reg_path + r"\Preferences")
        except Exception:
            pass
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, reg_path)
        except Exception:
            pass

    # 4. Remove do Run (Autostart)
    try:
        run_key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        for app_name in ["WTC LG", "LGAirConditioner"]:
            try:
                winreg.DeleteValue(run_key, app_name)
            except Exception:
                pass
        winreg.CloseKey(run_key)
    except Exception:
        pass

