# Extrato da Carteira — relatório diário automático

Você está rodando sem a Mileny presente, disparado pela tarefa agendada
`ExtratoCarteira-Mileny` (9h, ou assim que o PC liga). Produza o relatório
completo do dia. Trabalhe até o fim sozinho.

**Você não entrega — você grava.** Ao terminar, deixe dois arquivos no `%TEMP%`:
`extrato-AAAA-MM-DD.html` (o relatório) e `extrato-telegram-AAAA-MM-DD.txt` (o
resumo). O `rodar-extrato.ps1` copia, publica e manda no Telegram depois. Os
detalhes estão nos Passos 3 e 5 — leia antes de gravar qualquer coisa.

## Regras invioláveis

1. **NÃO aplique mudança nenhuma** — nem pausa, nem orçamento, nem ativação.
   Este relatório só diagnostica e sugere. Nada de `update.py`, `create.py`,
   `delete.py`, `advanced.py`.
2. **Só reporte número que veio do digest.** Nunca estime, nunca preencha
   buraco. Campo sem dado é `—`.
3. Conta com erro de API entra no relatório com o erro explicado. Nunca omita
   cliente.
4. Se a varredura falhar, não monte relatório com digest de dia anterior —
   mande o alerta de falha no Telegram (passo 5) e pare.

## Passo 1 — A varredura JÁ FOI FEITA

O `rodar-extrato.ps1` roda `diario.py varrer` no PowerShell **antes** de te chamar, e
só te invoca se o digest de hoje existir. **Não rode a varredura de novo** — ela leva
1–2 min e a segunda rodada só queima rate limit da conta.

Vá direto para o Passo 2. Se por algum motivo o digest de hoje não existir, pare e
avise pelo Telegram (Passo 5) — não monte relatório com o digest de ontem.

(Mudou em 04/09/2026: antes esse passo era seu. A tarefa agendada falhava 100%
silenciosa porque a regra de permissão do `python` tinha curinga no meio e nunca
casava — sem varredura, sem relatório, sem alerta, `exit 0`.)

## Passo 2 — Ler o digest

Leia com a ferramenta Read (nunca pelo stdout, que corrompe acento):

`meta-ads-ratos/relatorios/diario-AAAA-MM-DD.json` — data de HOJE.

### As 15 contas que a Mileny pediu (09/09/2026)

Essas são a espinha do relatório e **entram sempre**, mesmo com gasto zero — conta
parada é informação, não ausência de informação:

| Grupo | Contas |
|---|---|
| Franquias | Facilmart, Cheirin Bão MT, Boali, Açaí Fruit Show (franquia), Kascão CA 02 |
| Grupo TFS — indústria e revenda | TrendPel, Saborazzi, Açaí Fruit Show Indústria |
| Lojas físicas AFS | Teixeira de Freitas, Osasco, Loja FSA (Fraga/Maia) |
| Móveis e hospedagem | Desygn Móveis Jardim, Casa de Vidro Paraty |
| Marca/lojas | Cheirin Bão MKT |

