# Boali — Praças abertas para expansão

Lista oficial enviada pela Boali em **13/08/2026**. São as cidades com espaço
para novo franqueado. Qualquer cidade fora desta lista está fechada — sempre
cruzar com ela antes de sugerir geolocalização.

> **Exceção confirmada pela Mileny em 17/09/2026: São Paulo capital (`269969`) está ABERTA**, apesar
> de não constar nesta lista. Não excluir a capital. A lista pode estar incompleta: na dúvida sobre
> uma cidade, perguntar à Mileny antes de concluir que está fechada.

A rede tem 160+ lojas em 25 estados, mas a lista de unidades não é pública
(o `/onde-tem` do site é JavaScript e não expõe JSON). Esta lista é a única
fonte confiável de onde dá para anunciar.

---

## Corte por porte (referência IBGE 2022)

> **Corte vigente: até 220 mil habitantes**, afrouxado de 200k com o ok da
> Mileny em 13/08/2026.

### Até 200 mil habitantes — 41 praças

| Cidade | UF | Pop. aprox | Situação na CP 06 |
|---|---|---|---|
| Eusébio | CE | 53k | conjunto CIDADES SETADAS 30KM |
| Araguaína | TO | 171k | CIDADES PEQUENAS |
| Ji-Paraná | RO | 131k | CIDADES PEQUENAS |
| Parintins | AM | 104k | CIDADES PEQUENAS |
| Itacoatiara | AM | 101k | CIDADES PEQUENAS |
| Três Lagoas | MS | 123k | CIDADES PEQUENAS |
| Sorriso | MT | 102k | CIDADES PEQUENAS |
| Formosa | GO | 119k | CIDADES PEQUENAS |
| Balsas | MA | 93k | CIDADES PEQUENAS |
| Ilhéus | BA | 155k | CIDADES PEQUENAS |
| Jaraguá do Sul | SC | 185k | CIDADES PEQUENAS |
| São Bento do Sul | SC | 87k | CIDADES PEQUENAS |
| Balneário Camboriú | SC | 139k | CIDADES PEQUENAS |
| Lages | SC | 157k | CIDADES PEQUENAS |
| Teresópolis | RJ | 166k | CIDADES PEQUENAS |
| Poços de Caldas | MG | 169k | CIDADES PEQUENAS |
| Botucatu | SP | 148k | CIDADES PEQUENAS |
| Votuporanga | SP | 97k | CIDADES PEQUENAS |
| Itu | SP | 176k | CIDADES PEQUENAS |
| Salto | SP | 121k | CIDADES PEQUENAS |
| Tatuí | SP | 123k | CIDADES PEQUENAS |
| Catanduva | SP | 122k | CIDADES PEQUENAS |
| Barretos | SP | 122k | CIDADES PEQUENAS |
| Jaú | SP | 152k | CIDADES PEQUENAS |
| Ourinhos | SP | 114k | CIDADES PEQUENAS |
| Avaré | SP | 92k | CIDADES PEQUENAS |
| Araçatuba | SP | 198k | CIDADES PEQUENAS |
| Mogi Mirim | SP | 93k | CIDADES PEQUENAS |
| Bragança Paulista | SP | 171k | CIDADES PEQUENAS |
| São Caetano do Sul | SP | 153k | **sem cobertura** — satélite |
| Nova Lima | MG | 108k | **sem cobertura** — satélite |
| Lauro de Freitas | BA | 167k | **sem cobertura** — satélite |
| Palhoça | SC | 162k | **sem cobertura** — satélite |
| Senador Canedo | GO | 127k | **sem cobertura** — satélite |
| Trindade | GO | 135k | **sem cobertura** — satélite |
| Valparaíso de Goiás | GO | 170k | **sem cobertura** — satélite |
| Nossa Senhora do Socorro | SE | 186k | **sem cobertura** — satélite |
| Valinhos | SP | 130k | **sem cobertura** — satélite |
| Paulínia | SP | 112k | **sem cobertura** — satélite |
| Sertãozinho | SP | 127k | **sem cobertura** — satélite |
| Santa Bárbara d'Oeste | SP | 187k | **sem cobertura** — satélite |

