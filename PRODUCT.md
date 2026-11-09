# Product

<!-- impeccable:product-schema 1 -->

## Platform

adaptive

## Stack

Python 3.11+, PySide6 (Qt for Python), LG ThinQ API (Connect Cloud)

## Users

Usuários de ar-condicionado LG Dual Inverter no Windows buscando controle prático, ágil e não obstrutivo diretamente da sua estação de trabalho, sem precisar desbloquear o celular, abrir o app ThinQ ou procurar o controle remoto físico.

## Product Purpose

Prover um painel flutuante ultra-rápido na bandeja do sistema (System Tray) para monitoramento de temperatura ambiente e controle completo das funções essenciais do ar-condicionado em tempo real, integrando-se organicamente à experiência nativa do Windows 11.

## Positioning

Um flyout leve, com latência imperceptível, feedback visual animado do fluxo de ar e zero intermediários na nuvem: o aplicativo conecta a máquina local diretamente aos servidores oficiais da LG sem coletar telemetria ou passar por servidores de terceiros.

## Operating Context

- Executado continuamente em segundo plano minimizado na bandeja do Windows (System Tray).
- Aberto instantaneamente com um único clique no ícone perto do relógio do Windows 11/10.
- Fecha/recede automaticamente ao perder o foco (auto-hide padrão de flyouts do SO) para não atrapalhar o fluxo de trabalho do usuário.
- Ambiente de trabalho, escritório doméstico ou gaming desk onde o conforto térmico precisa ser ajustado com 1 a 2 cliques.

## Capabilities and Constraints

- **Formato:** Executável portátil para Windows com auto-start opcional silencioso no boot do SO via Registro (HKCU).
- **Segurança e Privacidade:** Credenciais locais protegidas na máquina do usuário (DPAPI / Windows Credential Manager) sem backend intermediário.
- **Fidelidade ao Hardware:** Respeito absoluto às regras e modos do equipamento físico (ex: controle de temperatura desativado no modo Fan / Ventilação).
- **Temas Dinâmicos:** Adaptação contínua e suporte a Dark Glass, True Black OLED e Light Mode sincronizados ou manuais.
- **Micro-animações e Hardware Acceleration:** Hero split com cortina de ar suave e aleta dinâmica a 60 FPS via PySide6 / QtSvg.

## Brand Commitments

- **Identidade:** LG Dual Inverter Voice Controller / Windows AC Controller.
- **Linguagem Visual:** Inspirado na fluidez e vidro escuro do macOS combinado à geometria limpa e cantos arredondados do Windows 11.
- **Tom de Voz:** Direto, técnico, polido e confiável.

## Evidence on Hand

- Código funcional e polido em `windows-ac-controller/ui_panel.py`.
- Mockups em alta fidelidade gerados no README (`assets/app_mockup_*.png`).
- Ícone moderno transparente em formato vetorial e ICO (`assets/ac-icon.png`, `assets/app_icon.ico`).
- Script de teste de conectividade com a API da LG (`test_connection.py`).

## Product Principles

1. **Invisível até ser necessário:** Foco absoluto em discrição na bandeja do sistema, sem janelas intrusivas ou alertas desnecessários.
2. **Fidelidade ao estado real:** O painel reflete o status verdadeiro do aparelho na nuvem, sem estados fantasma.
3. **Respeito à física do dispositivo:** As restrições visuais e interativas do app espelham exatamente as limitações operacionais da máquina física.
4. **Zero invasão de privacidade:** Todas as credenciais e conexões são ponto a ponto entre o cliente e a LG.

