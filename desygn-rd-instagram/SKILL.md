---
name: desygn-rd-instagram
description: >
  Skill de cliente: integracao Direct (Instagram) -> ManyChat -> RD Station ->
  vendedoras da Desygn Moveis Jardim. Contem o blueprint completo do bot de
  qualificacao no ManyChat (fluxo no a no) e o guia de montagem clique a clique.
  Use quando o usuario mencionar: Desygn + RD Station, ManyChat, bot do Direct,
  automacao do Instagram da Desygn, qualificacao de leads da Desygn, integracao
  RD, fluxo do Direct, rodizio de vendedoras, ou pedir para montar/ajustar/
  diagnosticar o fluxo de atendimento da Desygn.
---

# Desygn — Integração Direct → RD Station (ManyChat)

Automação de qualificação da Desygn Móveis Jardim: lead chega pelo Direct
(orgânico ou anúncio CTX), o bot ManyChat qualifica (nome, cidade, ambiente,
momento, WhatsApp), envia pro RD Station e distribui para a equipe de vendas.

## Contexto do cliente

- Cliente `desygn-moveis` no contas.yaml da meta-ads-ratos (act_982771069275570,
  @desygnmoveisjardim). Campanhas SÓ de Direct/WhatsApp — métrica = conversa
  iniciada (`metrica_lead: conversas`).
- Stack: ManyChat Pro + RD Marketing Pro + RD CRM Pro.
- Atendimento Brasil todo (sem filtro de cidade). Distribuição em rodízio para
  a equipe de vendas (nomes na Parte 4 do blueprint).
- **Estado:** blueprint final pronto para montar (~40 min de montagem).
- **Fase 2 (pendente):** capturar `ref` do anúncio em `origem_anuncio` e
  enviar eventos CAPI/Conversion Leads (usar `capi.py` da meta-ads-ratos +
  `references/capi-crm.md` de lá).

## Recursos da skill

| Arquivo | O que é | Quando ler |
|---|---|---|
| `FLUXO-MANYCHAT.md` | Blueprint nó a nó: gatilhos, mensagens de cada nó, campos, integração RD, rodízio | Para saber O QUE configurar/escrever em cada nó |
| `MONTAGEM-PASSO-A-PASSO.md` | Guia clique a clique da interface do ManyChat | Para guiar a Mileny na montagem ou diagnosticar onde algo foi configurado errado |

## Como usar

1. **Montagem do zero:** seguir `MONTAGEM-PASSO-A-PASSO.md` (onde clicar) com o
   `FLUXO-MANYCHAT.md` aberto (o que escrever). Ordem: setup → campos →
   conexão RD → gatilhos → fluxo → rodízio → testes.
2. **Ajuste pontual** (mudar mensagem, campo, vendedora do rodízio): localizar o
   nó no `FLUXO-MANYCHAT.md`, propor a mudança e atualizar o documento junto —
   o blueprint é a fonte de verdade do que está montado.
3. **Diagnóstico** ("lead não chegou no RD", "bot não respondeu"): checar na
   ordem — permissão de mensagens no celular do cliente (ON) → conexão do canal
   Instagram no ManyChat → integração RD autorizada → gatilhos ativos → campos
   mapeados. O passo a passo tem a localização de cada um.
4. **Campos do bot** (exatamente estes nomes, minúsculos, sem acento):
   `cidade`, `ambiente`, `momento`, `whatsapp`, `origem_anuncio`.

## Regras

- Login do ManyChat é DO CLIENTE (email Desygn); Mileny entra como Team Member.
- Não ativar gatilho de Comments por enquanto — foco em DM.
- Mudanças no fluxo em produção: propor → ok da Mileny → aplicar → atualizar o
  blueprint. Nunca deixar o documento divergir do que está montado.
