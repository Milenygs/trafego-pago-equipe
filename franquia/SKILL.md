---
name: franquia
description: Orquestrador de campanhas Meta Ads para franquias usando o Funil Espiral (Funil de Consciencia). Cria, analisa e otimiza campanhas de venda de franquia com um pedido em linguagem natural. Resolve o cliente pelo contas.yaml, aplica as regras tecnicas da Mileny e executa via a skill meta-ads-ratos (SDK oficial da Meta). Use quando o usuario mencionar: criar campanha de franquia, montar funil, funil espiral, analisar franquia, otimizar campanha de franquia, escalar franquia, ou citar uma franquia (Kascao CA02, Bem Querer Donuts, Bem Cosmeticos, Facilmart, Sou Coluna, Acai Fruit Show, Cheirin Bao, Ponto Alpha, Boali). Encerrados em 27/08/2026, nao atender: Maroma, 4MR, Slimcenter, Up Lavanderia, Dona Baunilha. Tambem dispara com /franquia.
---

# Franquia — Orquestrador do Funil Espiral

Skill que transforma **um pedido em linguagem natural** em ações reais no Meta Ads,
seguindo a metodologia do **Funil Espiral** da Mileny para venda de franquia.

Ela NÃO fala com a API diretamente — ela **orquestra** a skill `meta-ads-ratos`
(o motor, em `$HOME\OneDrive\.claude\skills\meta-ads-ratos\`). No PowerShell,
usar sempre `$HOME` nos caminhos (`~` entre aspas não expande).

## Como funciona (sempre nesta ordem)

1. **Identificar a intenção** do pedido:
   - `criar` / `montar funil` → construir as 4 fases do Funil Espiral
   - `analisar` / `como está` / `relatório` → puxar insights e diagnosticar
   - `otimizar` / `escalar` / `cortar` → analisar e propor/executar ajustes

2. **Resolver o cliente** lendo
   `$HOME\OneDrive\.claude\skills\meta-ads-ratos\contas.yaml`.
   - Pegar `conta_anuncio`, `pagina_facebook`, `instagram_id` e ler as `notas`
     (têm regras por cliente, ex: qual página usar para anúncio de franquia).
   - Se o cliente não estiver lá ou faltar Page/Instagram, avisar e perguntar.

3. **Ler as regras** antes de qualquer ação de escrita:
   - Este arquivo (playbook do Funil Espiral, abaixo)
   - `meta-ads-ratos\aprendizados.md` (regras aprendidas com erros reais da API —
     OBRIGATÓRIO antes de criar qualquer objeto)
   - `meta-ads-ratos\references\padroes-campanha.md`

4. **Executar via meta-ads-ratos** (`read.py`, `insights.py`, `targeting.py`,
   `create.py`, `update.py`, `advanced.py`). Ver a referência completa de
   subcomandos no `SKILL.md` da meta-ads-ratos.

5. **Validar e reportar** — sempre criar PAUSED, validar com `read.py` + `preview`,
   e só ativar com confirmação da Mileny.

## Formato de saída da intenção "analisar"

Montar o diagnóstico SEMPRE nesta estrutura:

```markdown
## [Cliente] — Diagnóstico do Funil Espiral (período)

**Visão geral:** gasto · leads · CPL · comparação com período anterior

### Estado por fase
| Fase | Campanha | Status | Gasto | Resultado | Leitura |
|---|---|---|---|---|---|
(fases 1-4; fase sem campanha ativa = "❌ ausente" — buraco no funil é achado, não omissão)

### Diagnóstico
(aplicar a tabela "Diagnóstico por métrica" do playbook; citar o dado que sustenta cada conclusão)

### Ações sugeridas
1. ação numerada com comando pronto
```

Só dados reais da API. Nunca estimar ou preencher lacuna com suposição.

---

## PLAYBOOK — Funil Espiral (aplicar em TODA franquia)

A lógica central: **o funil não vende franquia diretamente.** Ele leva o lead ao
formulário já convencido, por fases de consciência progressiva. O convite só chega
quando o lead já conhece o produto, a marca e o fundador.

### Princípios da era Andromeda / GEM / Lattice (2026)

O Funil Espiral (4 fases) CONTINUA válido — ele trata de **consciência progressiva**, não de micro-segmentação. Mas o motor de entrega da Meta mudou (retrieval Andromeda + modelo GEM + ranking Lattice). DENTRO de cada fase, aplicar:

1. **Poucos ad sets por fase, muitos criativos.** Não fragmente o frio em vários ad sets pequenos — consolide o público investidor em 1–3 ad sets e diversifique o criativo (3–5 por ad set). O GEM escolhe a pessoa a partir do criativo.
2. **CBO (Advantage Campaign Budget) por fase** — verba na campanha, a Meta concentra no ad set vencedor. Essencial em orçamento pequeno (evita ad sets cegos que não saem do aprendizado).
3. **⚠️ CBO ≠ Advantage+ Audience.** CBO (distribuição de verba) **PODE usar**. **Advantage+ Audience (expansão de público) segue OFF** — protege o perfil investidor. É a isso que o "SEMPRE OFF" se refere.
4. **Advantage+ Placements ON** (posicionamentos automáticos) — o Lattice aprende cross-surface (Reels → Feed).
5. **~50 conversões/semana por ad set** para sair do aprendizado — mais um motivo pra consolidar em vez de fragmentar.
6. **Em CBO a otimização trava após publicar** — definir o objetivo certo ANTES de subir; para trocar, duplicar a campanha e ajustar antes de publicar.

### Estrutura de campanhas (4 fases)

**Fase 1 — Alcance frio**
- Objetivo: Leads ou Tráfego (`OUTCOME_LEADS` / `OUTCOME_TRAFFIC`)
- Público: LAL 1–2% de semente qualificada + camadas de interesse (perfil investidor)
- Conteúdo: **vídeo de PRODUTO E EXPERIÊNCIA** — a loja, o produto, o atendimento,
  o momento bom de quem consome. **Ainda não vende franquia** (Funil de Consciência,
  etapas 1–2: primeiro o lead se apaixona pela marca). Decidido pela Mileny em 17/09/2026.
- Regra: vídeo é obrigatório (alimenta o público de videoview). Sem formulário; CTA
  nenhum ou suave.

**Fase 2 — Aquecimento: a marca também é um bom negócio**
- Objetivo: Engajamento (`OUTCOME_ENGAGEMENT`)
- Público: 365d de engajamento com página/perfil
- Conteúdo: sem CTA de formulário — franqueados e sua rotina, inaugurações, bastidor
  da operação, como o modelo funciona (Funil de Consciência, etapa 4). Ainda sem convite.

**Fase 3 — Fundador / Valores**
- Objetivo: Visualização de vídeo (`OUTCOME_AWARENESS`, video views)
- Público: 180d de engajamento
- Conteúdo: fundador falando — história, propósito, valores, cultura. Funciona como
  **filtro**: quem não compartilha os valores sai aqui (etapa 5).
- Regra: marcar esses vídeos ao criar o público de videoview

**Fase 4 — Convite direto**
- Objetivo: Leads, **formulário nativo Meta** (`OUTCOME_LEADS`, destination LEAD_FORM)
- Público: quente 180d (engajamento + visitas ao perfil + videoviews combinados)
- Conteúdo de prova real, OBRIGATÓRIO conter os 4 elementos:
  1. Franqueado real (como foi, o que mudou na rotina, o que quase o impediu)
  2. Loja em operação (movimento, atendimento)
  3. Números concretos — **não financeiros por padrão** (lojas, cidades, faixa de
     investimento do formulário). Faturamento, retorno e payback **só se a ficha do
     cliente em `OneDrive\Carteira\<grupo>\<cliente>\CLAUDE.md` liberar**, e então só o
     número oficial da franqueadora, com fonte. Regra decidida por cliente (17/09/2026).
  4. Fundador fazendo o convite (tom consultivo)
- Roteiros, ganchos e copy: skill `conteudo` (camadas 1–4 = Fases 1–4).
- CTA: "Solicitar informações" / "Quero conhecer a oportunidade" — **NUNCA "Saiba mais"**
- Formulário: tipo **Intenção mais alta** + Reduzir envios não intencionais: SIM + mostrar
  valor do investimento na tela de boas-vindas

### Regras técnicas obrigatórias (NUNCA violar)
- **Advantage+ audience: SEMPRE OFF** (`targeting_automation.advantage_audience: 0`) — em todas as fases. ⚠️ O campo antigo `targeting_optimization: 'none'` foi **DESCONTINUADO pela Meta** (a API rejeita com "campo removido") — usar `advantage_audience: 0`.
- **Formulário: "Intenção mais alta"**, nunca "Mais volume"
- **Lookalike: máx 1–2%** — semente = leads que viraram reunião/fecharam (NUNCA total de leads)
- **Sem boost de post** para geração de lead
- **Sempre criar PAUSED** — revisar antes de ativar
- **Ativar todos os níveis** ao ativar (campanha → adsets → ads)
- Segmentação demográfica: Sócio Proprietário, 33–52, ambos os gêneros
- Conta nova: começar pelo topo (Fases 1–3) antes de ativar leads quente

### Diagnóstico por métrica (usar em análise/otimização)
| Sintoma | Causa provável |
|---|---|
| CTR alto + zero leads (tráfego) | Objetivo errado — tráfego não gera lead |
| CPM alto + zero leads (leads quente) | Público pequeno ou criativo sem prova |
| CTR ok + zero leads (leads quente) | CTA errado ou formulário quebrado |
| Leads só na LAL, zero no quente | Público quente pequeno ou fases anteriores não cumpridas |

### Erros clássicos a evitar
CTA "Saiba mais" em leads · formulário "Mais volume" · pular a fase do fundador ·
criativo de leads sem prova real · Advantage+ Audience ligado · LAL com semente de todos os leads.

---

## Lógica CRM pós-lead (franquia)
- Capital SIM → ligar em até 2h
- Capital EM BREVE → contato em 24h
- Capital NÃO → fluxo de nutrição (não descartar)

## Documentos (quando pedir entregável)
Sempre 2 documentos separados (regra da Mileny):
1. **Estratégico (cliente)**: diagnóstico, funil, personas, budget faseado. Sem config técnica, sem copy.
2. **Técnico (interno)**: camadas de segmentação, budget diário, placements, tipo de formulário, cronograma.
Nomenclatura: `TIPO_CLIENTE_CONTEXTO.md`. Gerar `.md` (+ `.html`/`.pdf` se pedido).

## Segurança
- Confirmar antes de ativar ou deletar
- Orçamento em centavos (5000 = R$50,00) — confirmar valor
- Nunca expor o token
- Ao mostrar insights de conta, quebrar por campanha antes de atribuir resultado
