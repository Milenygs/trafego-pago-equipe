---
name: meta-ads-campaign-builder
description: >
  Planejador de campanhas Meta Ads (Facebook/Instagram) para clientes NAO-franquia
  da Mileny: moveis premium, hospedagem/temporada, lojas fisicas de rede e B2B
  industrial. Recebe cliente + objetivo e gera arquitetura de campanha completa
  (objetivo, publicos, estrutura de ad sets, framework de copy por posicionamento,
  orcamento em R$ e checklist de lancamento), seguindo os principios Andromeda/GEM/
  Lattice de 2026. Resolve o cliente pelo contas.yaml e entrega plano pronto para
  executar via meta-ads-ratos. Use quando o usuario pedir: planejar campanha,
  estruturar campanha, plano de midia, montar campanha, estrategia de anuncio para
  cliente que NAO e franquia (Desygn, Casa e Jardim, Maderarte, Varanda e Piscina,
  Casa de Vidro, Chales dos Ipes, QualyFibras, Saborazzi, TrendPel, lojas Acai
  Fruit Show). Para venda de FRANQUIA, usar a skill franquia (Funil Espiral).
tags: [ads]
---

# Meta Ads Campaign Builder — Planejamento (clientes não-franquia)

Monta a arquitetura completa de uma campanha Meta Ads — objetivo, públicos,
estrutura, copy framework e orçamento — ANTES de qualquer objeto ser criado.
Esta skill PLANEJA; a execução na API é da `meta-ads-ratos`; venda de franquia
é da skill `franquia` (Funil Espiral), não desta.

## Fluxo (sempre nesta ordem)

1. **Resolver o cliente** em `$HOME\OneDrive\.claude\skills\meta-ads-ratos\contas.yaml`:
   pegar `segmento`, `metrica_lead`, `notas` e IDs. O segmento define o modelo:
   - `moveis-premium` → lead qualificado (formulário intenção alta / WhatsApp / Direct)
   - `hospedagem` → sazonalidade + conversa WhatsApp; considerar datas/feriados
   - `loja-rede` → tráfego local geolocalizado (raio 1–3 km, visita ao perfil/WhatsApp)
   - `b2b` → leads de compradores/revendedores industriais (volume baixo, ticket alto)
   - Cliente não cadastrado → perguntar os dados; NUNCA inventar segmento.
2. **Intake** (perguntar só o que faltar): objetivo de negócio, verba mensal em R$,
   destino (formulário nativo, WhatsApp, Direct, site), criativos disponíveis,
   histórico (conta nova ou com pixel/públicos maduros).
3. **Montar o plano** com as regras abaixo.
4. **Entregar no formato de saída** e perguntar se executa via `meta-ads-ratos`
   (sempre criar PAUSED; regras de segurança da meta-ads-ratos valem).

## Princípios da era Andromeda / GEM / Lattice (2026) — SEMPRE aplicar

A Meta reescreveu o motor de entrega. O que funcionava em 2022 (muitos ad sets,
público estreito, empilhamento de interesses) **hoje sabota a entrega**:

1. **Poucos ad sets, muitos criativos.** 1–3 ad sets por campanha, 3–5 criativos
   por ad set. O GEM escolhe a pessoa a partir do criativo — o criativo é a
   principal alavanca de segmentação. NÃO empilhar interesse sobre interesse.
2. **Público amplo > estreito** na prospecção (2M+ é saudável). Estreitar só quando
   o cliente exige perfil qualificado/premium (móveis premium, B2B) — e mesmo aí,
   preferir filtrar pelo criativo e pelo formulário, não pela segmentação.
3. **CBO (Advantage Campaign Budget) por padrão** — verba na campanha.
   ⚠️ CBO ≠ **Advantage+ Audience** (expansão de público): Advantage+ Audience
   fica **OFF** quando o cliente exige público qualificado (`advantage_audience: 0`).
4. **Advantage+ Placements ON** — o Lattice aprende cross-surface (Reels → Feed).
5. **~50 conversões/semana por ad set** para sair do aprendizado. Verba não
   sustenta? Consolidar ad sets ou otimizar para evento mais raso (ex: conversa
   iniciada em vez de compra).
6. **Em CBO a otimização trava após publicar** — decidir o objetivo ANTES de subir;
   para trocar, duplicar a campanha e ajustar antes de publicar.

## Seleção de objetivo

