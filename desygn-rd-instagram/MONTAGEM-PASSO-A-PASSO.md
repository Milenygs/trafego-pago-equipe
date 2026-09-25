# ManyChat do zero — montagem clique a clique (Desygn)

> Companheiro do FLUXO-MANYCHAT.md. Este aqui é o "onde clicar";
> o outro é o "o que escrever em cada nó".
> Nomes de menu podem variar um pouco (o ManyChat atualiza a interface),
> mas a estrutura é essa. Tempo total: ~1h na primeira vez.

---

## 0. O modelo mental (leia antes — 2 min)

O ManyChat inteiro se resume a 3 conceitos:

1. **Gatilho (Trigger)** — o que FAZ o fluxo começar
   (ex: "pessoa mandou DM nova", "pessoa respondeu story")
2. **Fluxo (Flow/Automation)** — a sequência de balões numa tela de desenho
   (canvas). Você arrasta caixinhas e liga uma na outra com setas.
3. **Campo (Field)** — a "memória" do bot. Cada resposta do lead
   (cidade, ambiente...) é guardada num campo pra depois mandar pro RD.

Os tipos de caixinha que você vai usar (só 4):
- **Send Message** — bot fala
- **Ask a Question / User Input** — bot pergunta E guarda a resposta num campo
- **Condition** — bifurcação (se X então A, senão B) — não usamos mais (Brasil todo)
- **Action** — bastidor: enviar pro RD Station, adicionar tag, abrir Live Chat

---

## 1. Criar a conta (10 min)

1. Acessar **manychat.com** → *Get Started Free*
2. Entrar **com o email da Desygn** (criar um login novo, não usar o teu pessoal
   — o ativo é do cliente)
3. Ele pergunta qual canal conectar → escolher **Instagram**
4. Fazer login com o **Facebook que administra a página** Desygn Móveis Jardim
   (o teu serve, você é admin via BM) → autorizar o @desygnmoveisjardim
5. ⚠️ Se der erro de permissão: falta o passo do celular do cliente —
   Instagram do celular → Configurações → Mensagens e respostas de story →
   Ferramentas conectadas → **Permitir acesso às mensagens = ON**
6. Fazer o upgrade pro **Pro** (Settings → Billing) — a integração RD e o
   canal WhatsApp são Pro

Depois, em **Settings → Team Members → Add**, adicionar teu email pessoal
como admin (assim você acessa sem o login do cliente).

## 2. Criar os campos (5 min)

**Settings → Fields → User Fields → + New User Field**, criar um por um:

| Nome | Type |
|---|---|
| cidade | Text |
| ambiente | Text |
| momento | Text |
| whatsapp | Phone |
| origem_anuncio | Text |

(Nome exatamente assim, minúsculo, sem acento — facilita o mapeamento depois.)

## 3. Conectar o RD Station (5 min)

1. **Settings → Integrations** → procurar **RD Station** → *Connect*
2. Abre o login do RD → entrar com a conta RD da Desygn → *Autorizar*
3. Voltou pro ManyChat com "Connected" = pronto

## 4. Montar o fluxo do Direct (30 min)

### 4.1 Criar o fluxo
**Automation → + New Automation** → escolher começar do zero (*Start from
scratch* / *Build your own*) → dá nome: **"Qualificação Direct"**

Abre o canvas (tela quadriculada). O primeiro bloco é o gatilho.

### 4.2 Gatilho
Clicar em **"+ Add Trigger"** (ou "When...") → **Instagram**:
- **"User sends any message"** (às vezes aparece como *New Conversation* ou
  fica em Automation → *Default Reply*) — esse pega quem vem dos anúncios CTX
- **+ Add Trigger** de novo → **"Story Reply"** (qualquer resposta de story)
- (Opcional) **Keywords**: `preço, valor, orçamento, catálogo`

### 4.3 Os balões (seguir as copies do FLUXO-MANYCHAT.md, Parte 2)

**Nó 1 — boas-vindas + nome:**
1. Clicar no **+** depois do gatilho → **Instagram → Send Message**
2. Colar o texto de boas-vindas
3. No MESMO bloco, adicionar **"Ask a question"** (ou arrastar um bloco
   *User Input*): pergunta do nome → em **Save response to**, escolher
   **Full Name** (campo padrão do sistema)

