# CAPI — Açaí Fruit Show Franquias (implementação de referência)

**Conta:** `act_835633356015496` · **Pixel/Dataset:** `1930108940975664` ("Açaí Fruit Show Franquias")
**Status:** validado ponta a ponta em 08–10/08/2026. Primeira conta da carteira com o circuito completo funcionando.

Este é o modelo a copiar para os outros clientes. O guia genérico continua em `capi-crm.md`.

---

## 1. Por que existe

O formulário registra quem **preenche**. O CAPI devolve à Meta quem **presta**.

Sem isso, o algoritmo otimiza para volume de cadastro — foi exatamente o que produziu 83% de leads abaixo do ticket na AFS. Com os eventos voltando, ele aprende o perfil de quem avança no funil.

---

## 2. As quatro peças

| Peça | Onde | Estado |
|---|---|---|
| Pixel/dataset do cliente | `1930108940975664` | ativo, disparando |
| `leadgen_id` no CRM | campo da integração Meta → CRM | ✅ confirmado 10/08 |
| Critério objetivo de desqualificação | resposta do formulário | ✅ definido |
| Envio dos eventos | `capi.py batch` (hoje) → integração nativa (meta) | manual, automatizável |

**O `leadgen_id` é a peça central.** É o número de 15–17 dígitos que a Meta gera no envio do formulário e permite casamento exato — muito melhor que e-mail/telefone. Sem ele o match é aproximado.

Exemplo real validado:
```
lead_id 2293071588174588  (16 dígitos)
Fabio Mesquita Dozza · Poço Fundo/MG · 08/08/2026
Campanha CP-05 LAL_FRANQUEADOS · Anúncio AD13 MODELO LUCRATIVO
```

---

## 3. Como fizemos, passo a passo

### 3.1 Identificar o pixel
```powershell
python scripts/dataset.py list --account act_835633356015496
```
Retornou `1930108940975664`. **Atenção:** `enable_automatic_matching` estava `false` — vale ligar no Events Manager.

### 3.2 Puxar os leads com o leadgen_id direto da Meta
Não dependemos do CRM para isso — a Meta entrega os leads por formulário:
```
GET /{form_id}/leads?fields=id,created_time,field_data&limit=100
```
Cada item traz `id` (= `leadgen_id`) e `field_data` com as respostas.

Foi assim que descobrimos que **49 de 59 leads (83%) declaravam capital abaixo do ticket** — dado que estava na Meta e nunca chegava ao CRM porque o rótulo da pergunta não batia com o nome do campo.

### 3.3 Montar o CSV
Formato que o `capi.py batch` consome:
```csv
event_name,event_time,lead_id,email,phone
lead_desqualificado,1754640000,2293071588174588,[e-mail removido],[telefone removido]
```
`event_time` em Unix timestamp.

### 3.4 Enviar
```powershell
python scripts/capi.py batch `
  --pixel 1930108940975664 `
  --csv "caminho\arquivo.csv" `
  --crm rd_station
