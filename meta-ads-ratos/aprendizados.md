# Aprendizados — Meta Ads Ratos

Regras aprendidas durante o uso. O Claude DEVE ler este arquivo antes de criar qualquer objeto.

---

### 2026-09-24 — Vídeo com fala: TRANSCREVER antes de subir (quadros não bastam)
**Regra:** antes de subir vídeo com fala, transcrever o áudio inteiro (`faster_whisper`, modelo `small`, `int8`, CPU, com
`word_timestamps=True` para cortar) e conferir se a fala combina com o público do conjunto. A grade de quadros mostra texto na
tela e cenário, mas não o que a pessoa diz. Conferir também se aparece **tela de videochamada, planilha ou WhatsApp com nome ou
rosto de terceiros**. Isso sai do corte (LGPD).
**Para cortar:** usar `trim/atrim + concat` com afade de 30–40 ms e fazer o corte na troca de cena ou no começo da palavra. Com
legenda gravada no vídeo, achar o quadro exato em que a legenda troca (varrer a faixa da legenda a 10–30 fps) e começar ali.
Depois do corte, transcrever de novo o arquivo final.
**Contexto:** Cheirin 24/09. O DRE 2 subiu ativo em 3 conjuntos, conferido só por quadros, e terminava falando para quem quer
**ser franqueador**. Foi pausado com R$11 gastos. O DRE 4 tinha uma tela de videochamada com ~10 rostos e nomes, que foi cortada.

---

