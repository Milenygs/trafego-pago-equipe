# Cheirin Bão — Campanha LP FRANQUEADOS (fluxo direto com o franqueado)

**Conta:** `act_884652616778712` · **Criado:** 01/09/2026 · **Status:** blueprint, nada subido ainda
**Bloqueio atual:** o system user "Conversions API System User" (app *Relatórios campanhas*)
perdeu o acesso a esta conta — `(#200) Ad account owner has NOT grant ads_management`.
A conta não aparece mais em `read.py accounts`. Destravar no BM antes de executar.

---

## 1. O que muda nesta campanha

| | Campanhas atuais (05 / 09 / 10) | **Esta campanha** |
|---|---|---|
| Destino | Formulário nativo do Meta (ON_AD) | **LP `bl.cheirinbao.com.br/franqueados/`** |
| Conversão | `LEAD_GENERATION` (form) | **Conversão personalizada `LEAD FRANQUEADO CRIADA`** |
| Atendimento | Consultor do franqueador | **Franqueado fala direto com o lead** |
| Atribuição | `get_leads` × RD por telefone (form não passa UTM) | **UTM real — `utm_content` carrega o franqueado** |
| Geo | Cidades pinadas | **Estados inteiros (10 do Gestor A)** |
| Público | Engajamento/VV + LAL | **Igual — cópia da campanha antiga** |

**Decisão da Mileny (01/09):** manter a configuração de público da campanha
`[CAP] [LP] [CAMPANHA][FRANQUEADOS]`, que trouxe **7 vendas em 2026** (todas do criativo
VD02 Raissa, 5 delas via LP). **A geo é a única diferença**: estados inteiros no lugar
de cidades pinadas. Eu tinha sugerido um público novo (perfil investidor frio); a venda
manda mais que a taxa de qualificação de 7 dias — proposta descartada.

O ganho grande é a UTM: com LP, o `utm_content` chega no CRM de verdade — resolve
o problema de 25/08 (os 5 leads sem UTM, que obrigaram a separação na mão no ranking).

---

## 2. Estrutura

```
Campanha  13- [CONV] [LP] [FRANQUEADOS DIRETO] [ESTADOS]
          OUTCOME_LEADS · ABO · is_adset_budget_sharing_enabled=false
          bid_strategy LOWEST_COST_WITHOUT_CAP
  └─ Conjunto  01 - Perfil Investidor — 10 Estados
               OFFSITE_CONVERSIONS · R$200/dia · Instagram-only
     ├─ LP - Franqueado Alexandre
     ├─ LP - Franqueada Raissa
     ├─ LP - Franqueado Cleber
     ├─ LP - Franqueado Emerson
     ├─ LP - Franqueado Santoro
     └─ LP - Franqueada Julie
```

**Um conjunto só, seis criativos dentro** — padrão Espiral (conjunto por nível de
consciência, criativo é munição). Conjunto por franqueado repetiria o erro de 24/08:
os isolados 06/07 queimaram R$44 em 4h30 brigando no próprio leilão.

### promoted_object
```json
{"pixel_id": "1113125670113540", "custom_conversion_id": "<ID de LEAD FRANQUEADO CRIADA>"}
```
Ler o ID com `read.py` / Gerenciador de Eventos antes de criar — **`promoted_object` é
imutável depois de publicado** (subcode 3260011). Errar aqui = recriar o conjunto.

### Targeting — copiar da campanha antiga, trocar só a geo

**Procedimento (não remontar na mão):**

1. `read.py adsets-by-campaign --campaign <ID de [CAP][LP][CAMPANHA][FRANQUEADOS]>`
2. `read.py adset --id <conjunto>` → pegar o `targeting` inteiro
3. Trocar **só** `geo_locations` pelos 10 estados
4. Limpar os campos que a API não aceita mais na criação (a leitura ainda devolve):
   - `targeting_optimization` (removido, subcode 1870197)
   - `age_range` se `advantage_audience` for 0 (subcode 1487079)
   - normalizar `custom_audiences` para `[{"id": X}]`
5. **Não** incluir `excluded_geo_locations` no payload (ver risco 1)

**Geo nova — keys confirmadas via API (01/09):**