**Por que os satélites ficaram sem cobertura:** a Meta só aceita raio de
17 a 80 km em objeto `city`, e não oferece `medium_geo_area` (limite de
município) para essas cidades. A 17 km, São Caetano do Sul devolve 8,5
milhões de pessoas — a Grande São Paulo inteira. Nova Lima devolve BH
(1,8 mi) e Lauro de Freitas devolve Salvador (1,9 mi). Não dá para isolar
por geo; precisa de campanha de metrópole com copy nomeando a cidade.

### De 200 mil a 220 mil habitantes — 6 praças

Entraram no conjunto em 13/08/2026, todas medidas antes de subir:

| Cidade | UF | Pop. | Raio | Alcance | Razão |
|---|---|---|---|---|---|
| Luziânia | GO | 217k | 17km | 192 mil | 0,9x — isola bem |
| Passo Fundo | RS | 202k | 40km | 276 mil | 1,4x |
| Sobral | CE | 213k | 40km | 336 mil | 1,6x |
| Criciúma | SC | 215k | 30km | 394 mil | 1,8x |
| Águas Lindas de Goiás | GO | 218k | 17km | 384 mil | 1,8x |
| Rio Claro | SP | 208k | **17km** | — | a 25km dava 579 mil (2,8x): puxava Piracicaba e Limeira juntas |

**Razão** = alcance dividido pela população da cidade. Acima de ~2x é sinal
de que o raio está comprando a vizinha grande em vez da praça — foi o
critério usado pra apertar Rio Claro e pra cortar os 12 satélites acima.

### Acima de 200 mil habitantes — 104 praças

Norte/Nordeste: Belém, Ananindeua, Parauapebas, Porto Velho, Rio Branco,
Macapá, Boa Vista, São Luís, Imperatriz, Teresina, Fortaleza, Sobral,
Maracanaú, Juazeiro do Norte, Natal, Mossoró, Parnamirim, João Pessoa,
Campina Grande, Recife, Olinda, Maceió, Arapiraca, Aracaju, Salvador,
Camaçari, Feira de Santana

Centro-Oeste: Campo Grande, Dourados, Várzea Grande, Rondonópolis, Goiânia,
Anápolis, Aparecida de Goiânia, Rio Verde, Águas Lindas de Goiás, Luziânia,
Distrito Federal, Palmas

Sul: Curitiba, Londrina, Maringá, Cascavel, Foz do Iguaçu, Ponta Grossa,
São José dos Pinhais, Florianópolis, Blumenau, Criciúma, Itajaí, Chapecó,
São José, Porto Alegre, Caxias do Sul, Canoas, Gravataí, Passo Fundo, Pelotas

Sudeste: Vitória, Serra, Cariacica, Rio de Janeiro, Niterói, São Gonçalo,
Campos dos Goytacazes, Petrópolis, Volta Redonda, Nova Iguaçu,
Belo Horizonte, Juiz de Fora, Uberlândia, Divinópolis, Governador Valadares,
Uberaba, Contagem, Betim, Ribeirão das Neves

São Paulo: São Paulo (capital não listada), Campinas, Guarulhos, Santo André,
São Bernardo do Campo, Bauru, São José do Rio Preto, Jacareí,
Presidente Prudente, Praia Grande, Jundiaí, Piracicaba, Limeira, Diadema,
Mauá, Hortolândia, Sumaré, Taubaté, Franca, Araraquara, São Vicente,
Guarujá, Marília, Rio Claro, Santos, São José dos Campos, São Carlos,
Americana, Mogi das Cruzes, Cotia

---

## Praças que eu havia sugerido e estão FECHADAS

Inferidas antes da lista chegar, todas removidas da campanha:
Atibaia/SP · Birigui/SP · Varginha/MG · Araxá/MG · Patos de Minas/MG ·
Nova Friburgo/RJ · Resende/RJ · Brusque/SC · Bento Gonçalves/RS ·
Santa Cruz do Sul/RS · Erechim/RS · Toledo/PR · Apucarana/PR · Umuarama/PR ·
Pato Branco/PR · Lucas do Rio Verde/MT · Sinop/MT · Primavera do Leste/MT ·
Jataí/GO · Catalão/GO · Caldas Novas/GO · Luís Eduardo Magalhães/BA ·
Barreiras/BA
