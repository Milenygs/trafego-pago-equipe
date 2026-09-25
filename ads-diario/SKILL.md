---
name: ads-diario
description: Rotina diaria de gestao Meta Ads para todos os clientes com um pedido so. Varre todas as contas do contas.yaml, traz gasto/leads/CPL de ontem vs baseline, alerta saldo e limite de gasto no fim, anuncios reprovados, aprendizado limitado, e sugere acoes numeradas que so sao aplicadas com ok da Mileny. Envia resumo no Telegram. Use quando o usuario disser: rotina diaria, diario, roda o diario, varre as contas, relatorio diario, como estao as contas hoje, checa os clientes, saldo das contas, otimiza tudo. Tambem dispara com /ads-diario.
---

# Ads Diário — Rotina de gestão com um pedido só

Camada de rotina sobre a skill `meta-ads-ratos`. Varre os clientes do
`contas.yaml`, gera diagnóstico com dados reais da API e propõe ações numeradas.

## Regras invioláveis

1. **NUNCA aplicar mudança nenhuma (orçamento, pausa, ativação, exclusão) sem
   ok explícito da usuária.** A rotina SUGERE; ela decide.
2. **Só reportar dados que vieram do JSON do digest.** Nunca inventar, estimar
   ou preencher valores ausentes; campo sem dado aparece como `—`.
3. Cliente com erro de API entra no relatório com o erro explicado (ex: token
   sem acesso à conta). Nunca omitir cliente.
4. Aprovação em bloco ("faz tudo", "aplica as de kascao") é ambígua: antes de
   executar, listar exatamente quais números serão aplicados e confirmar.

## Fluxo

### 1. Varredura

```powershell
python "$HOME\OneDrive\.claude\skills\meta-ads-ratos\scripts\diario.py" varrer
```

(No PowerShell, `~` entre aspas NÃO expande — usar sempre `$HOME`.)

- Só alguns clientes: `--clientes maroma,kascao`
- Rodada avulsa sem gravar relatório: `--sem-salvar`
- Clientes com `diario: false` no contas.yaml são pulados
- Demora ~1–2 min para 16 clientes (várias chamadas de API). Rodar e aguardar;
  não relançar em paralelo.

### 2. Leitura do digest

Ler `meta-ads-ratos/relatorios/diario-AAAA-MM-DD.json` com a data de **hoje**
usando a ferramenta Read — **NUNCA do stdout do PowerShell**, que corrompe
acentos (cp1252). O arquivo é gravado em UTF-8 correto.

- Se o arquivo de hoje não existir, a varredura falhou: diagnosticar o erro do
  script. **Nunca montar relatório com digest de dia anterior** sem avisar.
- Conferir `data_execucao` e `referencia` no topo do JSON.

Estrutura do digest:

- `resumo`: clientes_varridos, clientes_com_erro, clientes_pulados,
  gasto_total_ontem, leads_total_ontem, alertas_criticos, alertas_atencao
- `clientes[]`: slug, nome, conta, alertas[] (com `gravidade`: critico |
  atencao), saldo, ontem, d7, d30, campanhas_ontem, ads_problema,
  adsets_learning_limited — ou `pulado` / `erro`

### 2b. Decisões vigentes — ANTES de sugerir qualquer ação

Para cada cliente do digest, ler `$HOME\OneDrive\Carteira\<grupo>\<cliente>\decisoes.md`
(mapa em `Carteira\CLAUDE.md`). Criado em 17/09/2026 porque a rotina sugeria
desfazer otimizações que ela mesma tinha proposto dias antes.

- Ação que contradiz "Decisões em andamento" (dentro do prazo) ou "Já testado e
  descartado" **não entra** como sugestão. Se o dado for forte o bastante para
  rever, a ação entra marcada assim: "⚠️ revê a decisão de DD/MM", com o dado novo.
- Mudança feita há menos de 48h nunca vira recomendação de corte.

### 3. Relatório — SEMPRE no formato "Extrato da Carteira"

