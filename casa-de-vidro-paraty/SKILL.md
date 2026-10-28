---
name: casa-de-vidro-paraty
description: >
  Skill de cliente: Casa de Vidro Paraty (hospedagem de luxo em Paraty Mirim, RJ).
  Contem identidade da marca, tom de voz, 3 publicos com segmentacao Meta Ads
  pronta (noivado, familia premium, grupos/celebracoes), banco de frases
  aprovadas, mapeamento de fotos por publico e estrutura de campanha. Use quando
  o usuario mencionar: Casa de Vidro, casa de vidro paraty, campanha da casa de
  vidro, anuncio de temporada em Paraty, criativos da casa de vidro, ou pedir
  qualquer acao de Meta Ads para este cliente.
---

# Casa de Vidro Paraty — Skill de Cliente (Meta Ads)

Conhecimento aprovado para campanhas da Casa de Vidro Paraty: públicos,
segmentações, frases e fotos. Execução na API via `meta-ads-ratos`.

## Integração com o ecossistema

- **Slug no contas.yaml:** `casa-de-vidro-paraty` (act_792396727164193)
- **Métrica de lead:** `conversas` — a conta roda SÓ Direct (IG) e WhatsApp.
  NUNCA medir pela ação "lead" nem sugerir formulário nativo sem a Mileny pedir.
- **Estado da conta (checado 21/08/2026 direto na API):** `account_status: 1`
  (ACTIVE), fatura de R$944,38 foi paga em 13/08. NÃO está mais UNSETTLED — se
  algum registro antigo disser o contrário, desconfiar e checar de novo com
  `read.py account-details`, esse estado muda rápido nessa conta.
- **Migração WhatsApp→Direct: já rodou, dados reais existem.** Campanha
  `[ENGAJ] [DIRECT] - Campanha Geral - P_personalizado 12/08` (`120248795623790510`,
  OUTCOME_ENGAGEMENT, ABO) tem 3 conjuntos (não 2): `[COMPORTAMENTO/FERIASFAMILIA]
  [DIRECT] — AB` (120248983660210510), `[AB]`/luxo (120248795624670510),
  `[DATACOMEMORATIVA/AMIGOS] [DIRECT]` (120248795624060510). Os 2 carrosséis +
  estático já foram criados e entregaram de 12/08 a 21/08.
  Config de Direct: `CONVERSATIONS` + `destination_type: INSTAGRAM_DIRECT` +
  `promoted_object {page_id}` + `bid_strategy: LOWEST_COST_WITHOUT_CAP`;
  no criativo, CTA `INSTAGRAM_MESSAGE`.
- **⚠️ Campanha Direct está PAUSADA no nível de campanha desde 21/08 ~09h40** (os
  3 conjuntos mostram `status: ACTIVE` mas `effective_status: CAMPAIGN_PAUSED` —
  nada entrega até reativar a campanha). Mileny editou os 3 conjuntos nessa manhã
  (desativou o FERIASFAMILIA, subiu orçamento do AMIGOS e do luxo pra R$100/dia
  cada) e a campanha ficou parada nesse meio-tempo. Confirmar com ela antes de
  reativar.
- **Leitura de performance 30d (22/07–20/08), custo por conversa
  (`onsite_conversion.total_messaging_connection`):**
  WhatsApp `120244195893530510`: R$5,39/conversa (R$4.821 / 894 conversas) — subiu
  bastante frente ao baseline antigo de R$3,71 (13/08), sinal de fadiga de
  criativo. Direct (blend): R$4,58/conversa (R$531,54 / 116 conversas), já
  batendo o WhatsApp. Por conjunto dentro do Direct: **FERIASFAMILIA (público
  amplo, sem interesses empilhados) R$2,41/conversa — o melhor de longe**;
  `[AB]`/luxo (resorts+viajante frequente) R$5,29/conversa; **AMIGOS/DATACOMEMORATIVA
  (interesses empilhados: casamento+noivado+data comemorativa+bens de luxo)
  R$7,42/conversa — o pior**. Padrão que se repete nessa conta: empilhar
  interesses de celebração/luxo sai mais caro que ir amplo e deixar o
  criativo/oferta filtrar.
