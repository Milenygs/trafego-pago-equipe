# Desygn Móveis — Fluxo ManyChat: Direct → RD Station → Vendedoras

> Blueprint completo pra montar no ManyChat. Tempo estimado: ~40 min.
> Plano da Desygn: RD Marketing Pro + RD CRM Pro. Bot: ManyChat Pro.
> ✅ Versão final — equipe de vendas preenchida (parte 4), atendimento
> Brasil todo (sem filtro de cidade). Pronto pra montar.

---

## Parte 0 — Setup (uma vez só)

1. Criar conta ManyChat com email da Desygn → plano Pro (~US$15/mês)
2. Adicionar Mileny como Team Member (Settings → Team Members)
3. No celular do cliente (Instagram @desygnmoveisjardim):
   Configurações → Mensagens e respostas de story → Ferramentas conectadas
   → **Permitir acesso às mensagens = ON**
4. ManyChat → Settings → Channels → Instagram → Connect (login FB de admin
   da página Desygn Móveis Jardim, ou login do IG)
5. ManyChat → Settings → Integrations → **RD Station → Connect** (autorizar
   com o login do RD da Desygn)

### Campos personalizados (Settings → Fields → User Fields)

| Campo | Tipo |
|---|---|
| `cidade` | Text |
| `ambiente` | Text |
| `momento` | Text |
| `whatsapp` | Phone |
| `origem_anuncio` | Text |

---

## Parte 1 — Gatilhos (Triggers)

Criar UM fluxo ("Qualificação Direct") com estes gatilhos apontando pra ele:

- **Instagram → New Conversation** (qualquer conversa nova)
- **Instagram → Story Reply** (respostas de story)
- Palavras-chave: `preço`, `valor`, `orçamento`, `informação`, `catálogo`
- ⚠️ NÃO ativar em "Comments" por enquanto (foco em DM)

Quando a pessoa vem de anúncio CTX, ela cai em New Conversation normalmente.
Se quiser rastrear o anúncio: nas campanhas, configurar o parâmetro `ref`
do anúncio e capturar em `origem_anuncio` (fase 2 — não bloqueia o resto).

---

## Parte 2 — Fluxo nó a nó

### Nó 1 — Boas-vindas
**Mensagem:**
> Oi! Que bom te ver por aqui 🌿
> Sou a assistente da Desygn Móveis. A gente cria ambientes externos de
> alto padrão — varandas, piscinas e áreas gourmet.
> Pra te atender direitinho, me diz teu nome?

**Entrada:** salvar em `Full Name` (campo padrão) → vai pro Nó 2

### Nó 2 — Cidade
**Mensagem:**
> Prazer, {{first_name}}! 😊
> Me conta: de qual cidade você fala?

**Entrada:** salvar em `cidade` → vai direto pro Nó 4

> ✅ A Desygn atende o Brasil todo — não há filtro de cidade. A pergunta
> fica só pra registro no RD (ajuda a vendedora e o remarketing regional).

### Nó 4 — Ambiente (qualificação principal)
**Mensagem:**
> Perfeito! E qual ambiente você quer transformar?

**Quick Replies (botões):**
- 🏊 Área da piscina → `ambiente` = "piscina"
- 🌿 Varanda/terraço → `ambiente` = "varanda"
- 🍖 Área gourmet → `ambiente` = "area gourmet"
- 🛋️ Outro/vários → `ambiente` = "outros"

→ Nó 5

### Nó 5 — Momento de compra
**Mensagem:**
> E em que momento você está?

**Quick Replies:**
- 🔨 Obra/reforma em andamento → `momento` = "obra em andamento"
- 📐 Projeto pronto, escolhendo móveis → `momento` = "escolhendo moveis"
- 💭 Pesquisando ideias → `momento` = "pesquisando"

→ Nó 6

### Nó 6 — WhatsApp (o dado que vira lead)
**Mensagem:**
> Última coisa, {{first_name}}: me passa teu WhatsApp com DDD?
> Assim uma das nossas consultoras te manda o catálogo e as condições
> desse mês direto por lá 📲

**Entrada:** tipo Phone → salvar em `whatsapp`
- Se inválido, repetir 1x: "Acho que faltou um número 🙈 me manda com DDD, ex: 31 99999-9999"

→ Nó 7

### Nó 7 — AÇÃO RD STATION ⭐ (o coração da integração)
**Action → RD Station → Send contact:**
- Email: (vazio — vai sem email mesmo; telefone identifica)
- Mapeamento: `Full Name` → Nome | `whatsapp` → Telefone/Celular |
  `cidade` → Cidade | `ambiente` e `momento` → campos personalizados no RD
  (criar antes no RD: Configurações → Campos personalizados)
- **Evento de conversão:** `lead-direct-desygn`
- Tag ManyChat: `enviado-rd` (pra não reenviar duplicado)

### Nó 8 — Encerramento + handoff
**Mensagem:**
> Fechou! 🎉 Já passei teus dados pra nossa equipe — a consultora te chama
> no WhatsApp ainda hoje (em horário comercial).
> Enquanto isso, dá uma olhada nos nossos projetos aqui no perfil 🌿

**Action:** marcar conversa como Open / atribuir a humano (Live Chat)
— quem responder DM depois disso é gente, não bot.

### Nó X — Fuga (rota de escape, ligada em todos os nós de pergunta)
Se a pessoa escrever algo fora do esperado 2x seguidas:
> Vou te conectar com uma consultora de verdade, só um instante! 💬

**Action:** abrir Live Chat + notificação interna.

---

## Parte 3 — No RD Station Marketing (automação)

Criar automação: **"Distribuição — Leads Direct Desygn"**