```json
"geo_locations": {
  "regions": [
    {"key": "460"}, {"key": "445"}, {"key": "459"}, {"key": "462"},
    {"key": "444"}, {"key": "442"}, {"key": "451"}, {"key": "455"},
    {"key": "461"}, {"key": "453"}
  ],
  "location_types": ["home", "recent"]
}
```
SP 460 · ES 445 · SC 459 · GO 462 · DF 444 · BA 442 · PB 451 · RN 455 · SE 461 · PI 453

**Preservar da campanha antiga:** faixa etária, `advantage_audience: 0`, Instagram-only.

### DOIS conjuntos, por nível de consciência (definido 01/09)

A inclusão do **Engajamento Pixel** separa a campanha em dois níveis. Não é preferência:
num só conjunto, o retargeting de site converte mais barato, leva quase toda a verba,
e o LAL nunca chega a rodar — a leitura dos dois se perde junto.

**`01 - Prospecção — 10 Estados` · R$140/dia**

| # | Público | ID | Prova |
|---|---|---|---|
| 1 | Base de leads **qualificados** do CRM | ver nota | pedido 01/09 |
| 2 | **LAL Franqueados** | `120253066981400602` | 2 avanços no pipeline |
| 3 | Público da **mentoria do Joel** | a confirmar | 3 das 7 vendas |

`excluded_custom_audiences`: franqueados atuais **+ o público do conjunto 02**
(senão os dois conjuntos brigam pela mesma pessoa no leilão).

**`02 - Engajamento Pixel` · R$60/dia**

Mesmo público do conjunto `04-Engajamento-Pixel` da campanha `33CampanhaFranqueados`
— pixel `1113125670113540` (visitantes de site/LP) + engajamento Instagram.
Prova: 1 das 7 vendas de 2026, e o único "Falar com o Franqueado" dessa origem no
pipeline (Dionat, MG). `excluded_custom_audiences`: franqueados atuais.

**Fora dos dois: os públicos de vídeo-view** (LIVE JOEL, IG_VIDEO_75%) — são os do
conjunto RAISSA, que fez 17 leads e **zero avanço** no pipeline de 01/09. Retargeting
de site ≠ vídeo-view; o primeiro entra, o segundo não.

**Vigiar a frequência do 02.** Público de retargeting de franquia é pequeno; R$60/dia
satura rápido. Se a frequência passar de ~3, cortar verba antes de mexer no criativo.

**⚠️ Por que a BASE LEADS RD sai das exclusões.** Na Meta, exclusão sempre vence inclusão
(aprendizado 12/08). Os leads qualificados do CRM estão *dentro* da BASE LEADS RD — mantê-la
excluída **anula o público 1 inteiro**, em silêncio, sem erro nenhum. E tirar a exclusão
não faz a base RD entrar: quem entra é só o que está em `custom_audiences`. A regra
"não pagar recadastro" continua respeitada, porque a base RD não-qualificada não é incluída.

**Nota sobre o público 1.** O que existe hoje é `SITE_LEADQUALIFICADO_90D_v2 (CAPI correto)`
(`120256487700540212`) — website/event-based, evento `lead_qualificado`, **retenção 90 dias**.
Com ciclo de venda longo (as vendas de 2026 vêm de março), 90 dias corta gente que ainda
fecha. **Melhor: exportar do CRM a lista completa de qualificados** (nome, e-mail, telefone)
e subir como custom audience de lista — não expira por janela.

**Sobre tamanho.** Públicos 1 e 3 são pequenos (centenas a poucos milhares); o LAL
Franqueados é ~1% do BR restrito a 10 estados. No mesmo conjunto, o LAL domina a entrega
e os dois de maior valor quase não gastam. Se depois de ~7 dias o breakdown mostrar isso,
o ajuste é somar os LALs de 1 e 3 (semelhantes) para escalar o perfil — não separar em
conjuntos, que fragmenta o aprendizado.

Localizar os IDs com `read.py custom-audiences --account act_884652616778712` e confirmar
com a Mileny antes de criar — existe um `LIVE JOEL` de engajamento que **não** é o da
mentoria.

**Único ajuste técnico obrigatório:** remover `ig_search` de `instagram_positions` — o
posicionamento quebra anúncio de **vídeo** com HARD_ERROR 2446429, e os 6 criativos aqui
são vídeo. Na campanha antiga isso não aparecia porque ela roda formulário nativo.

---

## 3. UTMs (o que o CRM lê)

Padrão por anúncio, `utm_content` **hardcoded** (nunca `{{ad.name}}` — espaço/acento
quebram o mapeamento no CRM):

