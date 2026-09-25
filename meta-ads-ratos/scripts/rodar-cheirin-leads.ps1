# Planilha de controle de leads da Cheirin Bao MT (Task Scheduler: "CheirinLeadsControle-Mileny").
# Roda o cheirin_leads_controle.py (sem IA) e grava relatorios\controle\cheirin-leads-controle.xlsx.
# Se falhar, avisa no Telegram - falha silenciosa foi o problema das rotinas em setembro.
#
# Rodar na mao:  powershell -ExecutionPolicy Bypass -File rodar-cheirin-leads.ps1
$ErrorActionPreference = 'Continue'

$scripts = Join-Path $HOME 'OneDrive\.claude\skills\meta-ads-ratos\scripts'
$hoje    = Get-Date -Format 'yyyy-MM-dd'
$log     = Join-Path $env:TEMP "cheirin-leads-$hoje.log"

"=== inicio $(Get-Date -Format 'HH:mm:ss') ===" | Out-File $log -Append -Encoding utf8
# Saida do Python em UTF-8 no log (com *>> o PowerShell 5.1 gravava UTF-16 no meio do arquivo UTF-8).
$env:PYTHONIOENCODING = 'utf-8'
& python (Join-Path $scripts 'cheirin_leads_controle.py') 2>&1 | ForEach-Object { "$_" } | Out-File $log -Append -Encoding utf8
$code = $LASTEXITCODE
"=== fim $(Get-Date -Format 'HH:mm:ss') - exit $code ===" | Out-File $log -Append -Encoding utf8

if ($code -ne 0) {
    $msg = "Planilha de leads da Cheirin nao atualizou ($hoje, exit $code). Log: $log"
    & python (Join-Path $scripts 'notify.py') telegram --text $msg *>> $log
}
exit $code
