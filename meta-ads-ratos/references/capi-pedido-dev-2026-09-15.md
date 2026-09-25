# Pedido ao dev do CRM AI FIRST — correção do CAPI para Conversion Leads (15/09/2026) · v3

Histórico do texto: v1 (Claude) → v2 (Mileny: prioridade, marcações múltiplas, tags, regra
da perda, perguntas, casos de teste) → **v3** (Mileny + Claude: AFS Franquia como terceiro
cliente, pergunta sobre a AFS sem nenhum evento em 28 dias, e hora do evento de entrada
vinda do CRM, não do `created_time` da Meta).

Base: documentação oficial da Meta (Conversion Leads — payload specification, CRM
integration passo 3 e verify your data passo 4), conferida em 15/09. Requisitos completos em
`capi-crm.md` §"Requisitos oficiais".

Substitui as especificações anteriores (artifact de 18/08 e documento de 02/09), que não
tinham `custom_data`, não mandavam a etapa inicial e mostravam `lead_id` como número sem
avisar do problema acima de 16 dígitos.

A regra da perda também protege o público de exclusão `CAPI_LEAD_DESQUALIFICADO_180D` da
Boali (sem ela, quem chegou à reunião e se perdeu seria excluído dos anúncios).

**Em aberto:** a Meta aceitar `lead_id` como texto não está confirmado na documentação (ela
descreve como número). O item 5 resolve.

---

