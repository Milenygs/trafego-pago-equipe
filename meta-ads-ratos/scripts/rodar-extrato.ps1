# Extrato da Carteira - relatorio diario completo (Task Scheduler: "ExtratoCarteira-Mileny").
# Roda o Claude Code em modo headless com o prompt de prompts/extrato-diario.md:
# varre as contas, monta o HTML no padrao do template, publica o artifact e
# manda o resumo no Telegram.
#
# Diferente da tarefa das 7h (AdsDiario-Mileny), que e deterministica e sem IA:
# esta aqui e o relatorio interpretado, com leitura e acoes sugeridas.
#
# A allowlist abaixo e proposital e restrita: so leitura da API (diario.py,
# insights.py, read.py, boletos.py) e envio de Telegram. Os scripts que ESCREVEM
# na Meta (update, create, delete, advanced) ficam de fora de proposito - o
# relatorio sugere, quem aplica e a Mileny.
#
# Rodar na mao:  powershell -ExecutionPolicy Bypass -File rodar-extrato.ps1
$ErrorActionPreference = 'Continue'

$skills = Join-Path $HOME 'OneDrive\.claude\skills'
$prompt = Join-Path $skills 'meta-ads-ratos\prompts\extrato-diario.md'
$hoje   = Get-Date -Format 'yyyy-MM-dd'
$log    = Join-Path $env:TEMP "extrato-carteira-$hoje.log"

# ATENCAO (corrigido 04/09/2026): regra de permissao casa por PREFIXO. Os padroes
# antigos tinham curinga no meio ('python *diario.py*') e NUNCA casavam - a tarefa
# falhava 100% silenciosa: sem varredura, sem relatorio, sem alerta, exit 0.
# Agora: prefixo de verdade, com o caminho relativo ao cwd ($skills).
$tools = @(
    'Read', 'Write', 'Edit', 'Glob', 'Grep', 'Artifact',
    'Bash(python meta-ads-ratos\scripts\diario.py:*)',
    'Bash(python meta-ads-ratos\scripts\insights.py:*)',
    'Bash(python meta-ads-ratos\scripts\read.py:*)',
    'Bash(python meta-ads-ratos\scripts\boletos.py:*)',
    'Bash(python meta-ads-ratos\scripts\tarefas.py:*)',
    'Bash(python meta-ads-ratos\scripts\notify.py:*)'
)

Set-Location $skills

"=== Extrato da Carteira - inicio $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" | Out-File $log -Encoding utf8

# A varredura roda AQUI, no PowerShell, e nao dentro do Claude. Assim o passo mais
# importante do relatorio nao depende de nenhuma regra de permissao casar.
$varrer = Join-Path $skills 'meta-ads-ratos\scripts\diario.py'
"--- varredura (PowerShell) $(Get-Date -Format 'HH:mm:ss') ---" | Out-File $log -Append -Encoding utf8
# stdout do diario.py e o digest inteiro (megabytes de JSON) — vai pro $null; o
# arquivo ja e gravado pelo proprio script. So o progresso (stderr) entra no log.
& python $varrer varrer 1>$null 2>>$log
$codeVarr = $LASTEXITCODE

$digest = Join-Path $skills "meta-ads-ratos\relatorios\diario-$hoje.json"
if ($codeVarr -ne 0 -or -not (Test-Path $digest)) {
    $msg = "Extrato da Carteira nao rodou hoje ($hoje): a varredura falhou (exit $codeVarr) e nao gerou o digest. Log: $log"
    "!! $msg" | Out-File $log -Append -Encoding utf8
    & python (Join-Path $skills 'meta-ads-ratos\scripts\notify.py') telegram --text $msg *>> $log
    "=== fim $(Get-Date -Format 'HH:mm:ss') - abortado na varredura ===" | Out-File $log -Append -Encoding utf8
    exit 1
}
"--- digest OK: $digest ---" | Out-File $log -Append -Encoding utf8

$texto = Get-Content $prompt -Raw -Encoding UTF8

# O relatorio leva ~10 min de geracao e a conexao ja caiu no meio ("Response
# stalled mid-stream", 04/09). Uma queda dessas custava o relatorio do dia
# inteiro, entao: duas tentativas. A varredura NAO repete — o digest ja existe.
$code = 1
foreach ($tentativa in 1..2) {
    "--- claude -p (tentativa $tentativa) $(Get-Date -Format 'HH:mm:ss') ---" |
        Out-File $log -Append -Encoding utf8
    $texto | & claude -p --model opus --allowed-tools @tools *>> $log
    $code = $LASTEXITCODE
    if ($code -eq 0) { break }
    if ($tentativa -lt 2) {
        "--- tentativa $tentativa falhou (exit $code); repetindo em 60s ---" |
            Out-File $log -Append -Encoding utf8
        Start-Sleep -Seconds 60
    }
}