### 2026-09-24 — Lead qualificado (QUALITY_LEAD) se lê em `results`, nunca no `fb_pixel_custom`
**Regra:** em conjunto `QUALITY_LEAD`, o que o Gerenciador mostra em "Resultados" é o campo `results` do insights
(`indicator: conversion_leads:conversion_lead`). Se ele vier sem `values`, são **0 qualificados**, mesmo com `lead` > 0.
O balde `offsite_conversion.fb_pixel_custom` **não** é contagem de qualificado: na Cheirin ele trazia 2 no 07A e o CRM
mostrou 0. Antes de dizer "trouxe X leads" num conjunto de CRM, separar: lead de formulário (`lead`) × qualificado
(`results`), e conferir no CRM pelos IDs da planilha.
**Contexto:** Cheirin 24/09. Afirmei "07A trouxe 9 leads, 2 qualificados". A Mileny via o painel zerado ("não tem
registro"). Os 4 leads conferidos no CRM estavam lá e nenhum era qualificado.

---

### 2026-09-24 — TODO conjunto sobe com geo, inclusive público personalizado/engajamento
**Regra:** nunca criar conjunto sem `geo_locations`. Público de engajamento do IG
(`IG_ENGAJ_*`, `IG_VIDEO_*`) inclui gente do mundo todo: sem geo, a Meta entrega fora do país.
"Mesmo público da campanha X" significa copiar os públicos **e aplicar a geo da praça**; se X não
tiver geo, não copiar essa falta. Sem praça definida, perguntar antes de criar. Depois de criar,
ler o conjunto e confirmar a geo.
**Contexto:** AP Ponto, `[BELO] Direct Público Quente 180D` (120245801239900358), copiado do
`[DIRECT_insta]` da ANIV17 (que estava sem geo por causa da trava de verificação). Em algumas horas:
73 países, R$9,46 de R$9,67 fora do Brasil, e as 9 conversas vieram todas do exterior. A Mileny
reclamou ("super errado"). Corrigido com BH 17 km + Contagem 17 km + Vespasiano 20 km.

### 2026-09-23 — Subcode 3858634 ("forneça um anunciante verificado"): mandar o anunciante no próprio conjunto
**Regra:** quando conjunto com `geo_locations` é recusado com **subcode 3858634**, incluir no
`POST act_XXX/adsets` (ou no update) os campos
`regional_regulated_categories: ["BRAZIL_REGULATION","VOLUNTARY_VERIFICATION"]` e
`regional_regulation_identities: {"universal_beneficiary": "<id>", "universal_payer": "<id>"}`.
Para descobrir o `<id>`, pedir à Mileny que preencha o anunciante em **um** conjunto pelo painel e
ler `GET {adset}?fields=regional_regulated_categories,regional_regulation_identities`. O `create.py adset`
ainda não tem flag para isso: usar POST direto (ver `criativos/ap-ponto/build_belo_lancamento.py`).
**Contexto:** AP Ponto, de 09/09 a 23/09 sem conseguir geo em conjunto nenhum. Destravou no Belo
em 23/09, com o id 609854092925940 (portfólio da AP Ponto) como beneficiário e pagador.

### 2026-09-19 — Aumento temporário de verba: `POST /{id}/budget_schedules` com início em :00/:15/:30/:45; vídeo grande: envio simples
**Regra 1:** para subir a verba por um período e voltar sozinho, usar `POST /{campanha CBO ou conjunto ABO}/budget_schedules`
com `budget_value` (centavos, o valor EXTRA), `budget_value_type: ABSOLUTE` e `time_start`/`time_end` em unix. Não precisa
mandar `daily_budget` junto (diferente do `budget_schedule_specs` no POST do conjunto). **O `time_start` tem que cair em
múltiplo de 15 minutos**. Sem isso, o erro é "Período de alta demanda inválido". Mínimo de 3h, até 8× a verba.
A leitura `GET /{id}/budget_schedules` funcionou nos 3 objetos. Esperar 35s entre chamadas no mesmo objeto (#613).
**Regra 2:** `create.py video` (upload em partes do SDK) falhou 2x num vídeo de 56 MB com code 1 "Please reduce the
amount of data you're asking for". O envio simples (`requests.post(act/advideos, files={"source": ...})`)
subiu 56–72 MB sem erro.
**Contexto:** Boali 19/09: +20% na captação até seg 10h e AD16–AD19 (`criativos/boali-rodrigo/`).

---

### 2026-09-18 — Página fora do usuário do sistema: o conector do Facebook (claude.ai) cria o anúncio
**Regra:** quando o 1885499 trava a criação de criativo e anúncio (a página não está no token), usar o conector
`mcp__claude_ai_facebook__` (`ads_create_creative` + `ads_create_ad`). Ele age com o login da Mileny, que
tem a página, e cria o anúncio PAUSED. Limitações: (1) sem `url_tags`: a UTM vai dentro do `link_url`
(`https://site/?utm_...`); (2) um texto principal só (sem `asset_feed_spec`); (3) o `degrees_of_freedom_spec`
com OPT_OUT funciona e desliga todos os aprimoramentos. Pausar e renomear anúncio segue funcionando no `update.py`.
A cópia de anúncio (`POST /{ad_id}/copies`) **não** funciona no app da skill: (#3) "Application does not have
the capability to make this API call".
**Contexto:** Kascão CA 02 18/09: 12 anúncios de vídeo nos conjuntos de lead, com a página ainda bloqueada.

---

### 2026-09-18 — `create.py image` quebrado; Sebrae descontinuado
**Regra 1:** `create.py image --file` falha com `AdAccount.create_ad_image() got an unexpected keyword
argument 'files'` (SDK atual). Até corrigir, subir a imagem direto: `POST act_XXX/adimages` com
`bytes` (base64) e `name`. `create.py video --file` funciona.
**Regra 2:** o interesse Sebrae `6003099842040` foi descontinuado (1870247). A Meta sugere
`6002884511422` (Pequena empresa). Cargos (`work_positions`, busca `type=adworkposition`)
funcionam com `advantage_audience: 0` e ficam no mesmo grupo do `flexible_spec` (OU) sem erro.
**Contexto:** Kascão CA 02 18/09: miniaturas dos AD30–AD33 e público E1-C Dono + Investidor.

---

### 2026-09-18 — Clonar conjunto: `explore_home` agora exige `explore` junto (subcode 2490392)
**Regra:** ao copiar `targeting` de um conjunto antigo, se `instagram_positions` tiver `explore_home` sem `explore`,
adicionar `explore` antes de criar. Sem isso: "Você também deve selecionar o Explorar do Instagram" (100/2490392).
O conjunto antigo continua rodando assim, e só a criação nova é recusada.
**Junto:** para trocar a UTM de um anúncio que tem a UTM **dentro do link** (`?utm_source=...`), não basta mudar o
`url_tags`: o link ficaria com dois `utm_source`. Recriar o criativo com o link sem query string e as UTMs só no `url_tags`.
**Contexto:** Desygn 18/09, campanha nova de site otimizando pelo Lead (120246409159540138).

---

### 2026-09-16 — create.py: `image --file` quebrado, `adset` pede conta, Diário usa entity_type em português
**Regra:** (1) `create.py image --file` falha com "create_ad_image() got an unexpected keyword argument 'files'".
Subir com `AdImage(parent_id=act)`, `img[AdImage.Field.filename]=caminho`, `img.remote_create()`.
(2) `create.py adset` exige `META_AD_ACCOUNT_ID` no ambiente, mesmo com `--campaign`.
(3) Em `account_activities`, `entity_type` só aceita `conta | campanha | conjunto | anuncio`, e `adset`/`ad` violam a check constraint.
(4) Interesses descontinuados continuam aparecendo na busca: Azimut `6016849949435` e Casa Vogue Brasil
`6016840441401` deram 1870247. Validar um por um com `targeting.py reach` antes de criar.
**Contexto:** conjunto NÁUTICO+LUXO da Desygn, 16/09.

---

### 2026-09-16 — "Usa o texto do post do Instagram": o app pode não conseguir ler
**Regra:** antes de prometer que leio a legenda de um post/reel dela, checar
`ads_get_ig_accounts` na conta. Se voltar `[]`, o app não tem `instagram_basic` naquele
@ — não há como ler legenda nem listar mídia, e `ads_get_ig_media` responde "not linked
to ad account". Nesse caso, **pedir o texto colado**, em vez de tentar caminhos
alternativos. Vale também a ordem de busca quando ela diz "o vídeo que acabei de subir":
vídeos da conta (`read.py videos`, ordenado por data), `activities` do dia, disco
(OneDrive/Downloads/Área de Trabalho) e só então perguntar — dizendo onde já procurei.
**Contexto:** Casa de Vidro 16/09 — "coloque o texto que está no vídeo onde o verão 1".
O vídeo não estava na conta de anúncios (o mais novo era de 10/09), não estava no disco e
o IG `17841472733937596` voltou `[]` no `ads_get_ig_accounts`. Ela colou o texto no chat.

### 2026-09-16 — Programação de orçamento com verba DIÁRIA não prende gasto em horário

Na Cheirin, 7 conjuntos rodaram com período de alta demanda (+100% nas janelas do Eduardo). Em 15/09, primeiro dia
inteiro, os 5 conjuntos comparáveis gastaram **R$411,33 de R$420 de base** — o aumento programado **não virou gasto em
faixa nenhuma**. O período de alta demanda só eleva o teto; quem decide gastar é a entrega. Para prender gasto em
horário existe um mecanismo só: **verba total + `pacing_type: ["day_parting"]` + `adset_schedule`** (conjunto não roda
fora da agenda). Conjunto publicado com verba diária não converte para total — tem que duplicar, e isso reinicia o
aprendizado.

**Erro de método que cometi junto:** medi a janela contra a média de terça a quinta e concluí "+90% na manhã, funciona".
Ao comparar com **dias em que a programação ainda não existia** (sexta e sábado, ajustando as bases), o ganho da manhã
caiu para ~10 pontos e a noite ficou negativa em todos os dias. E a maior noite do período (R$154, domingo 13/09) foi
**fora** da janela. **Regra:** efeito de programação de horário se mede contra dias sem a programação, nunca só contra
uma referência de dias úteis — dia da semana sozinho move o gasto mais que a programação.

**Leitura dos períodos costuma estar bloqueada:** `GET /{adset}/budget_schedules` devolve #10 em conta/app onde ontem
funcionava; `budget_schedule_specs` não existe como campo do conjunto (#100); o registro de atividades traz
`update_campaign_high_demand_periods` mas corta o `weekly_schedule`; o conector oficial da Meta não tem campo. Sobra o
Gerenciador ("Períodos de alta demanda") — pedir à Mileny em vez de insistir na API.

### 2026-09-15 — Programação de orçamento: enviar spec nova SOMA um período, não substitui
**Regra:** `budget_schedule_specs` num conjunto que já tem período cria **mais um** período — não troca o anterior, e a
Meta aceita mesmo com os mesmos dias/horários (o validate_only não acusa sobreposição). Para mudar o valor do aumento:
ler `GET /{adset}/budget_schedules` (id, budget_value), criar o novo e **apagar o antigo pelo id** (`DELETE /{id}`),
conferindo que sobrou um só. Lembrar também: o aumento é valor ABSOLUTO — mudou a base, tem que mudar o aumento.
**Contexto:** Cheirin 15/09 — PINO SP subiu de base R$70/+R$70 para R$150/+R$150 e ficou com os dois períodos
(+7000 e +15000) ativos. Eu tinha registrado em 13/09 que "a spec parece substituir" — estava errado.

### 2026-09-15 — Otimizar pelo evento do CRM: `promoted_object` precisa de `lead_ads_form_event_source_type`
**Regra:** conjunto de formulário com meta "Maximizar leads qualificados" pelo CRM é `optimization_goal: QUALITY_LEAD` +
`destination_type: ON_AD` + `promoted_object` com **todos** estes campos: `page_id`, `pixel_id` (o dataset do CRM),
`custom_event_type: "OTHER"`, `custom_event_str: "<evento de lead bom>"` e **`lead_ads_form_event_source_type:
"onsite_crm_single_event"`**. Sem o último, a Meta responde **subcode 2490291 "Não é uma fonte de dados CRM válida"** —
que parece configuração incompleta, mas é o payload. Só `page_id` + `pixel_id` dá 1885014. Antes de concluir que o CRM
"não está configurado", ler o `promoted_object` de um conjunto que já otimizou pelo CRM na própria conta e repetir.
**Contexto:** Cheirin 15/09 — concluí que o CRM não era fonte válida e escrevi mensagem pedindo ajustes ao dev; a
Mileny mostrou o Gerenciador de Eventos com a integração concluída. Com o campo, validou com verba total e diária.
Obs.: o mapeamento de etapas no Gerenciador de Eventos virou só-leitura — o evento se escolhe no conjunto.

### 2026-09-11 — Anúncio criado PAUSED pela API já entra na fila de análise
**Regra:** anúncio criado com `status: PAUSED` aparece com `effective_status: PENDING_REVIEW` minutos
depois, **mesmo com campanha e conjunto pausados**: a análise da Meta não espera a ativação. Ao orientar
a Mileny sobre horário, não dizer "ative cedo para a análise passar". O que vale é conferir
`effective_status`/`issues_info` antes do início programado e avisar se algum anúncio for reprovado.
Ativar cedo continua útil por outro motivo: não depender de alguém lembrar no horário, já que a
programação do conjunto segura o gasto.
**Contexto:** AFS Cidade Nova 11/09 — AD01 e AD02 (`120249315821840726`, `120249315823930726`),
criados PAUSED às 17h10, estavam `PENDING_REVIEW` com a campanha `120249315653180726` ainda PAUSED.

### 2026-09-11 — Criativo de Direct a partir de post do IG: o CTA exige `link`
**Regra:** criativo com `source_instagram_media_id` + `call_to_action` `INSTAGRAM_MESSAGE` precisa
de `value.link`. Mandar `{"app_destination":"INSTAGRAM_DIRECT","link":"https://www.instagram.com/"}`.
Sem o link, a criação do **criativo** falha com **subcode 2061015** ("O campo de link é
obrigatório"). A Meta preenche o `app_link` (`instagram://direct?userid=...`) sozinha. É o
**oposto** do WhatsApp (regra de 10/09), onde `link` dentro de `value` é recusado.
**Confirmado junto:** nesse mesmo criativo (carrossel de post do IG), o opt-out recurso a recurso
em minúscula (`advantage_plus_creative`, `enhance_cta`, `inline_comment`, `text_optimizations`,
`video_auto_crop`, `video_filtering`, `video_uncrop`) foi aceito na criação e expandiu para 83
recursos, todos OPT_OUT. A lista em maiúscula de 17/08 não foi necessária.
**Contexto:** Desygn 11/09, conjunto `120246294588720138` na `(M) [ENGJ_QUENTE_IG_ MSG] 15/06`,
clone do Navegantes. As 3 variantes de `degrees_of_freedom_spec` falharam com o mesmo erro até
entrar o link. O erro não tinha relação com o dof. Nesse conjunto de CONVERSATIONS criado sem
`location_types`, a leitura voltou `["frequently_in","home","recent"]`.

### 2026-09-11 — `["home","recent"]` é o PADRÃO ATUAL da Meta, não a opção descontinuada
**Regra:** conjunto criado hoje pela API **sem** `location_types` volta na leitura com
`["home","recent"]` (em `geo_locations` e em `excluded_geo_locations`) — é assim que a Meta grava o
novo default "mora ou esteve recentemente". Reenviar `["home","recent"]` num update também é aceito.
O que foi recusado em 10/09 é mandar `recent`/`travel_in` como escolha própria (ex.:
`["recent","travel_in"]`). **Nunca diagnosticar erro de painel pela presença de `home,recent`:**
a carteira inteira tem isso (Desygn, QualyFibras, AP Ponto de 2020, boosts de post) e roda normal.
Também: omitir o campo ou mandar `[]` num update não muda nada, e duplicar conjunto (`/copies`)
herda o valor.
**ERRO MEU que isso gerou:** afirmei à Mileny que era a causa do "erro · ajuste de público" da
Boali e recriei o PIN LOJA do CP 08 à toa (conjunto novo `120251217473750156`, antigo pausado como
`[ANTIGO]`). A recriação voltou idêntica. **Testar a hipótese num conjunto novo ANTES de agir.**
**Checar primeiro nesses casos:** `issues_info` **3858385 "Autentique sua conta"** — checkpoint de
segurança do perfil dela, trava criar/modificar anúncio **no painel**; o system user segue
escrevendo. E interesses **combinados** (`flexible_spec` com 2+ grupos = "E também deve
corresponder a"): na Cheirin MT isso já derrubou conjuntos com **1870250** ("usa opções de
direcionamento detalhado que foram combinadas. Edite seu público para remover ou substituir").
**Contexto:** Boali 11/09.

### 2026-09-10 — Criar ANÚNCIO exige permissão na página, mesmo reusando `creative_id`
**Regra:** a falta da página no `GET /me/accounts` do system user não bloqueia só
`POST act_XXX/adcreatives` — bloqueia também `POST act_XXX/ads`, com **subcode 1885499**
("O visualizador deve ter a permissão do anunciante na Página"). Testado reaproveitando um
`creative_id` que já rodava na própria conta: recusa igual. Ou seja, **não existe atalho** por
criativo existente; sem a página compartilhada, a conta vira somente-edição — dá para mexer em
targeting, verba e status, mas nenhum anúncio novo entra.
**Como agir:** antes de prometer build em conta que nunca subiu anúncio pela API, rodar o teste de
1 minuto (`GET /me/accounts` procurando o `pagina_facebook` do contas.yaml). Se faltar, o pedido à
Mileny é um só: compartilhar a página com o system user no BM, com permissão de **Anunciante**.
Criar o **conjunto** funciona normalmente — então dá para deixar tudo montado e pausado esperando
o desbloqueio, em vez de travar a entrega inteira.
**Contexto:** Kascão CA 02 10/09 — conjunto da LAL 1% de franqueados (`120250540625730090`) subiu,
o anúncio não. Confirma e amplia o aprendizado de 07/08/2026, que só falava de criativo.

### 2026-09-10 — `frequently_in` volta sozinho: CONFIRMADO em 2ª conta, e o sintoma é visual
**Regra:** o comportamento documentado em 08/09 (Casa de Vidro) **não era específico daquela conta**
— repetiu igual na Kascão CA 02, em conjunto de LEAD/OFFSITE_CONVERSIONS com cidades (não pino):
`POST` com `location_types: ["home"]` retorna sucesso e a releitura 20s depois traz
`["frequently_in","home"]`. Nos conjuntos de **vídeo/THRUPLAY** da mesma conta, no mesmo lote,
`["home"]` ficou **limpo e estável** — a reposição parece atrelada ao objetivo de conversão, não à
conta.
**O que isso gera do lado da Mileny:** ela abre o painel, vê "frequentemente nesta localização" ao
lado de "morando em" e reporta como **erro da alteração**. Não é erro. Ao entregar qualquer ajuste
de região, **avisar antes** que essa linha vai aparecer, senão o relatório parece ter dado errado.
**O que NÃO fazer:** insistir. Já custou 1 escrita + 1 releitura aqui, além das 2 da Casa de Vidro.
**Contexto:** Kascão CA 02 10/09 — `120249598287850090` e `120249598304550090`.

### 2026-09-10 — 2446429 em conjunto de LEAD/site também é o `ig_search`
**Regra:** o erro "Erro de validação do formato do Instagram" (2446429) em anúncio de **vídeo** não
acontece só em campanha de formulário nativo (regra de 17/08): aconteceu igual em conjunto de
**lead para site** (`OFFSITE_CONVERSIONS` + `WEBSITE`). Remover `ig_search` de
`instagram_positions` tirou os 6 anúncios de `WITH_ISSUES` e devolveu para `PENDING_REVIEW` em
~75 segundos, sem recriar nada.
**Diagnóstico que fecha rápido:** se o **mesmo vídeo** entrega num conjunto e falha noutro, o
problema é do par vídeo+conjunto — comparar `instagram_positions` dos dois antes de olhar criativo.
Foi o que resolveu aqui: os gêmeos no conjunto frio entregavam normalmente.
**Contexto:** Kascão CA 02 10/09 — 6 anúncios do Maurício no `KASC [QUENTE]`
(`120249598304550090`), subidos pela Mileny no painel.

### 2026-09-10 — `standard_enhancements` não pode mais ser enviado na criação do criativo
**Regra:** ao criar `adcreative`, **não** mandar `standard_enhancements` dentro de
`degrees_of_freedom_spec.creative_features_spec`. A Meta rejeita com **"Invalid parameter"** e
`error_user_msg` "O recurso de inclusão do campo de aprimoramentos padrão no criativo foi
descontinuado. Defina recursos individuais". O opt-out agora é recurso por recurso —
`advantage_plus_creative`, `enhance_cta`, `inline_comment`, `text_optimizations`,
`video_auto_crop`, `video_filtering`, `video_uncrop`, todos com `enroll_status: OPT_OUT`.
**A armadilha:** criativos antigos da conta **ainda devolvem** `standard_enhancements` quando você
lê eles. Copiar o `degrees_of_freedom_spec` de um criativo vencedor para um POST novo quebra —
foi exatamente o que aconteceu ao clonar o `1809873060459195` da Boali (criado em 30/07, lê com o
campo). Ler para copiar: tirar esse campo antes de reenviar.

### 2026-09-10 — `create.py video` imprime mais que o JSON; não parsear a última linha
**Regra:** quem chama `scripts/create.py` por `subprocess` tem que achar o bloco `{...}` na saída
(`rfind("{")` até `rfind("}")`), não `splitlines()[-1]`. O script imprime "Token carregado ..." e
warnings do SDK antes, e o JSON sai identado em várias linhas — a última linha é só `}`.
**Contexto:** primeiro build do depoimento da Boali. O vídeo de 66 MB subiu, o parse quebrou depois,
e o traceback deu a impressão de que o upload tinha falhado. Conferir `list_ad_videos` antes de
re-subir, para não duplicar vídeo na conta.

### 2026-09-09 — campanha sem CBO exige `is_adset_budget_sharing_enabled`
**Regra:** ao criar campanha **sem** orçamento de campanha (ABO, verba no conjunto), mandar
`is_adset_budget_sharing_enabled` explícito — `"false"` para que cada conjunto fique com a verba
dele. Sem o campo, a criação da campanha quebra com **subcode 4834011** ("É necessário especificar
True ou False no campo is_adset_budget_sharing_enabled").
**Contexto:** build do CP 07 da Boali. Com `true` os conjuntos compartilham 20% da verba — nesse
build isso anularia o motivo de usar ABO, que era garantir entrega ao conjunto de praça satélite
(público 4x menor que o de loja; em CBO ou com sharing ele não receberia nada).

### 2026-09-09 — vídeo puro exige `destination_type: ON_VIDEO` no ad set
**Regra:** conjunto que vai receber criativo de **vídeo sem link** (`object_story_spec.video_data`
sem `link_data`) precisa nascer com `destination_type: "ON_VIDEO"`. Sem isso o conjunto fica
`destination_type: UNDEFINED` e a criação do **ad** — não do conjunto — quebra com **subcode
2061015** ("O campo de website URL é obrigatório"). O erro engana: parece problema do criativo,
mas o criativo está certo e quem está errado é o conjunto.
**Contexto:** CP 07 da Boali. Conjunto e campanha subiram sem erro; os 4 ads falharam. O conjunto
modelo (CP 01, THRUPLAY, que já rodava) tinha `ON_VIDEO` — a whitelist de campos do build não
copiava esse campo. `destination_type` também **não aparece** no `read.py adset`, só na chamada
direta à Graph API pedindo o campo por nome.

### 2026-09-10 — pino em LUGAR (restaurante/hotel/academia) só funciona com `adset_schedule`
**Regra de negócio:** o raio mínimo da Meta é **1 km**, e em bairro urbano denso isso nunca isola o
estabelecimento — pega a torre comercial do lado. O que salva não é o raio, é o **horário**: o
problema do "pega quem trabalha ali" é um problema das 9h às 18h. Cortando o meio do dia, o que
sobra dentro do círculo é quem foi jantar / treinar / está hospedado, mais os moradores — que em
Jardins, Itaim, Leblon e Ipanema **são o alvo**, não contaminação.
Janela usada na Casa de Vidro: `6h-9h` e `18h-24h`, todos os dias — cobre jantar, academia de manhã
e de fim de tarde, e hóspede de hotel, de uma vez.
**Como se escreve:** `adset_schedule` é lista de `{start_minute, end_minute, days}` em minutos do
dia (6h=360, 18h=1080, 24h=1440) e `days` com **0=domingo**. Exige, junto e obrigatoriamente:
`pacing_type: ["day_parting"]`, `lifetime_budget` (daily_budget **não** aceita horário) e
`end_time`. Uma entrada não cruza a meia-noite — para 19h-01h são duas entradas.
**Efeito na verba:** concentrar R$50/dia em ~9h equivale a ~2,5x a pressão por hora de R$50
espalhados em 24h. Verba "pequena" com day_parting não é aposta pequena — contar isso ao dimensionar.
**Medição (antes de propor pino de lugar em qualquer conta):** medir a distância dos lugares aos
pinos de bairro que já rodam. Na Casa de Vidro, **8 de 8** clusters de restaurante de SP caíam
DENTRO dos pinos de 2 km existentes — o D.O.M. a **60 m** do centro do pino dos Jardins. Em alcance
é repetido; o ganho é poder ler por tipo de lugar. Script do cálculo no histórico de 10/09.
**Limite que nenhuma configuração resolve:** a Meta **não reporta resultado por `custom_location`**.
Um conjunto com 43 pinos responde "pinar lugar funciona?", nunca "qual lugar funciona?". Para a
segunda pergunta, um conjunto por tipo — e aí a verba multiplica. Dizer isso antes de montar.
**Sobreposição de pinos:** dentro do MESMO conjunto, `custom_locations` que se sobrepõem viram
**união** — não competem. Leblon com 5 pinos de 1 km no mesmo conjunto é seguro. Competição de
leilão só existe entre CONJUNTOS diferentes da mesma campanha.

### 2026-09-10 — a Meta RECUSA `recent` e `travel_in` em `location_types` (só `home` sobrou)
**Regra:** `POST` de conjunto com `location_types` contendo `recent` ou `travel_in` volta erro 100
**subcode 1870199**: *"Atualize o valor do campo location_types — agora todo o direcionamento por
localização alcançará pessoas que moram ou estiveram recentemente nas localizações selecionadas.
Remova todos os valores do campo location_types."* A solução é **omitir o campo inteiro**; a Meta
aplica `["frequently_in","home","recent"]` sozinha na criação. `["home"]` **sozinho ainda é
aceito** (provado no mesmo build: o conjunto com `home` passou e o com `recent,travel_in` foi
recusado, na mesma conta, no mesmo minuto).
**Impacto prático:** acabou a separação "quem MORA no pin" vs "quem VIAJA para o pin". Os dois
viram a mesma coisa — mora **ou** esteve recentemente. Em pin de **destino de lazer** a perda é
pequena (quem está em Angra/Búzios já é majoritariamente segunda residência). Em pin de **bairro
rico** continua valendo pedir `["home"]` explícito, que é o único filtro que ainda restringe —
lembrando que `frequently_in` volta sozinho de todo jeito (seção de 08/09).
**O sintoma no painel, que é como ela vê:** conjunto antigo criado antes da mudança não é corrigido
retroativamente — o **anúncio** dele vai para `Atualização necessária` (run_status 18,
`with_issue_code: 1885255`) e não entrega. Se a Mileny disser "deu erro de configuração no
anúncio" num conjunto com pinos, **checar `location_types` antes de olhar o criativo**. Não
aparece como reprovação: `issues_info` fica vazio e `ads_get_errors` devolve `[]` depois que o ad é
arquivado, então o rastro confiável é o `read.py activities` da conta.
**Contexto:** Casa de Vidro Paraty. O `[PIN/DESTINO]` (`120249369651930510`) da GEO-PIN de 08/09
tinha `["recent","travel_in"]` e derrubou os 2 ads dele em 09/09; o `[PIN/MORA]` irmão, com
`["home"]`, entregou normal os dias todos. Refeito em 10/09 sem o campo.

### 2026-09-10 — CTA `WHATSAPP_MESSAGE` não aceita `link` dentro de `value`
**Regra:** em `object_story_spec`, `call_to_action: {"type":"WHATSAPP_MESSAGE","value":{...}}` com
`link` volta erro **subcode 1815630** ("Há muitos parâmetros na chamada para ação / Remova o
parâmetro link"). Mandar só `{"app_destination": "WHATSAPP"}`. O número sai do
`promoted_object.whatsapp_phone_number` **do conjunto**, e a Meta preenche
`link: https://api.whatsapp.com/send` sozinha — o GET depois mostra o `link` que você não mandou.
**Por que isso é bom:** número fixo dentro do criativo foi exatamente o bug de 25/08 na Casa de
Vidro (carrosséis com `wa.me/553197681409` ignorando o `5511969565817` do conjunto). Agora a
plataforma impede. Em criativo de WhatsApp, **nunca** carregar número no spec.
**Vale também:** o `page_welcome_message` (ice breakers) é aceito em `video_data`, não só em
`link_data` — e é onde colocar o preço para qualificar, quando a copy não leva valor.

### 2026-09-09 — `location_types` é um campo do conjunto, não do pin
**Regra:** em `geo_locations`, `location_types` (`home` / `recent` / `frequently_in` / `travel_in`)
vale para **todos** os `custom_locations` do conjunto de uma vez. Não existe location_type por pin.
Se o plano pede `home` em alguns pins e `recent` em outros, isso força **conjuntos separados** —
decidir isso antes de montar o build, porque muda a arquitetura da campanha.
**Contexto:** plano de pins da Boali previa `home` em loja de rua de bairro nobre e `recent` em
shopping. Virou dois conjuntos — o que acabou coincidindo com a separação que já era correta por
outro motivo (pin de loja e pin de cidade satélite são níveis de consciência diferentes).

### 2026-09-09 — medir raio de pin com targeting AMPLO, não com o público final
**Regra:** para decidir raio de `custom_location`, rodar `delivery_estimate` **sem** o
`flexible_spec` — só geo + idade + plataforma. Com os interesses aplicados o número cai tanto que
a razão alcance ÷ população dá sempre "OK" e esconde raio estourado. Medir os dois: o **amplo**
responde "o raio pegou a cidade certa?", o **cheio** responde "sobra gente pra rodar?".
**Contexto:** primeira medição dos 9 pins da onda 1 da Boali deu todos abaixo de 0,52x e pareciam
todos bons. Refeita sem `flexible_spec`, Cotia saltou de 59.900 (3km) para 256.600 (4km) — o pin
atravessava para São Paulo capital (na época tida como praça fechada; **corrigido em 17/09: a capital
está ABERTA**). Valinhos fazia o mesmo com Campinas
(48.600 → 197.100). Um salto desproporcional entre raios vizinhos é a assinatura de que o raio
cruzou para a metrópole vizinha.

### 2026-09-09 — `delivery_estimate` devolve 1.000–1.000 como SENTINELA, não como medida
**Regra:** `get_delivery_estimate` às vezes responde `estimate_mau_lower_bound: 1000` e
`upper_bound: 1000` com `estimate_dau: 0` — isso é **valor sentinela de "não consegui estimar"**, não
público de mil pessoas. Acontece com targeting pesado (10 públicos personalizados + geo + exclusões)
e é **instável**: a mesma chamada, minutos depois, devolveu 414-487 mil. Nunca concluir "público
pequeno" a partir disso. O jeito de medir de verdade é **acumular os públicos um a um** e ver a
curva subir (9,3k → 112k → 141k → … → 474k); se cada passo responde, a estimativa funciona e só a
chamada cheia falhou. Confirmar sempre contra dado empírico: `reach`/`impressions`/`cpm` do conjunto
equivalente que já roda dizem mais que a estimativa.
**Contexto:** Cheirin Bão 09/09 — projeção do conjunto de teste de janela. O sentinela sugeria que o
público não sustentaria a verba; a medição acumulada mostrou 414-487 mil e o gargalo real era outro
(o conjunto-controle subentregando 20-40% do orçamento por ser novo e usar QUALITY_LEAD).

### 2026-09-09 — Dayparting: `adset_schedule` sobe pela API, mas exige vitalício e `pacing_type`
**Regra:** programação de horário funciona via API com três coisas juntas: `lifetime_budget` (diário
**não** aceita), `pacing_type: ["day_parting"]` e `adset_schedule` como lista de
`{"start_minute", "end_minute", "days", "timezone_type"}`. Minutos contam da meia-noite
(10h = 600, 17h = 1020, fim do dia = 1440) e **`days` usa 0 = domingo**, 1 = segunda … 6 = sábado.
`timezone_type: "USER"` resolve pelo fuso da conta (aqui `America/Sao_Paulo`). Confirmado gravando e
relendo. **Para testar duas janelas, criar dois conjuntos** — `adset_schedule` aceita várias faixas
no mesmo conjunto, mas aí a Meta distribui o vitalício livremente entre elas e não dá para garantir
verba nem ler resultado por janela.
**Contexto:** Cheirin Bão 09/09 — teste seg-qua 10h-16h (`120257514629510212`) e sondagem de domingo
19h-24h (`120257514823510212`), ambos na campanha 09, ao lado do controle sem janela.

### 2026-09-09 — Vitalício não vira diário: conjunto publicado tem tipo de orçamento imutável (subcode 1885256)
**Regra:** conjunto que já foi publicado com `lifetime_budget` **não aceita** virar `daily_budget`.
`POST` com `daily_budget` + `lifetime_budget: 0` devolve **100 / subcode 1885256** — "Não é possível
definir um orçamento recorrente: o orçamento atual não é recorrente". Vale o contrário também, e o
painel tem a mesma trava (não é limitação do script). Quando a Mileny pedir "põe R$ X por dia" numa
campanha que está no vitalício, o caminho é **conjunto novo com o diário já na criação** (reusando o
`creative_id` do anúncio antigo, que preserva a aprovação) e deixar o antigo pausado. Se a intenção
for só limitar o ritmo sem trocar o tipo, a alternativa é recalcular o `lifetime_budget` para
`gasto_até_agora + (diário desejado × dias restantes)`.
**Contexto:** AFS Osasco 09/09, `[INAUG] Grupo VIP WhatsApp` (vitalício R$ 900, R$ 433 gastos) →
recriada como `| R$60 dia` (`120252766588900472`). A Tainara tinha tentado o mesmo pelo painel no dia
anterior e resolveu do mesmo jeito, criando cópias com diário.

### 2026-09-08 — Formulário nativo: criação exige Page Access Token e `context_card` de 1 parágrafo só
**Regra:** Criar/listar formulário de lead é `POST|GET /{page_id}/leadgen_forms` e **exige Page Access
Token** (`GET me/accounts` → `access_token` da página); com o token de sistema dá erro 190
("This method must be called with a Page Access Token"). Armadilhas na criação:
- `context_card` com `style: PARAGRAPH_STYLE` aceita **UM único elemento** em `content`
  ("There can only be one element in content for PARAGRAPH_STYLE") — para dois parágrafos, mandar
  um texto só com `\n\n` no meio.
- Na criação vai `privacy_policy` (objeto `{url, link_text}`); na LEITURA o campo é
  `privacy_policy_url`. `cta_type` não existe como campo de leitura.
- Remover o `id` de `questions[]`, `context_card` e `thank_you_page` ao clonar de um form existente.
- **Clonar as `key` das perguntas e das opções literalmente** do form que já roda — é a chave que o
  CRM mapeia, não o rótulo (ver a armadilha de 2026-08-10 sobre reordenação no painel). Na Cheirin
  a chave de R$300 mil tem um underscore final (`acima_de_r$_300_mil_`); manter o typo é o certo.
- `is_optimized_for_quality: true` = "Intenção mais alta" (regra permanente da Mileny).
**Contexto:** Cheirin Bão 08/09 — form `1501397322023032` criado clonando o `FORM Bl 2`.

### 2026-09-08 — Formulário de lead NÃO se apaga: só arquiva (e não existe a borda `/ads`)
**Regra:** `DELETE /{form_id}` é sempre recusado ("Unsupported delete request... does not exist,
cannot be loaded due to missing permissions or does not support this operation"), inclusive em form
com 0 leads. O jeito de limpar é `POST /{form_id}` com `status: ARCHIVED` (com Page Access Token) —
some do seletor de formulário sem perder histórico. Também **não existe** `GET /{form_id}/ads`
(erro 100, "nonexisting field"): para saber se um form está preso em anúncio antes de arquivar,
varrer `AdAccount.get_ads(fields=["creative{id,object_story_spec}"])` com todos os `effective_status`
e procurar o form_id no JSON do criativo — 1.060 ads da Cheirin saíram em uma chamada paginada,
sem precisar ler criativo por criativo.
**Contexto:** Cheirin Bão 08/09 — limpeza dos 5 formulários de teste criados no dia.

### 2026-09-08 — Conferir `is_optimized_for_quality` do form que os ads REALMENTE usam
**Regra:** Não basta a regra "formulário sempre em Intenção mais alta" estar no playbook — conferir o
valor no form em uso. O jeito: para cada ad ATIVO, ler `creative.object_story_spec` e extrair
`lead_gen_form_id` (ele fica dentro de `call_to_action.value`), depois `GET /{form_id}?fields=
name,is_optimized_for_quality,leads_count`. Na Cheirin, os **8 anúncios de lead ativos** apontavam
para o `FORM Bl 2` (`3282443085242041`, 982 leads) com `is_optimized_for_quality: **false**` —
"Mais volume", exatamente o oposto da regra, e provável fator do problema crônico de qualificação.
**Contexto:** Cheirin Bão 08/09, descoberto ao criar o formulário novo.

### 2026-09-08 — Anúncio de VISITA AO PERFIL SOBE pela API: o CTA precisa de `value.link`
**Regra:** `VIEW_INSTAGRAM_PROFILE` **funciona** via API — não é preciso criar o anúncio no painel.
O que quebrava era o CTA sem link: `call_to_action: {"type":"VIEW_INSTAGRAM_PROFILE"}` cria o
criativo mas o ANÚNCIO falha com subcode **2061015** (`blame_field_specs: ["website URL"]`).
O certo é `{"type":"VIEW_INSTAGRAM_PROFILE","value":{"link":"https://www.instagram.com/USUARIO/"}}`.
Conjunto: `optimization_goal: PROFILE_VISIT` + `destination_type: INSTAGRAM_PROFILE` +
`billing_event: IMPRESSIONS` + `promoted_object: {"page_id":"...","smart_pse_enabled":false}`.
Criativo de vídeo exige miniatura (subcode **1443226**): se o criativo de origem não tiver
`image_hash` (caso dos criativos feitos de post orgânico), pegar via `AdVideo(video_id).get_thumbnails()`
e passar a `uri` em `image_url`. Isso REVOGA o aprendizado de 29/07/2026 ("só sobe pelo painel").
**Contexto:** Cheirin Bão 08/09 — build do Nível 1 do Funil Espiral (tráfego pro perfil, interesse café).

### 2026-09-08 — Público de vídeo por vídeos ESPECÍFICOS não sobe pela API (subcode 1870049)
**Regra:** `create.py video-audience --video-ids` é rejeitado com "Formato de regra não disponível
para público de engajamento de vídeo — use o formato de regra anterior". Testadas 4 variantes
(event_sources `video`, `ig_business` + filtro `video_id`, formato legado): todas falham. Público de
vídeo **por vídeo específico só pelo painel**. Pela API só dá o pool amplo (todos os vídeos da conta
IG/página). Detalhe: nos públicos dessa conta a fonte do Instagram é `{"type":"ig_business","id":934954819849986}`
— NÃO o `instagram_id` do contas.yaml (`17841400169946431`). Copiar o id da regra de um público existente.
**Contexto:** Cheirin Bão 08/09 — tentativa de isolar o pool de vídeo de CAFÉ do pool que o Leads Quente colhe.

### 2026-09-08 — BUG corrigido: `create.py video-audience` não estava no dispatcher
**Regra:** O subcomando existia no argparse mas faltava no dict `commands` do `main()` — qualquer chamada
caía no `print_help()` com exit 1 e nenhuma mensagem de erro. Corrigido. Ao adicionar subcomando novo no
`create.py`, lembrar de registrar nos DOIS lugares (subparser + dict `commands`).
**Contexto:** Cheirin Bão 08/09.

### 2026-09-01 — Pixel via GTM server-side não aparece no HTML: provar pelo `stats --aggregation url`
**Regra:** Raspar o HTML da página **não serve** para decidir se ela tem pixel. Com GTM
server-side (Stape, `*.stape.io`) e LiteSpeed/Rocket Loader, o `fbq` não existe no HTML nem no
bundle JS — mas o pixel dispara normalmente. O teste definitivo é olhar o dado do próprio pixel:
`dataset.py stats --id <pixel> --aggregation url --start ... --end ...` mostra em quais domínios
ele realmente disparou, e `--aggregation event` mostra quais eventos. Rodar isso em **todos** os
pixels da conta antes de escolher o `promoted_object` — em conta com vários pixels, o que está na
LP costuma não ser o que está no site institucional. O HTML só é prova de **ausência** quando
não há GTM nenhum: aí sim (como na página de obrigado do Cheirin) a página é cega de verdade.
**Contexto:** Cheirin Bão 01/09 — a LP `bl.cheirinbao.com.br/franqueados/` parecia sem pixel no
HTML; os dados mostraram 1.295 PageView + 56 `lead_form` no pixel `2525428314626049` via
`GTM-KLFFMKML`. Já a página de obrigado estava mesmo sem nada, e a conversão personalizada que
existia para ela ainda por cima apontava para o pixel errado — dois anos de "conversão" que nunca
contou nada. Complementa a regra de 2026-08-10 (nunca trocar o evento sem ler o que o site dispara).

### 2026-09-01 — customconversions: `event_source_id`, regra obrigatória com URL, e promoted_object sozinho
**Regra:** Três armadilhas encadeadas ao criar conversão personalizada e ligar num conjunto:
1. `POST act_XXX/customconversions` **não aceita mais `pixel_id`** — pede `event_source_id`
   ("(#100) The parameter event_source_id is required").
2. Regra só com evento (`{"and":[{"event":{"eq":"lead_form"}}]}`) é recusada com subcode **1760020**
   *"A conversion rule is required at creation time"*. Precisa de uma condição de URL junto:
   `{"and":[{"event":{"eq":"lead_form"}},{"or":[{"URL":{"i_contains":"dominio.com.br"}}]}]}`.
   Isso vale inclusive para evento custom — o que na prática é bom, porque restringe a conversão
   ao domínio certo.
3. No ad set, `promoted_object` com **`pixel_id` + `custom_conversion_id` juntos** dá subcode
   **1885014** ("combinação inválida de parâmetros"). Para conversão personalizada, mandar
   **só** `{"custom_conversion_id": "<id>"}` — a Meta resolve o pixel sozinha.
Lembrar que `promoted_object` é **imutável depois de publicado** (regra de 2026-08-10): escolher
o evento certo antes de subir, ou o conserto é conjunto novo.
**Contexto:** Cheirin Bão 01/09, build da campanha 12 de site para franqueados.

### 2026-08-29 — PowerShell: nunca fazer retry cego em create.py (cria duplicado)
**Regra:** Ao rodar `create.py` em loop no PowerShell, detectar sucesso **só pelo
JSON** (`if ($out -match '"id":\s*"(\d+)"')`). A linha `Criado ad com ID: ...` que
aparece no console **não entra** no `$out` do `| Out-String` — se o teste de sucesso
depender dela, o loop acha que falhou e o retry cria o mesmo anúncio de novo. Também:
JSON em argumento no PowerShell precisa das aspas escapadas (`'{\"creative_id\":\"123\"}'`);
com aspas simples puras o Python recebe `{creative_id:...}` e dá "JSON invalido".
**Contexto:** replicação dos criativos do dia na Cheirin Bão MKT — um retry 60/120/180s
gerou 4 anúncios idênticos no Ribeirão Preto e 2 no Niterói, todos ATIVOS; precisou
deletar os extras.

---

### 2026-08-26 — Instant Experience (Canvas) via API: esquema real dos campos
**Regra:** É possível criar Experiência Instantânea 100% via API (ao contrário do
que se pensava) usando `Page.create_canvas_element()` + `Page.create_canvase()`
do SDK — mas **exige Page Access Token**, não o token de sistema/usuário normal
usado pra Ads Manager (`User('me').get_accounts()` retorna o token de cada
página). Os nomes de campo corretos (não documentados nos objetos que a
biblioteca expõe, achados só via busca web + tentativa/erro guiada pelo erro
"Invalid keys X were found in param Y", que sempre revela o nome certo por
eliminação):
- `canvas_text`: `{"rich_text": {"plain_text": "..."}, "text_alignment": "CENTER"}`
- `canvas_video`: `{"video_id": "...", "style": "FIT_TO_WIDTH"}`
- `canvas_photo`: `{"photo_id": "..."}` (ou `photo_url`)
- `canvas_button`: `{"rich_text": {"plain_text": "..."}, "open_url_action": {"url": "..."}}`
  (**não** é `"action"`, é `"open_url_action"`)
Fluxo: criar cada elemento com `page.create_canvas_element(params={...})` →
guardar os IDs na ordem certa → `page.create_canvase(params={"name": "...",
"body_element_ids": [...], "is_published": False})` → o canvas retorna
`canvas_link` (`https://fb.com/canvas_doc/<id>`), mas **só funciona depois de
publicado** (`is_published: True`) — draft não renderiza nem em preview.
Publicar o canvas não expõe nada publicamente por si só (só quando anexado a
um anúncio ativo). O `canvas_link` só abre certo dentro do app Facebook/
Instagram — direto no navegador só redireciona pro Facebook normal. Pra
revisar de verdade: anexar o canvas a um ad creative (`link_data`/`video_data`
com `call_to_action.value.link = canvas_link`) e gerar o preview oficial via
`read.py preview --creative <id> --format INSTAGRAM_STANDARD`.
**Restrições de objetivo:** anúncio com Experiência Instantânea recusa
`optimization_goal: LANDING_PAGE_VIEWS` no Instagram (subcode 1815816,
"não aceito para a otimização selecionada") — usar `LINK_CLICKS` no lugar.
**Contexto:** Casa de Vidro Paraty 26/08/2026 — conta nunca tinha usado Canvas
antes, então não tinha exemplo pra copiar; schema inteiro veio de busca na
documentação pública da Graph API (`developers.facebook.com/docs/graph-api/
reference/canvas-text`, `canvas-button`, `canvas-open-url-action`) combinada
com os erros da própria API.

### 2026-08-25 — start_time de conjunto não é editável: sequenciar pelo STATUS (subcode 1815377)
**Regra:** Depois que o ad set existe, a Meta recusa qualquer alteração de `start_time` — *"A data inicial atual está dentro dos próximos 15 minutos e não pode ser alterada. Se quiser alterar a data inicial, exclua este conjunto de anúncios e crie outro."* `end_time` e `frequency_control_specs` continuam editáveis normalmente. Para **adiar** o início de um conjunto já criado, não tentar editar a data: deixar o conjunto **PAUSED** e ativar no dia desejado — com `lifetime_budget`, a verba se redistribui sozinha pelos dias que sobrarem entre a ativação e o `end_time`. Isso é o suficiente para sequenciar campanhas no tempo sem recriar nada.
**Contexto:** Inauguração da AFS Mantena 25/08 — as 2 campanhas foram criadas juntas e depois precisaram virar fases (tráfego 25-31/08, reconhecimento 30/08-04/09).

### 2026-08-25 — Teto de frequência trava a verba em público pequeno (cidade do interior)
**Regra:** Em campanha de REACH com `frequency_control_specs`, a capacidade máxima de gasto é `pessoas × max_frequency × dias × CPM/1000`. Em cidade pequena isso vira um teto real de verba, não uma proteção teórica: 19 mil pessoas × 2 impressões/dia × 6 dias a um CPM de R$1,50 dá **R$342** — uma verba de R$550 simplesmente não escoa e sobra sem entregar. **Antes de definir teto de frequência, fazer essa conta com o CPM mais BAIXO plausível** (é o pior caso para escoar verba, ao contrário do que a intuição diz). Referência de CPM de REACH em loja AFS: R$1,47 (Tomba, público de 450-530 mil). Raio 0 na cidade é o município fechado; a Meta só aceita raio a partir de **16km**, e aí o público costuma pular para 3-4x, pegando cidades vizinhas.
**Contexto:** Mantena 25/08 — teto criado em 2/dia foi corrigido para 3/dia ao sequenciar as campanhas.

### 2026-08-17 — `standard_enhancements` foi descontinuado no degrees_of_freedom_spec (subcode 3858504)
**Regra:** Na v25 a Meta recusa `standard_enhancements` dentro de `creative_features_spec` — *"O recurso de inclusão do campo de aprimoramentos padrão no criativo foi descontinuado. Defina recursos individuais."* E os nomes antigos em minúscula (`adapt_to_placement`, `add_text_overlay`, `video_auto_crop`, `music`…) também não passam mais na **criação**: a API só aceita esta lista fechada, em MAIÚSCULA — `IG_VIDEO_NATIVE_SUBTITLE`, `IMAGE_ANIMATION`, `PRODUCT_BROWSING`, `PRODUCT_METADATA_AUTOMATION`, `PROFILE_CARD`, `STANDARD_ENHANCEMENTS_CATALOG`, `TEXT_OVERLAY_TRANSLATION`. Continua valendo o atalho: mandar **5 desses em OPT_OUT** faz a Meta expandir sozinha para os 82 campos, todos OPT_OUT (confirmado relendo `degrees_of_freedom_spec` no criativo). Se a API reclamar de uma chave, a própria mensagem de erro lista o conjunto aceito no momento — usar ela como fonte da verdade, que essa lista muda com a versão.
**Contexto:** Cheirin Bão 17/08 — build de 9 criativos novos quebrou duas vezes seguidas nisso antes de subir.

### 2026-08-17 — Vídeo com menos de 500px de largura é recusado no Instagram (subcode 2875006)
**Regra:** A criação do **anúncio** (não do criativo) falha com *"A mídia não tem largura suficiente"* se o vídeo, imagem ou miniatura tiver menos de 500px de largura. O criativo é aceito normalmente — o erro só estoura no `POST act_XXX/ads`, o que confunde. Antes de subir, conferir a resolução com `ffmpeg -i` e reescalar o que estiver abaixo de 1080 de largura (`scale=1080:1920:flags=lanczos`). Não existe ffmpeg nesta máquina: instalar o binário estático com `pip install imageio-ffmpeg` e pegar o caminho via `imageio_ffmpeg.get_ffmpeg_exe()`.
**Contexto:** Cheirin Bão 17/08 — "CRIATIVO 03.mp4" veio 480x854 e foi o único dos 9 a quebrar. Reescalado pra 1080x1920 e subiu. Na mesma leva, 3 vídeos vieram em 4K a ~150 Mbps (563, 660 e 712 MB): recomprimidos com `-crf 23 -r 30` para 10-18 MB, sem perda visível e com upload muito mais rápido.

### 2026-08-13 — Conta UNSETTLED cria campanha e conjunto, mas NÃO cria criativo (subcode 1487194)
**Regra:** Em conta com `account_status: 3` (UNSETTLED, pendência de pagamento), a Meta **deixa criar campanha e ad set normalmente** e só bloqueia no `POST act_XXX/adcreatives`, com erro genérico *"Permissions error / o objeto que você está tentando acessar não está visível para você ou a ação é restrita a determinados tipos de conta"* (subcode 1487194). A mensagem aponta para permissão e **engana** — não é página, não é token, não é escopo. Antes de sair caçando asset no BM, rodar os dois testes que separam as hipóteses em 1 minuto:
1. `GET /me/accounts` — se a página aparece com `ADVERTISE`, o acesso ao asset está OK.
2. Criar um criativo descartável **em outra conta** do mesmo token, de propósito com `image_hash` inválido. Se voltar "Imagem não encontrada" (subcode 2446386) em vez de 1487194, o token passou da barreira de permissão e o problema é a conta de origem.

Confirmar com `GET act_XXX?fields=account_status,balance` + insights com `--time-increment 1`: conta UNSETTLED que parou de entregar tem `balance` > 0 e gasto zerado a partir do dia em que a cobrança falhou. Só destrava quitando.
**Contexto:** Casa de Vidro Paraty 12-13/08 — build da campanha de Direct. Campanha `120248795623790510` e os 2 conjuntos criaram sem erro; os criativos falharam 100% das tentativas, do carrossel completo até uma imagem simples, **inclusive o molde de WhatsApp que já rodava dentro da própria conta**. Conta com R$944,38 em aberto no Mastercard *8915 e entrega zerada desde 11/08. O mesmo teste na conta da Desygn passou.

### 2026-08-12 — excluded_geo_locations NÃO sai por update nem por duplicação
**Regra:** Exclusão geográfica em ad set existente é imutável na prática. Testado e falhou: omitir o campo no targeting completo, `{"regions": []}`, `{}`, e `{"regions": [], "countries": []}` — a API responde 200 nas quatro e o campo continua lá. Duplicar também não resolve (a cópia leva a exclusão junto). **A única saída é criar o ad set do zero**, montando `geo_locations` na mão, e criar com `status: PAUSED` — criado direto como `ACTIVE`, ele já nasce com a exclusão aplicada. Depois migrar os anúncios apontando para os mesmos `creative_id` e só então ativar.
**Contexto:** Cheirin Bão 12/08 — 18 ad sets ativos excluíam 16 estados, e em 9 deles a exclusão bloqueava 8 das próprias cidades incluídas (Salvador, Feira de Santana, João Pessoa, Campina Grande, Natal, Mossoró, Aracaju, Teresina): na Meta, **exclusão sempre vence inclusão**, então esses conjuntos entregavam em 15 das 23 cidades. Recriados 9 do zero; 7 ficaram limpos de forma estável. Dois (`01 - Leads Quente + Geo` e `03 - LAL`) reaplicaram a exclusão ao entrar em veiculação, em 3 tentativas — causa não identificada, mesma campanha e mesma config dos que funcionaram. Cuidado adicional: a investigação estourou o rate limit da conta (código 17, subcode 2446079).

**Atualização 2026-08-17 — a exclusão voltou em TODOS, e a reconstrução não é garantia.** Cinco dias depois, os 8 conjuntos ativos (inclusive os 7 que tinham ficado limpos) estavam de novo com os mesmos 16 estados. Rodadas de teste desta vez, todas com resposta `success: true` e **zero efeito**: omitir o campo, `{}`, `{"regions": []}`, `null`, `{"regions": [], "location_types": [...]}`, lista menor só sem os 5 estados do território, e POST HTTP direto sem o SDK. Diagnósticos que descartam as suspeitas óbvias:
- **Escrita funciona**: no mesmo conjunto, `age_min` 30→25 pegou na hora (revertido depois). O imutável é só o `excluded_geo_locations`.
- **`execution_options: ["validate_only"]` passa sem erro** — a Meta não acusa nada, só descarta em silêncio.
- **Não é Special Ad Category**: `special_ad_category: NONE` nas duas campanhas.
- **Não é terceiro reaplicando**: no log de atividades, os únicos atores que tocaram em `update_ad_set_target_spec` são o system user dos scripts e a própria Mileny.
- **Payload só com `excluded_geo_locations`** (sem o resto do targeting) retorna erro — a Meta exige o spec completo.
- Conjunto **novo criado PAUSED nasce limpo** (confirmado de novo em 17/08), o que mantém de pé a hipótese de que a reaplicação acontece ao entrar em veiculação.
**DIAGNÓSTICO FECHADO (17/08, mesma sessão) — o gatilho é o STATUS do conjunto:**
1. Com o conjunto **ACTIVE**, toda tentativa de mexer em `excluded_geo_locations` é aceita e descartada.
2. Com o conjunto **PAUSED**, a remoção **funciona** — o campo zera de verdade.
3. Ao reativar, a Meta **reaplica os 16 estados em ~5 segundos**. O log de atividades **não registra ator nenhum** para essa reaplicação: é server-side e silenciosa.
4. Conjunto **novo SEM ANÚNCIO**, criado sem o campo, fica ativo e limpo indefinidamente — validado em 4 cenários (só cidades do NE; estado de SP + cidades; só cidades SP+NE; e o targeting COMPLETO do conjunto real, com os 7 públicos custom e o público excluído), todos com 0 exclusões depois de 25-60s ativos.
5. **O gatilho é o ANÚNCIO entrando em veiculação.** Reconstruídos os 4 conjuntos de lead do zero, sem o campo, com os anúncios migrados (mesmos `creative_id`): os 4 nasceram com 0 exclusões enquanto pausados e, ~15s depois de ativar conjunto + anúncios, **os 16 estados voltaram nos 4**. Mesmo payload que fica limpo sem anúncio.

6. **A contaminação é da CAMPANHA, não da conta.** Criada uma campanha nova do zero (`OUTCOME_LEADS`, não duplicada) + conjunto + 1 anúncio real, tudo ativado: **0 exclusões depois de 60s**. Os 4 gêmeos que falharam tinham sido criados dentro das campanhas antigas (09) — é isso que os contaminava, não o fato de serem ad sets novos.

**Conclusão:** a regra de exclusão está grudada na **campanha**. Qualquer ad set criado dentro de uma campanha contaminada recebe os 16 estados assim que o anúncio entra em entrega, por mais limpo que tenha nascido. **A correção é recriar a CAMPANHA do zero** (nunca duplicar) e montar conjuntos e anúncios dentro dela — reaproveitar os mesmos `creative_id` preserva a prova social. Os 16 estados são exatamente todo o Norte + Nordeste (AC, AL, AM, AP, BA, CE, MA, PA, PB, PE, PI, RN, RO, RR, SE, TO), provavelmente resíduo de uma divisão de território antiga que ficou colada nas campanhas legadas.
**Ressalva do teste:** os 60s foram com o anúncio ainda em análise (`IN_PROCESS`). Confirmar de novo **depois que a campanha nova começar a gastar de verdade**, antes de migrar o resto.

**O que a recriação de campanhas mostrou (17/08, fim da sessão) — leia antes de tentar de novo:**
- Recriadas do zero as campanhas 09, 11 e 05. **Só a 05 ficou limpa** (1 conjunto, 2 anúncios) — verificada ainda com 0 exclusões **40+ minutos depois, ativa e entregando**. Não é job atrasado: a limpeza é real e estável.
- 09 (4 conjuntos) e 11 (3 conjuntos) sujaram em 15s, em **duas** tentativas — a segunda já com teto de 4 anúncios por conjunto.
- Testes sintéticos (targeting simples, sem públicos custom) sugeriram teto de 5: 2, 3 e 4 anúncios limpos, 5 sujo — inclusive com 5 cópias do MESMO criativo, o que descarta criativo ruim. **Mas esse teto não se confirmou no mundo real**: o conjunto `03 - Fundador` sujou com só 3 anúncios. Então a contagem não é a explicação completa — a variável continua não isolada.
- Configuração **empiricamente comprovada** nesta conta: **2 anúncios por conjunto**. O número de CONJUNTOS não importa — o que quebra é a quantidade de anúncios dentro de cada um.

**SOLUÇÃO QUE FUNCIONOU (17/08, fim do dia).** As 3 campanhas foram migradas com sucesso e estão **sem exclusão nenhuma**:
- Método: campanha NOVA criada do zero (nunca duplicada, `excluded_geo_locations` fora do payload) + conjuntos adicionados **um por vez**, cada um com **exatamente 2 anúncios**, reaproveitando os mesmos `creative_id` (preserva prova social). Ativar campanha → conjunto → anúncios, **verificar 20-40s depois**, e só então pausar o conjunto antigo equivalente. Verba fica neutra durante a migração e não há downtime.
- Resultado: 09 com 4 conjuntos limpos, 11 com 3 conjuntos limpos, 05 com 1 conjunto limpo. **4 conjuntos × 2 anúncios = limpo**; as tentativas anteriores com 4-6 anúncios por conjunto sujaram todas.
- **Erro transitório da Meta (código 2, `is_transient: true`)** aparece com frequência ao ativar anúncio em lote: implementar retry com espera de 20s, senão o script morre no meio da migração.
- Regra operacional desta conta até segunda ordem: **máximo 2 anúncios por conjunto**. Para testar 3, adicionar UM anúncio, verificar, e reverter se sujar.
- **Cuidado com rate limit:** essa investigação estourou o limite da conta (código 17, subcode 2446079) pela segunda vez. Espaçar os testes e não encadear dezenas de escritas.

### 2026-08-10 — promote_pages NÃO serve de gate para saber se a conta pode usar a página
**Regra:** `GET act_XXX/promote_pages` lista só as páginas que o **negócio dono da conta possui**. Página compartilhada por parceiro (Parceiros → Atribuir ativos) funciona normalmente no anúncio e **não aparece** nessa lista. Nunca concluir "a conta não pode anunciar com essa página" a partir de promote_pages vazio. O teste definitivo e barato é criar um criativo descartável (`POST act_XXX/adcreatives` com o page_id, sem anúncio, sem gasto) e depois deletar: se passar, o vínculo está OK.
**Contexto:** AFS Tomba 10/08 — a checagem acusou que a conta da FSA não podia usar a página do Tomba e a Mileny passou um tempo tentando reatribuir no BM sem necessidade; o compartilhamento de parceiro que ela já tinha feito bastava, e o criativo de teste criou na primeira tentativa.

### 2026-08-10 — OUTCOME_AWARENESS recusa CTA de visita ao perfil (subcode 1885396)
**Regra:** Em campanha `OUTCOME_AWARENESS` com criativo dinâmico (`asset_feed_spec`), a Meta rejeita `call_to_action_types: ["VIEW_INSTAGRAM_PROFILE"]` — "não é aceito para o objetivo OUTCOME_AWARENESS no conjunto de anúncios de criativo dinâmico". Campanha de reconhecimento vai **sem botão**, o que aliás casa com a regra permanente de que campanha sem destino não leva CTA.
**Contexto:** Build da inauguração do Tomba — a campanha A quebrou na criação do primeiro anúncio, depois do conjunto já criado.

### 2026-08-10 — targeting_optimization foi removido (subcode 1870197)
**Regra:** NÃO incluir `targeting_optimization` no targeting. A Meta removeu o campo: "não é necessário definir um valor porque ele foi removido". Detalhe traiçoeiro: **conjunto REACH ainda aceita** o campo silenciosamente, mas `LINK_CLICKS` e `PROFILE_VISIT` rejeitam. Ao copiar targeting de ad set antigo (a leitura ainda devolve o campo), remover antes de criar.
**Contexto:** Mesmo build — o conjunto de reconhecimento passou com o campo, o de tráfego quebrou com ele.

### 2026-08-10 — Conta pode não ser elegível a anúncios de Visita ao Perfil (subcode 2016153)
**Regra:** `optimization_goal: PROFILE_VISIT` + `destination_type: INSTAGRAM_PROFILE` pode falhar na criação do ANÚNCIO (não do conjunto) com "This account isn't eligible to use Profile Visit ads yet" — mesmo em conta que já roda campanha de visita ao perfil com OUTRO perfil. A elegibilidade parece amarrada ao perfil Instagram usado, não só à conta. Substituto elegível: `OUTCOME_TRAFFIC` + `LINK_CLICKS` com `link` para `instagram.com/USUARIO` e CTA `LEARN_MORE`. Entrega o mesmo destino, mas abre no navegador em vez de nativo.
**Contexto:** Tomba 10/08 — perfil `@acaifruitshowtomba` novo, 54 seguidores; a conta da FSA roda PROFILE_VISIT com o perfil da Fraga Maia sem problema.

### 2026-08-10 — Reordenar opções de formulário no Gerenciador NÃO reordena as chaves
**Regra:** Ao mover opções de uma pergunta de múltipla escolha pelo Ads Manager, a Meta troca os **valores** de posição mas mantém as **chaves** onde estavam. Resultado: `key: acima_300` passa a valer `"Acima de R$100mil"`. Qualquer automação (CRM, CAPI, filtro) que leia a chave em vez do texto lê o valor invertido, silenciosamente. **Sempre conferir `questions[].options[].key` vs `.value` depois de qualquer edição de formulário**, e se estiverem trocados, recriar o formulário do zero — não dá pra corrigir chave em formulário publicado.
**Contexto:** AFS 10/08 — a Mileny reordenou o Capital Disponível para começar em R$100mil; as três chaves ficaram invertidas em relação aos rótulos.

### 2026-08-10 — leadgen_forms: o que a API NÃO deixa ler nem escrever
**Regra:** Complemento do checklist de 08/08:
- `GET /{form_id}?fields=privacy_policy` falha ("nonexisting field") — não dá pra clonar um formulário lendo tudo; ler `name,questions,context_card,thank_you_page,locale` e preencher `privacy_policy` na mão.
- Na **criação**, perguntas padrão (FULL_NAME, PHONE, EMAIL, CITY, STATE) **não aceitam `label` nem `key`** — só `{"type": "..."}`. Com label: subcode 1892063. Mas a **leitura** devolve label e key nelas, então copiar o retorno direto quebra.
- Nome de formulário é único na página: repetir dá subcode 1892019.
- `GET /{page_id}/leadgen_forms` (listar) falha com o token de system user, mesmo podendo criar. Não dá pra inventariar nem limpar órfãos via API — só pelo Gerenciador.
**Contexto:** AFS 10/08 — 3 execuções perdidas e ~8 formulários órfãos acumulados até fechar a versão final.

### 2026-08-10 — Evento de conversão é IMUTÁVEL em conjunto publicado (subcode 3260011)
**Regra:** Depois que um ad set foi publicado, a API recusa qualquer alteração em `promoted_object` (pixel, evento de conversão, conversão personalizada) e em `optimization_goal` — "Não é possível fazer edições em um conjunto de anúncios publicado". O único caminho é **criar conjunto novo** com o evento certo e pausar o antigo. Conferir o `promoted_object` ANTES de publicar; depois não tem conserto.
**Contexto:** Desygn 10/08 — os 3 conjuntos da campanha (M) [SITE] otimizavam por uma conversão personalizada de URL que nunca disparava. Tentativa de apontar pro evento Lead falhou nos 3; resolvido recriando os conjuntos (v4) e migrando os 6 anúncios.

### 2026-08-10 — video_data não aceita image_url e image_hash juntos
**Regra:** Ao copiar um `object_story_spec` de criativo existente para criar outro, **remover o `image_url`** se houver `image_hash` (a leitura devolve os dois, a escrita recusa: "Só um de image_url e image_hash deve ser especificado"). O `image_hash` é o que vale — o `image_url` é só a URL assinada da miniatura.
**Contexto:** Rebuild dos anúncios de vídeo da Desygn 10/08 — 4 de 6 falharam na primeira execução por isso.

### 2026-08-11 — NÃO pausar conjunto por teoria antes do dado chegar
**Regra:** Conjunto que acabou de subir precisa de tempo pra mostrar resultado. Se a decisão de pausar vem de uma dedução técnica ("esse evento não existe no site") e não de performance medida, **esperar o dado**. Conversão tem atraso de atribuição — o número de hoje de manhã não é o número que existia ontem à tarde. Antes de pausar qualquer conjunto, rodar insights em **nível de anúncio** com leads e CPL, nunca decidir só pela config.
**Contexto:** Desygn 10-11/08 — criei os conjuntos v4 (destino home + evento Lead), pausei poucas horas depois por concluir que o site não disparava `Lead`, e troquei pelos v5. No dia seguinte os v4 pausados apareceram com **8 leads a R$27,80 de CPL** (melhor da campanha, contra R$54 dos v3), e os v5 tinham gasto R$23 em 24h sem nenhum lead. Tive que religar os v4 e pausar os v5. A Mileny percebeu antes de mim, olhando o Gerenciador.

### 2026-08-10 — NUNCA trocar o evento de otimização sem ler o que o site realmente dispara
**Regra:** Antes de mudar `promoted_object`, confirmar **no HTML do site** quais eventos existem de fato. Em WordPress com PixelYourSite, a config fica no objeto `pysOptions` inline — ler `staticEvents`, `dynamicEvents`, `triggerEvents` e `enable_success_send_form`. Se só houver `PageView`, então **o único sinal de lead é a conversão personalizada por URL**, e otimizar por `custom_event_type: LEAD` aponta pra um evento que ninguém envia. Cuidado com dois falsos sinais: (1) a chamada `wp-json/pys-facebook/v1/event` é o PageView server-side, NÃO um evento de lead; (2) `learning_stage_info.conversions: 0` não prova que o evento não dispara — checar `first_fired_time`/`last_fired_time` da conversão personalizada antes de concluir qualquer coisa.
**Contexto:** Desygn 10/08 — conclui que o PYS mandava `Lead` no envio do formulário e recriei os 3 conjuntos otimizando por Lead do pixel. Estava errado: o site só manda PageView. Tive que recriar tudo de novo (v5) apontando de volta pra conversão personalizada. Dois rebuilds e prova social perdida por não ter lido a config do plugin antes.

### 2026-08-10 — Ad set não entrega conversão se a landing page não tem o caminho de conversão
**Regra:** Antes de culpar pixel/evento, conferir se a **página de destino do anúncio** tem o formulário. Anúncio que cai em página de produto só com botão de WhatsApp nunca vai gerar conversão de formulário, por mais certo que esteja o rastreamento. Abrir a URL de destino e procurar `<form` antes de mexer em qualquer configuração da campanha.
**Contexto:** Desygn — 4 dos 6 anúncios da campanha (M) [SITE] apontavam pra páginas de produto sem formulário; o formulário (Contact Form 7 `f47`) só existe na home e na página de obrigado.

### 2026-08-08 — Criar formulário de lead via API (checklist que evita 4 erros seguidos)
**Regra:** `POST /{page_id}/leadgen_forms` exige, além de name/locale/questions/privacy_policy:
- `follow_up_action_url` — sem ele: subcode 1892085 "Campos ausentes: FollowUpActionURL"
- `context_card.style`: `PARAGRAPH_STYLE` aceita **um único** item em `content`; `LIST_STYLE` aceita vários, mas **cada bullet < 80 caracteres**
- `is_optimized_for_quality: true` é o que liga "Intenção mais alta" — dá pra setar via API, não precisa do Ads Manager
- **O rótulo (`label`) da pergunta é o que o CRM usa pra mapear o campo.** Se o CRM tem campo "Capital Disponível", a pergunta tem que se chamar exatamente isso, senão a resposta é capturada pela Meta e nunca chega no CRM.
- Formulário publicado é **imutável** — pra corrigir pergunta, criar outro.
**Contexto:** AFS 08/08 — 83% dos leads declaravam capital abaixo do ticket e o comercial nunca via, porque o rótulo não batia com o campo do RD.

### 2026-08-08 — LEAD_GENERATION só aceita atribuição de 1 dia
**Regra:** Em ad set com `optimization_goal: LEAD_GENERATION`, o `attribution_spec` só aceita `{"event_type":"CLICK_THROUGH","window_days":1}`. Passar 7 dias falha com subcode 1885423.
**Contexto:** Build da CP-09 da AFS.

### 2026-08-08 — Criativo de vídeo exige miniatura explícita
**Regra:** `video_data` no `object_story_spec` precisa de `image_hash` OU `image_url`, senão a criação falha ("O anúncio precisa de uma miniatura de vídeo"). Pegar via `GET /{video_id}/thumbnails` e usar a que tem `is_preferred: true`.
**Contexto:** Vídeos de apresentação da CP-08 da AFS.

### 2026-08-08 — add_users do SDK quebra no Python 3.14 (hashear na mão)
**Regra:** `CustomAudience.add_users(..., is_raw=True)` estoura "object supporting the buffer API required". Contornar com SHA-256 manual (`hashlib.sha256(valor.strip().lower().encode()).hexdigest()`) e `POST /{audience_id}/users` com `payload={"schema":["EMAIL"],"data":[[hash],...]}`. Telefone: só dígitos, com DDI 55 na frente, antes de hashear.
**Contexto:** Público de exclusão de leads desqualificados da AFS.

### 2026-08-08 — degrees_of_freedom_spec: "standard_enhancements" foi descontinuado
**Regra:** NUNCA incluir a chave `standard_enhancements` no `creative_features_spec`. A Meta descontinuou o campo e rejeita a criação do criativo com subcode 3858504 ("O criativo não deve incluir aprimoramentos padrão"). Definir só os recursos individuais.
**Contexto:** Build dos estáticos da AFS Franquias 08/08 — a lista completa de OPT_OUT quebrou na primeira execução por causa dessa única chave.

### 2026-08-08 — instagram_positions: explore_home exige "explore" junto
**Regra:** Ao usar `explore_home` em `instagram_positions`, incluir também `explore` no mesmo array. Sozinho, a API rejeita com subcode 2490392.
**Contexto:** Criação dos conjuntos frios da AFS 08/08.

### 2026-09-08 — `instagram_positions: None` significa TODOS, não "nenhum"
**Regra:** Ao auditar posicionamentos, conjunto que volta com `instagram_positions` ausente/`None` está entregando em **todos** os posicionamentos do Instagram — Explorar incluso. Se além disso `publisher_platforms` também vier `None`, é Advantage+ placements: Facebook, Audience Network e Messenger ligados (fura a regra de Instagram-only da Mileny). Filtrar auditoria só por `"explore" in positions` deixa esses conjuntos passarem batido.
**Regra 2:** A API é **inconsistente** com `explore_home` sem `explore`: em alguns conjuntos ela rejeita a escrita de targeting (subcode 2490392), em outros aceita e **adiciona `explore` sozinha**. Ou seja, o targeting gravado pode não ser o que foi enviado — reler sempre depois de escrever, nunca assumir que o POST passou como mandado.
**Contexto:** Boali 08/09 — limpeza do Explorar. 16 conjuntos tinham Explorar explícito e mais 4 tinham por omissão, incluindo a CP 05 a R$250/dia e um conjunto novo em Advantage+ placements.

### 2026-08-08 — Interesses de "franquia" foram descontinuados pela Meta
**Regra:** NÃO usar `6014988918616` (Franquia) nem `6003421934889` (Franquia/Franchising) — ambos descontinuados, a API rejeita com subcode 1870247. Alternativa oficial sugerida pela própria Meta: `6003241592011` (Business model / modelo de negócios). **Sempre validar interesse antes de criar o ad set** com `GET act_XXX/delivery_estimate?targeting_spec=...` — o `targeting.py interests` ainda retorna IDs mortos na busca.
**Contexto:** Público frio da AFS 08/08 — dois interesses de franquia quebraram a criação em sequência.

### 2026-08-08 — Exclusões de direcionamento detalhado não existem mais
**Regra:** O campo `exclusions` (interests/behaviors) em targeting foi removido pela Meta (subcode 3858492). Para separar públicos por perfil, usar `flexible_spec` (E lógico entre grupos) em vez de excluir. Exclusão de público personalizado (`excluded_custom_audiences`) continua funcionando normalmente.
**Contexto:** Conjuntos frios da AFS 08/08 — a ideia era excluir "Proprietários de pequenas empresas" do conjunto de CLT em transição.

### 2026-08-08 — Vídeo pode reprovar no Instagram por conjunto (code 2446429)
**Regra:** O erro `2446429` ("Erro de validação do formato do Instagram") é do par vídeo+conjunto, não do criativo. Se aparecer, testar o MESMO vídeo com o criativo original em outro conjunto antes de mexer em `degrees_of_freedom_spec` ou posicionamentos — se falhar também, o vídeo não serve para aquele conjunto e o certo é trocar de criativo. Não adianta recriar o criativo nem ligar `adapt_to_placement`/`video_auto_crop`.
**Contexto:** AFS 08/08 — o vídeo `759360116576015` (MODELO LUCRATIVO, melhor CPL do quente) roda na CP-04 mas reprova em qualquer conjunto novo da CP-07. Substituído por `1271310064932514` (VOCÊ INVESTIRIA).

### 2026-08-07 — Acesso à conta de anúncio NÃO garante acesso à página (erro 10 / subcode 3858749)
**Regra:** Criar criativo é criar um dark post NA PÁGINA — exige que o system user do token tenha função **Anunciante ou superior na página**, o que é um asset separado da conta de anúncio. Ler campanhas e **subir vídeo/imagem funcionam mesmo sem isso** (são account-level), então o erro só aparece na hora do `create_ad_creative`. Antes de um build grande em conta nova, checar `GET /me/accounts` e confirmar que a `pagina_facebook` do contas.yaml está na lista com `ADVERTISE`. Se não estiver, pedir ao admin da página pra compartilhar a página com o system user no BM. Escopos do token (pages_manage_posts etc.) estarem "granted" NÃO substitui o acesso ao asset.
**Contexto:** Kascão CA 02 — os 4 vídeos subiram normal pra `act_1435086545094716`, mas os 8 criativos falharam: a página `167959616608948` (Kascão Sorvetes) não aparece no `/me/accounts` do system user "relatórios-automaçoes" (33 páginas listadas, essa não). Campanhas antigas da conta foram criadas pelo Ads Manager na mão, por isso o gap nunca tinha aparecido.

### 2026-07-19 — Criativo WhatsApp (CTWA) exige app_destination no CTA
**Regra:** Ao criar criativo com call_to_action WHATSAPP_MESSAGE, SEMPRE passar o CTA completo: `{"type":"WHATSAPP_MESSAGE","value":{"app_destination":"WHATSAPP","link":"https://api.whatsapp.com/send"}}`. Só o type falha com subcode 2061015 ("campo de link é obrigatório"). Para criativo de post IG: usar `source_instagram_media_id` (media ORIGINAL, não o effective) + `instagram_user_id` + `object_id` (page). O `page_welcome_message` (saudação com pergunta qualificatória) pode ser copiado de um criativo WhatsApp existente da conta.
**Contexto:** Build da campanha (M) [WPP] [PUBLICO_COMPRADOR] da Desygn 19/07; molde copiado do criativo 4025188431119155.

### 2026-07-19 — age_range no targeting conflita com Advantage+ Audience OFF
**Regra:** Ao copiar targeting de ad set existente para criar um novo com `advantage_audience: 0`, SEMPRE remover o campo `age_range` (expansão de idade do Advantage+). Com ele presente a API rejeita com subcode 1487079 ("targeting_automation must be enabled to use age_range"). Usar só age_min/age_max.
**Contexto:** Criação do conjunto CONDOMINIOS na campanha WPP da Desygn; targeting copiado de ad set antigo que tinha advantage_audience=1.

### 2026-07-19 — degrees_of_freedom_spec com standard_enhancements foi DESCONTINUADO
**Regra:** A API rejeita criativo novo com `degrees_of_freedom_spec.creative_features_spec.standard_enhancements` (subcode 3858504 — "defina recursos individuais"). NÃO copiar o degrees_of_freedom_spec de criativos antigos; omitir o campo ou definir cada recurso individual (image_touchups, text_optimizations etc.).
**Contexto:** Mesmo build 19/07: replicar o dof do criativo modelo falhou; resolvido omitindo o campo.

---

### 2026-04-03 — Sempre incluir CTA no criativo
**Regra:** Ao criar criativos (create.py creative), SEMPRE incluir call_to_action_type. Padrão: LEARN_MORE pra tráfego, SIGN_UP pra leads, SHOP_NOW pra vendas. Nunca criar criativo sem CTA.
**Contexto:** Criou carrossel sem botão de CTA. Usuário teve que corrigir manualmente.

### 2026-04-03 — Carrossel Instagram: multi_share_end_card=false
**Regra:** Em campanhas de visita ao perfil Instagram, SEMPRE usar multi_share_end_card=false e multi_share_optimized=false no criativo.
**Contexto:** Cartão "Ver mais" sem URL quebrou o anúncio em 10 posicionamentos. O end_card exige uma URL de destino que não existe em campanhas de perfil.

### 2026-04-03 — Sempre passar instagram_user_id no criativo
**Regra:** Ao criar criativos pra Instagram, SEMPRE usar --instagram-user-id com o ID da conta Instagram do cliente (do contas.yaml).
**Contexto:** Sem instagram_user_id, o ad não publica no Instagram. Erro: "Seu anúncio deve ser associado a uma conta do Instagram."

### 2026-04-03 — Desligar format options em carrosséis
**Regra:** Ao criar ads de carrossel, SEMPRE passar --degrees-of-freedom-spec com OPT_OUT pra carousel_to_video, image_touchups e standard_enhancements.
**Contexto:** "Blocos de coleção" e "mídia única" distorcem o carrossel sequencial. Desligar pra manter ordem dos slides.

### 2026-07-09 — explore_home exige explore junto
**Regra:** Ao criar ad set com instagram_positions incluindo explore_home, SEMPRE incluir "explore" tambem. A API rejeita explore_home sozinho (subcode 2490392), mesmo que ad sets antigos apareçam so com explore_home na leitura.
**Contexto:** Criacao do ad set da Maderarte falhou ate adicionar "explore" na lista.

### 2026-07-09 — Publico Advantage+ nao desliga: criar ad set novo
**Regra:** Ad set criado com advantage_audience=1 NAO permite trocar flexible_spec/interesses por controles depois (subcode 1359202). Para mudar interesses nesses casos, criar ad set NOVO com advantage_audience=0 na mesma campanha e pausar o antigo.
**Contexto:** Troca de interesses do SOFA VOLUPTA (Desygn) foi bloqueada pela API; resolvido criando [REGIOES] - SOFA VOLUPTA [INTERESSES CJ].

### 2026-07-09 — Campanha com CBO desativado trava tipo de orcamento
**Regra:** Se a campanha ja teve orcamento de campanha (CBO) desativado, ad sets novos nela so aceitam o MESMO tipo de orcamento de antes (subcode 1885994). Se lifetime falhar, usar daily equivalente (ex: R$50/dia x 5 dias = R$250) com end_time.
**Contexto:** Ad set novo na campanha (M) [ENGJ_QUENTE_IG_MSG] da Desygn rejeitou lifetime_budget; resolvido com daily 5000 + end_time.

### 2026-07-14 — Campanha ABO exige is_adset_budget_sharing_enabled
**Regra:** Ao criar campanha SEM orcamento de campanha (ABO), SEMPRE passar is_adset_budget_sharing_enabled (true/false; padrao da Mileny: false). Sem o campo a API rejeita com subcode 4834011.
**Contexto:** Criacao da (M) [ENGJ_QUENTE_WPP] 14/07 da Desygn falhou via create.py; resolvido com POST direto incluindo o campo.
**Atualizado 2026-08-25:** o create.py JA envia o campo (scripts/create.py:57, flag --adset-budget-sharing, default false) — nao precisa mais de POST direto. So lembrar do campo em script proprio que fale com o Graph na mao.

### 2026-07-14 — Ad set de mensagem exige bid_strategy explicito
**Regra:** Ao criar ad set de CONVERSATIONS (msg no Direct/WhatsApp), SEMPRE passar --bid-strategy LOWEST_COST_WITHOUT_CAP explicito. Sem isso a API rejeita com subcode 2490487 ("valor de lance obrigatorio para a estrategia de lance"), mesmo a campanha e o ad set fonte nao tendo bid cap.
**Contexto:** Criacao do [BR] - NAVEGANTES [INTERESSES LUXO] na Desygn falhou 2x ate passar o bid_strategy explicito. O erro so ficou claro consultando error_user_msg via chamada direta a Graph API (os scripts mostram so o subcode).

### 2026-07-14 — Ad set de engajamento/video exige destination_type
**Regra:** Em campanhas OUTCOME_ENGAGEMENT, SEMPRE passar --destination-type no create.py adset: ON_POST para POST_ENGAGEMENT, ON_VIDEO para THRUPLAY. Para leads com formulario nativo: ON_AD + promoted_object page_id. Sem isso a API aceita o ad set mas REJEITA os ads com subcodes confusos (2061015 sem CTA, 1885154 com CTA).
**Contexto:** Build do funil Boali: ads das fases 2-3 falharam repetidamente ate copiar o destination_type das campanhas antigas da conta. QUALITY_LEAD + ON_AD tambem existe mas exige integracao Conversion Leads (subcode 1885760) — usar LEAD_GENERATION como padrao.

### 2026-07-14 — CBO exige bid_strategy na campanha
**Regra:** Ao criar campanha CBO via API (daily_budget na campanha), definir bid_strategy=LOWEST_COST_WITHOUT_CAP na campanha ANTES de criar ad sets. Sem isso o ad set falha com subcode 1815857.
**Contexto:** Build Boali: 4 campanhas CBO criadas sem bid_strategy; ad sets so passaram apos api_update com LOWEST_COST_WITHOUT_CAP.

### 2026-07-14 — Imagem estatica nao roda como photo_data no Instagram
**Regra:** Anuncio de imagem para posicionamentos Instagram nao aceita photo_data puro (subcode 2446383) nem link_data em otimizacao POST_ENGAGEMENT (1885154). Para estatico em fase de engajamento: publicar organico e impulsionar, converter em video, ou usar em campanha de trafego com link_data.
**Contexto:** Estaticos ModeloV2/TamanhoDoMercado da Boali ficaram fora da fase 2 por isso.

### 2026-07-09 — Campanha ARCHIVED so edita nome
**Regra:** Campanha arquivada/excluida no Ads Manager nao aceita mudanca de status nem de config via API (subcode 1487566) — so nome. duplicate-campaign --deep NAO copia ad sets/ads arquivados (vem vazio). Reconstruir filhos manualmente reutilizando os creative_ids (criativos sobrevivem ao arquivamento).
**Contexto:** [CP3] da Maderarte foi arquivada no meio da operacao; a copia veio sem filhos e o ad set foi recriado na mao.

### 2026-07-19 — CTA WHATSAPP_MESSAGE em video_data nao aceita value.link
**Regra:** Em criativos de video para WhatsApp (video_data), o call_to_action deve ser apenas {"type":"WHATSAPP_MESSAGE"} SEM value.link (subcode 1815630). O destino vem do ad set (destination_type WHATSAPP + promoted_object page_id). Em link_data (carrossel/imagem) o value.link e aceito.
**Contexto:** Build da campanha de videos da Casa de Vidro falhou ate remover o link do CTA.

### 2026-07-21 — Anuncio limpo sempre: desligar Advantage+ Creative Enhancements
**Regra (Mileny, permanente para TODAS as campanhas do Funil Espiral):** Todo anuncio novo (imagem ou video) deve ser criado com degrees_of_freedom_spec desligando os creative enhancements automaticos da Meta (IA, musica, toques automaticos, overlays). Passar isso direto no create_ad (nao depois via update - se o ad ja estiver ARCHIVED o campo fica bloqueado).
**⚠️ CORRIGIDO 2026-07-24:** os campos originalmente listados aqui (standard_enhancements, image_touchups, text_improvements, add_overlays, visual_touch_ups, music, 3d_animation, image_templates) estao DESCONTINUADOS pela API (ver regra de 2026-07-19 acima) e causam erro subcode 3858504 em criativo de video. Os campos validos hoje (confirmados no build dos 3 creatives de prova social da AFS) sao: advantage_plus_creative, enhance_cta, text_optimizations, video_auto_crop, video_uncrop, pac_relaxation — todos com enroll_status OPT_OUT. Campos como inline_comment, reveal_details_over_time, show_destination_blurbs, show_summary, video_filtering existem mas sao so informativos (podem ficar OPT_IN). Meta muda esses nomes de campo com frequencia — se der subcode 3858504 ou "defina recursos individuais", ler um creative recente e funcional da propria conta (`GET /{creative_id}?fields=degrees_of_freedom_spec`) pra pegar os nomes atuais antes de tentar de novo.
**Contexto:** Mileny pediu explicitamente para nunca deixar "sugestoes de outros videos ativos" ligadas - a Meta vem ativando esses enhancements por padrao e ela quer o anuncio sempre "limpo".

### 2026-07-21 — Campanhas de video/engajamento NUNCA tem botao de CTA
**Regra (Mileny, permanente):** Anuncios em campanhas de objetivo Engajamento (POST_ENGAGEMENT) ou Visualizacao de video (THRUPLAY) devem ser criados SEM call_to_action no object_story_spec - so video_data com title/message, nenhum botao. CTA (LEARN_MORE, SIGN_UP, VIEW_INSTAGRAM_PROFILE) e exclusivo de campanhas de trafego/leads/visita-perfil (Fases 1 e 4 do Funil Espiral).
**Contexto:** Confirmado ao subir os 8 novos criativos da AFS Franquias (fases 1-4) - o padrao ja existia nos ads antigos de CP02/CP03 dessa conta (sem CTA), Mileny reforcou como regra fixa daqui pra frente.

### 2026-07-21 — CAPI so aceita eventos dos ultimos 7 dias
**Regra:** Eventos offline via Conversions API (Purchase, Lead, etc) sao rejeitados pela Meta (subcode 2804003) se o event_time for mais antigo que 7 dias da data de envio. Se o fechamento real for mais antigo, enviar com o timestamp ATUAL (perde precisao de atribuicao mas mantem o sinal de valor pro aprendizado do pixel) e avisar o cliente que quanto mais rapido repassar os dados de venda, melhor a atribuicao.
**Contexto:** Evento da Casa de Vidro (aluguel Stenio Munhoz, fechado 08/04/2026) foi rejeitado ao tentar registrar com a data real - resolvido reenviando com datetime.now().

### 2026-07-21 — Ad set com orcamento vitalicio e data vencida bloqueia criacao de ad
**Regra:** Se um ad set tem lifetime_budget + end_time no passado, criar ad novo falha (subcode 3858750, "conjunto de anuncios expirou"). Estender o end_time exige que o lifetime_budget total seja proporcional aos dias (ex: end_time daqui a 5 meses pediu lifetime_budget > R$2.725 mesmo o ad set tendo so R$175 configurado). Mais simples: criar um ad set NOVO com daily_budget (sem end_time) em vez de tentar reativar o antigo.
**Contexto:** Ad set "REGIAO NORDESTE" (FASE 01 - INDEX, conta Industria AFS) tinha end_time de 05/05/2026 (vencido). Resolvido criando "REGIAO NORDESTE - v2" com daily_budget.

### 2026-07-21 — Campanha com bid_strategy custo mais baixo trava optimization_goal entre ad sets
**Regra:** Numa campanha ja publicada com bid_strategy de custo mais baixo, todos os ad sets precisam ter o MESMO optimization_goal do primeiro ad set (subcode 1885760: "otimizacao para selecoes de veiculacao de anuncios deve ser igual"). Para adicionar um ad set com objetivo diferente (ex: POST_ENGAGEMENT numa campanha que ja tem THRUPLAY), criar uma CAMPANHA NOVA, nao um ad set na existente.
**Contexto:** Tentar criar ad set POST_ENGAGEMENT dentro de "[VIDEO 10 ANOS][ENGAJAMENTO]" (que ja tinha ad set THRUPLAY) falhou; resolvido criando campanha separada "[CARROSSEIS][ENGAJAMENTO] - INDUSTRIA".

### 2026-08-17 — Lead ad com Formulário do Meta: link obrigatório mesmo sem site
**Regra:** Ao criar criativo de anúncio de formulário nativo (ad set com `destination_type: ON_AD`), a Meta exige um campo de link mesmo o destino sendo o formulário:
- `video_data`: o link vai DENTRO de `call_to_action.value`, junto do `lead_gen_form_id` → `{"type":"LEARN_MORE","value":{"lead_gen_form_id":"X","link":"http://fb.me/"}}`. Sem o link: HARD_ERROR 2446429 no ad (fica WITH_ISSUES e não entrega).
- `asset_feed_spec`: exige `link_urls` + `link_url_label` nas asset_customization_rules. Sem isso: erro 100 / subcode 1885800 "URL do link do criativo ausente".
- `link_data`: exige `link` no nível do link_data.
Usar SEMPRE `http://fb.me/` como placeholder (é o que a própria Meta usa em lead ad puro) — com destino ON_AD o formulário prevalece e nada vaza pro site. Nunca colocar a URL real do cliente aí, senão o clique pode ir pro site.
**Contexto:** Migração da campanha QUENTE da Facilmart de "Formulário e site" (WEBSITE_AND_LEAD_FORM) para "Formulário do Meta" (ON_AD). Os 4 criativos falharam em sequência até acertar o formato de cada tipo.

### 2026-08-17 — Posicionamento ig_search não aceita vídeo em anúncio de formulário
**Regra:** O posicionamento `ig_search` (Pesquisa do Instagram) quebra anúncios de VÍDEO em campanhas de lead com formulário nativo — HARD_ERROR 2446429 "Erro de validação do formato do Instagram", o ad fica WITH_ISSUES e nunca entrega. Ao montar conjunto de vídeo pra lead, deixar `instagram_positions: ["stream","story","reels","profile_feed"]` SEM ig_search. Conjunto de imagem com asset_feed_spec aceita ig_search normalmente.
**Regra de diagnóstico:** ad com 2446429 quase sempre é posicionamento incompatível com o formato do criativo — testar removendo posicionamentos antes de mexer no criativo.
**Contexto:** Os 3 ads de vídeo da campanha QUENTE original da Facilmart estavam travados com esse erro desde a criação (14/05) e nunca entregaram — ninguém tinha percebido porque o conjunto vivia pausado. Removido o ig_search na campanha nova e destravou na hora.

### 2026-08-17 — Trocar destino de campanha de lead exige campanha nova, não edição
**Regra:** `destination_type` e `optimization_goal` do ad set não podem ser editados depois de publicado. Pra trocar "Formulário e site" (WEBSITE_AND_LEAD_FORM + OFFSITE_CONVERSIONS + promoted_object com pixel) por "Formulário do Meta" (ON_AD + LEAD_GENERATION + promoted_object com page_id), o caminho é duplicar: campanha nova → conjuntos novos com o destino certo → criativos NOVOS (os antigos carregam a URL do site no CTA e são imutáveis) → pausar a antiga. Copiar targeting com `custom_audiences` normalizado pra `[{"id": X}]` e geo só com `key`/`radius`/`distance_unit`.
**Contexto:** Facilmart, campanha CP 03 QUENTE.

### 2026-08-27 - Cliente com evento custom precisa de acoes_lead no contas.yaml
**Regra:** `diario.py` conta lead por `action_type`. A ordem padrao e: se existir `lead` no dicionario de actions, usa so ele; senao soma os tipos de `LEAD_ACTION_TYPES`. Cliente cujo lead e um evento CUSTOM do pixel nao cai em nenhum dos dois e reporta **0 leads todo dia**, gerando alerta CRITICAL falso de CPL.
Conserto: declarar `acoes_lead` no `contas.yaml` do cliente com os action_types exatos. `extrair_leads(actions, tipos)` e `resumo_periodo(row, tipos)` aceitam a lista e somam so ela; sem a chave o comportamento antigo continua igual (retrocompativel).
```yaml
ponto-alpha:
  acoes_lead:
    - "offsite_conversion.custom.748385968314493"   # WEBINAR NOVA
    - "offsite_conversion.custom.1216939777063621"  # LEAD WEBINAR
```
**Como descobrir o action_type certo:** puxar insights do cliente com o campo `actions` e olhar os `offsite_conversion.custom.<id>` que aparecem com volume. O `<id>` e o id da conversao customizada, nao o do pixel.
**Contexto:** Ponto Alpha reportava 0 leads no diario havia meses e ninguem tinha percebido porque o alerta parecia ruido. AP Ponto tinha o problema oposto - CPL R$ 832 no alerta - porque contava so `lead` e ignorava o `offsite_conversion.fb_pixel_custom`. Depois do conserto, CPL d7 da AP Ponto = R$ 40,26.

### 2026-09-08 - `frequently_in` volta sozinho no `location_types` e nao sai por update
**Regra:** ao criar um conjunto com `location_types` explicito, a Meta **acrescenta `frequently_in` sozinha na ativacao**, e um `POST` depois disso com o spec completo pedindo so `["home"]` retorna `success: true` e e **descartado em silencio** — a releitura 35s depois traz `["frequently_in","home"]` de novo. Mesmo padrao do `excluded_geo_locations` de 17/08: com o conjunto ACTIVE a Meta aceita e joga fora. Pausar/remover/reativar tambem nao resolve, porque ela reaplica na reativacao.
**Impacto pratico (importa quando o geo E o filtro):** `home` = quem MORA no raio; `frequently_in` = quem esta frequentemente ali, ou seja **quem trabalha no lugar**. Em pino de bairro rico (Jardins, Leblon) isso readmite garcom, manobrista, porteiro e comercio — justamente o publico que o pino queria excluir. Nao invalida o teste, mas suja: contar com isso ao ler o resultado, e nao prometer a ninguem que o conjunto pega "so quem mora".
**O que NAO fazer:** insistir em remover. Ja custou 2 escritas + 2 releituras aqui; e default da plataforma, nao contaminacao de conta.
**Contexto:** Casa de Vidro Paraty 08/09 — campanha `[GEO-PIN] ALTO PADRAO SP-RJ` (`120249369648020510`), conjunto `[PIN/MORA]` (`120249369649830510`) com 15 pinos de 2 km. O `[PIN/DESTINO]` (`120249369651930510`) ficou `["frequently_in","recent","travel_in"]` — nesse caso `frequently_in` atrapalha menos, porque em destino de lazer quem esta "frequentemente ali" ja e majoritariamente segunda residencia.