```text
CAPI (CRM AI FIRST) — correção para Conversion Leads · v3

Clientes: Cheirin Bão (pixel 1113125670113540), Boali (pixel 4253291668254806,
nunca o 1247434766734345) e Açaí Fruit Show Franquia (pixel 1930108940975664).
A correção é a mesma nos três; muda só o pixel.
Base: documentação oficial da Meta — Conversion Leads.

PRIORIDADE PARA HOJE (nesta ordem)
  A) Formato do evento com custom_data em TODO envio (item 2). Na Boali os
     eventos chegam hoje sem nenhum parâmetro; só isso já muda o status na Meta.
  B) Evento de entrada disparando na criação do lead (item 1).
  C) Evento automático por etapa + marcações múltiplas + tags (item 1).
  D) Validação (item 5) e as três respostas do item 4.

1) TODA ETAPA ENVIA UM EVENTO COM O NOME DELA
   Hoje cada etapa só pode enviar um dos 5 eventos fixos, e a etapa sem marcação
   fica "não envia". A Meta exige que TODAS as etapas sejam enviadas, inclusive a de entrada.
   - Toda etapa envia automaticamente um evento com o próprio nome quando o lead entra nela.
   - Inclui a criação: lead que já nasce na primeira etapa dispara na hora
     (Boali: novo_cadastro · Cheirin: leads_novos · AFS: leads_novos).
   - Nome fixo por etapa: minúsculo, sem acento, sem espaço (nao_atendeu, primeiro_contato).
     Se a etapa for renomeada no CRM, o nome do evento não muda.
   - Os 5 botões continuam como marcação extra (lead_qualificado, reuniao_agendada,
     proposta_enviada, venda, lead_desqualificado).
   - UMA ETAPA PODE TER MAIS DE UMA MARCAÇÃO. Ex.: 1ª reunião = reuniao_agendada +
     lead_qualificado. Todas as marcações da etapa enviam, além do evento com o nome dela.
   - TAGS TAMBÉM ENVIAM. Tag marcada no painel (ex.: "lead com potencial" na Boali)
     envia seus eventos no momento em que é aplicada.
   - Cada par (lead, evento) é enviado uma vez só. Se o lead passar por várias etapas
     ou tags marcadas com lead_qualificado, só a primeira envia.
   - REGRA DA PERDA: lead_desqualificado só envia se o lead NUNCA passou por etapa ou tag
     marcada com lead_qualificado, reuniao_agendada, proposta_enviada ou venda.
     (Lead que chegou à reunião e depois se perdeu era lead bom; marcar como
     desqualificado ensina a Meta a fugir do perfil certo.)
     O evento com o nome da etapa de Perda continua sendo enviado normalmente.

2) FORMATO DO EVENTO
{
  "data": [{
    "event_name": "novo_cadastro",
    "event_time": 1789477200,
    "action_source": "system_generated",
    "user_data": {
      "lead_id": "1234567890123456",
      "em": ["<sha256 do e-mail>"],
      "ph": ["<sha256 do telefone>"]
    },
    "custom_data": {
      "event_source": "crm",
      "lead_event_source": "<mesmo nome que já chega na Cheirin>"
    }
  }]
}

   - action_source: sempre "system_generated".
   - custom_data: obrigatório em todo evento. lead_event_source com exatamente o mesmo
     nome que já chega hoje nos eventos da Cheirin, igual nos três clientes.
   - lead_id: o leadgen_id da Meta (15 a 17 dígitos), sem hash. Guardar como texto e nunca
     converter para Number em JavaScript. Enviar como texto e confirmar no teste (item 5)
     que a Meta aceita; se rejeitar, enviar como número montado direto a partir do texto.
   - em: SHA-256 do e-mail sem espaços e em minúsculo.
   - ph: SHA-256 do telefone só com dígitos: 55 + DDD + número.
   - event_time: unix em segundos com a hora e o minuto reais em que o lead entrou na etapa
     (não só a data). Precisa ser depois da criação do lead e no máximo 7 dias antes do
     envio. Converter o horário de Brasília para UTC corretamente.
   - No evento de entrada, usar a hora em que o lead chegou ao CRM, não o created_time
     da Meta. A Meta exige que o event_time seja DEPOIS da geração do lead; horário igual
     pode ser descartado.

3) ESCOPO E ENVIO
   - Todos os funis que recebem lead de formulário da Meta, nos três clientes.
   - Nesse envio, só lead de formulário da Meta (com leadgen_id). Landing page e orgânico
     ficam de fora (vão num envio separado, a combinar).
   - Enviar na hora. Se usar lote: máximo 1.000 eventos, e um erro descarta o lote inteiro.
   - Gravar o status e o corpo da resposta da Meta e mostrar a mensagem de erro no ❌ do painel.
   - Não reenviar eventos antigos em massa: a Meta descarta evento com mais de 7 dias e
     reenvio duplicado distorce o aprendizado.

4) TRÊS PERGUNTAS PARA RESPONDER
   - Boali: por que os eventos chegam na Meta sem nenhum parâmetro ("Não foi detectado
     nenhum parâmetro de evento"), enquanto os da Cheirin chegam com o nome do CRM?
     Qual configuração está diferente entre as duas contas?
   - Cheirin: a cobertura de leads zerou a partir de 03/09, o mesmo dia em que chegaram
     142 lead_qualificado de uma vez. Houve reenvio em massa ou mudança no envio nessa data?
   - AFS Franquia: NENHUM evento do CRM chegou no pixel 1930108940975664 nos últimos
     28 dias (nem lead_desqualificado). O usuário "acaifruit admr" tem permissão completa
     no pixel, e ele é o único pixel da empresa. A integração da AFS está ativa no First?
     Os envios estão sendo feitos e recusados? Mostrar o último status/resposta da Meta.

5) VALIDAÇÃO (nos três clientes, antes de dar por pronto)
   - Mandar um evento com test_event_code (aba Testar eventos) e conferir na resposta que
     a Meta aceitou o lead_id. Depois tirar o código: evento de teste não conta.
   - Em até 1 hora os eventos aparecem no Gerenciador de Eventos como CRM (não como "web"),
     com event_source e lead_event_source.
   - Testar os 3 casos com lead real: (a) lead criado já na etapa de entrada,
     (b) lead que pula direto para uma etapa com 2 marcações, (c) lead que chegou à
     reunião e depois foi para Perda (NÃO pode enviar lead_desqualificado).
   - Depois de 1 dia aparece o check verde.
   - Cobertura de leads (Configurações → Ver relatórios) em 60% ou mais.
   - Na Boali, o aviso "Conecte seu CRM" sai de pendente.
   - Mandar o JSON real enviado de um evento de entrada e de um lead_qualificado de cada cliente.
```
