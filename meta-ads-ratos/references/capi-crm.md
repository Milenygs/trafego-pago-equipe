# CAPI / Conversion Leads com múltiplos CRMs

> **Implementação de referência funcionando: `capi-afs-franquia.md`.**
> Açaí Fruit Show foi a primeira conta com o circuito completo validado
> (pixel → leadgen_id no CRM → evento recebido). Copiar aquele passo a passo
> para os próximos clientes; este arquivo é a teoria.

Objetivo: devolver ao Meta a **qualidade** de cada lead (qualificado, reunião,
venda) para poder otimizar campanhas por *Conversion Leads* em vez de volume
de formulário. Isso resolve estruturalmente o problema de lead desqualificado.

## O conceito em 30 segundos

1. O lead entra pelo formulário nativo do Meta (ou landing page) e cai no CRM.
2. Quando o status muda no CRM (virou oportunidade, agendou reunião, comprou),
   um evento é enviado de volta ao **pixel/dataset do cliente** via CAPI.
3. Depois de ~2 semanas com volume de eventos, muda-se a otimização do ad set
   para "Conversion Leads" — o Meta passa a buscar gente parecida com quem
   **avança no funil**, não com quem só preenche.

**Cada cliente tem seu próprio pixel/dataset** — os eventos nunca se misturam.
O que padronizamos entre clientes são os NOMES dos eventos:

```
lead_qualificado → reuniao_agendada → proposta_enviada → venda
(+ lead_desqualificado, também é sinal útil)
```

## Requisitos oficiais (conferidos na documentação da Meta em 15/09/2026)

Fontes: `conversion-leads-integration` (visão geral), `payload-specification`,
`crm-integration/3-implementing-the-crm-integration`, `/4-verify-your-data`,
`/5-configure-your-sales-funnel`.

| Item | Regra oficial |
|---|---|
| Elegibilidade | ≥200 leads/mês de formulário nativo · etapa-alvo em até 28 dias · taxa da etapa 1–40% · envio ≥1x/dia |
| `event_name` | Livre. **Mandar TODAS as etapas conforme mudam, inclusive a inicial (lead bruto)** — 100 leads = 100 eventos de entrada |
| `event_time` | Unix em segundos da mudança de etapa · até 7 dias antes do envio · **depois** da hora de geração do lead, senão é descartado · nunca fazer backfill mexendo na data |
| `action_source` | `system_generated` |
| `custom_data` | **Obrigatório:** `event_source: "crm"` + `lead_event_source: "<nome do CRM>"` |
| `user_data.lead_id` | leadgen_id de 15–17 dígitos, sem hash · inválido = evento rejeitado · e-mail/telefone só com hash |
| Lote | Até 1.000 eventos · um erro descarta o lote inteiro |
| Escopo | "Do not use this specification for events not related to this optimization" — lead que não veio de formulário nativo não entra NESTE envio. Lead de landing page/orgânico vai num envio separado (e-mail e telefone com hash) para público, lookalike e campanha de site |
| Repetição | Sem `event_id`, a Meta não tem como saber que um evento é repetido. A proteção é na origem: cada par (lead, evento) sai uma vez só. Marcar `lead_qualificado` em várias etapas é seguro só com essa regra funcionando (já houve `lead_qualificado` repetido até 3x por lead) |
| Verificação | Evento aparece em até 1h com os dois `custom_data` · check verde após 1 dia · **Lead Coverage ≥ 60%** (Configurações → Ver relatórios) · aba Diagnóstico sem erro |
| Funil | A doc ainda descreve edição no Gerenciador de Eventos; em 15/09 o painel da Cheirin estava só leitura, com o evento escolhido no conjunto. Vale o painel |

**Nomes de etapa na carteira:** manter os 5 padrão + `lead_novo` (entrada de todo lead) +
etapas intermediárias com nome próprio (`atendeu`, `nao_atendeu`, `standby`). Nunca
rebatizar etapa intermediária como `lead_qualificado`: contamina o evento que a campanha usa.