```
utm_source=facebook&utm_medium=cpc&utm_campaign=13-LP-FRANQUEADOS-DIRETO&utm_content=<VD>&utm_term={{adset.id}}&utm_id={{ad.id}}
```

**Identificação pelo NOME, sem o código VD** (decisão da Mileny, 01/09) — o código VD
era numeração de arquivo de vídeo, não de pessoa, e já tinha colisão na conta
(`VD08 - FRANQUEADA RAISSA HOOK2` vs. VD08 = Julie). O nome do franqueado é estável:
troca o vídeo, a atribuição continua certa.

| Nome do anúncio | `utm_content` |
|---|---|
| LP - Franqueado Alexandre | `franqueado-alexandre` |
| LP - Franqueada Raissa | `franqueada-raissa` |
| LP - Franqueado Cleber | `franqueado-cleber` |
| LP - Franqueado Emerson | `franqueado-emerson` |
| LP - Franqueado Santoro | `franqueado-santoro` |
| LP - Franqueada Julie | `franqueada-julie` |

Padrão do valor: **minúscula, hífen, sem acento**. UTM com espaço vira `%20` e com
acento vira `%C3%A3` no log do CRM — o mapeamento quebra silenciosamente.

O prefixo `LP -` no nome do anúncio separa esta linha dos ads antigos (`VD02 - FRANQUEADO
RAISSA` etc.) em qualquer breakdown por nome de anúncio, já que os dois fluxos vão
conviver enquanto as campanhas 05/09 seguirem rodando.

`utm_campaign` **novo e exclusivo** (`13-LP-FRANQUEADOS-DIRETO`): os criativos VD02 e
VD07 feitos no painel já rodam `utm_campaign=08-%20FRANQUEADOS` nas campanhas 05 e 09.
Sem separar por campaign, o CRM soma linhas de campanhas diferentes — foi o que
obrigou a separação manual no ranking de 25/08.

**Checar antes de subir:** a LP precisa gravar as UTMs em campos hidden do formulário.
Se não gravar, o CRM não identifica o franqueado e a campanha inteira perde o sentido.

---

## 4. Verba

Teto da conta = **R$1.000/dia** (hoje ~R$1.120). Esta campanha entra **por realocação**:
- **R$100** do Aquecimento (R$150 → R$50)
- **R$100** do BOFU (R$200 → R$100)

**Não tocar** em Quente, 04-LAL nem RAISSA — são as camadas de fundo, e o RAISSA roda o
VD02, único criativo com venda registrada. (Eu tinha proposto pausar o RAISSA pela taxa
de qualificação de 13%; revertido quando as 7 vendas apareceram.)

Total conta permanece ~R$1.120/dia. Confirmar o corte com a Mileny antes de aplicar.

**Atenção ao alcance:** sair de 27 cidades pinadas para 10 estados inteiros multiplica o
público (o conjunto antigo estimava 118-139k MAU). Com R$200/dia a entrega espalha fino
por 10 estados. Se o CPM subir e o volume de conversão não acompanhar na primeira semana,
o ajuste é verba — não mexer no público, que é o que está sendo testado.

---

## 5. Riscos conhecidos

1. **`excluded_geo_locations` fantasma** — as campanhas legadas reaplicavam os 16 estados
   do Norte/Nordeste ~15s depois do anúncio entrar em veiculação. **6 dos 10 estados aqui
   (ES, BA, PB, RN, SE, PI) estão nessa lista.** Campanha nova do zero é o método que
   funcionou em 17/08. **Reler o targeting 30-60s depois de ativar** e conferir que
   `excluded_geo_locations` está vazio.
2. **Aprendizado da conversão nova** — `LEAD FRANQUEADO CRIADA` precisa de volume. Com
   R$200/dia e CPL de site provavelmente acima do form nativo, pode não fechar o
   aprendizado em 7 dias. Se travar, avaliar antes de mexer no criativo.
3. **Distribuição entre franqueados** — com 6 criativos em 1 conjunto, a Meta concentra
   em 1-2. Os outros franqueados vão receber pouco lead. Isso é performance funcionando,
   não erro; se o comercial exigir volume igual por franqueado, isso vira decisão
   comercial e o caminho é rodízio manual de criativo, não 6 conjuntos.
