---
name: meta-ads-api-automation
description: >
  Regras de seguranca anti-bloqueio para automacao da Meta Ads API. Complementa a
  meta-ads-ratos com o que fazer ANTES de operacoes de escrita em volume e COMO
  reagir a throttling, erros de quota e sinais de bloqueio. Use quando: rodar
  operacoes em lote (muitas criacoes/edicoes seguidas), receber erro de rate limit
  (codigos 17, 32, 80004, 613), aparecer aviso de bloqueio/restricao de conta ou
  app, configurar app novo no Meta for Developers, ou o usuario perguntar sobre
  limites da API, throttling, quota, modo Live, verificacao de empresa.
---

# Meta Ads API — Automação Segura (anti-bloqueio)

A Meta não bloqueia automação; bloqueia **comportamento robótico abusivo**.
Estas regras complementam as regras de segurança da `meta-ads-ratos` (criar
PAUSED, confirmar antes de ativar/deletar, orçamento em centavos) — não as repetem.

## Rate limit: como operar

1. **Distribuir chamadas no tempo.** Nunca disparar rajadas de escrita; os scripts
   da meta-ads-ratos já incluem delay de 1s entre escritas — não contornar isso.
2. **Monitorar os headers de quota** em operações de volume:
   - `X-Ad-Account-Usage` — uso da quota da conta de anúncios
   - `X-Business-Use-Case-Usage` — uso por caso de negócio
   Acima de ~80%, pausar a operação e avisar a usuária.
3. **Backoff exponencial** em erro de throttling (códigos 17, 32, 80004, 613):
   esperar 60s → 120s → 240s. Após 3 falhas seguidas, PARAR, registrar o erro e
   escalar para a usuária. Nunca re-tentar imediatamente em loop.

## Tratamento de erro

- Analisar `error_user_msg` antes de re-tentar — os scripts mostram só o subcode;
  quando ambíguo, consultar a Graph API direto para ler a mensagem completa
  (ver aprendizados.md da meta-ads-ratos, regra de 2026-07-14).
- Erro de política/permissão NÃO se resolve com retry — reportar e parar.
- Validar payload localmente antes de enviar (CTA presente, IDs válidos,
  targeting bem-formado) — erro evitável repetido sinaliza automação ruim.

## Operação em lote (muitos objetos de uma vez)

- Criar em sequência com os delays padrão, nunca em paralelo.
- A cada ~10 escritas, fazer 1 leitura de verificação (read.py) — confirma estado
  e espaça as escritas.
- Builds grandes (funil completo, 4+ campanhas): avisar a usuária do tempo
  estimado e executar em blocos, validando cada bloco antes do próximo.

## Configuração do app (Meta for Developers)

- **App em modo Live** (não Development) — obrigatório para dark posts e criativos
  via API. Erro "app em modo de desenvolvimento" → mudar no painel do app.
- **Páginas vinculadas/autorizadas no app** que vai anunciar por elas.
- **Verificação de empresa (Business Verification)** em dia para permissões
  avançadas.
- **Permissões mínimas**: só `ads_management`/`ads_read` e o que for realmente
  usado. Menos escopo = menos superfície de bloqueio.

## Estratégia de adoção (contas/clientes novos)

1. **Fase 1 — leitura:** só relatórios e diagnósticos (read.py, insights.py).
2. **Fase 2 — escrita assistida:** criações PAUSED com revisão da usuária (padrão
   atual do ecossistema).
3. **Fase 3 — volume:** lotes maiores só depois de histórico limpo na conta.
Conta recém-acessada no BM: começar SEMPRE na fase 1 por alguns dias.

## Referências

- Rate limiting: https://developers.facebook.com/docs/marketing-api/overview/rate-limiting/
- Padrões de anúncio: https://www.facebook.com/business/learn/lessons/advertising-standards-best-practices