- **Plano de corte:** WhatsApp e Direct já rodaram em paralelo (12/08–21/08).
  Com o Direct batendo o WhatsApp no agregado, decisão de pausar o WhatsApp fica
  pra Mileny — dados já dão pra decidir.
- Estrutura recomendada (era Andromeda/GEM 2026): 1 campanha CBO com os 3
  conjuntos abaixo, 2–3 criativos por conjunto, Advantage+ Placements ON,
  Advantage+ Audience OFF (público premium qualificado).
- **Público 4 — Full-Service R$10k (criado 21/08/2026, PAUSED):**
  `[ANIVERSARIOMARCO/FULLSERVICE] [DIRECT]` (`120249031378930510`), dentro da
  campanha Direct. Diária R$10.000 tudo incluso, gancho de aniversário marcante
  (40/50 anos) ou família alto padrão em grupo grande — diferente do Público 3
  (Grupos/Celebrações) que é o ticket padrão. 32-64 anos, RJ/SP/MG, R$50/dia.
  Segmentação **estreita e qualificada de propósito** (bloco E, não OU): 
  interesses Aniversário (evento) + Gestão de eventos + life event "amigos de
  aniversariantes no mês", **E também** bens de luxo + gastronomia + comportamento
  "produtos de alto valor no Brasil" + "viajante internacional frequente".
  Decisão de ir estreito em vez de amplo veio de dado real da conta, não teoria:
  ver [[qualidade-de-lead-nao-e-cpl]] — nessa conta, FERIASFAMILIA (amplo, sem
  interesse) trouxe conversa a R$2,41 mas só 2 aluguéis fecharam desde março;
  AMIGOS (interesse empilhado) custa R$7,42/conversa só que filtra melhor.
  CPL baixo aqui é alerta, não vitória. Frases de overlay aprovadas por ela em
  21/08: *"Algumas datas não se repetem. Esta merece uma casa inteira."* e
  *"Vocês só chegam. A casa cuida de todo o resto."* — faltam imagem
  (`DSCF5426`/`DSCF5290`, hash ainda não resolvido) e criativo/anúncio pra
  ativar. Não ativar o conjunto sem ok explícito dela.
- **Reformulação de qualificação (21/08/2026):** ela reportou "o Direct tá
  trazendo muito lead ruim" e pediu pra reformular FERIASFAMILIA (Direct e
  WhatsApp) e a campanha de WhatsApp em geral, seguindo a mesma lógica do
  Público 4. Mudanças feitas:
  - `[COMPORTAMENTO/FERIASFAMILIA] [DIRECT] — AB` (120248983660210510) e
    `[COMPORTAMENTO/FERIASFAMILIA]` (WhatsApp, 120245832996310510): estavam
    com uma contradição lógica (`Newlywed (1 year)` + `Pais de adolescente` no
    mesmo bloco E, praticamente incompatíveis) — removido o "recém-casado".
    Adicionado bloco de afluência (comportamento: produtos de alto valor no
    Brasil + viajante internacional frequente) OR'd com o interesse de luxo já
    existente. Ficou: (pais com filhos OU casado) E (viagem 1ª classe/resort
    de luxo OU comportamento de alto valor).
  - **Público novo — `[REGIAO/ALTOPADRAO] RJ-SP-ES-MG`** (WhatsApp,
    `120249031521570510`, PAUSED, R$50/dia): público definido primariamente
    por região (adicionou Espírito Santo, que não estava em nenhum conjunto
    até então) + um único filtro de comportamento de afluência (alto valor no
    Brasil + viajante internacional), sem interesse de ocasião — mais amplo
    que o Público 4, mais filtrado que ir só por idade+geo.
  - **Aprendizado técnico:** criar ad set novo com `explore_home` em
    `instagram_positions` sem incluir `explore` junto falha com subcode
    2490392 (bug conhecido da conta, ver `aprendizados.md`).
