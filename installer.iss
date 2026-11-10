; Instalador do WTC LG (Inno Setup 6)
; Uso: ISCC.exe /DAppVersion=1.0.0 installer.iss   (scripts\build.ps1 faz isso)

#define AppName "WTC LG"
#ifndef AppVersion
  #define AppVersion "1.0.0"
#endif
#define AppExe "WTC LG.exe"

[Setup]
; AppId identifica o app para atualizacoes: gere uma vez e NUNCA mude
AppId={{08F4B0C1-3690-4615-96C0-11F86A8BA24F}
AppName={#AppName}
AppVersion={#AppVersion}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
PrivilegesRequired=lowest
OutputDir=release
OutputBaseFilename=WTC-LG-Setup-{#AppVersion}
SetupIconFile=assets\app_icon.ico
UninstallDisplayIcon={app}\{#AppExe}
Compression=lzma2
SolidCompression=yes
CloseApplications=yes
WizardStyle=modern

; Assistente enxuto: sem boas-vindas, grupo do Menu Iniciar e tela "pronto para instalar".
; Resta a escolha da pasta de instalacao, a barra de progresso e a tela final (com a opcao de abrir o app).
; Em atualizacoes o Inno reutiliza a pasta da instalacao anterior (UsePreviousAppDir, padrao).
DisableWelcomePage=yes
DisableDirPage=no
DisableProgramGroupPage=yes
DisableReadyPage=yes

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "dist\WTC LG\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppExe}"

[Run]
Filename: "{app}\{#AppExe}"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent
; Instalacao silenciosa (usada pelo atualizador do app): reabre o app na bandeja, sem abrir o painel
Filename: "{app}\{#AppExe}"; Parameters: "--silent"; Flags: nowait runasoriginaluser; Check: WizardSilent

[UninstallRun]
; Fecha o app se estiver na bandeja, senao os arquivos ficam em uso e sobram na pasta
Filename: "{sys}\taskkill.exe"; Parameters: "/F /IM ""{#AppExe}"""; Flags: runhidden; RunOnceId: "KillWtcLg"

[CustomMessages]
brazilianportuguese.PurgeData=Deseja remover tambem suas credenciais LG ThinQ e preferencias deste computador?%n%nEscolha "Nao" para mante-las caso volte a instalar o WTC LG.
english.PurgeData=Do you also want to remove your LG ThinQ credentials and preferences from this computer?%n%nChoose "No" to keep them in case you reinstall WTC LG.

[Code]
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usUninstall then
  begin
    { Inicializacao com o Windows: sempre removida, senao sobra uma entrada apontando para um exe inexistente }
    RegDeleteValue(HKEY_CURRENT_USER, 'Software\Microsoft\Windows\CurrentVersion\Run', 'WTC LG');
  end;

  if CurUninstallStep = usPostUninstall then
  begin
    { Desinstalacao silenciosa nunca apaga dados do usuario }
    if not UninstallSilent then
    begin
      if MsgBox(CustomMessage('PurgeData'), mbConfirmation, MB_YESNO or MB_DEFBUTTON2) = IDYES then
      begin
        { Cofre DPAPI (credentials.vault) e preferencias (QSettings) }
        DelTree(ExpandConstant('{userappdata}\WTC LG'), True, True, True);
        RegDeleteKeyIncludingSubkeys(HKEY_CURRENT_USER, 'Software\WTC LG');
      end;
    end;
  end;
end;
