# Gera os artefatos do release: instalador (Inno Setup) e ZIP portatil.
# Uso (na raiz do projeto):  powershell -ExecutionPolicy Bypass -File scripts\build.ps1

$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

# Versao unica: __version__ em ui_panel.py
$match = Select-String -Path ui_panel.py -Pattern '^__version__\s*=\s*"([^"]+)"'
if (-not $match) { throw "__version__ nao encontrado em ui_panel.py" }
$version = $match.Matches[0].Groups[1].Value
Write-Host "==> Versao: $version"

$pyinstaller = "venv\Scripts\pyinstaller.exe"
if (-not (Test-Path $pyinstaller)) { throw "PyInstaller nao encontrado. Rode: venv\Scripts\python.exe -m pip install pyinstaller" }

$iscc = @(
    "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "$env:ProgramFiles\Inno Setup 6\ISCC.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $iscc) { throw "Inno Setup 6 nao encontrado (https://jrsoftware.org/isdl.php)" }

Write-Host "==> Limpando build anterior"
Remove-Item -Recurse -Force build, dist, release -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force release | Out-Null

Write-Host "==> PyInstaller"
& $pyinstaller "WTC LG.spec" --noconfirm --clean
if ($LASTEXITCODE -ne 0) { throw "PyInstaller falhou" }

Write-Host "==> Instalador (Inno Setup)"
& $iscc "/DAppVersion=$version" installer.iss
if ($LASTEXITCODE -ne 0) { throw "Inno Setup falhou" }

Write-Host "==> ZIP portatil"
$zip = "release\WTC-LG-Portable-$version.zip"
Compress-Archive -Path "dist\WTC LG" -DestinationPath $zip -Force

Write-Host "==> SHA256"
@(Get-ChildItem release -File) | ForEach-Object {
    $hash = (Get-FileHash $_.FullName -Algorithm SHA256).Hash.ToLower()
    "{0}  {1}" -f $hash, $_.Name
} | Tee-Object -FilePath release\SHA256SUMS.txt

Write-Host "`nPronto. Arquivos em release\"
