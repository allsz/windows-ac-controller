# LG Dual Inverter - Windows 11 System Tray App

Aplicativo moderno para a bandeja do sistema (System Tray) do Windows 11/10 para controle em tempo real do ar-condicionado **LG Dual Inverter Voice** via nuvem **LG ThinQ API**.

Desenvolvido em **Python 3.11+** com **PySide6 (Qt)**, inspirado nas diretrizes visuais do macOS e flyouts modernos do Windows 11 (Dark Glass, Glassmorphism e micro-animações a 60 FPS).

---

## Recursos e Destaques

- **Flyout Inteligente na Bandeja:** Posicionamento automático próximo ao relógio/área de notificação com auto-ocultação ao perder foco.
- **Sincronização Bidirecional em Tempo Real:** Consulta assíncrona do status real do aparelho na nuvem LG ThinQ sem travar a interface gráfica.
- **Hero Split Animado:** Cortina de vento volumétrica e suave (Option A) que se expande, ondula e curva suavemente em direção a $+X$, acompanhando o estado de energia do aparelho.
- **Cores Dinâmicas por Modo de Operação:**
  - **Cool:** Cortina azul ciano suave
  - **Heat:** Cortina em tom quente suave
  - **Fan:** Cortina cinza neutro
  - **Dry:** Cortina verde menta suave
- **Controle de Temperatura de Alta Precisão:**
  - Steppers vetoriais centralizados `(+)` e `(−)` com limites seguros (18°C a 30°C).
  - Slider customizado com trilha contínua em gradiente e efeito de arrasto fluido com debounce inteligente (400ms).
- **Cards Interativos:**
  - **Mode:** Seleção rápida entre Cool, Heat, Fan e Dry.
  - **Fan Speed:** Rotação horária suave do ícone ao passar o mouse ou quando selecionado.
  - **Sleep:** Temporizadores rápidos (1h, 2h, 4h, 8h ou Off).
  - **Airflow:** Controle de oscilação contínua (*Swing*) e aleta fixa (*Vertical*) com animação fluida.
- **Modo Eco:** Interruptor animado para desligar ou ligar a luz do visor do ar-condicionado.

---

## Pré-requisitos

1. **Python 3.10+** (recomendado Python 3.11 ou 3.12).
2. Conta de desenvolvedor ou token pessoal de acesso (**PAT - Personal Access Token**) da LG ThinQ obtido em [LG ThinQ Connect](https://thinqconnect.lgthinq.com).

---

## Instalação

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd "Ar Condicionado"
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
# No Windows PowerShell:
venv\Scripts\Activate.ps1
# Ou no CMD:
venv\Scripts\activate.bat
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

---

## Configuração

Copie o arquivo de exemplo `.env.example` para `.env`:
```bash
copy .env.example .env
```

Edite o arquivo `.env` com suas credenciais:
```ini
THINQ_PAT=thinqpat_seu_token_aqui
THINQ_COUNTRY=BR
THINQ_CLIENT_ID=windows_ac_tray_app
THINQ_DEVICE_ID=seu_device_id_aqui
```

> **Dica:** Para descobrir o `DEVICE_ID` do seu ar-condicionado, execute:
> ```bash
> python test_connection.py
> ```
> O script listará todos os aparelhos LG vinculados à sua conta com os respectivos IDs.

---

## Como Executar

Para iniciar o aplicativo na bandeja do sistema:
```bash
python ui_panel.py
```

- Clique com o botão esquerdo no ícone da bandeja para abrir/fechar o painel flutuante.
- Clique com o botão direito para o menu de contexto (Abrir Painel / Sair).

---

## Compilando para Executável Windows (.exe)

Para gerar o instalador/executável independente (sem necessidade de ter Python instalado na máquina):

1. Instale o PyInstaller:
```bash
pip install pyinstaller
```

2. Execute o comando de build incluindo a pasta de assets:
```bash
pyinstaller --noconsole --onefile --windowed --add-data "assets;assets" --icon="assets/eco.png" --name "LGAirConditioner" ui_panel.py
```

O executável final será gerado na pasta `dist/LGAirConditioner.exe`. Certifique-se de colocar o arquivo `.env` no mesmo diretório do `.exe`.

---

## Estrutura do Projeto

```text
├── assets/                 # Ícones vetoriais SVG, assets gráficos e frames
├── scratch/                # Scripts de testes unitários e validações visuais
├── .env.example            # Template de variáveis de ambiente seguras
├── .gitignore              # Regras de exclusão para Git
├── requirements.txt        # Dependências do projeto
├── test_connection.py      # Diagnóstico e descoberta de dispositivos LG
├── test_control.py         # Teste interativo via terminal
└── ui_panel.py             # Aplicativo principal (GUI PySide6 + LG ThinQ)
```

---

## Licença

Projeto desenvolvido para fins de estudo e automação residencial pessoal.