- **WhatsApp oficial confirmado 25/08/2026:** `+55 11 96956 5817`
  (`5511969565817`). Achamos e corrigimos um bug real: os 2 carrosséis
  principais de WhatsApp (AMIGOS e FERIASFAMILIA) tinham o número
  `+55 31 97681409` **fixo dentro do próprio criativo** (`link_data.link` e
  cada `child_attachment`), que ignora e sobrescreve o
  `promoted_object.whatsapp_phone_number` do conjunto (que já estava correto).
  Ou seja, o anúncio de maior peso de cada conjunto mandava gente pro número
  errado sem ninguém perceber. Corrigido criando creatives novos com o número
  trocado (creatives de vídeo tipo `video_data` usam link genérico
  `api.whatsapp.com/send` e herdam do conjunto — esses já estavam certos;
  só creatives `link_data`/carrossel hardcodam o número). **Ao auditar
  qualquer conta com múltiplos criativos WhatsApp, sempre checar o número
  dentro do `object_story_spec`, não só o do ad set.**
- **Apresentação em PDF da casa (recebida 25/08/2026):** conteúdo completo e
  aprovado (tagline "O Luxo do Simples" / "O Essencial Elevado", estrutura A
  Refúgio → A Casa (5 suítes, 12 hóspedes) → Piscina Infinita → Gastronomia
  Caiçara → Serviços Exclusivos (Tudo Incluso) → Experiências Sensoriais →
  Costeira Privativa → fechamento com CTA "Solicitar Reserva"). **Não tem
  preço em nenhuma página** — mesmo gap que os anúncios já tinham. Virou a
  base do roteiro de Experiência Instantânea (ver abaixo).
- **Correção de copy "casa inteira, não pousada" (25-26/08/2026):** ela notou
  que o texto liderava com "piscina privativa... acesso exclusivo... privacidade
  absoluta" e só citava "casa" no fim, de passagem — lê como suíte de pousada
  de luxo com piscina própria, não propriedade inteira. Copy final aprovada,
  usada em todos os criativos novos/corrigidos:
  *"Uma casa inteira, só sua, em Paraty Mirim — não é suíte, não é pousada: é a
  propriedade completa, com piscina privativa de frente pro mar e acesso
  exclusivo de barco. Diárias a partir de R$10 mil (mínimo 2 noites), tudo
  incluso. Veja disponibilidade e conheça a casa completa."*
  Aplicada em: criativo do site (`2582347685586610`), os 2 vídeos de piscina
  ativos no WhatsApp (AMIGOS `4627132774242896`, FERIASFAMILIA `2094671227819188`,
  ads `120248119449700510`/`120248119434270510`) e o criativo do drone+IX
  (`2135155540747207`). Os 2 carrosséis principais (Amigos/Família) já tinham
  "casa inteira" no texto original — não precisaram dessa correção, só a do
  número de WhatsApp (ver abaixo).
- **Campanha de site criada 24/08/2026:** `[TRAFEGO] Full-Service 10k - 24-08
  (site + IX)` (`120249096259920510`, OUTCOME_TRAFFIC, ABO — **sem** orçamento
  de campanha, só de conjunto, senão a Meta rejeita com subcode 1885621
  "só pode orçamento de conjunto OU de campanha"). Foi pedido dela: "página
  qualifica antes do WhatsApp" em vez de conversa direta — o site já tinha
  preço + serviços + botão de WhatsApp prontos, não precisou criar página nova.
  Renomeada em 26/08 pra tirar "[SITE]" do nome sozinho, porque passou a ter
  2 conjuntos com destino diferente:
  - `[TRAFEGO/SITE] ALTOPADRAO RJ-SP-MG-ES` (`120249096260670510`, R$50/dia,
    `LANDING_PAGE_VIEWS`, RJ/SP/MG/ES, interesse amplo de afluência) → vai de
    verdade pro site.
  - `[IX] ALTOPADRAO RJ-SP-MG-ES` (`120249131600860510`, R$50/dia,
    `LINK_CLICKS` — **não pode ser `LANDING_PAGE_VIEWS`**, a Meta rejeita
    Experiência Instantânea nesse objetivo pra Instagram com subcode 1815816)
    → abre a Experiência Instantânea, termina no WhatsApp. Mesma segmentação
    de região+afluência do conjunto de site.