**O entregável é o HTML do Extrato publicado como Artifact, nunca uma tabela
markdown solta no chat.** Decidido pela Mileny em 03/09/2026: o formato do
relatório é o mesmo em todo pedido — a rotina automática das 9h, o pedido
avulso no chat ("me traz um relatório das contas X e Y"), o recorte de 3 dias,
o de um cliente só. Muda o conteúdo, nunca a forma.

1. Copiar CSS e estrutura de `meta-ads-ratos/references/extrato-carteira-template.html`
   e trocar os dados pelos do digest.
2. Gravar em `meta-ads-ratos/relatorios/extrato/extrato-AAAA-MM-DD.html`.
   Se já existir um extrato do dia, republicar o MESMO arquivo (mantém a URL);
   só criar arquivo novo em data nova.
3. Publicar com a ferramenta Artifact: favicon 📊, title `Extrato da Carteira`.
4. No chat, mandar só o link + 3 a 5 linhas do que é urgente. A leitura
   completa mora no artifact.

Ordem das seções (a mesma do template):

- **header** — h1 `Extrato da Carteira`, período, lede dizendo quais contas
  entraram e quais dias são fechados, e a faixa de KPIs
- **Saldo — quem para primeiro** — cards `.rw` com barra `.meter`, ordenados
  por urgência. Em conta pré-paga o número que vale é **o menor entre saldo e
  folga do limite de gasto** — em várias contas o limite trava antes do
  dinheiro, e o relatório tem que mostrar qual dos dois é
