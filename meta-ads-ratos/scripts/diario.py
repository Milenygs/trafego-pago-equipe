#!/usr/bin/env python3
"""
Meta Ads Ratos - Rotina Diaria
Varre todos os clientes do contas.yaml e gera um digest JSON com:
  - Saldo / limite de gasto / status da conta
  - Insights de ontem, 7d e 30d (gasto, leads, CPL, CTR, CPM, frequencia)
  - Campanhas de ontem (gasto > 0) com CPL por campanha
  - Ads reprovados ou com problema
  - Ad sets em aprendizado limitado
  - Alertas com gravidade e acao sugerida (NADA e aplicado automaticamente)

Uso:
  python diario.py varrer                      # todos os clientes
  python diario.py varrer --clientes maroma,kascao
  python diario.py varrer --sem-salvar         # nao grava relatorios/diario-*.json

Config opcional por cliente no contas.yaml:
  cpl_alvo: 45.00          # CPL alvo em reais (senao usa baseline 30d)
  gasto_min_alerta: 20.00  # so alerta CPL/leads se gastou mais que isso ontem
  diario: false            # pula o cliente na varredura
  acoes_lead: [...]        # action_types que contam como lead (sobrepoe o padrao;
                           # ex: ["lead", "offsite_conversion.fb_pixel_custom"])
"""

import argparse
import datetime as dt
import json
import os
import sys

# Console do Windows usa cp1252 e quebra com emoji em nome de campanha
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import init_api, print_error

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTAS_PATH = os.path.join(SKILL_DIR, "contas.yaml")
RELATORIOS_DIR = os.path.join(SKILL_DIR, "relatorios")

ACCOUNT_STATUS = {
    1: "ATIVA", 2: "DESATIVADA", 3: "PENDENCIA_PAGAMENTO",
    7: "EM_ANALISE_DE_RISCO", 8: "PAGAMENTO_PENDENTE", 9: "PERIODO_DE_CARENCIA",
    100: "FECHAMENTO_PENDENTE", 101: "FECHADA",
}

INSIGHT_FIELDS = [
    "spend", "impressions", "clicks", "ctr", "cpm", "frequency",
    "actions", "conversions", "cost_per_action_type", "reach",
]