1. **Gatilho:** conversão identificador = `lead-direct-desygn`
2. **Ação:** Marcar como oportunidade → funil de vendas (isso cria o
   negócio no RD CRM pela integração Marketing↔CRM)
3. **Ação:** Distribuir Leads Entre os Responsáveis → selecionar as
   vendedoras (rodízio sequencial)
4. (Opcional) Notificar responsável por email a cada lead novo

## Parte 4 — No RD CRM

1. Confirmar que a equipe de vendas está cadastrada como usuária ativa no RD CRM
   (e selecionada na ação de distribuição da Parte 3, item 3):

   | Vendedor(a) | Email |
   |---|---|
   | Yasmin Moura (YM) | [e-mail removido] |
   | Maria Bárbara (MB) | vendas3@desygnmoveisjardim.com.br |
   | Jessica Barroso (JB) | [e-mail removido] |
   | Breno Castro (BC) | breno@desygnmoveisjardim.com.br |
2. Funil: definir em qual etapa o negócio nasce (ex: "Lead Direct")
3. Integração Marketing↔CRM ativa (Configurações → Integrações)

---

## Parte 5 — Teste de ponta a ponta (antes de avisar as vendedoras)

1. De um Instagram pessoal, mandar DM pro @desygnmoveisjardim
2. Percorrer o fluxo inteiro respondendo as perguntas
3. Conferir: contato apareceu no RD Marketing com o evento
   `lead-direct-desygn`? Negócio criado no CRM? Caiu pra uma vendedora?
4. Fazer 2-3 testes seguidos e confirmar que o rodízio alterna

---

## Parte 6 — Canal WhatsApp (Coexistence) 📲

> Mesmo ManyChat, mesma automação no RD — só muda o canal de entrada.
> Leads de WhatsApp (CTWA, link da bio, botão do site) caem no mesmo rodízio.

### 6.1 Conectar o número da loja (Coexistence — beta, disponível no Brasil)

**Pré-requisitos:**
- Número usa o app **WhatsApp Business** (não o WhatsApp comum) atualizado
- Número NÃO pode já estar conectado a outra API/plataforma
- Quem conecta precisa do celular da loja em mãos (escaneia QR code)

**Passos:**
1. ManyChat → Settings → **WhatsApp → Connect**
2. Escolher **"Connect your WhatsApp number with Coexistence"**
3. Seguir o fluxo da Meta (login FB admin + QR code no celular da loja:
   WhatsApp Business → Dispositivos conectados)
4. Pronto: o app do celular CONTINUA funcionando — vendedoras atendem
   como sempre, e o ManyChat vê/automatiza as mesmas conversas

### 6.2 Fluxo de qualificação WhatsApp (mais curto que o do Direct)

**Gatilho:** WhatsApp → New Conversation (primeira mensagem do contato)

⚠️ IMPORTANTE: o telefone JÁ VEM automático no WhatsApp — não pedir.
O bot só roda na PRIMEIRA interação; depois do handoff quem fala é humana
(configurar o fluxo pra não disparar em conversa já aberta).

**Nó W1 — Boas-vindas + nome**
> Oi! Aqui é da Desygn Móveis 🌿 Que bom que você chamou!
> Pra te atender direitinho: qual o seu nome?
→ salvar em Full Name

**Nó W2 — Cidade**
> Prazer, {{first_name}}! De qual cidade você fala?
→ salvar em `cidade`

**Nó W3 — Ambiente** (mesmos botões do Direct)
> E qual ambiente você quer transformar?
- 🏊 Área da piscina / 🌿 Varanda / 🍖 Área gourmet / 🛋️ Outro
→ salvar em `ambiente`

**Nó W4 — AÇÃO RD STATION**
- Send contact: Full Name → Nome | telefone (automático) → Celular |
  `cidade`, `ambiente` → campos
- **Evento de conversão: `lead-whats-desygn`** (diferente do Direct,
  pra medir cada canal separado)
- Tag: `enviado-rd`

**Nó W5 — Encerramento + handoff**
> Perfeito, {{first_name}}! Uma das nossas consultoras já vai te responder
> por aqui mesmo 😉 Enquanto isso, me conta: o que você tem em mente pro
> espaço? Pode mandar foto do ambiente que ajuda muito!
→ marcar conversa como Open (Live Chat) — vendedora assume NESTA conversa

### 6.3 No RD — ajustar a automação existente

Na automação "Distribuição — Leads Direct Desygn" (Parte 3):
- Adicionar o evento `lead-whats-desygn` como segundo gatilho
  (OU duplicar a automação — mesmo rodízio, mesmas 4 pessoas)
- Renomear para "Distribuição — Leads Direct + Whats Desygn"

### 6.4 Cuidados do Coexistence

- É beta: se uma mensagem do bot não sair, checar Settings → WhatsApp → status
- O bot NUNCA deve responder conversa que a vendedora já assumiu — por isso
  o gatilho é só New Conversation + handoff imediato após W4
- Respostas rápidas/etiquetas do app continuam funcionando normalmente
- Teste de ponta a ponta igual Parte 5: mandar msg de um número novo,
  conferir contato no RD com evento `lead-whats-desygn` + rodízio

---

## Fase 2 (depois de rodando)

- `ref` nos anúncios CTX → CPL real por criativo dentro do RD
- Evento CAPI "lead qualificado" de volta pro Meta (capi.py) →
  campanhas otimizam por lead com WhatsApp, não por conversa
- Regras de distribuição avançadas via Make (por cidade/horário), se precisar
- Campanhas CTWA (Click-to-WhatsApp) na Desygn: hoje as campanhas dela são
  Direct; com o canal Whats integrado, vale testar CTWA — o lead chega com
  telefone desde o primeiro segundo