- **Franquias** — **direto em `Otimizações por conta`** (`.opts` com pares "o
  que fazer" `.do` e "por quê" `.why`), **sem bloco `.acct` por conta**: nada de
  tabela de campanhas nem `.read` (pedido da Mileny em 11/09/2026). O número que
  sustenta cada recomendação vai no `.why`; franquia sem gasto no dia entra numa
  linha `.note` no fim da seção
- **Lojas físicas**, **Desygn**, **Construtora** — bloco `.acct`
  por conta (cabeçalho com act_id e forma de pagamento, tabela de campanhas,
  parágrafo `.read` de leitura), uma seção por grupo que aparecer no pedido
- **Fora do Extrato desde 15/09/2026** (pedido da Mileny): Ponto Alpha (por
  enquanto), Casa e Jardim Móveis, Maderarte e Varanda e Piscina — em nenhuma seção.
  QualyFibras entrou nessa lista em 18/09/2026
- **Grupo TFS** (TrendPel, Saborazzi, AFS Indústria): a seção **voltou em 18/09/2026**,
  com um bloco `.acct` por conta. A linha abaixo fica só como histórico: **sem seção** desde
  15/09/2026, pedido da Mileny. Só a linha de saldo e o boleto acionável ficam
- **Verba: programado × gasto** — TODO DIA, logo depois do Saldo (pedido de
  15/09/2026). Gasto do dia × verba programada por conta (CBO, soma dos conjuntos
  ABO, vitalícia ÷ dias, programação por horário); "não bate" abaixo de 80% ou
  acima de 125%, sempre com a causa provável. Regra completa no Passo 2c do
  `meta-ads-ratos\prompts\extrato-diario.md`
- **Distribuição de conteúdo — franquias** — ÀS SEXTAS (e quando ela pedir), logo
  depois de Franquias: nível Espiral de cada conjunto, coerência dos criativos
  ativos com o nível, posts novos do Instagram e buracos de munição. Regra no
  Passo 2d do mesmo prompt
- **O que eu faria hoje** — `ol.acts`, em ordem de urgência
- **footer** — data, período, contas incluídas, e a frase de que nada foi
  aplicado

Regras de conteúdo que valem dentro do Extrato:

- `.read` e `.why` são leitura, não repetição da tabela: dizem o que o número
  significa e o que fazer com ele
- marcar `.good` / `.flag` nas células que sustentam a leitura
- pendência combinada (tarefas.yaml) e boleto acionável entram ANTES dos
  alertas de campanha, porque têm prazo externo
- comando exato (`update.py ad --id ... --status PAUSED`) dentro de `<code>`
  na otimização correspondente

Blocos de conteúdo que continuam valendo, no lugar equivalente do HTML:

```markdown
## Diário — DD/MM (dados de ontem, DD/MM)

**Resumo:** R$ X.XXX gastos · N leads · N alertas críticos · N atenção · N erros de acesso

### 📌 Para hoje
- **[cliente]** título da pendência combinada — com os passos na ordem.

### 🧾 Boletos
- **[cliente]** HOJE é dia de enviar o boleto de R$ X — vence em DD/MM (terça).

### 🔴 Alertas críticos
- **[cliente]** descrição do alerta (dado que o sustenta)

### 🟡 Atenção
- **[cliente]** descrição

### Por cliente
| Cliente | Gasto ontem | Leads | CPL ontem | CPL 30d | Situação |
|---|---|---|---|---|---|
| Cheirin Bão | R$ 210 | 4 | R$ 52,50 | R$ 44,10 | 🟡 |

### Ações sugeridas
1. **[kascao]** Pausar ad "Carrossel-V2" reprovado — `update.py ad --id 123 --status PAUSED`
2. ...

Responda com os números para aplicar (ex: "aplica 1 e 3").
```

Semântica: 🔴 = tem ≥1 alerta crítico · 🟡 = só alertas de atenção · 🟢 = sem
alertas. Cada ação sugerida traz o comando exato pronto, nunca genérico.

A seção **🧾 Boletos** vem do bloco `boletos` do digest e só aparece quando há
item `critico` ou `atencao` — em dia calmo, omitir a seção inteira. Ela vem
ANTES dos alertas de campanha porque é a única parte com prazo externo (o
cliente precisa receber e pagar). Detalhe da regra em "Calendário de boletos".

CPL usa a ação "lead" da conta; se o cliente mede outra coisa (compra, conversa
no WhatsApp), anotar no contas.yaml e adaptar a leitura.

### 4. Notificação Telegram

Depois do relatório no chat, enviar versão RESUMIDA (resumo geral + alertas
críticos + quantidade de ações sugeridas), em texto puro sem markdown, máx.
~3.500 caracteres:

```powershell
python "$HOME\OneDrive\.claude\skills\meta-ads-ratos\scripts\notify.py" telegram --text "..."
```

Se `TELEGRAM_BOT_TOKEN`/`TELEGRAM_CHAT_ID` não estiverem no .env da
meta-ads-ratos: avisar UMA vez nesta sessão, apontar o setup
(`notify.py --help` tem o passo a passo com @BotFather e `notify.py chat-id`)
e seguir em frente — nunca bloquear o relatório por causa do Telegram.

### 5. Aplicação das ações (só com ok)

Quando a usuária aprovar ("aplica 1 e 3"):

1. Se a aprovação for ambígua (regra inviolável 4), confirmar a lista primeiro.
2. Executar cada ação com os scripts da meta-ads-ratos (`update.py`,
   `advanced.py`...), respeitando as regras de segurança da skill (orçamento em
   centavos, ativar todos os níveis, rate limit).
3. Confirmar cada ação relendo o objeto na API — reportar o estado real, não o
   comando enviado.
4. Registrar cada ação aplicada na pasta do cliente em `OneDrive\Carteira`:
   `historico\<mês>.md` (no topo) + `decisoes.md` (linha nova com "esperar até").
   Essa é a regra da meta-ads-ratos; sem esse registro, a rotina de amanhã sugere desfazer.

## Configuração de metas por cliente

No `contas.yaml`, chaves opcionais que a rotina entende:

```yaml
  meu-cliente:
    cpl_alvo: 45.00          # alerta se CPL de ontem passar disso
    gasto_min_alerta: 20.00  # ignora alertas de CPL/lead abaixo desse gasto/dia
    diario: false            # tira o cliente da varredura
```

Sem `cpl_alvo`, a régua é o histórico da própria conta (CPL 30d + 30%).
Quando a usuária disser "o CPL alvo da Boali é X", gravar no contas.yaml.

## Pendências agendadas (tarefas.yaml)

Ação que a Mileny já decidiu e marcou para um dia ("amanhã de manhã ativamos
tudo junto"). Diferente do resto do relatório, **não é sugestão minha** — por
isso vai no TOPO, antes dos alertas e das ações sugeridas.

A agenda fica em `$HOME\OneDrive\Carteira\_Central\tarefas.yaml` desde 25/09/2026
(pasta compartilhada com a estagiária: a lista é a mesma nas duas máquinas).
Tarefa nova se escreve nesse arquivo, não dentro da skill.

Motor: `scripts/tarefas.py`, que só lê `tarefas.yaml` (não chama a API), pelo
mesmo motivo do boletos.py — o lembrete sai mesmo com a varredura quebrada.

```powershell
python "$HOME\OneDrive\.claude\skills\meta-ads-ratos\scripts\tarefas.py" hoje
python "$HOME\OneDrive\.claude\skills\meta-ads-ratos\scripts\tarefas.py" agenda
python "$HOME\OneDrive\.claude\skills\meta-ads-ratos\scripts\tarefas.py" concluir --id <slug>
```

Aparece no bloco `tarefas` do digest, no resumo das 7h e no Extrato das 9h. Item
não concluído vira `ATRASADA` e **continua cobrando todo dia** com a contagem de
dias — só sai com `concluir`. A `observacao` costuma ser a dependência que trava
a tarefa; nunca omitir do relatório.

Ao concluir uma tarefa que envolveu escrita na Meta, lembrar das duas regras que
vêm junto: registrar em `account_activities` do FlowTraffic (visível ao cliente)
e na pasta do cliente em `OneDrive\Carteira` (`historico\` + `decisoes.md`).

## Calendário de boletos (Grupo TFS / Açaí Fruit Show)

Regra combinada com a cliente: **pagamento sempre em terça ou quinta, boleto
enviado sempre na quinta, ciclo de 28 dias.** 28 (4 semanas) em vez de 30 trava
o dia da semana para sempre — 30 dias empurra a data 2 dias por mês e em dois
ciclos ela já cai fora de terça/quinta — e deixa ~2 dias de saldo sobrando por
ciclo, que é a margem para a conta nunca parar.

Motor: `scripts/boletos.py`, que só lê o contas.yaml (não chama a API). Por isso
o aviso continua saindo mesmo quando a varredura falha por rate limit ou token.

```powershell
python "$HOME\OneDrive\.claude\skills\meta-ads-ratos\scripts\boletos.py" agenda
python "$HOME\OneDrive\.claude\skills\meta-ads-ratos\scripts\boletos.py" hoje
```

Config por cliente no contas.yaml:

```yaml
    boleto:
      valor: 1000.00
      ciclo_dias: 28
      vencimento_ancora: "2026-09-22"   # 1º vencimento; nada antes dela é cobrado
      envio_dias_antes: 5               # 5 = quinta anterior a uma terça
      forma: prepago | cartao
```

Dois alertas saem daí, e eles são diferentes:

- **BOLETO** — vem do calendário: quando enviar, quando vence.
- **BOLETO_NAO_PAGO** — cruza o calendário com a API: o vencimento passou e o
  `funding_event_successful` da conta é anterior a ele, ou seja, o dinheiro não
  entrou. É o alerta que o calendário sozinho nunca pegaria.

⚠️ Conta com `forma: cartao` (hoje só a Açaí Indústria, VISA *3859) **não tem
saldo pré-pago nem evento de recarga** — ali o calendário é só previsão, e o
sinal real de que parou é `status_conta: PENDENCIA_PAGAMENTO` / `valor_a_faturar`.
Não confiar no BOLETO_NAO_PAGO nessa conta; confiar no alerta de status.

Ao mudar valor ou ciclo, mexer TAMBÉM em `orcamento_ciclo_valor`/`_dias`, que é
o que gera o RITMO_ACIMA_DO_ORCAMENTO — se o boleto não cobre o ritmo de gasto,
é esse alerta que avisa antes do saldo acabar.

## Fora do escopo da rotina

Perguntas avulsas ("compara essa semana com a passada na Desygn") usam direto
os scripts da meta-ads-ratos (`insights.py --time-ranges`). Esta skill é só a
rotina; a caixa de ferramentas é a outra.

## Automação (ativa desde 2026-07-16)

Três camadas automáticas — as duas primeiras rodam sem IA, a terceira é o
relatório interpretado. Esta skill continua servindo para o pedido avulso no
chat:

1. **Local, 7h (Task Scheduler "AdsDiario-Mileny")**: roda
   `scripts/rodar-diario.ps1` → `diario.py varrer` + `resumo_telegram.py`
   (resumo determinístico no Telegram, sem IA). Se a varredura falhar, o
   próprio `resumo_telegram.py` envia alerta de falha no Telegram.
   Só funciona com o PC ligado.
2. **Nuvem, 7h (rotina claude.ai "Diario Meta Ads — resumo push")**: agente na
   nuvem lê as contas pelo conector facebook e envia notificação push pro app
   do Claude — funciona com o PC desligado. Somente leitura. Gerenciar em
   https://claude.ai/code/routines (id trig_01GCY7E61c7RtiiptmAw745B).
3. **Local, 9h (Task Scheduler "ExtratoCarteira-Mileny", ativa desde
   2026-09-02)**: roda `scripts/rodar-extrato.ps1`, que chama o Claude Code em
   modo headless (`claude -p`) com o prompt
   `meta-ads-ratos/prompts/extrato-diario.md`. Esse é o relatório **completo e
   interpretado** — o "Extrato da Carteira": régua de saldo, bloco por conta com
   tabela de campanhas e leitura, otimizações por conta, e "O que eu faria hoje".
   Gera `relatorios/extrato/extrato-AAAA-MM-DD.html`, publica como Artifact e
   manda o resumo + link no Telegram.
   A tarefa tem `StartWhenAvailable`: se o PC estiver desligado às 9h, ela roda
   assim que ligar. Log em `%TEMP%\extrato-carteira-AAAA-MM-DD.log`.
   O padrão visual e a ordem das seções vêm de
   `references/extrato-carteira-template.html` (base: relatório de 31/08/2026) —
   mexer no template muda o relatório de amanhã.
   A allowlist de ferramentas do `rodar-extrato.ps1` é proposital: só scripts de
   leitura + notify. `update.py`, `create.py`, `delete.py` e `advanced.py` estão
   fora, então a rotina não consegue aplicar nada mesmo se quisesse.

⚠️ Ao adicionar/remover cliente da rotina, atualizar TRÊS lugares: contas.yaml
(flag `diario`), e a lista de contas no prompt da rotina da nuvem.

O resumo local das 7h abre com o bloco 🧾 BOLETOS quando há algo a fazer no dia
(silencioso em dia calmo).

A tarefa "RecargaTFS-Mileny" foi **desativada em 02/09/2026** (Disabled, não
excluída — reverter com `Enable-ScheduledTask -TaskName RecargaTFS-Mileny`).
Ela mandava um lembrete quinzenal fixo com os valores antigos (R$250/500/750)
e ficou redundante quando o aviso de boleto entrou no resumo diário. O script
`lembrete_recarga_tfs.py` continua no repositório e já lê o calendário certo,
caso alguém reative a tarefa.

Se a usuária relatar que o resumo das 7h não chegou: checar a tarefa local
(`Get-ScheduledTask AdsDiario-Mileny`), o log em `%TEMP%\ads-diario-AAAA-MM-DD.log`,
e a rotina na nuvem no link acima.
