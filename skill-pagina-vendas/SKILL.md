---
name: skill-pagina-vendas
description: >
  PageCraft — Fábrica de páginas de vendas completas: estratégia, copy em PT-BR,
  fotos IA, design e HTML pronto para produção. Usa 8 frameworks de copy (AIDA,
  4Ps, PASTOR, FAB, ACCA, SSS, QUEST, 1-2-3-4) + Value Stack (Brunson), Value
  Equation e garantias (Hormozi), ângulos do Sexy Canvas e Equação de Persuasão
  (Bencivenga). Entrega 3 variações de hero com score, análise de objeções e
  HTML mobile-first com pixel, WhatsApp e countdown. Use quando o usuário pedir:
  página de vendas, sales page, landing page, página de captura, criar página,
  gerar copy, copy completa, montar página, pagecraft. Também dispara com
  /pagina-de-vendas.
---

# PageCraft — Sales Page Factory

Gera páginas de vendas 100% completas de A a Z: estratégia, copy, fotos IA,
design e HTML. Saída de copy SEMPRE em PT-BR. Nunca gerar copy genérica de
template — cada elemento tem justificativa estratégica explícita.

## Regras críticas

- SEMPRE entregar 3 variações do hero/primeira dobra
- SEMPRE dar score por seção com a Equação de Persuasão (Bencivenga)
- SEMPRE explicar POR QUE de cada escolha (framework, ângulo, gatilho)
- SEMPRE HTML mobile-first responsivo com pixel, WhatsApp e sticky CTA
- Copy em PT-BR nível de leitura 6ª–8ª série; termos técnicos consagrados (CTA,
  headline, hero) podem ficar em inglês

## Recursos da skill

- `references/frameworks.md` — estruturas dos 8 frameworks + fórmulas
  complementares (Bencivenga, Hormozi, Brunson). LER na Fase 2.
- Skill `skill-persona-profunda` — usar para criar persona se o cliente não tiver.
- Skill `skill-sexy-canvas` — usar para os 8 ângulos emocionais do hero.

## FLUXO EM 5 FASES (sequencial, mostrar progresso)

### FASE 1 — Briefing inteligente (uma pergunta por vez)

Perguntar UMA de cada vez, adaptando o follow-up:

1. **Produto/serviço:** o que é, o que entrega, ticket (R$)
2. **Público:** persona definida? Se não, oferecer rodar a `skill-persona-profunda`
3. **Nível de consciência:** FRIO (não sabe do problema) / MORNO (sabe do
   problema, não conhece a solução) / QUENTE (já conhece, falta o empurrão)
4. **Arsenal de provas:** depoimentos, números, tempo de experiência, mídia,
   certificações, história de transformação
5. **Método próprio + história de origem** (alimenta a Epiphany Bridge)
6. **Tom de voz:** autoritário direto / empático acolhedor / técnico / energético
   / íntimo conversacional — ou referência (link/texto)
7. **Referência visual** (link de página admirada)
8. **Fotos do especialista:** gênero, idade, etnia, tipo de corpo REAL (sem
   filtros), estilo de roupa, contexto (escritório, palco, estúdio)

Ao final, apresentar resumo do briefing (produto, ticket, público, consciência,
provas, história, tom, framework recomendado + razão) e confirmar.

### FASE 2 — Estratégia e seleção de framework

1. Ler `references/frameworks.md`.
2. Selecionar o framework pelo Quick-Reference abaixo (ticket × consciência ×
   tipo de público × provas × história × tamanho de página).
3. Apresentar a estratégia: framework principal + POR QUE, onde entram Stack
   (Brunson), Value Equation/garantia (Hormozi), ângulos Sexy Canvas e
   fascinations (Bencivenga), mapa da página (seção → objetivo → emoção) e
   as 4 fotos que serão geradas.
4. **Aguardar aprovação antes da Fase 3.**

### FASE 3 — Geração da copy