- **Experiência Instantânea construída e PUBLICADA de verdade (26/08/2026)**
  — ao contrário do que essa skill dizia antes ("API não suporta bem"), deu
  pra montar 100% via API depois de descobrir o esquema certo (ver
  `aprendizados.md` para os nomes de campo). Canvas `1375459734776554`
  ("Casa de Vidro - Experiencia Instantanea 26-08"), 15 blocos em sequência
  usando SÓ vídeos que já existiam na conta (sem cortar, ela não tem ferramenta
  de edição — vídeos ficaram no tamanho original de 30-50s, não nos 5-10s
  ideais) + textos baseados na apresentação em PDF dela, com 2 adições que o
  PDF não tinha: bloco de preço (R$10 mil) e 3 frases sensoriais reescritas
  (as originais do PDF — "aqui o mundo desacelera", "acordar e mergulhar no
  mar" — foram consideradas clichê por ela). Blocos, em ordem: vídeo piscina/
  drone (capa) → "O Luxo do Simples" → "Não tem estrada até aqui..." → "A
  Casa: 5 Suítes/12 Hóspedes" → vídeo recepção → vídeo quartos → vídeo
  gastronomia → Serviços Exclusivos/Tudo Incluso → vídeo praia → "a piscina
  termina onde o mar começa" → "o chef pergunta..." → "ninguém mais
  desembarca" → Costeira Privativa/distâncias → preço → botão "Solicitar
  Reserva" (WhatsApp `+55 11 96956 5817`).
  Anúncio: `120249131618090510` (PAUSED), criativo `2135155540747207` (vídeo
  drone "Short Reels 2.mov", `1066868269230302`, 19s — trocado do vídeo de
  piscina original a pedido dela; usa a miniatura da piscina por falta de
  frame do drone, revisar se incomodar). Preview oficial gerado via
  `read.py preview --creative <id> --format INSTAGRAM_STANDARD`.
  **Fluxo de aprovação usado:** criar canvas com `is_published: False` não
  adianta pra revisão — o link só renderiza publicado, e mesmo publicado só
  abre certo dentro do app (não no navegador direto). O jeito real de revisar
  é gerar o preview oficial do anúncio depois de anexar o canvas a um
  creative.
- **Formulário do site — para onde vão os cadastros (checado no código do site
  em 03/09/2026):** o site é Next.js e o form "Solicite sua Reserva" (nome,
  e-mail, telefone, check-in, check-out, mensagem) faz POST **em paralelo pra
  dois destinos de terceiros**, nenhum deles acessível à Mileny:
  1. webhook n8n do dev/agência —
     `https://n8n-gwcorp-dbh3dvhpa2g9hpbb.eastus2-01.azurewebsites.net/webhook/submit-form`
  2. backend próprio na AWS —
     `https://5i177ib24c.execute-api.us-east-1.amazonaws.com/prod/api/quotes`
  Basta um dos dois responder OK pra redirecionar pra `/sucesso`.
  **CORRIGIDO em 09/09/2026 pela Mileny: os cadastros CHEGAM nela, por uma
  página que o dev criou.** A leitura anterior desta skill ("não existe painel,
  planilha nem e-mail no meio do caminho") estava errada — ela foi tirada só do
  código do front, que de fato não mostra destino nenhum, mas o dev montou uma
  tela de consulta em cima do backend. **Não repetir a recomendação de "pedir um
  nó de saída no n8n": não é necessário.** Quando precisar dos leads (ex.: pra
  julgar qualidade num teste), o caminho é pedir a ela — não tenho o link nem
  acesso.
  **`/sucesso` é thank-you page real** (URL própria, status 200) e o pixel
  `1994872427748737` está instalado nela disparando `PageView` — dá pra criar
  conversão personalizada por URL contendo `/sucesso` e otimizar o conjunto de
  site por ela em vez de `LANDING_PAGE_VIEWS`. O site **não** dispara `Lead` no
  submit (só `PageView` + GA4 `G-MXV0E3WW1J`).
- **CAPI de leads qualificados (desde 19/08/2026):** pixel `1994872427748737`
  ("Pixel de Casa de Vidro", HEALTHY, automatic matching ligado). Sem CRM e sem
  formulário nativo, o match é por telefone (o próprio número do WhatsApp).
  Fluxo Nível 1 manual: ela marca lead qualificado/venda, anota em
  `meta-ads-ratos/relatorios/casa-de-vidro-capi/leads_qualificados.csv`, e eu
  envio com `capi.py batch`. Detalhes completos em
  `meta-ads-ratos/references/capi-casa-de-vidro.md`.

- **Campanha LEAD-SITE (`120249304293900510`, OUTCOME_LEADS, CBO R$100/dia) —
  o que roda hoje:** conversão personalizada **`1193058906236264`
  ("Lead - Solicitação de Reserva")** já existe e é por onde os conjuntos
  otimizam (a thank-you page `/sucesso` virou conversão de verdade, como a
  skill previa). Conjunto ativo `120249304293890510` "SP-RJ": R$307,20 em 30d
  (até 08/09), **2 leads a R$153,60**, mirando os **estados** de SP e RJ
  inteiros + interesses de viagem de luxo. O irmão `120249369573460510` está
  ACTIVE mas com **R$0 e 0 impressão** — não entrega, verificar.
- **Teste de pin geográfico (criado 08/09/2026, PAUSED):** campanha
  `[GEO-PIN] ALTO PADRAO SP-RJ - 08/09` (`120249369648020510`, ABO), criada
  porque ela reportou *"não tô acertando o público que paga 10.000 a diária"*.
  Dois conjuntos, R$50/dia cada, só Instagram, 35-65, **sem interesse nenhum**
  (o geo é o filtro), otimizando pela conversão acima, com `IG_SEGUIDORES`
  excluído:
  - `[PIN/MORA] BAIRROS ALTO PADRAO SP-RJ` (`120249369649830510`) — 15 pinos de
    2 km com `location_types: ["home"]` nos bairros onde essa gente mora.
  - `[PIN/DESTINO] ANGRA-ILHABELA-BUZIOS-CAMPOS-PARATY` (`120249369651930510`)
    — 9 pinos com `location_types: ["travel_in","recent"]` em destino de
    segunda residência.
  Anúncio nos dois é o mesmo creative do conjunto que já roda
  (`1383106124018245`), de propósito: o teste é de público, não de criativo.
  **Por que não pinamos restaurante/hotel:** raio mínimo de 1 km em bairro
  urbano pega junto quem trabalha no lugar, e `recent` mira qualquer um que
  passou — não separa quem paga de quem serve. Raciocínio completo em
  [[pin-geografico-filtra-renda]]. Leitura marcada no `tarefas.yaml`
  (`cdv-geo-pin-ler-resultado`, 16/09) e o critério é o veredito dela sobre a
  qualidade dos contatos, **não** o CPL.
- **O que roda hoje (13/09/2026): `[GEO-PIN/WHATS] ALTO PADRAO SP-RJ - 10/09`**
  (`120249402919690510`), destino WhatsApp, 4 conjuntos ativos a R$50/dia
  cada (MORA, DESTINO, LUGARES com janela 6-9h/18-24h, LUGARES-BR). Desde
  13/09, a pedido dela, **os 4 têm "Viajantes internacionais frequentes"
  (`6022788483583`) como E obrigatório** em cima do pino (um grupo único de
  `flexible_spec`). Pino sozinho não separava renda. Alcance caiu 4-5x (o
  menor, LUGARES-BR, ficou com 70-82 mil). Base de antes, de 10 a 13/09: 28
  conversas a ~R$20. Ao ler o teste, separar **antes × depois de 13/09**.
  Detalhe no `historico.md`.
- **Carrosséis nos 4 conjuntos (15-16/09/2026):** refiz o "Carrossel Eventos-
  whats 2" em 2 versões de **4 imagens** (a 1ª é a arte com frase). O original
  (`990953357192435`) **não se reaproveita**: tem `wa.me/553197681409` fixo em
  cada card (bug de 25/08), sem `instagram_user_id` e com end card ligado.
  - **B2 — `1634330338389409`, ATIVO nos 4 conjuntos** (ads
    `120249466671330510` MORA, `120249466676740510` DESTINO,
    `120249466680230510` LUGARES, `120249466684090510` LUGARES BR). Copy =
    texto do vídeo "onde o verão 1" dela, adaptado: "Descubra o luxo absoluto…"
    + lista de diferenciais + "não somos pousada: é o aluguel por temporada do
    espaço completo" + chamada de WhatsApp.
  - **A — `905074225778543`, PAUSED** (4 ads), copy "Raro. Inteiro. Só de
    vocês." Fica de reserva para comparar argumento depois.
  - **Instagram dela ficou legível em 26/09/2026** pela Graph API direta
    (`GET /17841472733937596/media` + `/{media}/insights`: reach, saved, shares,
    views). O `ads_get_ig_accounts` do conector segue `[]`, então testar pela Graph
    antes de pedir texto colado.
- **Funil de 26/09/2026:** topo com video view do "Onde o verão 1" (mesmos pinos
  da WHATS) + engajamento com o Reel "Nosso refúgio no paraíso!" (bairros alto
  padrão SP-RJ-MG) e fundo com conjunto QUENTE na WHATS. Visita ao perfil não
  roda nessa conta (2016153). Estado e IDs no `decisoes.md` da Carteira.

## Identidade da Marca

**Nome:** Casa de Vidro Paraty · **Local:** Paraty Mirim, RJ
**Instagram:** @casadevidro.paraty · **Site:** https://casadevidroparaty.com.br/
**Assinatura visual:** `CASA DE VIDRO  •  PARATY MIRIM  •  RJ`

**Tom de voz:** Poético, minimalista, sensorial. NUNCA ostentoso. A natureza é
parte da arquitetura emocional. Luxo = exclusividade e silêncio, não ostentação.

**Tipografia:** frase principal em Cormorant Garamond Light (italic); rodapé em
Montserrat ExtraLight (CAPS, tracking +150).

## Públicos e Segmentação Meta Ads

### Público 1 — Noivado / Pedido de Casamento
- Homem 28–40 planejando o pedido; classe A, renda familiar R$25k+/mês;
  SP, DF, RJ, BH, Fortaleza; já foi a Noronha/Trancoso/Jeri
- **Segmentação:** 26–42, masculino primário + feminino; interesses: anéis de
  noivado, casamentos de luxo, resorts boutique, viagens premium; comportamento:
  relacionamento sério
- **Overlay:** *"A casa que você descreveu para os seus amigos sem saber que existia."*
  (alt: *"Quando você vê, sabe. Este é o lugar."*)
- **Foto:** DSCF5249 — piscina infinita fundindo com a baía (sem pessoas)
- **Legenda:** "Porque datas especiais merecem lugares especiais. Da chegada ao
  último detalhe — você vive o momento, a Casa de Vidro cuida do resto.
  Consulte disponibilidade para o seu evento."

### Público 2 — Família Premium
- Casal 38–55 com filhos 8–16; renda R$80k+/mês; viaja 3–4x/ano; busca
  privacidade que hotel de luxo não dá
- **Segmentação:** 35–58, todos; interesses: viagens de luxo em família, casas
  de temporada exclusivas, hotéis 5 estrelas; comportamento: pais, renda alta;
  gatilho sazonal: férias de julho e janeiro
- **Overlay:** *"Aqui, o luxo é a natureza."* (alt: *"Férias que a família vai lembrar."*)
- **Foto:** DSCF5082 — pergolado + deck + piscina + vista da baía
- **Legenda:** "Algumas experiências não têm preço — e essa é uma delas. Uma casa
  inteira só de vocês. Privacidade, conforto e natureza a dois passos do mar.
  Consulte disponibilidade para as próximas férias."

### Público 3 — Grupos / Celebrações
- Amigos 28–45; aniversários, despedidas, retiros; classe A dividindo custo;
  querem algo fora do resort convencional
- **Segmentação:** 26–48, todos; interesses: viagens em grupo, experiências
  únicas, casas de temporada, lifestyle premium; comportamento: viajantes
  frequentes, plataformas de aluguel de luxo
- **Overlay:** *"Raro. Inteiro. Só de vocês."* (alt: *"O mar, a casa, e as pessoas que importam."*)
- **Foto:** DSCF5426 — casa completa + piscina + palmeiras
- **Legenda:** "Quando você vê, sabe. Este é o lugar. Casa completa com
  privacidade total em Paraty Mirim. Para grupos que querem uma experiência que
  ninguém esquece."

## Frase Universal (capa / awareness)

> *"Uma casa que poucos conhecem. Uma experiência que ninguém esquece."*

**Foto:** DSCF5290 — casal na piscina com vista para a baía (a mais forte).

## Banco de Frases Aprovadas

**Overlay (na foto):** as 4 acima + "Para quem escolhe experiências, não apenas
destinos." (família+noivado) · "O essencial elevado ao máximo." (todos) ·
"Uma experiência que não se repete. Apenas se vive." (noivado) · "Aqui, o tempo
tem outro ritmo." (todos, sensorial)

**Legenda (texto do anúncio):** as 3 dos públicos + "Para quem sabe que uma casa
inteira vale mais do que um hotel." (todos) + (aprovadas em 28/09/2026, vídeo
Culinária) "A mesa já está posta." · "O café da manhã é servido no deck, de frente
para a baía de Paraty Mirim. E a gastronomia caiçara da casa acompanha o dia, com
cardápio personalizado, criado para vocês."

