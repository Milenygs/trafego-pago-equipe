# Rotina diaria agendada (Task Scheduler: tarefa "AdsDiario-Mileny").
# 1. Varre todas as contas (diario.py varrer) -> gera relatorios/diario-HOJE.json
# 2. Envia resumo no Telegram (resumo_telegram.py)
# Se a varredura falhar, o resumo_telegram.py envia alerta de falha sozinho.
# Sem IA envolvida — 100% deterministico. O relatorio completo com acoes
# continua sendo o /ads-diario dentro do Claude Code.
$ErrorActionPreference = 'Continue'

$scripts = Join-Path $HOME 'OneDrive\.claude\skills\meta-ads-ratos\scripts'
$hoje = Get-Date -Format 'yyyy-MM-dd'
$log = Join-Path $env:TEMP "ads-diario-$hoje.log"

& python (Join-Path $scripts 'diario.py') varrer *> $log
& python (Join-Path $scripts 'resumo_telegram.py') *>> $log
# 3. Mudancas feitas no painel (Mileny e Tai) -> historico do cliente em Carteira (28/10/2026)
& python (Join-Path $scripts 'registrar_log.py') *>> $log