**Nó 2 — cidade:**
+ → *Ask a question* → texto da cidade → *Save response to* → **cidade**
(Pra escrever {{first_name}} no texto: digitar `{{` que abre a lista de campos.)

**Nó 4 — ambiente (botões):**
1. + → *Send Message* → texto "qual ambiente..."
2. No balão, clicar **+ Quick Reply** → criar os 4 botões
   (🏊 Área da piscina / 🌿 Varanda / 🍖 Área gourmet / 🛋️ Outro)
3. Em CADA botão: **Action → Set User Field** → `ambiente` = piscina
   (varanda / area gourmet / outros) → e ligar a seta do botão pro próximo nó
   — os 4 botões apontam pro MESMO próximo nó

**Nó 5 — momento:** igual ao nó 4, com os 3 botões salvando em `momento`

**Nó 6 — WhatsApp:**
*Ask a question* → texto do WhatsApp → em **Reply type**, escolher **Phone**
(valida o formato sozinho) → *Save response to* → `whatsapp`
→ em *Retry*, ativar 1 tentativa com a mensagem do "faltou o DDD 🙈"

**Nó 7 — mandar pro RD (o coração):**
1. + → **Action**
2. **+ Action → RD Station → Send contact/lead to RD Station**
   (o nome exato varia; é a única action do RD)
3. Mapear: Nome ← Full Name | Telefone ← whatsapp | cidade ← cidade |
   ambiente ← ambiente | momento ← momento
4. **Conversion identifier / evento**: `lead-direct-desygn`
5. No MESMO bloco Action: **+ Action → Add Tag** → criar tag `enviado-rd`

**Nó 8 — encerramento + handoff:**
1. + → *Send Message* → texto de encerramento
2. + → **Action → Mark conversation as Open** (abre no Live Chat pra
   equipe responder como humano)

### 4.4 Rota de fuga
Nos *Ask a question*, aba **"If no valid reply"** (ou *Skip button*): apontar
pra um balão "Vou te conectar com uma consultora 💬" + *Action → Mark as Open*.

### 4.5 Ativar
Botão **Set Live / Publish** no canto superior direito. Sem isso o fluxo
existe mas não roda (erro clássico de primeira vez 😉).

## 5. Testar (10 min)

1. De um Instagram que NÃO seja admin (teu pessoal serve), mandar DM
   pro @desygnmoveisjardim: "quero saber preço"
2. Responder o fluxo inteiro
3. Conferir: **Contacts** no ManyChat → o contato com os campos preenchidos
4. No RD Marketing → Contatos → procurar o lead → tem que estar lá com o
   evento `lead-direct-desygn`
5. Automação do RD (Parte 3 do blueprint) criada? → negócio no CRM → rodízio

## 6. WhatsApp (Parte 6 do blueprint) — só depois do Direct rodar

1. **Settings → WhatsApp → Connect** → **"Connect with Coexistence"**
2. Precisa do CELULAR DA LOJA: WhatsApp Business → Dispositivos conectados →
   escanear o QR
3. Duplicar o fluxo: abrir "Qualificação Direct" → menu ⋯ → **Duplicate** →
   renomear "Qualificação WhatsApp" → trocar o gatilho para
   **WhatsApp → New Conversation** → APAGAR o nó 6 (telefone já vem) →
   na Action do RD, trocar o evento para `lead-whats-desygn`
4. Testar de um número que nunca falou com a loja

## 7. Dia a dia das vendedoras

Elas não precisam entrar no ManyChat:
- **Instagram**: respondem pelo próprio Direct ou pelo Live Chat do ManyChat
  (aba **Chats**) — o bot já marcou a conversa como aberta
- **WhatsApp**: respondem pelo app do celular, como sempre (Coexistence)
- O lead qualificado chega pra elas é PELO RD CRM (rodízio) — é lá que
  trabalham a oportunidade

## Se travar

Manda print da tela pro Claude que eu destravo. Os 3 erros mais comuns:
1. Fluxo montado mas não publicado (Set Live)
2. "Permitir acesso às mensagens" desligado no Instagram do cliente
3. Campo mapeado errado na Action do RD (telefone em campo de texto)
