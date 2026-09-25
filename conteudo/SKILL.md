---
name: conteudo
description: Agente de criacao de conteudo e criativos para toda a carteira da Mileny (franquias, lojas de acai, B2B do grupo TFS, construtora, moveis e hospedagem). Vai do angulo ao anuncio pausado - banco de angulos por cliente, pauta por camada do Funil de Consciencia, matriz de ganchos, roteiro com gancho e corpo separados, historias de fundador e franqueado, carrossel e estatico, briefing de gravacao, as tres variantes de copy no formato do Meta e o checklist "Vale o scroll?" como portao final. Use quando o usuario mencionar: pauta, pauta de conteudo, o que gravar, roteiro, roteiro de video, gancho, hook, ganchos, banco de angulos, angulo novo, criar conteudo, criativo, copy de anuncio, carrossel, estatico, historia do fundador, depoimento, video do franqueado, briefing de gravacao, cortes, variantes de copy, V1 V2 V3, aprovar criativo, checklist vale o scroll, o que mandar pro editor. Tambem dispara com /conteudo.
---

# Conteúdo — do ângulo ao anúncio

Skill de **produção** para a carteira inteira. A `meta-ads-ratos` sobe, a `franquia`
estrutura o funil, o `prompt-analise-criativo.md` diagnostica peça pronta — esta resolve
o que vem antes: **o que gravar, por quê, para quem e em qual camada.**

Regra que sustenta o sistema: **conteúdo não começa em roteiro, começa em ângulo.**
Roteiro sem ângulo vira institucional genérico — exatamente o que o portão 1 reprova.

Fontes do método (17/09/2026): aulas em `Roteiro de Conteudo Clientes\aulas\`
(Funil de Consciência, franqueados como primeiro contato, criativos que vendem, guia de
conteúdo), materiais do Notion (Gancho e Corpo, Matéria-Prima, 30 roteiros) e o garimpo
das squads antigas de copy, storytelling e Hormozi. Resumos em
`Roteiro de Conteudo Clientes\estudo\`.

## Referências (ler a da etapa em curso)

| Arquivo em `references\` | Etapa |
|---|---|
| `linha-vermelha.md` | **sempre** — o que nunca entra e a regra de números por cliente |
| `angulos-e-ganchos.md` | 1 (ângulo) e 3 (ganchos) |
| `camadas-e-consciencia.md` | 2 (pauta) |
| `roteiros-e-historias.md` | 3 (roteiro, história, franqueado) |
| `formatos-e-producao.md` | 2 (formato), 3.5 (briefing de gravação), peça-mãe e cortes |
| `modelos-carrossel.md` | 3 quando o formato for carrossel ou estático |
| `copy-meta.md` | 4 (V1/V2/V3, provas, CTA por tipo de cliente) |
| `teste-e-metricas.md` | depois que roda |
| `materia-prima.html` | coleta com o comercial do cliente |

## Ordem obrigatória

Nenhuma etapa pula. Faltou insumo → pedir o insumo, nunca preencher com suposição.

```
0. cliente → 1. ÂNGULO → 2. PAUTA → 3. ROTEIRO → 3.5 BRIEFING → 4. VARIANTES → 5. PORTÃO → sobe pausada
```

---

## 0. Resolver o cliente

1. Ficha do cliente: `$HOME\OneDrive\Carteira\<grupo>\<cliente>\CLAUDE.md` (mapa em
   `Carteira\CLAUDE.md`). Ler: tipo de cliente, conta, regras, tom de voz, e o campo
   **`numeros_financeiros_em_anuncio`** (sem o campo = proibido; ver `linha-vermelha.md`).
2. `decisoes.md` da mesma pasta: o que está no ar e o que não mexer.
3. Banco de ângulos: `Carteira\<grupo>\<cliente>\angulos.md` (modelo em
   `conteudo\angulos\_MODELO.md`). Se não existir, a etapa 1 cria.
4. `meta-ads-ratos\contas.yaml`: `conta_anuncio`, `instagram_id`, `notas`.

Cliente fora da Carteira → inativo: avisar e perguntar, nunca adivinhar.
**Um cliente por vez**: ângulo, frase, prova e público de um nunca entram em outro.

## 1. ÂNGULO — a matéria-prima

Ângulo é **a objeção, a crença, a dor ou o desejo específico** que a peça ataca, com
frase literal de fonte real. Não é tema ("bastidor") nem formato ("depoimento").

| Isso não é ângulo | Isso é ângulo |
|---|---|
| "Falar da qualidade do produto" | "Ele acha que franquia de alimentação só dá certo em shopping" |
| "Depoimento de franqueado" | "Ele tem o capital mas não largou o emprego — quem opera?" |
| "Mostrar a fábrica" | "Ele já se queimou numa franquia que prometeu suporte e sumiu" |

Fontes em ordem de valor: comercial/CRM → conversas de WhatsApp e Direct (a 1ª mensagem
do lead) → comentários → franqueados e clientes atuais → dono da marca (diferenciais
escondidos) → Biblioteca de Anúncios → Reclame Aqui e fóruns. Meta: **20 frases reais**
antes de abrir ângulos novos.

Cada ângulo registra: elemento e tipo de falsa crença (veículo/interna/externa),
perfil (propósito/retorno), nível, camada, frase literal, fonte, **emoção-alvo**,
**cena concreta**, **crença única em uma frase**, **mecanismo (causa raiz → solução)**,
**teste ABT** e status. Formato completo e perguntas de coleta em `angulos-e-ganchos.md`.

**Saúde do banco:** mínimo de **2 ângulos `novo`** por cliente; se zerar, a próxima
ação é mandar a Matéria-Prima, não produzir. Banco sem atualização há mais de 30 dias =
fadiga criativa chegando. Camada 4 com munição para os três tipos de falsa crença.

## 2. PAUTA — qual camada está sem munição

Pauta não é calendário: é **preencher o buraco do funil**, lido na conta (e no
`decisoes.md`), não no feeling.

```bash
python read.py campaigns --account act_XXX --status ACTIVE
python insights.py ads --account act_XXX --date-preset last_14d   # frequência e volume por peça
```

Prioridade: (1) camada **sem peça ativa**; (2) camada com peça em **frequência > 2,5**;
(3) camada com **1 só criativo**; (4) categoria de conteúdo que o banco não tem.

Uma pauta = **um ângulo + uma camada + um formato + uma emoção**. Dentro de um conjunto,
os criativos **variam o tom emocional**, não só o gancho (Andromeda).

Camadas (Funil de Consciência, decidido em 17/09/2026 — detalhe e adaptação por tipo de
cliente em `camadas-e-consciencia.md`):

| Camada | O que a peça faz | CTA |
|---|---|---|
| 1 — Produto e experiência | encanta: loja, produto, momento bom. **Não vende franquia.** | nenhum ou suave |
| 2 — A marca é um bom negócio | franqueados, rotina, inaugurações, bastidor, como o modelo funciona | nenhum |
| 3 — Fundador e valores | história, propósito, valores — **filtro** | nenhum |
| 4 — Prova e convite | prova real + convite consultivo | verificação de região (franquia) / do tipo de cliente |

Espiral: quem não clicou volta para 1–3 com **ângulo mais fundo**, nunca a mesma peça.
Meta de 12–15 pontos de contato diferentes no público quente.

## 3. ROTEIRO — gancho e corpo

Gancho e corpo são **blocos separados**: o corpo precisa funcionar com qualquer gancho
da matriz. Entrega sempre **pronta para gravar** (nunca "fala de dor"):

```
PEÇA: ADxx [ANGULO] [FORMATO] descrição curta
Cliente · Ângulo A07 · Camada 4 · Nível 4 · Duração alvo 35–50s
Crença única: "…" · Estrutura · Emoção · O que esta peça testa