"--- claude terminou (exit $code) $(Get-Date -Format 'HH:mm:ss') ---" | Out-File $log -Append -Encoding utf8

# ============================================================================
# ENTREGA - roda no PowerShell de proposito (corrigido 09/09/2026)
# ============================================================================
# Por que aqui e nao dentro do Claude: entre 05 e 07/09 a tarefa montou o
# relatorio certo tres dias seguidos e nao entregou nenhum. Em sessao headless,
# (1) Write em 'meta-ads-ratos\relatorios\extrato\' e barrado como "sensitive
# file" (o caminho tem .claude no meio e a trava vence o allowlist), (2) toda
# chamada a python pede approval que ninguem concede, e (3) nao existe tool de
# publicar Artifact nem de mandar Telegram. Resultado: relatorio 100% pronto,
# preso na maquina, falha silenciosa.
#
# A saida e a mesma que resolveu a varredura em 04/09: tirar o passo do Claude.
# O prompt agora so GRAVA em $env:TEMP (que passa liso) e este bloco publica.
$notify = Join-Path $skills 'meta-ads-ratos\scripts\notify.py'
$destino = Join-Path $skills "meta-ads-ratos\relatorios\extrato\extrato-$hoje.html"
$resumoTxt = Join-Path $env:TEMP "extrato-telegram-$hoje.txt"

# O HTML pode estar em qualquer um dos tres lugares que ja funcionaram em sessao
# headless. Ordem de preferencia: Temp (o combinado), Desktop e destino oficial.
$candidatos = @(
    (Join-Path $env:TEMP "extrato-$hoje.html"),
    (Join-Path $HOME "OneDrive\Desktop\extrato-carteira-$hoje.html"),
    $destino
)
$html = $candidatos | Where-Object { Test-Path $_ } | Select-Object -First 1

if ($html) {
    "--- HTML encontrado: $html ---" | Out-File $log -Append -Encoding utf8
    if ($html -ne $destino) {
        $pastaDestino = Split-Path $destino -Parent
        if (-not (Test-Path $pastaDestino)) {
            New-Item -ItemType Directory -Force -Path $pastaDestino | Out-Null
        }
        Copy-Item $html $destino -Force
        "--- copiado para $destino ---" | Out-File $log -Append -Encoding utf8
    }
} else {
    "!! nenhum HTML encontrado nos caminhos conhecidos" | Out-File $log -Append -Encoding utf8
}

# 1) o resumo em texto. --file existe justamente porque o tool PowerShell corta
#    comando em 965 bytes e o resumo tem ~3.500 chars.
if (Test-Path $resumoTxt) {
    & python $notify telegram --file $resumoTxt *>> $log
    "--- resumo enviado no Telegram ---" | Out-File $log -Append -Encoding utf8
} elseif ($html) {
    & python $notify telegram --text "Extrato da Carteira de $hoje pronto - o resumo em texto nao foi gerado, o relatorio completo vai no anexo." *>> $log
}

# 2) o relatorio em si, como anexo. Em sessao headless nao ha como publicar
#    Artifact, entao o anexo e o jeito de o relatorio chegar no celular dela.
if ($html) {
    & python $notify document --path $destino --caption "Extrato da Carteira - $hoje" *>> $log
    "--- HTML enviado como anexo ---" | Out-File $log -Append -Encoding utf8
}

# 3) nada pronto: avisa. Falha silenciosa foi o problema de setembro inteiro.
if (-not $html -and $code -eq 0) {
    & python $notify telegram --text "Extrato da Carteira ($hoje): o Claude rodou sem erro mas nao deixou o HTML em nenhum caminho conhecido. Log: $log" *>> $log
}

"=== fim $(Get-Date -Format 'HH:mm:ss') - exit $code ===" | Out-File $log -Append -Encoding utf8

# Se o Claude nem rodou, o resumo no Telegram nunca sai - avisa aqui.
# Este bloco roda no PowerShell de proposito: e o unico caminho de aviso que nao
# depende do Claude nem de regra de permissao (ver historico 04/09/2026).
if ($code -ne 0) {
    $msg = "Extrato da Carteira nao rodou hoje ($hoje). Duas tentativas falharam (ultimo exit $code). A varredura funcionou e o digest esta gravado; faltou so o relatorio. Log: $log"
    & python $notify telegram --text $msg *>> $log
}

exit $code