Usar SOMENTE frases deste banco (são aprovadas pelo cliente). Frase nova =
propor e marcar como "aguardando aprovação".

## Fotos e criativos

**Pasta de trabalho (informada pela Mileny em 13/08/2026):**
`C:\Users\MilenyGalvão\OneDrive\Área de Trabalho\CLAUDE CODE\casa-de-vidro\criativos`

É onde ela larga criativo novo pra subir. Checar a pasta quando ela disser que
"colocou um criativo novo". Criativos que ela entrega já vêm com overlay pronto
e são aprovados por definição — não precisam passar pelo banco de frases (o banco
vale pra quando NÓS escrevemos o overlay).

⚠️ As fotos ORIGINAIS (DSCF*.jpg, sem overlay) e o script `gerar_criativos.py`
estavam no perfil antigo (`C:\Users\milen\...`) e continuam inacessíveis
(verificado 2026-07-16). Se precisar delas, perguntar — não procurar às cegas.

Referência dos arquivos (nomes originais):
| Arquivo | Público | Descrição |
|---|---|---|
| DSCF5290.jpg | Capa/todos | Casal na piscina + baía |
| DSCF5249.jpg | Noivado | Piscina infinita + baía |
| DSCF5082.jpg | Família | Pergolado + deck + piscina |
| DSCF5426.jpg | Grupos | Casa completa + palmeiras |

**Formatos:** Feed 1080x1350 (4:5) · Quadrado 1080x1080 · Stories/Reels 1080x1920.

## Estrutura de Campanha

```
Campanha CBO: Casa de Vidro Paraty — [objetivo]
├── Conjunto 1: Noivado — DSCF5249 + 2 overlays
├── Conjunto 2: Família Premium — DSCF5082 + 2 overlays
└── Conjunto 3: Grupos — DSCF5426/DSCF5290 + 2 overlays
```

Destino: Direct/WhatsApp (conversa iniciada). Criar tudo PAUSED, validar preview,
ativar só com ok da Mileny (regras da meta-ads-ratos).
