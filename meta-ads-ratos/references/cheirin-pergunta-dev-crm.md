# Cheirin Bão — CAPI parou de entregar em 01/09. Auditoria pedida no backend.

**Para:** dev do CRM AI FIRST
**Data:** 02/09/2026
**Pixel / dataset:** `1113125670113540`
**Conta de anúncios:** `act_884652616778712`

---

## Resumo executivo

O CAPI **funcionou normalmente de 12/08 a 31/08** e **parou completamente em 01/09**.
Desde então, toda mudança de etapa aparece com ❌ no painel do CRM e **nenhum evento chega
na Meta**.

O lado da Meta foi testado por fora e está saudável: ela aceita exatamente o mesmo tipo de
evento, com o mesmo formato, sem erro. **A quebra está no backend do CRM — no gatilho, na
montagem do payload ou na chamada HTTP.**

---

## O que já foi descartado (com evidência, não suposição)

| Hipótese | Como foi testada | Resultado |
|---|---|---|
| Meta rejeitando os eventos | Envio manual do mesmo evento, mesmo pixel, mesmo formato | `events_received: 1`, sem erro |
| Pixel errado | `is_crm: true`, é a fonte de CRM da conta | pixel correto |
| Permissão do system user | `Conversions API System User` (`1373588638320216`) | `ADVERTISE, UPLOAD, ANALYZE, EDIT` |
| Pixel não vinculado à conta | `shared_accounts` | `act_884652616778712` presente |
| Modo teste / código de teste | campo esvaziado e salvo | falha continua |
| Código de teste inválido causando rejeição | envio manual com código inválido de propósito | Meta aceitou mesmo assim |
| Mapa de etapas errado | revisado no painel | correto (ver abaixo) |
| Dois eventos do mesmo lead na mesma etapa | enviados manualmente com o mesmo `lead_id` | ambos processados |
| `lead_id` errado | leads seguem chegando com `leadgen_id` após 31/08 | identificador disponível |
| Mudança do lado da Meta | log de atividades da conta 28/08–02/09 | nenhuma alteração de pixel, ativo, permissão ou token |

O mapa de etapas está correto e **não deve ser alterado**:

| Etapa | Eventos |
|---|---|
| Em Contato | nenhum |
| Reunião | `lead_qualificado` + `reuniao_agendada` |
| Proposta | `lead_qualificado` + `proposta_enviada` |
| Ganho | `lead_qualificado` + `venda` |
| Perda | `lead_desqualificado` |

---

## Linha do tempo

| Data | Evento |
|---|---|
| 12/08 – 29/08 | `lead_qualificado` e `reuniao_agendada` chegando normalmente |
| 24/08 – 28/08 | pico de `lead_desqualificado` (42 na semana) |
| **31/08** | último dia com evento entregue (8 `lead_desqualificado`) |
| **01/09** | **para completamente.** Primeiras falhas registradas no painel |
| 02/09 | 6 tentativas, 6 falhas |

Últimas tentativas registradas no painel do CRM, todas com ❌ — usar estes horários para
localizar nos logs:

```
02/09/2026 05:07:33   Lead qualificado + Reunião agendada   (1a Reunião)
02/09/2026 05:10:35   Lead qualificado + Reunião agendada   (1a Reunião)
02/09/2026 05:24:02   Lead qualificado + Reunião agendada   (1a Reunião)
01/09/2026 17:58:10   Lead qualificado + Reunião agendada   (1a Reunião)
01/09/2026 14:14:11   Lead desqualificado                   (Perda)
```

Confirmado do lado da Meta: nenhum desses chegou. O `last_fired_time` do pixel para eventos
de servidor não se move desde 01/09, e a contagem de eventos do dia só reflete os envios
manuais de teste.

---

## O que precisa ser auditado

O caminho inteiro, do gatilho até a resposta:

**gatilho da mudança de etapa → montagem do payload → chamada HTTP → resposta da Meta → log/retentativa**

Perguntas objetivas:

1. O **gatilho** de envio está sendo executado depois de 31/08? (ou o ❌ é registrado antes
   de qualquer tentativa de rede?)
2. A chamada para `graph.facebook.com` está **realmente saindo**?
3. Qual o **status HTTP e o corpo da resposta** que a Meta devolve? Esse é o dado mais
   importante — ele resolve sozinho.
4. Há **timeout, erro de rede, exceção silenciosa ou falha de fila**?
5. A configuração de **pixel e token está sendo carregada corretamente em runtime**?
   (o token da Meta é de usuário do sistema e **não expira** — confirmado)
6. Existe **fila de eventos pendente ou travada** acumulando desde 01/09?
7. Houve **deploy, mudança de variável de ambiente, segredo, rotina ou regra** em
   **31/08 ou 01/09**?

**O ❌ do painel precisa expor a mensagem de erro.** Hoje ele mostra só o X, sem detalhe —
isso está impedindo o diagnóstico. Se possível, logar e exibir o retorno da chamada.

---

## Payload de referência — este formato foi testado e a Meta aceita

```json
POST https://graph.facebook.com/v21.0/1113125670113540/events

{
  "data": [{
    "event_name": "lead_qualificado",
    "event_time": 1756789200,
    "action_source": "system_generated",
    "user_data": { "lead_id": 4097309120401962 }
  }]
}
```

Resposta esperada: `{"events_received": 1, "messages": [], "fbtrace_id": "..."}`

Detalhes que importam:

- `lead_id` vai **sem hash**, como número inteiro — é ID nativo da Meta
- `event_time` é o momento da **mudança de etapa**, não o da criação do lead
- A Meta rejeita evento com mais de **7 dias**
- **Nenhum `test_event_code`** — com ele preenchido os eventos não contam nas campanhas

---

## Como saber que voltou

Mover um lead real para "1a Reunião" e conferir que a contagem de `lead_qualificado` e
`reuniao_agendada` do dia sobe no Gerenciador de Eventos. Enquanto ficar parada, não voltou —
resposta de sucesso na API não é garantia de nada se a chamada não estiver saindo.

---
*Verificado via API da Meta em 02/09/2026.*