⚠️ **Fora do relatório desde 15/09/2026, a pedido da Mileny:** **Ponto Alpha** ("por
enquanto" — ela avisa quando volta), **Casa e Jardim Móveis**, **Maderarte** e **Varanda
e Piscina**. **QualyFibras** também saiu, a pedido dela em 18/09/2026. Não entram em
nenhuma seção: nem corpo, nem saldo, nem verba, nem "Outras contas com gasto", nem
"O que eu faria hoje", nem distribuição de conteúdo. A varredura pode continuar lendo
essas contas; o relatório é que não as mostra.

✅ **Grupo TFS VOLTOU ao relatório em 18/09/2026**, a pedido da Mileny. Ele tinha
saído em 15/09. A seção "Grupo TFS — indústria e revenda" volta completa: um bloco
`.acct` por conta, com tabela de campanhas e `.read`, e o KPI "Leads B2B" no header.
As otimizações de mídia voltam a entrar em "O que eu faria hoje". A linha na régua
de **Saldo** (quando pré-paga) e o **boleto** continuam como antes.

A varredura continua ampla (todas as contas com `diario: true`). As demais que
tiverem gastado no dia entram numa seção curta **"Outras contas com gasto"** no
fim, uma linha cada (conta, gasto, leads, CPL, um alerta se houver) — assim
nenhum cliente some do radar, mas o corpo do relatório é o que ela pediu.

Confira `data_execucao` e `referencia` no topo. Estrutura: `resumo`,
`clientes[]` (slug, nome, conta, alertas[] com `gravidade`, saldo, ontem, d7,
d30, campanhas_ontem, ads_problema, adsets_learning_limited, boletos).

Se precisar de recorte que o digest não traz, use `insights.py` (leitura).

## Passo 2b — OBRIGATÓRIO: o que nós mexemos na janela

**Nunca interprete número sem antes saber o que foi alterado no período.** Em
03/09/2026 o relatório leu "lead a R$ 9,92 = curioso" na AFS Franquia quando
aquilo era o resultado dos dois dias em que a geo estava errada — e no terceiro
dia, já corrigida, a campanha fez zero lead. O relatório descreveu como sintoma
uma coisa que era consequência da nossa própria correção. A Mileny reclamou, com
razão: **isso tem que ser lembrado antes de gerar a otimização.**

Duas fontes, as duas obrigatórias:

1. **Diário do cliente** — conector do **Lovable** (não o do Supabase), projeto
   `afdb2a23-d03e-49f6-a03a-090bc48bc8d5`:

   ```sql
   select ad_account_id, performed_at, category, entity_name, action
   from account_activities
   where performed_at >= now() - interval '7 days'
   order by ad_account_id, performed_at desc;
   ```

2. **`decisoes.md` de cada cliente** em `$HOME\OneDrive\Carteira\<grupo>\<cliente>\`
   (mapa em `Carteira\CLAUDE.md`): o que está valendo, com o prazo de "não mexer
   até" e o que já foi testado e descartado. **Nenhuma otimização do Extrato pode
   contradizer uma linha desse arquivo sem dizer isso no `.why`**, com a data da
   decisão e o dado novo. Se precisar dos IDs e do motivo técnico, ler o
   `historico\AAAA-MM.md` da mesma pasta (o mais recente fica no topo).
   O antigo `meta-ads-ratos/historico.md` está congelado desde 17/09/2026.

Classifique cada conta antes de escrever qualquer leitura:

- **janela limpa** — nada mexido no período. A média de 3 dias vale como veredito.
- **janela contaminada** — mudança estrutural dentro do período (criativo trocado,
  formulário novo, geo corrigida, conjunto ligado/desligado, verba cortada). A
  média **não vale**: quebre por dia com `insights.py --time-increment 1` e
  compare antes × depois da mudança. Nunca recomende cortar algo que entrou em
  aprendizado nas últimas 48h.

Isso vira uma seção própria no HTML, **antes** do saldo — ver Passo 3.

## Passo 2c — OBRIGATÓRIO todo dia: verba programada × verba gasta

Pedido da Mileny em 15/09/2026: **"verificar sempre a verba utilizada no dia e ver
se bate com o programado."** Vale para todas as contas do corpo do relatório
(franquias, lojas, Desygn, Casa de Vidro, AP Ponto) e para "Outras contas com
gasto".

Para cada conta, com scripts de leitura (confira os nomes das flags com `--help`):

- verba programada: `read.py campaigns --account act_X` e `read.py adsets --account
  act_X` com `effective_status`, `daily_budget`, `lifetime_budget`, `end_time`,
  `campaign_id`. **Valores em centavos.**
  - CBO → `daily_budget` da campanha; ABO → soma dos `daily_budget` dos conjuntos
    ativos; vitalícia → o que resta ÷ dias até o `end_time`.
  - Conta com **programação de verba por horário** (Cheirin Bão MT desde 14/09) →
    informe base e pico; não compare só com a base.
- verba gasta no dia de referência: `insights.py account --account act_X --level
  adset --time-range '{"since":"AAAA-MM-DD","until":"AAAA-MM-DD"}'` com
  `adset_id,adset_name,campaign_name,spend`. Conjunto pausado/encerrado que gastou
  no dia entra também.
- **Não bate** = gasto abaixo de 80% ou acima de 125% do programado (a Meta pode
  passar até 75% num dia; acima de 125% já merece olhar). Sempre dizer a causa
  provável quando o dado mostrar: sem saldo, ligado/desligado no meio do dia,
  aprendizado, vitalícia no fim, verba alterada sem registro no Diário.
- Verba que **subiu sem mudança registrada** no Passo 2b é alerta crítico.

Vira a seção **"Verba: programado × gasto"**, logo depois do Saldo (Passo 3).

## Passo 2d — SÓ ÀS SEXTAS: distribuição de conteúdo das franquias (lista A FAZER)

Pedido da Mileny em 15/09/2026, **ajustado por ela no mesmo dia: "não precisa puxar de
todos instagram — quero que inclua isso no relatório para a gente fazer"**. Ou seja:
a rotina **não** varre os posts do Instagram. Às sextas o relatório traz a seção como
**checklist do que a gente faz na semana**, por franquia, com o que já se sabe da conta
(anúncios ativos por conjunto e o que ficou pendente da sexta anterior). O levantamento
de posts é item da lista, não trabalho da rotina automática.

O que a checklist cobre, para cada franquia do relatório (Facilmart, Cheirin Bão MT,
Boali, Açaí Fruit Show Franquia, Kascão CA 02 — Ponto Alpha fora por enquanto):

1. **Nível do Funil Espiral de cada conjunto ativo** (1 = alcance frio, vídeo sobre a
   oportunidade · 2 = aquecimento, desejo/bastidores, sem CTA de formulário · 3 =
   fundador/valores · 4 = convite, com prova real e CTA nunca "Saiba mais").
2. **Anúncios ativos em cada conjunto** (`read.py ads-by-adset` + `creatives-by-ad`):
   o que a peça diz, o nível que ela serve e se é **coerente** com o nível do conjunto.
3. **Publicações novas no Instagram** desde a sexta anterior (`read.py instagram-posts
   --ig-id` do contas.yaml; Facilmart não tem id — descobrir pelo criativo): nível
   que cada post serviria e se já está em anúncio. No perfil da Cheirin Bão, separar
   post de consumidor (não serve ao funil de franquia).
4. **Buracos**, na ordem da skill `conteudo`: camada sem peça ativa > frequência acima
   de 2,5 > camada com 1 só criativo > peça rodando no nível errado > post novo bom
   para uma camada sem munição.

Vira a seção **"Distribuição de conteúdo — franquias"**, logo depois de Franquias
(Passo 3). Nos outros dias, a seção não aparece.

## Passo 3 — Montar o HTML

Modelo obrigatório: `meta-ads-ratos/references/extrato-carteira-template.html`.
Copie o CSS inteiro e a estrutura; troque só os dados. Escreva em

`%TEMP%\extrato-AAAA-MM-DD.html`

⚠️ **É no TEMP, não em `relatorios/extrato/`** (mudou em 09/09/2026). Nesta sessão
headless o `Write` dentro de `meta-ads-ratos\relatorios\` é barrado como "sensitive
file" — o caminho tem `.claude` no meio e a trava vence o allowlist. Entre 05 e
07/09 o relatório ficou pronto três dias seguidos e não foi entregue nenhuma vez
por causa disso. O `rodar-extrato.ps1` copia do TEMP para o destino oficial e
manda no Telegram depois que você terminar — **não tente gravar no destino final
nem chamar o `notify.py` você mesmo.**

Ordem das seções, igual ao modelo:

1. **Header** — `<h1>Extrato da Carteira</h1>`, período à direita, lede de 2–3
   linhas dizendo o que está no relatório e o que é dado parcial, e a régua de
   KPIs (investido, leads franquia + CPL médio, conversas Desygn, contas
   paradas, leads B2B do Grupo TFS + CPL). O KPI "Leads B2B" voltou em 18/09/2026.
2. **Antes de ler os números** — a seção do Passo 2b. Tabela com Conta / Quando /
   O que mudou / Efeito na leitura, e um bloco `.callout` quando houver correção
   a fazer em relatório anterior. Se nada foi mexido na semana, escreva uma linha
   dizendo isso e siga — a seção nunca é omitida, porque a ausência de mudança
   também é informação.
3. **Saldo — quem para primeiro** — autonomia estimada, ordenada da mais crítica
   para a mais folgada, com as classes `st-crit`, `st-warn`, `st-ok`, `st-off`.
   Use **o menor entre saldo e folga do limite de gasto**. Contas no cartão não
   entram na régua; diga isso na nota.

   ⚠️ **Em conta pré-paga, `spend_cap` e saldo são o mesmo fato.** A Meta gere o
   cap espelhando o total já financiado, ele sobe sozinho na recarga e **não é
   editável por API** (erro 100 / subcode 1487840, "Alteração inválida para uma
   conta pré-paga"; um POST com `spend_cap: 0` responde `success` mas é no-op).
   Então: nunca reporte `LIMITE_GASTO` como alerta separado do `SALDO_BAIXO`
   nessas contas — é uma linha só — e **nunca recomende "subir o limite de gasto"**
   ali, porque é impossível de executar. O cap só é ação real em conta de
   cartão/faturamento (Boali, AP Ponto), onde é teto independente.
3b. **Verba: programado × gasto** — TODO DIA (Passo 2c). Tabela Conta /
   Programado/dia (onde) / Gasto / % / Bate? / Causa provável. Conta que bate ocupa
   uma linha curta; a que não bate leva a causa. Nunca omitir.
4. **Franquias** — ⚠️ **sem bloco `.acct` por conta**: nada de tabela de
   campanhas, `.stat` ou `.read` nesta seção. Pedido da Mileny em 11/09/2026:
   "não tem necessidade de enviar a parte Franquias, já pode pular para
   otimizações". A seção abre só com o `sec-head` (`Franquias — otimizações por
   conta`, com gasto e leads do grupo no `.count`) e vai direto para o item 5.
   Franquia sem gasto no dia (parada, sem campanha, erro de API) entra numa
   linha `.note` no fim da seção — nunca some do relatório.
5. **Otimizações por conta** (é o corpo de Franquias) — blocos `.opt`, um por
   conta de franquia com gasto, cada um com `.do` (o que fazer, imperativo) e
   `.why` (o número que justifica). Como não há mais tabela, **é no `.why` que o
   dado da conta aparece**: gasto, leads e CPL do dia e a comparação que sustenta
   a leitura. **Só entra recomendação que tenha base fora da janela
   contaminada;** conta contaminada leva um `.do` dizendo o que não mexer e até
   quando. Quando uma recomendação anterior for derrubada pelos dados novos,
   diga isso explicitamente num `.do` — não a apague em silêncio.
5b. **Grupo TFS — indústria e revenda** (de volta em 18/09/2026). Um bloco `.acct`
   por conta (TrendPel, Saborazzi, AFS Indústria): cabeçalho com act_id e forma de
   pagamento, `.stat` de gasto, leads e CPL, tabela de campanhas e `.read`. Entra
   sempre, mesmo com gasto zero. Modelo no template, logo depois de Franquias.
6. **Lojas físicas — rede Açaí Fruit Show** — aqui a métrica é impressão/CPM,
   não lead.
7. **Desygn Móveis Jardim** — métrica é contato (conversa do Direct + lead de
   site), conforme `acoes_lead` no contas.yaml.
8. **Construtora — AP Ponto** — CPL aparece, mas a régua combinada é custo por
   venda no CV CRM; sempre dizer isso.
9. **O que eu faria hoje** — `<ol class="acts">` em ordem de urgência. Item já
   resolvido leva `class="done"`.
10. **Footer** — quando os dados foram puxados, o período, o que ficou de fora, e
    se alguma alteração foi aplicada.

**Pendência combinada com data entra no TOPO de "O que eu faria hoje", antes de
qualquer sugestão minha** — é ação que a Mileny já decidiu, não diagnóstico meu.
Vem do bloco `tarefas` do digest (ou de `scripts/tarefas.py hoje --json`), só os
itens com `gravidade: critico`. Liste os `passos` na ordem e destaque a
`observacao`, que costuma ser a dependência que trava tudo. Item `ATRASADA` leva
os dias de atraso no texto. Se não houver item crítico, não invente a seção.

Regras de leitura que valem sempre:

- **CPL baixo em ticket alto é alerta, não vitória.** Franquia de R$ 270 mil a
  R$ 40 o lead significa curioso entrando. Franquia barata (Facilmart, R$ 58
  mil) a R$ 16 está no lugar certo. Sempre relacione CPL ao ticket.
- Frequência acima de ~1,7 pede criativo novo — diga isso.
- Conta parada por saldo é "parada, não fraca" — não trate como performance.
- Primeira pessoa, direto, sem jargão. Cada afirmação carrega o número que a
  sustenta.

## Passo 4 — Publicar (se der)

Tente publicar o HTML como Artifact (favicon 📊, title `Extrato da Carteira`).
Em sessão headless a ferramenta Artifact costuma não existir — se não existir ou
falhar, **siga em frente sem ela**. O relatório chega no Telegram como anexo de
qualquer jeito; o link é um bônus, não o entregável.

Se conseguir a URL, ela entra na última linha do resumo do Passo 5.

## Passo 5 — Escrever o resumo (quem manda é o PowerShell)

Grave o resumo em texto puro, sem markdown, no máximo ~3.500 caracteres, em:

`%TEMP%\extrato-telegram-AAAA-MM-DD.txt`

Conteúdo, nessa ordem: resumo geral (gasto, leads, CPL), contas paradas ou
prestes a parar, os alertas críticos, as 3 primeiras ações de "O que eu faria
hoje" e, se houver, o link do artifact.

⚠️ **Não chame o `notify.py`.** Em sessão headless o `python` pede aprovação que
ninguém concede — foi assim que o Telegram falhou de 05 a 07/09, inclusive com
`--file`. O `rodar-extrato.ps1` lê esse arquivo e dispara o envio fora do
sandbox, junto com o HTML em anexo. Seu trabalho termina ao gravar os dois
arquivos no TEMP.

Se a varredura tiver falhado, você nem foi chamado — o `.ps1` avisa sozinho.