| Meta de negócio | Objetivo Meta | Observação |
|---|---|---|
| Lead qualificado (móveis, B2B) | `OUTCOME_LEADS` + formulário "Intenção mais alta" | Volume menor, qualidade maior |
| Conversa WhatsApp/Direct | `OUTCOME_ENGAGEMENT` (CONVERSATIONS) | Medir por conversa iniciada (`metrica_lead: conversas`); exige `--bid-strategy` explícito (ver aprendizados.md) |
| Reserva/temporada | Tráfego p/ WhatsApp ou site + retarget | Janela de decisão longa; retarget é obrigatório |
| Loja física | Tráfego local / alcance geolocalizado | Raio 1–3 km; criativo com referência do bairro |
| Remarketing | `OUTCOME_LEADS`/`OUTCOME_SALES` sobre público quente | Trazer visitante de volta |

## Públicos

**Prospecção:** amplo por padrão + LAL 1–2% de semente qualificada (clientes que
COMPRARAM/fecharam — nunca lista total de leads). Camada de interesse única e
larga quando o segmento exigir (ex: interesse em decoração/arquitetura para
móveis premium).

**Retargeting (janelas padrão):**

| Público | Janela | Uso |
|---|---|---|
| Visitantes do site | 30d | retarget amplo |
| Página de preço/produto | 14d | alta intenção — CTA direto |
| Engajou com anúncio sem clicar | 30d | consideração |
| Videoview 50%+ | 30d | aquecido |
| Abriu formulário e não enviou | 14d | recuperação |

**B2B industrial (Saborazzi, TrendPel, QualyFibras):** lista de clientes → LAL 1%
é o melhor sinal; excluir estudantes/curiosos; volume baixo é normal — julgar por
custo por lead qualificado, não por volume.

## Framework de copy (3–5 variações por ad set)

| Variação | Ângulo | Estrutura |
|---|---|---|
| 1 | Dor | pergunta sobre a dor → solução → CTA |
| 2 | Resultado | promessa concreta com número → prova → CTA |
| 3 | Prova social | cliente real + resultado → convite |
| 4 | Contraintuitivo | quebra de mito do nicho → reposicionamento |
| 5 | Produto | destaque do diferencial → benefício |

Limites por posicionamento: Feed = headline 40 chars, texto 125 visíveis;
Stories/Reels = visual-first, gancho nos 3 primeiros segundos, texto mínimo.
CTA do botão sempre coerente com o destino (nunca "Saiba mais" para lead).

## Orçamento (R$/mês do cliente)

| Verba mensal | Prospecção | Retargeting | Teste de criativo |
|---|---|---|---|
| até R$ 1.500 | 70% | 30% | dentro da prospecção (CBO decide) |
| R$ 1.500–5.000 | 60% | 25% | 15% |
| R$ 5.000+ | 50% | 25% | 25% |

Lances: Lowest Cost para começar; Cost Cap só depois de ~50 conversões de histórico.
Orçamento na API é em **centavos** (5000 = R$ 50,00) — confirmar valor antes de executar.

## Formato de saída

```markdown
# Plano de Campanha Meta — [Cliente] — [DATA]

**Objetivo:** ... | **Verba:** R$ .../mês | **Destino:** ... | **Métrica de sucesso:** ... (usar metrica_lead do contas.yaml)

## Estrutura
(árvore campanha → 1–3 ad sets → 3–5 criativos, com objetivo da API, CBO on/off, Advantage+ Audience on/off)

## Públicos
(por ad set: definição, tamanho estimado, exclusões)

## Copy
(por ad set: 3–5 variações com texto primário, headline, CTA)

## Orçamento e lances
(tabela em R$; valores da API em centavos)

## Checklist de lançamento
- [ ] Pixel/eventos verificados  - [ ] UTMs definidas  - [ ] Exclusões aplicadas
- [ ] Tudo criado PAUSED  - [ ] Preview validado  - [ ] Ok da Mileny para ativar

## Monitoramento semana 1-2
Dia 1–3 entrega/reprovações · Dia 4–7 CTR/CPC · Dia 7–14 primeiras conversões · Dia 14 corte/escala
```

Quando a Mileny pedir entregável para o cliente, seguir a regra dos 2 documentos
(estratégico sem config técnica + técnico interno) definida na skill `franquia`.

## Fora do escopo

- Venda de franquia → skill `franquia` (Funil Espiral, 4 fases)
- Execução na API, duplicação, url_tags → skill `meta-ads-ratos`
- Rotina diária de contas → skill `ads-diario`
