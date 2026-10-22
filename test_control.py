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
DEVICE_ID = os.getenv("THINQ_DEVICE_ID", "947e6dea7dd7be07c5e1b7821664f80c1db9845fbf75d6d4f33c60d206d7ab3a")

async def send_command(payload: dict):
    async with ClientSession() as session:
        api = ThinQApi(session=session, access_token=PAT, country_code=COUNTRY, client_id=CLIENT_ID)
        print(f"\n[ENVIANDO COMANDO] Payload: {json.dumps(payload)}")
        result = await api.async_post_device_control(DEVICE_ID, payload)
        print(f"[RESPOSTA]: {result}")
        
        await asyncio.sleep(1)
        print("\n[VERIFICANDO NOVO STATUS DO APARELHO]...")
        status = await api.async_get_device_status(DEVICE_ID)
        status_data = status.body if hasattr(status, "body") else status
        temp = status_data.get("temperature", {})
        op = status_data.get("operation", {})
        flow = status_data.get("airFlow", {})
        mode = status_data.get("airConJobMode", {})
        
        print(f" -> Modo de Energia: {op.get('airConOperationMode')}")
        print(f" -> Temperatura Quarto: {temp.get('currentTemperature')} C")
        print(f" -> Temperatura Alvo: {temp.get('targetTemperature')} C")
        print(f" -> Modo de Operacao: {mode.get('currentJobMode')}")
        print(f" -> Velocidade Vento: {flow.get('windStrength')}")

async def interactive_menu():
    while True:
        print("\n" + "=" * 50)
        print("   CONTROLE DO AR CONDICIONADO (TESTE DO BEEP)")
        print("=" * 50)
        print(" [1] Ligar o ar (POWER ON)")
        print(" [2] Desligar o ar (POWER OFF)")
        print(" [3] Mudar temperatura alvo (ex: 21, 22, 23 C)")
        print(" [4] Ligar/Desligar Oscilacao Vertical (Swing)")
        print(" [5] Ligar/Desligar Luz do Visor (Display)")
        print(" [6] Apenas verificar status atual")
        print(" [0] Sair")
        print("=" * 50)
        
        choice = input("Escolha uma opcao (0-6): ").strip()
        
        if choice == "1":
            print("\nEnviando comando para LIGAR...")
            await send_command({"operation": {"airConOperationMode": "POWER_ON"}})
        elif choice == "2":
            print("\nEnviando comando para DESLIGAR...")
            await send_command({"operation": {"airConOperationMode": "POWER_OFF"}})
        elif choice == "3":
            temp_str = input("Digite a temperatura desejada (18 a 30): ").strip()
            try:
                t = float(temp_str)
                await send_command({"temperature": {"targetTemperature": t}})
            except ValueError:
                print("Valor invalido!")
        elif choice == "4":
            sub = input("Deseja ativar oscilacao? (s/n): ").strip().lower()
            await send_command({"windDirection": {"rotateUpDown": (sub == "s")}})
        elif choice == "5":
            sub = input("Luz do display (1: ON, 2: OFF): ").strip()
            mode = "ON" if sub == "1" else "OFF"
            await send_command({"display": {"light": mode}})
        elif choice == "6":
            await check_status_only()
        elif choice == "0":
            print("Saindo...")
            break
        else:
            print("Opcao invalida!")

async def check_status_only():
    async with ClientSession() as session:
        api = ThinQApi(session=session, access_token=PAT, country_code=COUNTRY, client_id=CLIENT_ID)
        status = await api.async_get_device_status(DEVICE_ID)
        status_data = status.body if hasattr(status, "body") else status
        temp = status_data.get("temperature", {})
        op = status_data.get("operation", {})
        flow = status_data.get("airFlow", {})
        mode = status_data.get("airConJobMode", {})
        swing = status_data.get("windDirection", {})
        disp = status_data.get("display", {})
        
        print("\n--- STATUS ATUAL DO AR CONDICIONADO ---")
        print(f" Potencia:       {op.get('airConOperationMode')}")
        print(f" Temp Quarto:    {temp.get('currentTemperature')} C")
        print(f" Temp Alvo:      {temp.get('targetTemperature')} C")
        print(f" Modo:           {mode.get('currentJobMode')}")
        print(f" Vento:          {flow.get('windStrength')} ({flow.get('windStrengthDetail')})")
        print(f" Oscilacao:      {'Ligada' if swing.get('rotateUpDown') else 'Desligada'}")
        print(f" Luz do Visor:   {disp.get('light')}")
        print("---------------------------------------")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == "power_on" or cmd == "on":
            asyncio.run(send_command({"operation": {"airConOperationMode": "POWER_ON"}}))
        elif cmd == "power_off" or cmd == "off":
            asyncio.run(send_command({"operation": {"airConOperationMode": "POWER_OFF"}}))
        elif cmd == "temp":
            val = float(sys.argv[2]) if len(sys.argv) > 2 else 22.0
            asyncio.run(send_command({"temperature": {"targetTemperature": val}}))
        elif cmd == "status":
            asyncio.run(check_status_only())
        else:
            print(f"Comando desconhecido: {cmd}")
    else:
        asyncio.run(interactive_menu())