```
Retorno esperado: `{"eventos_no_csv": N, "events_received": N, "lotes": 1}`

### 3.5 O que a chamada faz por baixo
```
POST https://graph.facebook.com/v21.0/1930108940975664/events
{ "data": [{
    "event_name": "lead_desqualificado",
    "event_time": 1754640000,
    "action_source": "system_generated",
    "user_data": { "lead_id": 2293071588174588 }
}]}
```
**O `lead_id` vai dentro de `user_data` e SEM hash** — é ID nativo da Meta. E-mail e telefone, quando usados, vão em SHA-256 (o `capi.py` normaliza e hasheia sozinho).

---

## 4. Regras aprendidas na prática

**Janela de 7 dias.** A Meta recusa eventos mais antigos que isso (subcode 2804003). Na primeira tentativa, 47 dos 49 eventos foram rejeitados — só 2 estavam na janela. **Não existe backfill histórico.** Por isso o envio precisa ser pelo menos semanal, de preferência diário.

**Nomes de evento padronizados** entre todos os clientes:
```
lead_qualificado → reuniao_agendada → proposta_enviada → venda
(+ lead_desqualificado, que também é sinal útil)
```

**Otimização do conjunto continua `LEAD_GENERATION`.** Não trocar para Conversion Leads antes de haver volume — a API rejeita com subcode 1885760 se a integração não estiver madura.

---

## 5. Como o CRM devolve o sinal (combinado em 11/08)

O CRM não fala com a Meta sozinho. O circuito é:

```
lead entra pelo formulário  →  CRM guarda COM o leadgen_id
Gleice trabalha e classifica  →  conector detecta  →  evento vai pro dataset
Meta casa pelo leadgen_id  →  aprende
```

**A Gleice faz UMA coisa: marca a tag `qualificado`.** Todo o resto é lido do trabalho que ela já faz.

| Evento | De onde sai | Ação manual? |
|---|---|---|
| `venda` | etapa Fechado / status ganho | não |
| `proposta_enviada` | etapa Proposta | não |
| `reuniao_agendada` | etapa Reunião | não |
| **`lead_qualificado`** | **tag `qualificado`** | **sim — única novidade** |
| `lead_desqualificado` | etapa Perda | não |
| `lead_desqualificado` | capital abaixo do ticket | não (vem do formulário) |

**Por que tag e não etapa para o qualificado:** etapa é foto do momento. Se o lead passar por "Qualificado" e seguir para "Reunião" antes do envio, o sinal se perde. Tag é permanente e acumulativa — foi a Mileny que identificou isso.

**Definição acordada de lead qualificado:** declarou R$ 200 mil ou mais **e** o comercial falou com a pessoa **e** ela confirmou que quer seguir. O julgamento humano tem precedência sobre o capital declarado (pode haver financiamento, sócio, FGTS).

**Filtro obrigatório:** só o pipeline **Closer**. O export traz Trendpel e indústria junto.

**Anti-duplicação:** `relatorios/capi_afs_enviados.json` guarda cada par (lead_id, evento) já enviado. Rodando 2x/semana, ninguém recebe o mesmo sinal duas vezes; quando o lead evolui de qualificado para reunião, o novo sinal passa normal.

**Cadência:** 2x por semana (ex: terça e sexta). A janela da Meta é de 7 dias contados da **mudança de estágio**, não da criação do lead — envio semanal deixa o pior caso no limite.

### Etapas reais do funil Closer (mapeadas em 13/08/2026)

| # | Etapa no CRM | Evento enviado |
|---|---|---|
| 1 | Leads Novos | — |
| 2 | Retorno 1º Dia | — |
| 3 | Retorno 2º Dia | — |
| 4 | Retorno 3º Dia | — |
| 5 | Não Atendeu | — |
| 6 | Atendeu | — |
| 7 | StandBy | — |
| 8 | **1a Reunião** | `reuniao_agendada` |
| 9 | **Falar com o Franqueado** | `reuniao_agendada` |
| 10 | **2a Reunião - COF** | `proposta_enviada` (COF = oferta formal) |
| 11 | **Ficha Cadastral** | `proposta_enviada` |
| 12 | **3a Reunião - Falar com o Diretor** | `proposta_enviada` |
| 13 | **Disparo de Mensagens** | `proposta_enviada` |
| 14 | **Ganho** | `venda` |
| 15 | **Perda** | `lead_desqualificado` |

O mapa no script é **explícito**, não por trecho de texto — senão "3a Reunião - Falar com o Diretor" seria confundido com uma primeira reunião e sub-sinalizaria. Se aparecer etapa fora da lista, o script imprime `!! ETAPA DESCONHECIDA` em vez de ignorar calado.

**Outros pipelines na mesma conta de CRM** (ignorar): Trendpel, Saborazzi, Açai Fruit Show, Distribuidores, Repasse Loja, Fale conosco. O filtro `Pipeline == Closer` cuida disso.

---

## 5.1 Critério de desqualificação (AFS)

Formulários em uso a partir de 10/08:

| Formulário | ID | Intenção alta |
|---|---|---|
| `AFS FRANQUIA EXPANSAO QUALIFICADO` | `1800556261308285` | sim |
| `AFS FRANQUIA EXPANSAO CONTROLE` | `1385814793614198` | não (só CJ2 Salvador) |

Regra de classificação pela resposta de **Capital Disponível**:

| Resposta | Chave | Evento |
|---|---|---|
| Acima de R$100mil | `acima_100` | `lead_desqualificado` — abaixo do ticket de R$270 mil |
| Acima de R$200mil | `acima_200` | aguardar classificação do comercial |
| Acima de R$300mil | `acima_300` | aguardar classificação do comercial |

> **Conferir sempre `key` vs `value`.** Reordenar opções pelo Gerenciador troca os valores e mantém as chaves, invertendo o significado silenciosamente. Aconteceu na AFS em 10/08.

O que conta como `lead_qualificado` de fato quem define é o comercial (Gleice) — precisa de critério objetivo acordado, não impressão.

---

## 6. Por que Conversion Leads ainda não

Exigências oficiais da Meta vs. realidade da conta:

| Requisito | Meta exige | AFS |
|---|---|---|
| Volume | 200 leads/mês | ~30 ❌ |
| Meta Lead ID no CRM | obrigatório | ✅ |
| Envio | ≥1x/dia | manual ❌ |
| Etapa em até 28 dias | sim | ✅ |
| Taxa de conversão da etapa | 1–40% | ✅ |

Aos R$ 250/dia e com a rede absorvendo 4–6 franqueados novos por ano, os 200/mês custariam ~R$38 mil/mês. **Está fora de alcance por estrutura, não por configuração.** O CAPI aqui serve para: acumular histórico no pixel, alimentar públicos qualificados no futuro e dar atribuição real por anúncio.

---

## 7. Próximo passo — automatizar

**Correção de 18/08/2026:** o CRM da AFS **não é o RD e não é parceiro do Events
Manager**. É um CRM próprio ("CRM Fist"), cujo app está vinculado à **BM da
Slimcenter**. Não existe conector para ligar — a chamada de CAPI tem que ser
implementada do lado do CRM.

**Bloqueio encontrado:** o pixel `1930108940975664` pertence à BM
`1801420144091312` ("AÇAI FRUIT SHOW") e `shared_agencies` está **vazio** — o app
do CRM não tem acesso de escrita ao dataset. Sem resolver isso, nada do lado do
dev funciona.

**Decisão (18/08): token de system user, não compartilhar o pixel.** Compartilhar
o dataset da AFS com a BM da Slimcenter misturaria ativos de dois clientes e
teria de ser refeito cliente a cliente. Com token, o CRM guarda um por cliente e
o mesmo modelo serve para Slimcenter, Boali, Cheirin.

1. BM da AÇAI FRUIT SHOW → Configurações do Negócio → Usuários do sistema → criar
   `crm-capi` → Adicionar ativos → Fontes de dados → pixel → permissão **Gerenciar**
2. Gerar token com `ads_management` + `business_management`, entregar ao dev
3. Dev implementa `POST /1930108940975664/events` na mudança de etapa (payload da
   seção 3.5; `lead_id` sem hash dentro de `user_data`)
4. Só o pipeline **Closer**; disparo no momento da mudança (janela de 7 dias)
5. Guardar par (lead_id, evento) para não duplicar

**`leadgen_id` confirmado pela Mileny em 18/08:** já chega na identificação do
lead ao entrar no CRM — logo sai no export, e o casamento é exato.

Até o dev entregar, o `capi.py batch` roda 2x/semana com o export do Closer.

---

## 8. Estado em 10/08/2026

- ✅ Pixel identificado e disparando
- ✅ `leadgen_id` chegando no CRM
- ✅ Envio validado — 2 eventos recebidos
- ✅ Critério de desqualificação definido e legível pelo comercial
- ⬜ Ligar correspondência automática no pixel (segue `false` em 18/08)
- ⬜ Criar system user `crm-capi` na BM da AFS e passar o token ao dev do CRM
- ⬜ Dev do CRM implementar o POST na mudança de etapa
- ⬜ Acordar com a Gleice o que é `lead_qualificado`
- ⬜ Rotina 2x/semana de envio até a automação entrar

## 9. Estado em 18/08/2026 — o custo de não ter rodado

Diagnóstico do pixel: `health: DEGRADED`, automatic matching `false`, e nos
últimos 7 dias **apenas `PageView` (444) e `Lead` (20) — zero
`lead_desqualificado`**. A rotina de envio nunca começou depois de 10/08.

Resultado prático: a Meta passou a semana sem saber que os leads viraram Perda e
continuou comprando o mesmo perfil. O anúncio `PROVA SOCIAL FRANQUEADO` gerou 17
leads a R$ 8,48 (43% declarando acima de R$ 300 mil) e o comercial reportou
**nenhum lead qualificado**. É a demonstração de que o CAPI aqui não é refinamento
— é o que impede a campanha de derivar para quem preenche formulário fácil.

---

## 10. Topologia de permissões — o que travou o dia inteiro

**Três permissões diferentes que todo mundo trata como uma só.** Foi presumir que
eram a mesma coisa que custou a tarde de 18/08:

| O que se quer fazer | O que exige | Falha típica |
|---|---|---|
| Ler os leads do formulário | Página como ativo + `leads_retrieval` | — |
| **Enviar evento pro dataset** | só `ads_management` + pixel vinculado à conta de anúncio | — |
| Editar configuração do pixel | **pixel atribuído como ativo ao system user** | code 10, mensagem vazia |

Consequências observadas na AFS:

- O CRM tinha o `leadgen_id` chegando (permissão 1) mas **não conseguiria enviar
  evento nenhum** — o pixel não estava entre os ativos do `acaifruit admr`.
- O system user da agência (`relatórios-automaçoes`, BM Mileny Marketing
  `1453030282528473`) **enviou os 9 eventos sem ter o pixel** — permissão 2 basta.
- Ligar automatic matching falhou repetidas vezes (permissão 3). Resolvido pela
  Mileny no painel.

**Parceria ≠ ativo.** A Mileny Marketing já era parceira da BM da AFS (é assim que
a agência administra as contas de anúncio), e mesmo assim `shared_agencies` do
pixel voltava vazio. Ser parceiro não entrega o ativo; o ativo é marcado
separadamente, em Parceiros → Adicionar ativos → Fontes de dados.

**Padrão que funciona nos três clientes:** system user **dentro da BM do cliente**,
com o pixel atribuído. Confirmado lendo `assigned_users` de cada pixel — nenhum
dos usuários de CAPI de Boali ou Cheirin pertence à BM da agência.

### Comandos de verificação

```powershell
python scripts/dataset.py diagnostics --id <PIXEL>
```
```
GET /<PIXEL>/assigned_users?business=<BM_DO_CLIENTE>&fields=id,name,tasks
GET /<PIXEL>/shared_agencies?fields=id,name
```
Alvo: um usuário com `ADVERTISE,UPLOAD,ANALYZE,EDIT`.

---

## 11. Roteiro de replicação — Boali e Cheirin Bão

A implementar depois que a AFS estiver validada. **O app `CRM AI FIRST` e os cinco
nomes de evento são os mesmos**; muda só o pixel de destino e o filtro de pipeline
— por isso a especificação pede ao dev que ambos sejam configuração, não valor
fixo no código.

| Cliente | Conta | Pixel de destino | BM dona |
|---|---|---|---|
| Açaí Fruit Show | `act_835633356015496` | `1930108940975664` | 1801420144091312 |
| Boali | `act_295475086762368` | `4253291668254806` (`lead franquia`) | 920268164725941 |
| Cheirin Bão franquia | `act_884652616778712` | **a confirmar** — ver abaixo | 225005935945447 |

> **Cheirin: o pixel de destino ainda NÃO está decidido.** Correção de 19/08 — o
> conjunto que já recebe CAPI é **`Novo CB - 07/26` (`2525428314626049`)**, não o
> `[Novo Pixel] Cheirin Bão - 23/01` (`1113125670113540`) que estava anotado aqui
> antes. O `Novo CB` é o único ativo conectado à `act_884652616778712`, tem o
> `Conversions API System User` (`1373588638320216`) com
> `ADVERTISE,UPLOAD,ANALYZE,EDIT`, automatic matching ligado, e já recebe um evento
> próprio chamado **`lead_form`** (119 em 30 dias, ~4/dia desde 30/07).
> **Confirmado em 19/08 no Gerenciador de Eventos: a integração do `lead_form` é
> "Várias" — API de Conversões E navegador.** Ou seja, o dev do CRM AI FIRST já
> implementou CAPI nesta conta; a parte de navegador vem do pixel do site na
> `poscadastro.cheirinbao.com.br`.
> **O que isso significa para a AFS:** não é integração nova para o dev — mesmo
> endpoint e mesma autenticação, mudando o gatilho (mudança de etapa em vez de
> entrada do lead), o pixel de destino e o `user_data` (que passa a levar
> `lead_id` sem hash).
> **O que isso NÃO resolve:** `lead_form` avisa que o lead chegou — informação que
> a Meta já tem. Nenhum evento de funil (reunião, proposta, venda, Perda) existe
> em nenhum dos clientes.
> Antes de replicar na Cheirin: confirmar qual conjunto as campanhas de franquia
> realmente usam como `promoted_object`. A BM `UF Gestão de Marcas e Patentes` tem
> ~10 pixels (`Pixel de Cheirin Bão`, `Loja - Cheirin Bão`, `XFranchise`, `Novas
> Landing Pages`, `BeautyB Only`, `DS_Women`, `Depile-se`…), vários com alerta —
> escolher por ID conferido, jamais por nome.

### Mapas de etapa por cliente (levantados em 19/08/2026)

**Os três clientes usam formulário nativo da Meta** (`LEAD_GENERATION` +
`destination_type: ON_AD`), então os três têm `leadgen_id` e casamento exato. O
dev escreve um código só. Confirmado na Boali lendo os conjuntos ativos.

**Cheirin Bão** — quase idêntico à AFS: **não tem** os "Retorno 1º/2º/3º Dia", a
Perda fica na posição 3, e tem uma etapa a mais, **`Incoerente`**.

| Etapa | Evento |
|---|---|
| Leads Novos · Não Atendeu · Atendeu · StandBy | — |
| Perda | `lead_desqualificado` |
| **Incoerente** | `lead_desqualificado` |
| 1a Reunião · Falar com o Franqueado | `reuniao_agendada` |
| 2a Reunião COF · Ficha Cadastral · 3a Reunião · Disparo de Mensagens | `proposta_enviada` |
| Ganho | `venda` |

> `Incoerente` (a confirmar com o comercial) parece ser o lead cujo dado não fecha
> — o perfil que na AFS apareceu como nome de Instagram e telefone inválido. Se
> for isso, é o sinal **mais limpo** de todos: Perda é ambígua, Incoerente não.

**Boali** — funil mais longo e com **"Lead qualificado" como etapa própria**: ali
o sinal de qualificação não depende de tag nova, ao contrário da AFS.

| Etapa | Evento |
|---|---|
| Novo cadastro · Não atendeu · Primeiro contato · Qualificação | — |
| 1ª reunião com o Daniel | `reuniao_agendada` + `lead_qualificado` |
| COF/DRE/Minuta · Ficha cadastral · Emissão de contrato · Aguardando pagamento · Pagamento | `proposta_enviada` |
| Lead qualificado · tag `lead com potencial` | `lead_qualificado` |
| Vendido (Won) | `venda` |
| Perda (Lost) | `lead_desqualificado`, com a condicional abaixo |
| **Lead internacional** | **a definir** — se for candidato fora do Brasil, vale `lead_desqualificado` |

**Regra da Perda (vale para os três):** `lead_desqualificado` só dispara na Perda
**se o lead nunca passou por etapa positiva**. Um lead que chegou à reunião e
depois se perdeu era um lead bom — mandar desqualificado nele contradiz o
`reuniao_agendada` já enviado e ensina a Meta a fugir do perfil certo.

**Volume relativo (19/08):** Boali roda ~R$700/dia em campanhas de lead (CP-04
R$350, CP-05 R$250, CP-06 R$100) contra R$197 da AFS — é onde o CAPI tem mais a
render. A Boali já tem público `LAL QUALIFICADOS`, sinal de que a qualificação já
é feita à mão lá.

---

---

## 12. CHEIRIN BÃO — estado real em 02/09/2026 (LEIA ANTES DA §11)

⚠️ **As notas de 19/08 abaixo estão desatualizadas em dois pontos.** Corrigido depois de
auditar a conta com a Mileny em 01-02/09:

### 12.1 O dev ENTREGOU — os eventos de funil existem

A §11 diz *"nenhum evento de funil (reunião, proposta, venda, Perda) existe em nenhum dos
clientes"*. **Isso não vale mais para a Cheirin.** Em agosto/2026, no pixel
`1113125670113540`:

| Evento | Agosto |
|---|---|
| `lead_desqualificado` | 55 |
| `lead_qualificado` | 12 |
| `reuniao_agendada` | 6 |

Bate com o mapa de etapas da Cheirin da §333. O envio é **automático na mudança de etapa** —
não é lote manual. Não precisa reconstruir nada disso.

### 12.2 Pixel: a §11 tinha duas notas contraditórias. A correta é esta

| Pixel | Papel real | `is_crm` |
|---|---|---|
| **`1113125670113540`** ([Novo Pixel] Cheirin Bão - 23/01) | **fonte de CRM — recebe os eventos de funil** | **true** |
| `2525428314626049` (Novo CB - 07/26) | mede as landing pages (`bl.cheirinbao.com.br`), recebe `lead_form` | false |

A nota de 19/08 que mandava usar o `Novo CB` para CAPI estava errada — ela confundiu
`lead_form` (evento de LP) com evento de funil. **O dev escolheu o pixel certo.**

Os dois têm o `Conversions API System User` (`1373588638320216`) com
`ADVERTISE,UPLOAD,ANALYZE,EDIT` e os dois estão vinculados à `act_884652616778712`.
Permissão não é o problema.

### 12.3 Funil único — a §"duas operações" não se aplica ao CRM

Confirmado pela Mileny em 02/09: **os dois gestores jogam no mesmo funil do CRM.** A
distinção de captação (formulário nativo × landing page) continua existindo, mas **não** se
traduz em pipelines separados. Não filtrar por pipeline nesta conta.

### 12.4 A Cheirin PASSA nos requisitos da Meta — diferente da AFS

A §6 registra que a AFS não alcança Conversion Leads por volume. **Na Cheirin o quadro é
outro:**

| Requisito | Meta exige | Cheirin (02/09) |
|---|---|---|
| Volume de leads | 200/mês | **300 em 30d** ✅ |
| Taxa de conversão da etapa | 1–40% | **4,0%** (12/300) ✅ |
| Meta Lead ID disponível | obrigatório | ✅ formulário nativo |
| Envio | ≥1x/dia | ✅ automático na mudança de etapa |

**É o cliente da carteira onde Conversion Leads é viável hoje.**

### 12.5 O que continua travado — e é a única coisa

Os eventos chegam, mas **não casam**. É exatamente o §8 ("evento aceito não é evento
casado"):

- `valid_entries: 0` · `matched_entries: 0`
- Pedir um ad set `QUALITY_LEAD` apontando o evento do funil é recusado:

```
subcode 2490291 — "Não é uma fonte de dados CRM válida.
Para promoted_object, precisam ser dados do CRM com a configuração concluída."
```

Detalhe que confirma: as ações `offsite_*_add_meta_leads` batem **1:1** com `lead` em toda
janela (88/88, 179/179, 301/301, 1206/1206). Se houvesse estágio de CRM reconhecido, seriam
menores. Não há informação de qualificação chegando ao relatório.

**`QUALITY_LEAD` só com `page_id` é ACEITO** (testado em validate_only) — mas otimiza pelo
palpite genérico da Meta, não pelo CRM. Não vale antes de concluir o mapeamento.

> ⚠️ **CORREÇÃO 15/09/2026 — a recusa 2490291 acima pode ter sido do payload, não da conta.** Na Cheirin, o mesmo
> erro sumiu ao incluir `lead_ads_form_event_source_type: "onsite_crm_single_event"` no `promoted_object` (junto de
> `page_id`, `pixel_id`, `custom_event_type: OTHER`, `custom_event_str`). O CRM da Cheirin está conectado, com
> aprendizado concluído, e o conjunto otimizando por `lead_qualificado` valida. Ver aprendizados.md 15/09. Antes de
> repetir o diagnóstico "evento não casa / CRM não configurado" na AFS ou na Boali, refazer o teste com esse campo.

### 12.6 Não existe API para concluir o mapeamento

Testado e descartado em 02/09: `crm_data_sources`, `lead_stages`, `crm_stages`,
`leadgen_conversion_configs` (no pixel, na página e no negócio) retornam *"Unknown path
components"*; escrever `crm_stage_mapping` direto no pixel é campo inexistente.
**É etapa de painel, no Gerenciador de Eventos.** Claude não faz.

### 12.7 A pergunta objetiva para o dev

Hipótese que sobrou depois de descartar pixel, permissão e pipeline: **o valor mandado em
`user_data.lead_id` pode não ser o `leadgen_id` da Meta**, e sim o ID interno do CRM.

O `leadgen_id` é número de **16–17 dígitos** gerado pela Meta. Amostra real puxada da API em
02/09 (formulários `3282443085242041` e `1967027103944401`):

```
4097309120401962   02/09 04:21
1048218674594179   01/09 23:29
1642505307242472   01/09 23:14
1610319314467068   01/09 20:39
28727505656853570  01/09 00:32   (17 dígitos)
```

Perguntar ao dev: *"o `lead_id` que vocês mandam no `user_data` é este número da Meta, ou é
o ID do lead dentro do CRM?"* — se for o do CRM, nada casa, e é a explicação completa do
`matched_entries: 0`.

Como conferir sem depender dele: `GET /{form_id}/leads?fields=id,created_time,campaign_id`
devolve o `leadgen_id` de cada lead. Comparar com o que está gravado no CRM.

---

### Cheirin: duas operações na mesma conta (informado pela Mileny em 19/08 — ver §12.3, o CRM é um só)

**A conta de franquia da Cheirin é dividida entre dois gestores, com modelos de
captação diferentes:**

| | Mileny | O outro gestor |
|---|---|---|
| Captação | **Formulário nativo da Meta** | Landing page |
| Identificador | `leadgen_id` — casamento **exato** | sem `leadgen_id` — casa por e-mail/telefone em hash |
| Evento que já existe | nenhum | `lead_form` (do `poscadastro.cheirinbao.com.br`) |

Consequências práticas:

1. **O `lead_form` do dataset `Novo CB - 07/26` é do funil do outro gestor**, não
   dos leads da Mileny. Não usar como referência de volume nem de qualidade.
2. **Os leads da Mileny na Cheirin têm `leadgen_id`**, igual à AFS. A replicação
   lá é a mesma arquitetura da Açaí, não uma variação — o dev reaproveita tudo.
3. **Um mesmo dataset vai receber sinais de dois funis diferentes.** Ao ler
   resultado ou montar público a partir dos eventos, filtrar por campanha/origem;
   os números crus misturam as duas operações.
4. Confirmar em qual pipeline do CRM caem os leads de cada gestor antes de mapear
   as etapas — o mapa do funil Closer é da AFS e pode não valer aqui.
> **Correção de 15/09 (Mileny):** "Cheirin Bão - Principal" é a conta de anúncios do
> **outro gestor**, não um segundo nome da MT. A MT (`act_884652616778712`) é a da
> Mileny. As duas usam o mesmo dataset `1113125670113540`. A nota antiga ("mesma
> conta com dois nomes") estava errada e levou a uma conclusão errada em 15/09.
> Continua valendo: **escolher sempre por ID, nunca por nome.**

Estado verificado em 18/08: as três já estão com automatic matching ligado, e as
três já têm system user com permissão completa no pixel certo.

### Passo a passo, na ordem

Quem executa cada passo está marcado. Não pular a ordem: os passos 1–4 são
pré-requisito do 5, e o 8 é o único que prova que funcionou.

**1. Diagnóstico do pixel** *(Claude)*
```powershell
python scripts/dataset.py diagnostics --id <PIXEL_DO_CLIENTE>
```
Registrar `health`, `enable_automatic_matching` e quais eventos já chegam. Serve
de linha de base — sem isso não dá pra saber depois se o que apareceu foi o dev.

**2. Conferir quem tem o pixel** *(Claude)*
```
GET /<PIXEL>/assigned_users?business=<BM_DO_CLIENTE>&fields=id,name,tasks
```
Alvo: um system user com `ADVERTISE,UPLOAD,ANALYZE,EDIT`. Se vier vazio ou só
`ANALYZE`, é o bloqueio da AFS se repetindo — vai para o passo 3.

**3. Atribuir o pixel ao system user do CRM** *(Mileny, no painel)*
Configurações do Negócio da BM do cliente → Usuários do sistema → o usuário do
CRM → **Adicionar ativos** → **Fontes de dados** → o pixel → **Gerenciar**.
Não é criar usuário novo, e não é parceria: é marcar o ativo. Ver §10.

**4. Automatic matching** *(Mileny, no painel)*
Events Manager → pixel → Configurações → "Correspondência automática avançada" →
ligar → e-mail, telefone, nome, cidade, estado, CEP. Em 18/08 já estava ligado nos
três clientes — conferir, não presumir.

**5. Mapear as etapas daquele pipeline** *(Mileny + Claude)*
**O mapa do funil Closer é da AFS.** Cada cliente tem nomes de etapa próprios.
Listar as etapas reais e traduzir para os cinco eventos padrão, sempre de forma
explícita — nunca por trecho de texto (buscar "Reunião" faz "3a Reunião - Falar
com o Diretor" cair como primeira reunião).

**6. Passar pixel + mapa de etapas ao dev** *(Mileny)*
Se ele construiu a AFS com pixel e pipeline como configuração — como a
especificação pediu — aqui é só trocar dois parâmetros. Nada de código novo.

**7. Regra de capital, se o formulário do cliente tiver a pergunta** *(dev)*
Lead que entra declarando capital abaixo do ticket dispara `lead_desqualificado`
na hora. Não vem de etapa, vem da resposta do formulário — é o passo que mais
gente esquece e o que mais rápido corrige a entrega.

**8. Validar antes de dar por pronto** *(Claude)*
Mover um lead real de etapa e conferir três coisas: o `lead_id` **casou** (evento
aceito não é evento casado — `events_received` volta sucesso mesmo sem
correspondência), os nomes de evento estão exatos, e o `event_time` é o da
mudança de etapa. Confirmar em `dataset.py events` que o evento aparece atribuído
à campanha de origem.

**Armadilhas já conhecidas:**

- **Boali tem um segundo pixel**, `Expansão BOALI Brasil` (`1247434766734345`), em
  que o system user de CAPI tem apenas `ANALYZE`. Apontar pra ele faz o envio
  falhar. O certo é o `lead franquia`.
- **Cheirin franquia tem 5 pixels vinculados à conta**, 3 deles de outras marcas
  (`DS_Women`, `Pixel Depile-se`, `Jornada 6D`), de BMs diferentes. Escolher o
  pixel errado é fácil — o certo é `[Novo Pixel] Cheirin Bão - 23/01`.
- **Cheirin MKT (`act_1398047248415230`) não tem pixel nenhum.**
- **O app é infraestrutura compartilhada.** Restrição no `CRM AI FIRST` (modo
  Development, verificação de empresa vencida, limite de chamadas) derruba o CAPI
  de todos os clientes ao mesmo tempo. A BM Mileny Marketing está `not_verified` —
  verificar destrava quota de API.

**Especificação entregue ao dev (versão curta, só AFS):**
https://claude.ai/code/artifact/517567f0-fb46-4806-9465-13394594153b