**JavaScript:** leadgen_id de 17 dígitos passa de `Number.MAX_SAFE_INTEGER`. Guardar como
texto e nunca converter para `Number`.

## Como o Meta casa o evento com o lead

- **Formulário nativo Meta**: usar o `lead_id` (leadgen_id) — match perfeito.
  O RD Station guarda esse dado? Nem sempre. Se o CRM não guardar, usar email+telefone.
- **Landing page / outros**: enviar `email` e `phone` hasheados (o `capi.py` já
  normaliza e hasheia sozinho). Match bom, não perfeito.

## Arquitetura por nível de maturidade

### Nível 1 — Lote manual (dá pra começar HOJE, sem depender de ninguém)
1. Exportar do CRM (RD, Kommo, planilha do cliente...) um CSV com os leads que
   mudaram de status: colunas `event_name,event_time,lead_id,email,phone`.
2. Rodar: `python scripts/capi.py batch --pixel PIXEL_DO_CLIENTE --csv arquivo.csv --crm rd_station`
3. Fazer isso 1-2x por semana por cliente. Já alimenta o histórico do pixel.

### Nível 2 — Automático via middleware (recomendado)
- **RD Station Marketing**: tem webhook nativo de "marcado como oportunidade" e
  "venda". Webhook → Zapier/Make/n8n → HTTP POST no endpoint CAPI (mesmo payload
  do capi.py). Um cenário por cliente, mudando só pixel + token.
- **Kommo / Pipedrive / Agendor / planilha**: mesmo desenho — trigger de mudança
  de estágio → POST CAPI. Zapier já está conectado aqui no Claude e pode montar isso.
- A "espinha" é sempre igual: `evento do CRM → tradução para nome padronizado → CAPI do pixel certo`.
  Só o conector de entrada muda por CRM.

### Nível 3 — Integração nativa (quando o CRM permite)
- **HubSpot e Salesforce**: integração de 1 clique no Events Manager (desde abr/2026).
- **RD Station**: verificar no Events Manager > Parceiros; senão, fica no nível 2.

## Passo a passo para ativar num cliente

1. `python scripts/dataset.py list --account act_XXX` — confirmar o pixel do cliente.
2. `python scripts/dataset.py diagnostics --id PIXEL` — checar saúde antes.
3. No Events Manager do cliente: aba **Testar eventos** → copiar o `test_event_code`.
4. Enviar evento de teste: `capi.py send --pixel PIXEL --event-name lead_qualificado --email teste@teste.com --test-code CODIGO`
5. Ver o evento aparecer no Events Manager. Se apareceu, começar envio real (sem --test-code).
6. Alinhar com o comercial do cliente O QUE é "lead qualificado" (critério objetivo!).
7. Acumular 2+ semanas de eventos. Volume ideal: 250+ eventos qualificados/mês
   por conta. Com menos, otimizar para o evento mais frequente do funil (ex:
   lead_qualificado em vez de venda).
8. No ad set: mudar otimização para o evento do funil (Conversion Leads).
   **Mudou em set/2026:** a Meta tirou o mapeamento de etapas do Gerenciador de
   Eventos (lá o funil ficou só leitura). O evento agora se escolhe no conjunto:
   campanha de Leads com formulário → conjunto → meta "Maximizar o número de leads
   qualificados" → dataset → evento. Conjunto publicado não troca evento: duplicar
   e escolher ANTES de publicar. Depois, auditar o duplicado (o painel religa as
   melhorias de IA ao duplicar) e ler o `promoted_object` gravado.
   Esperar CPL bruto subir 10-20% e qualidade subir 30-50% — avisar o cliente
   ANTES para não estranhar o relatório.

## Ordem sugerida de rollout (menos fricção primeiro)

1. Clientes com comercial ativo e CRM organizado (franquias com equipe de expansão).
2. Clientes onde a própria Mileny controla a planilha de leads (nível 1 direto).
3. Clientes sem CRM: começar com formulário de maior intenção + planilha padrão.