4. **Página de obrigado promete consultor** — `poscadastro.cheirinbao.com.br` diz *"um
   consultor entrará em contato"*. O anúncio promete falar com o franqueado. Alinhar o
   texto, senão o lead esfria entre o cadastro e o contato.
5. ~~VD08 ambíguo~~ — **resolvido em 01/09**: identificação passou a ser pelo nome do
   franqueado, sem código VD. Ver seção 3.

---

## 6. Fase 2 (depois de ~50-100 conversões)

Criar LAL 1% de quem completou `LEAD FRANQUEADO CRIADA` e abrir o **02 - LAL Lead
Franqueado** na mesma campanha. É o único público genuinamente novo que não canibaliza
o `04 - LAL —FRANQUEADOS` (hoje o melhor da conta, R$137-139/qualificado).

---

## 7. Copies por franqueado

Uma objeção por franqueado — assim os 6 não competem pelo mesmo argumento dentro do
conjunto. CTA `LEARN_MORE` em todos. Preencher `[CIDADE]` antes de subir.

**LP - Franqueado Alexandre** · *"não sou do ramo"* · título: **Fale com quem já abriu, não com vendedor**
> O Alexandre nunca tinha trabalhado com café. Hoje ele toca uma Cheirin Bão em [CIDADE].
>
> No vídeo ele conta o que ninguém fala antes de assinar: quanto tempo levou até a loja andar sozinha, o que ele faria diferente e o que muda de verdade na rotina de quem sai do emprego pra ter o próprio negócio.
>
> Se essa é a tua dúvida, fala com ele. Não com um consultor — com quem já passou por isso.
>
> 👉 Toque em Saiba mais e converse direto com o Alexandre.

**LP - Franqueada Raissa** · *"dá pra tocar sem largar tudo?"* · título: **A verdade sobre os primeiros meses**
> A Raissa vai ser sincera com você.
>
> Ela mostra a loja por dentro, o movimento de um dia comum, e responde o que quase todo mundo pergunta em off: dá pra tocar sem largar tudo? quanto tempo no balcão? e os primeiros meses, como são de verdade?
>
> Quem está pesquisando franquia merece ouvir isso de quem vive, não de quem vende.
>
> 👉 Toque em Saiba mais e fale direto com a Raissa.

**LP - Franqueado Cleber** · *"quanto realmente entra?"* · título: **A conta real de quem já opera**
> Todo mundo pergunta a mesma coisa: "mas quanto entra por mês?"
>
> O Cleber resolveu responder. No vídeo ele abre a operação dele — ticket, movimento, o que mais pesa no custo e a partir de quando o caixa começou a fazer sentido.
>
> Sem promessa. Sem número mágico. A conta de quem opera.
>
> 👉 Toque em Saiba mais e converse direto com o Cleber.

**LP - Franqueado Emerson** · *"fico sozinho depois de assinar?"* · título: **E depois que assina, você fica sozinho?**
> O que o Emerson mais ouve de quem quer abrir: "e depois que eu assinar, fico sozinho?"
>
> No vídeo ele conta como foi a abertura da loja dele, quem apareceu quando deu problema, e o que a rede resolve no dia a dia — do fornecedor ao treinamento da equipe.
>
> Franquia boa se prova no primeiro problema, não na apresentação.
>
> 👉 Toque em Saiba mais e fale direto com o Emerson.

**LP - Franqueado Santoro** · *"vale a pena vs. outras opções?"* · título: **Por que ele escolheu café e não outra coisa**
> O Santoro olhou várias oportunidades antes de escolher a Cheirin Bão.
>
> No vídeo ele explica o raciocínio: por que café, por que essa marca, o que ele avaliou de risco e o que hoje ele já sabe que pesou na decisão.
>
> Se você está comparando opções agora, essa conversa vale mais que qualquer apresentação comercial.
>
> 👉 Toque em Saiba mais e fale direto com o Santoro.

**LP - Franqueada Julie** · *"quanto tempo até destravar?"* · título: **Do "quero abrir" à loja rodando**
> A Julie ainda lembra da ansiedade das primeiras semanas.
>
> No vídeo ela conta o caminho do "quero abrir" até a loja rodando: o que consumiu mais tempo, o que ela subestimou, e a partir de quando parou de sentir que estava aprendendo tudo de uma vez.
>
> É o tipo de coisa que só quem passou consegue te contar.
>
> 👉 Toque em Saiba mais e fale direto com a Julie.
