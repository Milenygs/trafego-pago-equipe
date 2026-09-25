# CAPI — Casa de Vidro Paraty

**Conta:** `act_792396727164193` · **Pixel:** `1994872427748737` ("Pixel de Casa de Vidro")
**Status em 19/08/2026:** pixel HEALTHY, automatic matching já ligado. Só dispara
`PageView` hoje — nenhum evento de lead ainda.

Existe um segundo pixel na conta, `1973780593218569` ("leads- finalização
cadastro"), que nunca disparou (sem `last_fired_time`) — não usar.

## Por que este cliente é diferente da AFS/Boali/Cheirin

Casa de Vidro **não tem CRM nem formulário nativo Meta** — o destino é conversa
(WhatsApp, migrando para Direct do IG). Não existe `leadgen_id`, então o match
não pode ser por ID exato. O identificador disponível é o **telefone**: é
literalmente o número que mandou mensagem no WhatsApp, então o match tende a
ser bom mesmo sendo hash (a Meta casa por telefone com boa precisão quando o
número é o mesmo usado na conta do Facebook/Instagram da pessoa).

Isso trava no **Nível 1** (lote manual) da arquitetura em `capi-crm.md` — não dá
para pular pro Nível 2/3 sem um CRM guardando o histórico de conversas.

## Fluxo

1. Mileny marca quais conversas do WhatsApp/Direct viraram lead qualificado
   (interessado real, datas e orçamento compatíveis) e, mais adiante,
   reserva confirmada.
2. Anota em `relatorios/casa-de-vidro-capi/leads_qualificados.csv`
   (`event_name,event_time,phone,email` — email só se tiver, não é obrigatório):
   ```csv
   event_name,event_time,phone,email
   lead_qualificado,2026-08-19T14:30,+5524999998888,
   venda,2026-08-20T10:00,+5524999998888,
   ```
3. Enviar (eu rodo isso quando ela pedir ou na rotina periódica):
   ```powershell
   python scripts/capi.py batch --pixel 1994872427748737 --csv relatorios/casa-de-vidro-capi/leads_qualificados.csv --crm manual
   ```
4. Limpar as linhas já enviadas do CSV depois de confirmar `events_received`
   (sem histórico de anti-duplicação automático aqui — é o cliente controlando
   manualmente, diferente da AFS que tem `capi_afs_enviados.json`).

**Janela de 7 dias** (aprendido na AFS): a Meta rejeita evento com `event_time`
mais antigo que isso. Não dá pra fazer backfill de conversas antigas — o envio
precisa ser pelo menos semanal a partir de agora.

**Nomes de evento padronizados** (mesmos de todos os clientes):
`lead_qualificado → reuniao_agendada → proposta_enviada → venda` (+ `lead_desqualificado`).
Para hospedagem provavelmente só `lead_qualificado` e `venda` (reserva
confirmada) fazem sentido no funil real — usar os outros só se existir uma
etapa intermediária de fato.

## Não confundir com o estado da conta

A conta está **UNSETTLED** (pendência de pagamento) e migrando de WhatsApp para
Direct — isso afeta entrega de anúncio, não o envio de CAPI. O pixel recebe
evento independente da conta de anúncio estar entregando ou não.

## Histórico de envios

- **19/08/2026:** primeiro lote real — 12 leads que iniciaram conversa no
  WhatsApp e mostraram interesse (contatos passados pela Mileny), todos
  `lead_qualificado`, `events_received: 12`. Evento aceito não é evento casado
  — conferir depois no Events Manager se apareceram atribuídos a campanha.
  CSV limpo após esse envio (linhas já mandadas não ficam acumulando).
- **21/08/2026:** lote de `lead_desqualificado` — 318 contatos únicos (lista
  que ela tinha em telefone, só número + nome ocasional), `events_received: 318`
  em 4 lotes. Sem data individual por contato — usei o timestamp do envio pra
  todos (não é a data real da conversa, só o que a janela de 7 dias da Meta
  aceita). Tirei 2 antes de mandar: número dela mesma ("Mileny 011") e um
  contato "Facebook Business" com DDI +44 (Reino Unido, claramente não é lead).
  Ficaram na lista alguns nomes que parecem parceiro/fornecedor, não hóspede
  (RF Serviços & Locações, Elysson Booking, Fred Booking, Sítio Three Little
  Berries e Domos, Sérgio Beraldo Casa De Vidro, Corretora Lu Dantas Canaã) —
  ela não confirmou se são leads de anúncio ou contato de parceiro; se ela
  disser que não são, precisa reenviar sem eles (Meta não tem endpoint de
  "desfazer" evento CAPI, mas o próximo lote de qualificado pode ajudar a
  reequilibrar). Confirmação em `dataset.py events` pode demorar a aparecer
  mesmo com `events_received` correto no envio — não é sinal de falha.
  Os 2 fechamentos (vendas) desde março que ela mencionou dia 21/08 **não
  apareceram no pixel** (`dataset.py events` só mostrava `PageView` +
  `lead_qualificado`, nenhum `venda`) — ela disse que "já foi enviado" por
  outro caminho, mas o registro do pixel não confirma isso. Vale conferir com
  ela de novo se esses 2 eventos de venda de fato chegaram no Meta.

## Quando faz sentido evoluir de nível

Se em algum momento ela passar a controlar os leads numa planilha estruturada
(Google Sheets, Notion) em vez de "lembrar quem qualificou", dá pra automatizar
com Zapier lendo a planilha e postando no endpoint CAPI — mesmo desenho do
Nível 2 em `capi-crm.md`. Não vale a pena antes disso pelo volume desta conta.