LEAD_ACTION_TYPES = (
    "lead",
    "onsite_conversion.lead_grouped",
    "offsite_conversion.fb_pixel_lead",
    "leadgen_grouped",
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_clientes(filtro=None):
    import yaml
    with open(CONTAS_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    clientes = data.get("clientes") or {}
    slugs = list(clientes.keys())
    if filtro:
        pedidos = [s.strip() for s in filtro.split(",") if s.strip()]
        faltando = [s for s in pedidos if s not in clientes]
        if faltando:
            print_error(f"Clientes nao encontrados no contas.yaml: {', '.join(faltando)}")
            sys.exit(1)
        slugs = pedidos
    return [(slug, clientes[slug]) for slug in slugs]


def extrair_leads(actions, tipos=None, conversions=None):
    """Extrai total de leads da lista de actions sem contar duplicado.

    tipos: lista de action_types vinda do contas.yaml (chave acoes_lead). Quando
    informada, soma exatamente esses tipos — usado por conta que mede lead por
    conversao customizada do site (ex: AP Ponto), onde a acao padrao 'lead' so
    pega o formulario nativo e ignora a maior parte do volume.

    conversions: o campo `conversions` dos insights, que quebra o balde generico
    `offsite_conversion.fb_pixel_custom` por evento nomeado
    (`...fb_pixel_custom.NOME_DO_EVENTO`). Necessario quando a conta tem CAPI de
    CRM mandando varios eventos pro mesmo pixel — sem isso o balde generico soma
    o mesmo lead em cada etapa que ele avanca no CRM.
    """
    if not actions and not conversions:
        return 0
    mapa = {a.get("action_type"): float(a.get("value", 0)) for a in (actions or [])}
    for c in (conversions or []):
        mapa.setdefault(c.get("action_type"), float(c.get("value", 0)))
    if tipos:
        return int(sum(mapa.get(t, 0) for t in tipos))
    if "lead" in mapa:
        return int(mapa["lead"])
    total = sum(v for k, v in mapa.items() if k in LEAD_ACTION_TYPES)
    return int(total)


def resumo_periodo(row, tipos=None):
    """Converte uma linha de insights em resumo compacto."""
    if not row:
        return None
    spend = float(row.get("spend") or 0)
    leads = extrair_leads(row.get("actions"), tipos, row.get("conversions"))
    return {
        "gasto": round(spend, 2),
        "leads": leads,
        "cpl": round(spend / leads, 2) if leads else None,
        "impressoes": int(row.get("impressions") or 0),
        "cliques": int(row.get("clicks") or 0),
        "ctr": round(float(row.get("ctr") or 0), 2),
        "cpm": round(float(row.get("cpm") or 0), 2),
        "frequencia": round(float(row.get("frequency") or 0), 2),
        "periodo": f"{row.get('date_start')} a {row.get('date_stop')}",
    }


def centavos_para_reais(valor):
    try:
        return round(int(valor) / 100, 2)
    except (TypeError, ValueError):
        return None


def buscar_ultima_recarga(account):
    """Busca a data do funding_event_successful mais recente (recarga de saldo pre-pago).

    A API nao filtra get_activities por event_type via params (ignora o filtro
    silenciosamente), entao busca um lote maior (mais recente primeiro) e filtra
    no cliente.
    """
    try:
        desde = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=120)).strftime("%Y-%m-%d")
        activities = account.get_activities(
            fields=["event_type", "event_time"],
            params={"limit": 300, "since": desde},
        )
        for a in activities:
            d = a.export_all_data()
            if d.get("event_type") == "funding_event_successful":
                return d.get("event_time")
    except Exception:
        return None
    return None


def parse_saldo_prepago(display_string):
    """Extrai o saldo em reais de strings tipo 'Saldo disponível (R$93,66 BRL)'."""
    import re
    if not display_string or "aldo" not in display_string:
        return None
    m = re.search(r"R\$\s*([\d. ]*\d,\d{2})", display_string)
    if not m:
        return None
    try:
        return float(m.group(1).replace(".", "").replace(" ", "").replace(",", "."))
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Coleta por cliente
# ---------------------------------------------------------------------------

