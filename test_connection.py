import os
import asyncio
import json
from aiohttp import ClientSession
from dotenv import load_dotenv
from thinqconnect import ThinQApi

load_dotenv()

PAT = os.getenv("THINQ_PAT")
COUNTRY = os.getenv("THINQ_COUNTRY", "BR")
CLIENT_ID = os.getenv("THINQ_CLIENT_ID", "windows_ac_tray_app")

async def main():
    print("=" * 60)
    print(" [TESTE DE CONEXAO LG THINQ - ETAPA 1]")
    print(f" Pais: {COUNTRY}")
    print(f" Client ID: {CLIENT_ID}")
    print(f" Token PAT: {PAT[:12]}...{PAT[-4:]}")
    print("=" * 60)
    
    async with ClientSession() as session:
        api = ThinQApi(
            session=session,
            access_token=PAT,
            country_code=COUNTRY,
            client_id=CLIENT_ID
        )
        
        print("\n1. Consultando lista de dispositivos...")
        try:
            device_list_resp = await api.async_get_device_list()
            print(f"Tipo retornado: {type(device_list_resp)}")
            
            devices = device_list_resp if isinstance(device_list_resp, list) else getattr(device_list_resp, "body", [])
            if not devices:
                print("Nenhum dispositivo encontrado na resposta:")
                print(device_list_resp)
                return

            print(f"\nDispositivos encontrados ({len(devices)}):")
            ac_devices = []
            for d in devices:
                d_id = d.get("deviceId")
                info = d.get("deviceInfo", {})
                d_type = info.get("deviceType", d.get("deviceType"))
                alias = info.get("alias", d.get("alias", "Sem nome"))
                model = info.get("modelName", d.get("modelName", "Modelo desconhecido"))
                print(f"  - [{d_type}] '{alias}' (Modelo: {model}, ID: {d_id})")
                if "AIR_CONDITIONER" in str(d_type).upper() or "AC" in str(d_type).upper():
                    ac_devices.append({"deviceId": d_id, "alias": alias, "model": model, "deviceInfo": info})

            if not ac_devices:
                print("\nAVISO: Nenhum ar condicionado identificado explicitamente.")
                print("Dados completos dos dispositivos:")
                print(json.dumps(devices, indent=2, ensure_ascii=False))
                return

            # Testar status do primeiro ar condicionado
            target_ac = ac_devices[0]
            target_id = target_ac.get("deviceId")
            print(f"\n2. Consultando status do Ar Condicionado: '{target_ac.get('alias')}'...")
            status_resp = await api.async_get_device_status(target_id)
            status_data = status_resp.body if hasattr(status_resp, "body") else status_resp
            print("Status retornado com sucesso!")
            print(json.dumps(status_data, indent=2, ensure_ascii=False))

            print("\n3. Consultando perfil de capacidades do aparelho...")
            profile_resp = await api.async_get_device_profile(target_id)
            profile_data = profile_resp.body if hasattr(profile_resp, "body") else profile_resp
            print("Perfil obtido com sucesso!")
            if isinstance(profile_data, dict):
                print(f"Chaves no perfil: {list(profile_data.keys())}")
                if "property" in profile_data:
                    print(f"Propriedades: {list(profile_data['property'].keys())}")
            else:
                print(f"Dados do perfil: {profile_data}")

            print("\n" + "=" * 60)
            print("CONEXAO REALIZADA COM SUCESSO TOTAL!")
            print("=" * 60)

        except Exception as e:
            print(f"\nERRO ao comunicar com LG ThinQ: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