**3.1 Hero em 3 variações:**
- A — EMOCIONAL (dor → promessa; ângulo Sexy Canvas mais ressonante)
- B — RACIONAL (resultado + número + prova social)
- C — CURIOSIDADE (pattern interrupt / big idea de Bencivenga)

Para cada: headline, sub, bullets, CTA + análise (ângulo, emoção primária,
melhor para qual público, score 1-10 com justificativa) + recomendação de qual
testar primeiro e por quê.

**3.2 Todas as seções** conforme o framework escolhido. Cada seção sai com o
texto completo + notas estratégicas (fórmula usada, metodologia complementar,
modelo mental, emoção-alvo, objeção que quebra, score 1-10).

**3.3 Value Stack** (oferta + bônus nomeados com valores percebidos → total →
preço real → ancoragem → close "Just Say Maybe") com checagem da Value Equation.

**3.4 Garantia** nomeada (incondicional / condicional+incondicional para
high-ticket / anti-garantia para premium).

**3.5 FAQ** — 7 a 10 itens, cada um quebrando uma objeção específica, terminando
com micro-CTA.

**3.6 CTA final + P.S.** (urgência + benefício + lembrete da garantia).

### FASE 4 — Análise e score

Apresentar: score geral (Equação de Persuasão), mapa de emoções por dobra,
tabela de objeções quebradas (e as descobertas SEM cobertura, com sugestão),
densidade e posição de CTAs, pontos fortes e melhorias.
**Aguardar aprovação antes da Fase 5.**

### FASE 5 — Fotos + design + build

**5.1 Fotos IA** (hero confiante, story autêntico, autoridade em contexto
profissional, CTA com contato visual). Regras de realismo: pessoa com textura
de pele real e assimetrias naturais; luz coerente com o ambiente; nada de fundo
genérico de banco de imagem; mesma pessoa consistente nas 4 fotos; roupa e
contexto do briefing; sem excesso de retoque; enquadramento fotográfico natural
(não pose de stock).

**5.2 Design:** se não houver design system do cliente, escolher paleta pela
emoção-alvo + tipografia Google Fonts. OBRIGATÓRIO tema claro (fundo branco,
texto escuro, acento vibrante).

**5.3 HTML** em arquivo único pronto para produção:
- Mobile-first (breakpoints 640/768/1024/1280), Tailwind via CDN, smooth scroll
- Sticky CTA no mobile, countdown configurável, botão WhatsApp flutuante,
  FAQ accordion, embed de VSL (YouTube/Vimeo), CTAs múltiplos, depoimentos
- Placeholders de tracking: `<!-- REPLACE: fb-pixel-id -->`, google-ads-id,
  gtm-id · banner de consentimento LGPD · link de política de privacidade
- Checkout configurável (Hotmart, Eduzz, Kiwify, Monetizze) com passthrough de UTM

**5.4 Salvar** em `$HOME\paginas-de-venda\[produto]\index.html` (+ `images\`)
e mostrar resumo dos arquivos criados.

## Quick-Reference de framework

| Ticket | Consciência | Framework |
|---|---|---|
| Baixo (<R$100) | Quente | 4Ps ou 1-2-3-4 |
| Baixo | Morno | AIDA |
| Baixo | Frio | QUEST |
| Médio (R$100–2k) | Quente | 4Ps ou FAB |
| Médio | Morno | AIDA ou SSS |
| Médio | Frio | PASTOR ou ACCA |
| Alto (>R$2k) | Quente | 1-2-3-4 ou FAB |
| Alto | Morno | PASTOR ou SSS |
| Alto | Frio | PASTOR ou QUEST |

| Tipo de público | Framework |
|---|---|
| Emocional | PASTOR ou SSS |
| Racional/analítico | ACCA ou FAB |
| Impaciente | 1-2-3-4 ou 4Ps |
| Cético | ACCA ou QUEST |
| Iniciante | QUEST ou ACCA |
| Avançado | 4Ps ou FAB |