def coletar_cliente(slug, cfg, hoje):
    from facebook_business.adobjects.adaccount import AdAccount

    account_id = (cfg.get("conta_anuncio") or "").strip()
    if not account_id:
        return {"slug": slug, "nome": cfg.get("nome"), "erro": "conta_anuncio vazia no contas.yaml"}

    account = AdAccount(account_id)
    resultado = {"slug": slug, "nome": cfg.get("nome"), "conta": account_id, "alertas": []}
    acoes_lead = cfg.get("acoes_lead") or None

    ontem = hoje - dt.timedelta(days=1)
    d7_ini = hoje - dt.timedelta(days=7)
    d30_ini = hoje - dt.timedelta(days=30)
    fmt = "%Y-%m-%d"

    # --- 1. Detalhes da conta (saldo, limite, status) ---
    det = account.api_get(fields=[
        "name", "account_status", "currency", "amount_spent",
        "spend_cap", "balance", "funding_source_details",
    ])
    status_code = det.get("account_status")
    funding = det.get("funding_source_details") or {}
    saldo = {
        "status_conta": ACCOUNT_STATUS.get(status_code, str(status_code)),
        "gasto_acumulado": centavos_para_reais(det.get("amount_spent")),
        "limite_de_gasto": centavos_para_reais(det.get("spend_cap")),
        "valor_a_faturar": centavos_para_reais(det.get("balance")),
        "forma_pagamento": funding.get("display_string") or funding.get("type"),
        "saldo_prepago": parse_saldo_prepago(funding.get("display_string")),
    }
    if saldo["saldo_prepago"] is not None:
        ultima_recarga = buscar_ultima_recarga(account)
        if ultima_recarga:
            dt_recarga = dt.datetime.fromisoformat(ultima_recarga.replace("Z", "+00:00"))
            saldo["ultima_recarga"] = dt_recarga.strftime("%Y-%m-%d")
            saldo["dias_desde_recarga"] = (dt.datetime.now(dt.timezone.utc) - dt_recarga).days
    resultado["saldo"] = saldo

    # --- 2. Insights conta: ontem + 7d + 30d numa chamada so ---
    time_ranges = [
        {"since": ontem.strftime(fmt), "until": ontem.strftime(fmt)},
        {"since": d7_ini.strftime(fmt), "until": ontem.strftime(fmt)},
        {"since": d30_ini.strftime(fmt), "until": ontem.strftime(fmt)},
    ]
    rows = account.get_insights(fields=INSIGHT_FIELDS, params={
        "level": "account", "time_ranges": time_ranges,
    })
    periodos = {}
    for row in rows:
        d = row.export_all_data()
        ini, fim = d.get("date_start"), d.get("date_stop")
        if ini == fim == ontem.strftime(fmt):
            periodos["ontem"] = d
        elif ini == d7_ini.strftime(fmt):
            periodos["d7"] = d
        elif ini == d30_ini.strftime(fmt):
            periodos["d30"] = d
    resultado["ontem"] = resumo_periodo(periodos.get("ontem"), acoes_lead)
    resultado["d7"] = resumo_periodo(periodos.get("d7"), acoes_lead)
    resultado["d30"] = resumo_periodo(periodos.get("d30"), acoes_lead)

    # --- 3. Campanhas de ontem com gasto ---
    camp_rows = account.get_insights(
        fields=["campaign_id", "campaign_name", "objective"] + INSIGHT_FIELDS,
        params={
            "level": "campaign",
            "time_range": {"since": ontem.strftime(fmt), "until": ontem.strftime(fmt)},
            "filtering": [{"field": "spend", "operator": "GREATER_THAN", "value": 0}],
        })
    campanhas = []
    for row in camp_rows:
        d = row.export_all_data()
        r = resumo_periodo(d, acoes_lead)
        r.pop("periodo", None)
        r.pop("frequencia", None)
        r.update({
            "campanha_id": d.get("campaign_id"),
            "nome": d.get("campaign_name"),
            "objetivo": d.get("objective"),
        })
        campanhas.append(r)
    campanhas.sort(key=lambda c: c["gasto"], reverse=True)
    resultado["campanhas_ontem"] = campanhas

    # --- 4. Ads com problema (so os que podem entregar) ---
    #
    # ⚠️ A Meta NAO limpa o effective_status quando o anuncio e pausado: um ad
    # reprovado que voce pausou continua devolvendo WITH_ISSUES/DISAPPROVED para
    # sempre. Sem olhar o `status` proprio do anuncio, o alerta critico se repete
    # todo dia eternamente. Caso real (04/09/2026): o ad da Facilmart
    # 120244582183360388 estava PAUSED desde 22/05 e continuava sendo reportado,
    # e o da Boali 120250721955130156 desde 25/08. A Mileny cobrou, com razao.
    ads_problema = []
    campanhas_ativas = set()
    for c in account.get_campaigns(fields=["id"],
                                   params={"effective_status": ["ACTIVE"], "limit": 200}):
        campanhas_ativas.add(c.export_all_data().get("id"))
    ads = account.get_ads(
        fields=["name", "status", "effective_status", "adset_id", "campaign_id"],
        params={"effective_status": ["DISAPPROVED", "WITH_ISSUES"], "limit": 50})
    for ad in ads:
        d = ad.export_all_data()
        # o proprio anuncio ja foi pausado/arquivado: problema resolvido, nao alerta
        if d.get("status") in ("PAUSED", "ARCHIVED", "DELETED"):
            continue
        # sem campaign_id = nao da pra saber; mantem o alerta por seguranca
        if d.get("campaign_id") and d["campaign_id"] not in campanhas_ativas:
            continue
        ads_problema.append({
            "ad_id": d.get("id"), "nome": d.get("name"),
            "status": d.get("effective_status"), "campanha_id": d.get("campaign_id"),
        })
    resultado["ads_problema"] = ads_problema

    # --- 5. Ad sets em aprendizado limitado ---
    learning_limited = []
    adsets = account.get_ad_sets(
        fields=["name", "learning_stage_info", "daily_budget", "campaign_id"],
        params={"effective_status": ["ACTIVE"], "limit": 100})
    for adset in adsets:
        d = adset.export_all_data()
        info = d.get("learning_stage_info") or {}
        if info.get("status") == "FAIL":
            learning_limited.append({
                "adset_id": d.get("id"), "nome": d.get("name"),
                "orcamento_diario": centavos_para_reais(d.get("daily_budget")),
                "campanha_id": d.get("campaign_id"),
            })
    resultado["adsets_learning_limited"] = learning_limited

    # --- 6. Regras / alertas ---
    resultado["alertas"] = gerar_alertas(cfg, resultado)
    return resultado