MATRIZ DE GANCHOS (o corpo é o mesmo)
  G1 [categoria] VISUAL: …  VERBAL: "…"  (Parada/Relevância/Entrega)
  G2 …
  G3 …

CORPO
[5-15s]  CONEXÃO: por que a situação dele é essa (vocabulário da fonte)
[15-30s] MECANISMO: causa raiz → solução
[30-40s] PROVA: logo depois do mecanismo, não financeira por padrão
[40-50s] CTA: uma instrução (ou nenhuma nas camadas 1–3)
```

**Ganchos:** escrever 10, em 4+ categorias, dar nota (Parada, Relevância, Entrega),
reprovar Relevância < Parada, ficar com os 3 melhores. Visual em 0–3s, verbal até 5s.
Categorias e processo em `angulos-e-ganchos.md` (Parte B).

**Estruturas:** base, educativa curta/longa, APAG, regra do modelo, auditoria de
acusação, história (Normal → Explosão → Novo Normal), manifesto do fundador
(Mim → Nós → Agora), franqueado-convite e franqueado-rotina. Técnicas de retenção
(loop aberto, contraste, virada por bloco, reincorporação, recompensa) em
`roteiros-e-historias.md`. Carrossel/estático: `modelos-carrossel.md`.

Regras que não se negociam:
- **Abre com tensão, nunca com credencial.** Autoridade entra depois do mecanismo.
- **Filtra, não atrai todos.** Em ticket alto, gancho aspiracional é defeito.
- **Mostra em vez de contar; emoção antes de análise.**
- **Números financeiros: regra por cliente** (`linha-vermelha.md`). Escassez sempre
  territorial e real. Nunca garantia.
- **Produção nativa:** vertical, celular, luz natural, fala direta, legenda legível.

## 3.5 BRIEFING — o que mandar para quem grava e edita

Toda peça aprovada no roteiro sai com o briefing de gravação (modelo, diretrizes de
filmagem e checklist do que o cliente manda em `formatos-e-producao.md`). Sem
**autorização de uso de imagem** de quem aparece, a peça não sobe.

Vídeo longo (entrevista, manifesto) = **peça-mãe**: sair com a lista de 5–10 cortes, cada
um com seu ângulo e camada.

## 4. VARIANTES — três de copy para a MESMA peça

| | Papel | CTA |
|---|---|---|
| **V1** | o ângulo puro, sem pedir nada | nenhum |
| **V2** | mesmo ângulo + convite leve (moldura de prêmio) | verificação suave |
| **V3** | ângulo + autoridade, prova e "para quem não é" | verificação direta |

Nos campos do Meta, separados e prontos para colar:
```
Texto principal: (essencial em ~125 caracteres; 1ª frase curta que puxa a 2ª)
Título: (até 40)
Descrição: (até 30)
```

CTA por tipo de cliente, provas permitidas e regras de escrita em `copy-meta.md`.
Franquia: `Verifique Sua Região Agora` · `Sua Cidade Ainda Está Disponível?` — convite a
checar disponibilidade, nunca a comprar.

## 5. PORTÃO — o checklist antes de subir

Rodar `meta-ads-ratos\references\checklist-vale-o-scroll.html` (**18 itens, 3 portões**,
atualizado em 17/09/2026). O portão 1 é eliminatório: qualquer "não" e a peça **volta
para a etapa 3**. Se a peça volta 3 vezes, o problema é o ângulo.

Saída do portão: o resumo de pendências por número + a **falha fatal** (o que mais
derruba a peça) + os **ganhos rápidos** (correções de menos de 5 minutos).

Passou → nomear e subir:
- Criativo: `ADxx [ANGULO] [FORMATO] descrição` (tags de ângulo para franquia:
  CAPTACAO · EMOCIONAL · PROVA · DOR · BASTIDOR · FUNDADOR · CONVITE). Variação de gancho:
  sufixo `G1`/`G2`/`G3`.
- Público: **sempre com `M` na frente**
- Sobe **PAUSED**, Instagram apenas, Advantage+ Audience OFF e ajustes automáticos do
  criativo em OPT_OUT — via `franquia` / `meta-ads-ratos`
- Registrar: `decisoes.md` e `historico\` do cliente na Carteira, `account_activities`
  (Diário do cliente, conector do Lovable) e o status do ângulo no banco

## Depois que roda

Sequência de teste (ganchos → corpo → combinação), métricas com fórmula (hook rate,
body rate) e leitura por parte do vídeo em `teste-e-metricas.md`. A regra da carteira se
sobrepõe: **em ticket alto, nunca concluir que o criativo é bom só por CPL baixo** —
cruzar com a classificação do comercial antes de escalar.

A peça testada volta para o banco de ângulos com o resultado **por elemento**. O próximo
ângulo nasce do que o anterior ensinou, não de um calendário.

## Saída padrão da skill

Quando a Mileny pede pauta ou roteiro, entregar nesta ordem, sem enfeite:

1. **Buraco identificado** — qual camada, com o dado da conta que sustenta
2. **Ângulo escolhido** — código, frase literal da fonte, crença única, por que agora
3. **Roteiro** — matriz de ganchos + corpo, pronto para gravar
4. **Briefing de gravação** — resumido, com o que falta do cliente
5. **V1/V2/V3** — nos campos do Meta
6. **Pendências do portão** — falha fatal e ganhos rápidos

Entrega para cliente (pauta do mês, briefing): página HTML no padrão visual do pitch
da Maroma.

## Material do cliente

`references\materia-prima.html` — vai para o comercial do cliente e traz as respostas
da coleta da etapa 1: as seis perguntas num formulário que monta o briefing. Artifact:
https://claude.ai/code/artifact/a54c0fb3-85f2-4cb7-9b67-883e94f38af0

Cadência: **mensal** por padrão, e **imediata** quando o banco de ângulos zerar — nunca
inventar ângulo. Com franqueados e o dono, usar as perguntas extras de
`angulos-e-ganchos.md` §A4.

## Segurança
- Nada sobe ativo. Ativação é manual, sempre da Mileny.
- Não misturar marcas.
- Sem dado real do comercial, dizer que falta — nunca inventar objeção.
- A skill antiga `criativos-e-copys-funil-espiral` (claude.ai) está **desalinhada**
  (títulos de faturamento, "últimas franquias", clientes encerrados). Não usar como fonte.
