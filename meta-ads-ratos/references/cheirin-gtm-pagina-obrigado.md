# Cheirin Bão — instalar o rastreamento na página de obrigado

> ## ⚠️ RESOLVIDO — NÃO ENVIAR ESTE PEDIDO (verificado na API em 03/09/2026)
>
> **A página de obrigado TEM rastreamento e a medição funciona.** O que existe lá é o
> pixel **`1113125670113540`** ("[Novo Pixel] Cheirin Bão - 23/01", o mesmo do CAPI) —
> não o `2525428314626049` que este documento presumia. Confirmado: 5 eventos em 7 dias
> com URL de `poscadastro.cheirinbao.com.br`.
>
> **A conversão que vale é `[M] LEAD/LP FRANQUEADOS` (`2554956741641990`)**, no pixel
> `1113125670113540`, regra `PageView` + URL contém
> `https://poscadastro.cheirinbao.com.br/franqueados/`. Último disparo 03/09 05:35.
> É por ela que a campanha `✅12- [SITE] [FRANQUEADOS]` (`120257321396340212`) otimiza,
> via `custom_conversion_id` no `promoted_object` dos dois conjuntos.
>
> **Resultado real 01–03/09:** R$ 484,68 · **4 conversões · R$ 121,17 cada**. Não é
> verba cega.
>
> **A conversão citada abaixo (`1080802127773569`) é um chamariz:** está ARQUIVADA,
> nunca disparou, e está amarrada ao pixel errado. Existem 7 conversões personalizadas
> nessa conta, 4 delas arquivadas e com nomes quase idênticos — sempre conferir
> `is_archived` e `last_fired_time` antes de concluir que algo não mede.
>
> **Lição:** o `/franqueados/` existe e a regra está certa. E a agregação `aggregation=url`
> do `/{pixel}/stats` devolve **só o domínio, sem o caminho** — a própria LP aparece como
> `https://bl.cheirinbao.com.br/` estando em `/franqueados/`. Esse dado NÃO serve para
> concluir nada sobre path.
>
> O texto abaixo fica só como registro do estado de 01/09.

---

**Para:** dev / responsável pelo site
**Site:** `poscadastro.cheirinbao.com.br` (WordPress 6.8.6 + Elementor)
**Página:** `https://poscadastro.cheirinbao.com.br/franqueados/`

## O problema (estado de 01/09/2026 — superado)

A landing page `bl.cheirinbao.com.br/franqueados/` já tem o Google Tag Manager instalado e
funcionando. A **página de obrigado não tem nada** — nem GTM, nem pixel, nem dataLayer.

Isso significa que hoje é impossível medir quantas pessoas concluíram o cadastro. A campanha
de anúncios consegue medir o envio do formulário, mas não a confirmação — que é o número que
realmente importa.

## O que precisa ser feito

Instalar **o mesmo container** que já roda na landing page: `GTM-KLFFMKML`.
É o mesmo código, sem alteração nenhuma. Ele é servido por um servidor próprio (Stape), então
**não use o snippet padrão do site do Google** — use exatamente o que está abaixo, copiado da
landing page que já funciona.

### 1. No `<head>`, o mais no topo possível

```html
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],j=d.createElement(s);j.async=!0;j.src="https://gdcmzjwz.sa.stape.io/7fogdcmzjwz.js?"+i;f.parentNode.insertBefore(j,f)})(window,document,'script','dataLayer','75k0ytnu=ExNXPTkuSSw2MSw3Ji4oQQxKWFRc')</script>
```

### 2. Logo depois da abertura do `<body>`

```html
<noscript><iframe src="https://gdcmzjwz.sa.stape.io/ns.html?id=GTM-KLFFMKML" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
```

**Onde colocar no WordPress:** se o tema for filho, em `header.php`. Se não, o caminho seguro é
um plugin de inserção de código no cabeçalho (Insert Headers and Footers, WPCode ou similar) —
o mesmo método que provavelmente foi usado na landing page.

### 3. Conferir dentro do GTM

O container `GTM-KLFFMKML` precisa ter a tag do **Pixel da Meta `2525428314626049`** disparando
`PageView` com gatilho **"Todas as páginas"**. Se o gatilho hoje estiver restrito ao domínio
`bl.cheirinbao.com.br`, é preciso incluir `poscadastro.cheirinbao.com.br` também — senão o
container carrega mas a tag não dispara.

⚠️ **Atenção ao pixel certo.** A conta tem mais de um. O que mede as landing pages é o
`2525428314626049` ("Novo CB - 07/26"). O `1113125670113540` é do site institucional
(`cheirinbao.com.br`) — **não use esse**.

## Como saber que funcionou

Depois de publicar, é só acessar a página de obrigado uma vez. Em poucos minutos o domínio
`poscadastro.cheirinbao.com.br` passa a aparecer nos eventos do pixel. Dá para conferir pelo
Gerenciador de Eventos da Meta, ou pela Mileny, que verifica direto pela API.

## Depois que estiver no ar — passo do lado dos anúncios

Já existe a conversão personalizada criada e esperando:
**"CB | LEAD FRANQUEADO - POS-CADASTRO"** (`1080802127773569`), regra = PageView com URL
contendo `poscadastro.cheirinbao.com.br/franqueados`.

Ela só começa a contar quando o GTM subir. E, do lado da campanha, migrar a otimização para
ela exige **criar um conjunto novo** — a Meta não deixa trocar o evento de conversão de um
conjunto já publicado.

---
*Gerado em 01/09/2026. Contexto completo no `historico.md` da skill meta-ads-ratos.*