# ---------------------------------------------------------------------------
# Regras
# ---------------------------------------------------------------------------

def gerar_alertas(cfg, r):
    alertas = []
    gasto_min = float(cfg.get("gasto_min_alerta") or 20)
    cpl_alvo = cfg.get("cpl_alvo")
    ontem, d7, d30, saldo = r.get("ontem"), r.get("d7"), r.get("d30"), r.get("saldo", {})

    def add(tipo, gravidade, msg, acao=None):
        alerta = {"tipo": tipo, "gravidade": gravidade, "msg": msg}
        if acao:
            alerta["acao_sugerida"] = acao
        alertas.append(alerta)

    # Conta com problema de status
    if saldo.get("status_conta") not in ("ATIVA", None):
        add("CONTA", "critico",
            f"Conta com status {saldo['status_conta']} - anuncios podem estar parados.",
            "Verificar pagamento/saldo no Gerenciador imediatamente.")

    # Saldo pre-pago acabando (comparado com o ritmo de gasto dos 7d)
    saldo_prepago = saldo.get("saldo_prepago")
    media_7d_saldo = (d7["gasto"] / 7) if d7 and d7.get("gasto") else 0
    if saldo_prepago is not None and media_7d_saldo >= 10:
        dias_restantes = saldo_prepago / media_7d_saldo
        if dias_restantes < 2:
            add("SALDO_BAIXO", "critico",
                f"Saldo pre-pago de R$ {saldo_prepago:.2f} cobre menos de {max(dias_restantes, 0):.1f} dia(s) no ritmo atual (R$ {media_7d_saldo:.2f}/dia).",
                "Avisar o cliente HOJE para recarregar, ou reduzir orcamentos ate a recarga.")
        elif dias_restantes < 4:
            add("SALDO_BAIXO", "atencao",
                f"Saldo pre-pago de R$ {saldo_prepago:.2f} cobre ~{dias_restantes:.1f} dias no ritmo atual (R$ {media_7d_saldo:.2f}/dia).",
                "Programar recarga com o cliente.")

    # Ciclo de recarga (conta prepaga) - controle de 15 em 15 dias
    dias_desde_recarga = saldo.get("dias_desde_recarga")
    if dias_desde_recarga is not None:
        ciclo = float(cfg.get("recarga_ciclo_dias") or 15)
        if dias_desde_recarga >= ciclo + 5:
            add("RECARGA_ATRASADA", "critico",
                f"Ultima recarga foi ha {dias_desde_recarga} dias (em {saldo.get('ultima_recarga')}) - ciclo alvo e de {ciclo:.0f} dias.",
                "Recarregar hoje - ja passou bem do ciclo combinado.")
        elif dias_desde_recarga >= ciclo:
            add("RECARGA_ATRASADA", "atencao",
                f"Ultima recarga foi ha {dias_desde_recarga} dias (em {saldo.get('ultima_recarga')}) - ciclo alvo e de {ciclo:.0f} dias.",
                "Programar recarga essa semana pra manter o ciclo de 15 dias.")

    # Boleto do ciclo — calendario combinado com o cliente (bloco `boleto:` no
    # contas.yaml). Roda junto com o saldo real: o calendario diz QUANDO enviar,
    # a API diz se o ciclo anterior chegou a ser pago.
    if cfg.get("boleto"):
        try:
            import boletos as calendario
            sit = calendario.situacao(cfg["boleto"], dt.date.today())
            if sit["gravidade"] in ("critico", "atencao"):
                add("BOLETO", sit["gravidade"], sit["msg"], sit.get("acao"))
            pendencia = calendario.checar_ciclo_anterior(sit, saldo.get("ultima_recarga"))
            if pendencia:
                add("BOLETO_NAO_PAGO", "critico", pendencia,
                    "Cobrar o pagamento do ciclo anterior antes que a conta pare.")
        except Exception as e:
            add("BOLETO", "info", f"Nao consegui calcular o calendario de boleto: {e}",
                "Conferir o bloco `boleto:` desta conta no contas.yaml.")

    # Ritmo vs orcamento combinado do ciclo (ex.: R$500 pra 15 dias = R$33,33/dia)
    orc_valor, orc_dias = cfg.get("orcamento_ciclo_valor"), cfg.get("orcamento_ciclo_dias")
    if orc_valor and orc_dias and d7 and d7.get("gasto"):
        teto_diario = float(orc_valor) / float(orc_dias)
        media_7d_orc = d7["gasto"] / 7
        razao_orc = media_7d_orc / teto_diario if teto_diario else 0
        if razao_orc >= 1.3:
            add("RITMO_ACIMA_DO_ORCAMENTO", "critico",
                f"Ritmo dos ultimos 7d (R$ {media_7d_orc:.2f}/dia) esta {razao_orc:.1f}x o teto do ciclo (R$ {teto_diario:.2f}/dia, combinado R$ {float(orc_valor):.2f}/{float(orc_dias):.0f}d).",
                "Reduzir orcamento diario das campanhas agora - nesse ritmo o saldo nao fecha o ciclo.")
        elif razao_orc >= 1.1:
            add("RITMO_ACIMA_DO_ORCAMENTO", "atencao",
                f"Ritmo dos ultimos 7d (R$ {media_7d_orc:.2f}/dia) esta {razao_orc:.1f}x o teto do ciclo (R$ {teto_diario:.2f}/dia, combinado R$ {float(orc_valor):.2f}/{float(orc_dias):.0f}d).",
                "Ajustar orcamento diario pra nao passar do combinado.")

    # Limite de gasto proximo
    cap, gasto_acum = saldo.get("limite_de_gasto"), saldo.get("gasto_acumulado")
    if cap and gasto_acum:
        uso = gasto_acum / cap
        if uso >= 0.95:
            add("LIMITE_GASTO", "critico",
                f"Limite de gasto da conta em {uso:.0%} (R$ {gasto_acum:.2f} de R$ {cap:.2f}).",
                "Aumentar ou zerar o spend_cap da conta, ou avisar o cliente para recarregar.")
        elif uso >= 0.80:
            add("LIMITE_GASTO", "atencao",
                f"Limite de gasto da conta em {uso:.0%} (R$ {gasto_acum:.2f} de R$ {cap:.2f}).",
                "Programar recarga/aumento de limite antes de estourar.")

    if not ontem or ontem["gasto"] == 0:
        media_7d = (d7["gasto"] / 7) if d7 and d7["gasto"] else 0
        if media_7d > 10:
            add("SEM_ENTREGA", "critico",
                f"Conta nao gastou nada ontem (media 7d era R$ {media_7d:.2f}/dia).",
                "Checar saldo, campanhas pausadas ou anuncios reprovados.")
        return alertas

    # Gasto anomalo vs media 7d
    media_7d = (d7["gasto"] / 7) if d7 and d7["gasto"] else 0
    if media_7d >= 10:
        razao = ontem["gasto"] / media_7d
        if razao >= 1.6:
            add("GASTO_ACELERADO", "atencao",
                f"Gasto de ontem (R$ {ontem['gasto']:.2f}) foi {razao:.1f}x a media dos 7d (R$ {media_7d:.2f}/dia).")
        elif razao <= 0.4:
            add("ENTREGA_CAIU", "atencao",
                f"Gasto de ontem (R$ {ontem['gasto']:.2f}) foi so {razao:.0%} da media dos 7d (R$ {media_7d:.2f}/dia).",
                "Checar aprendizado, saldo e status dos ad sets.")

    # CPL
    if ontem["gasto"] >= gasto_min:
        if ontem["leads"] and ontem["cpl"]:
            if cpl_alvo:
                alvo = float(cpl_alvo)
                if ontem["cpl"] > alvo * 1.5:
                    add("CPL_ALTO", "critico",
                        f"CPL de ontem R$ {ontem['cpl']:.2f} vs alvo R$ {alvo:.2f} (+{(ontem['cpl']/alvo-1):.0%}).",
                        "Revisar campanhas com pior CPL em campanhas_ontem e considerar pausar/realocar verba.")
                elif ontem["cpl"] > alvo:
                    add("CPL_ALTO", "atencao",
                        f"CPL de ontem R$ {ontem['cpl']:.2f} acima do alvo R$ {alvo:.2f}.")
            elif d30 and d30["cpl"]:
                if ontem["cpl"] > d30["cpl"] * 1.3:
                    add("CPL_ALTO", "atencao",
                        f"CPL de ontem R$ {ontem['cpl']:.2f} vs baseline 30d R$ {d30['cpl']:.2f} (+{(ontem['cpl']/d30['cpl']-1):.0%}).")
        else:
            # Gastou e nao gerou lead - so e critico se ha campanha de leads ativa
            tem_campanha_leads = any(
                (c.get("objetivo") or "").endswith("LEADS") for c in r.get("campanhas_ontem", []))
            if tem_campanha_leads:
                add("SEM_LEADS", "critico",
                    f"Gastou R$ {ontem['gasto']:.2f} ontem em campanha de leads e nao registrou nenhum lead.",
                    "Checar formulario/pixel e criativos; se persistir 2+ dias, pausar e revisar.")

    # Frequencia alta 7d
    if d7 and d7.get("frequencia") and d7["frequencia"] > 4:
        add("FREQUENCIA", "atencao",
            f"Frequencia 7d em {d7['frequencia']:.1f} - risco de fadiga de criativo.",
            "Trocar/adicionar criativos ou ampliar publico.")

    # Ads com problema
    for ad in r.get("ads_problema", []):
        add("AD_PROBLEMA", "critico",
            f"Ad '{ad['nome']}' com status {ad['status']}.",
            f"Revisar/editar ou pausar: python scripts/update.py ad --id {ad['ad_id']} --status PAUSED")

    # Learning limited
    if r.get("adsets_learning_limited"):
        nomes = ", ".join(a["nome"] for a in r["adsets_learning_limited"][:5])
        add("APRENDIZADO_LIMITADO", "info",
            f"{len(r['adsets_learning_limited'])} ad set(s) em aprendizado limitado: {nomes}.",
            "Considerar consolidar ad sets/orcamento para sair do aprendizado limitado.")

    return alertas


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def cmd_varrer(args):
    from facebook_business.exceptions import FacebookRequestError

    init_api()
    hoje = dt.date.today()
    clientes = load_clientes(args.clientes)

    resultados = []
    for slug, cfg in clientes:
        if cfg.get("diario") is False:
            resultados.append({"slug": slug, "nome": cfg.get("nome"), "pulado": True})
            continue
        print(f"Varrendo {slug}...", file=sys.stderr)
        try:
            resultados.append(coletar_cliente(slug, cfg, hoje))
        except FacebookRequestError as e:
            resultados.append({
                "slug": slug, "nome": cfg.get("nome"), "conta": cfg.get("conta_anuncio"),
                "erro": f"{e.api_error_code()}: {e.api_error_message()}",
            })
        except Exception as e:
            resultados.append({
                "slug": slug, "nome": cfg.get("nome"), "conta": cfg.get("conta_anuncio"),
                "erro": str(e),
            })

    ok = [r for r in resultados if not r.get("erro") and not r.get("pulado")]

    # Calendario de boletos: nao depende da API, entao continua valendo mesmo
    # quando a conta falha na varredura (rate limit, token, etc).
    try:
        import boletos as calendario
        bloco_boletos = calendario.montar_hoje(hoje)
        por_slug = {r.get("slug"): r for r in resultados}
        for item in bloco_boletos["itens"]:
            saldo_cli = (por_slug.get(item["slug"]) or {}).get("saldo") or {}
            pendencia = calendario.checar_ciclo_anterior(item, saldo_cli.get("ultima_recarga"), hoje)
            if pendencia:
                item["pendencia_ciclo_anterior"] = pendencia
            item["saldo_prepago"] = saldo_cli.get("saldo_prepago")
    except Exception as e:
        bloco_boletos = {"data": hoje.isoformat(), "itens": [], "erro": str(e)}

    # Pendencias agendadas (tarefas.yaml) — tambem independem da API.
    try:
        import tarefas as agenda
        bloco_tarefas = agenda.montar_hoje(hoje)
    except Exception as e:
        bloco_tarefas = {"data": hoje.isoformat(), "itens": [], "erro": str(e)}

    digest = {
        "data_execucao": dt.datetime.now().isoformat(timespec="seconds"),
        "referencia": "ontem = " + (hoje - dt.timedelta(days=1)).isoformat(),
        "resumo": {
            "clientes_varridos": len(ok),
            "clientes_com_erro": len([r for r in resultados if r.get("erro")]),
            "clientes_pulados": len([r for r in resultados if r.get("pulado")]),
            "gasto_total_ontem": round(sum((r.get("ontem") or {}).get("gasto", 0) for r in ok), 2),
            "leads_total_ontem": sum((r.get("ontem") or {}).get("leads", 0) for r in ok),
            "alertas_criticos": sum(1 for r in ok for a in r.get("alertas", []) if a["gravidade"] == "critico"),
            "alertas_atencao": sum(1 for r in ok for a in r.get("alertas", []) if a["gravidade"] == "atencao"),
            "boletos_acionaveis": sum(1 for i in bloco_boletos["itens"]
                                      if i["gravidade"] in ("critico", "atencao")),
            "tarefas_para_hoje": sum(1 for i in bloco_tarefas["itens"]
                                     if i["gravidade"] == "critico"),
        },
        "boletos": bloco_boletos,
        "tarefas": bloco_tarefas,
        "clientes": resultados,
    }

    if not args.sem_salvar:
        os.makedirs(RELATORIOS_DIR, exist_ok=True)
        caminho = os.path.join(RELATORIOS_DIR, f"diario-{hoje.isoformat()}.json")
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(digest, f, indent=2, ensure_ascii=False)
        digest["arquivo_salvo"] = caminho

    print(json.dumps(digest, indent=2, ensure_ascii=False, default=str))


def main():
    parser = argparse.ArgumentParser(description="Rotina diaria Meta Ads")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("varrer", help="Varre clientes e gera digest JSON")
    p.add_argument("--clientes", help="Slugs separados por virgula (padrao: todos)")
    p.add_argument("--sem-salvar", action="store_true", help="Nao gravar em relatorios/")
    p.set_defaults(func=cmd_varrer)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
