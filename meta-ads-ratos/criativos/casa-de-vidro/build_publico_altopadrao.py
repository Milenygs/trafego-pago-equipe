#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Casa de Vidro Paraty — 4o conjunto: ALTO PADRAO FULL-SERVICE (diaria R$10.000).

Publico novo pedido pela Mileny (21/08/2026):
  grupos de amigos 32+ comemorando datas marcantes (40, 50 anos)
  OU familias de alto padrao que viajam com mais gente (grupo grande /
  multigeracional), para a oferta de diaria de R$10.000 com TUDO INCLUSO
  (chef, staff, concierge, barqueiro).

Entra como 4o conjunto DENTRO da campanha de Direct que ja existe:
    Campanha 120248795623790510  [ENGAJ] [DIRECT] - Campanha Geral - P_personalizado 12/08
    +- 120248795624060510  [DATACOMEMORATIVA/AMIGOS] [DIRECT]      R$80/dia
    +- 120248795624670510  [COMPORTAMENTO/FERIASFAMILIA] [DIRECT]  R$80/dia
    +- (este script)       [ALTOPADRAO/FULLSERVICE] [DIRECT]       R$50/dia

Este script NAO inventa ID de interesse nem de cidade: resolve tudo em tempo de
execucao pela propria API (/search) e clona a estrutura (posicionamentos,
exclusao de seguidores, destino) lendo o conjunto AMIGOS que ja funciona.
Assim o conjunto novo nasce identico no que importa e diferente so no publico.

NAO cria criativo nem anuncio. As 2 frases de overlay desta oferta sao NOVAS e
estao aguardando aprovacao da cliente (regra do banco de frases da skill
casa-de-vidro-paraty). Anuncio so depois do "ok" dela.

Uso:
    python build_publico_altopadrao.py --dry    # resolve + estimativa, nao escreve nada
    python build_publico_altopadrao.py          # cria o conjunto PAUSED
    python build_publico_altopadrao.py --com-poa    # inclui Porto Alegre
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.abspath(os.path.join(AQUI, "..", ".."))
API = "https://graph.facebook.com/v21.0/"

# ---------------------------------------------------------------------------
# Conta e ativos (mesmos do build_direct.py)
# ---------------------------------------------------------------------------

CONTA = "act_792396727164193"
PAGINA = "949028168287242"

CAMPANHA = "120248795623790510"
ADSET_MODELO = "120248795624060510"       # AMIGOS — molde estrutural que ja roda

NOME = "[ALTOPADRAO/FULLSERVICE] [DIRECT]"
VERBA = 5000                              # centavos = R$50,00/dia
IDADE_MIN = 32
IDADE_MAX = 65

# Pracas premium ja validadas na conta + Curitiba.
# Porto Alegre fica de fora do lancamento (distancia e o publico daquele ticket
# gravita pra Floripa/Punta del Este); entra depois se Curitiba performar.
CIDADES = [
    ("Sao Paulo", "SP"),
    ("Rio de Janeiro", "RJ"),
    ("Brasilia", "DF"),
    ("Belo Horizonte", "MG"),
    ("Fortaleza", "CE"),
    ("Curitiba", "PR"),
]
CIDADES_EXTRA = [("Porto Alegre", "RS")]
RAIO_KM = 30      # captura a regiao metropolitana (Alphaville, Barra, Nova Lima...)

# Um unico bloco OR. Nao empilhar bloco E: na era Andromeda/GEM o publico amplo
# entrega melhor e quem filtra o perfil e o criativo + a oferta de R$10 mil.
# Se vier volume sujo demais, ai sim quebrar em 2 blocos (ver --estreito).
INTERESSES = [
    "Luxury goods",
    "Luxury vehicles",
    "Fine dining",
    "Wine",
    "Champagne",
    "Resort",
    "Luxury resorts",
    "Vacation rental",
    "Chef",
    "Cooking",
    "Party planning",
    "Birthday",
    "Anniversary",
    "Air travel",
    "Cruise ship",
]
COMPORTAMENTOS = [
    "Engaged Shoppers",
    "Frequent Travelers",
    "Frequent International Travelers",
    "Luxury goods",
]

# ---------------------------------------------------------------------------


def token():
    caminho = os.path.join(SKILL, ".env")
    for linha in open(caminho, encoding="utf-8"):
        if linha.strip().startswith("META_ADS_TOKEN"):
            return linha.split("=", 1)[1].strip().strip('"')
    sys.exit("META_ADS_TOKEN nao encontrado em " + caminho)


TOKEN = token()


def get(path, params):
    params = dict(params)
    params["access_token"] = TOKEN
    url = API + path + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url) as r:
        return json.load(r)


def post(path, params, oque):
    corpo = {k: (json.dumps(v) if isinstance(v, (dict, list)) else v) for k, v in params.items()}
    corpo["access_token"] = TOKEN
    dados = urllib.parse.urlencode(corpo).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(API + path, data=dados)) as r:
            saida = json.load(r)
            print("  OK  %-34s %s" % (oque, saida.get("id")))
            return saida.get("id")
    except urllib.error.HTTPError as e:
        erro = json.loads(e.read().decode("utf-8")).get("error", {})
        print("  ERRO %-33s" % oque)
        print("       msg :", erro.get("message"))
        print("       user:", erro.get("error_user_title"), "|", erro.get("error_user_msg"))
        print("       sub :", erro.get("error_subcode"))
        return None


def checar():
    """Mesma trava do build_direct.py: conta fora do status 1 quebra a criacao."""
    conta = get(CONTA, {"fields": "name,account_status,balance,amount_spent,disable_reason"})
    status = conta.get("account_status")
    saldo = int(conta.get("balance", 0)) / 100
    print("Conta    :", conta.get("name"))
    print("Status   :", status, "(1=ativa, 2=desativada, 3=UNSETTLED)")
    print("Em aberto: R$ %.2f" % saldo)
    if status != 1:
        print()
        print("BLOQUEADO. Com a conta fora do status 1 a Meta recusa criacao/criativo.")
        print("Quitar o valor em aberto no gerenciador de pagamentos e rodar de novo.")
        return False
    print("OK — pode criar.")
    return True


# ---------------------------------------------------------------------------
# Resolucao de geo e interesses pela propria API (nada hardcodado)
# ---------------------------------------------------------------------------


def achar_cidade(nome, uf):
    r = get("search", {"type": "adgeolocation", "location_types": '["city"]',
                       "q": nome, "locale": "pt_BR", "limit": 25})
    for c in r.get("data", []):
        if c.get("country_code") == "BR" and (c.get("region") or "").strip():
            if uf in (c.get("region_id_str") or "") or _uf_bate(c.get("region"), uf):
                return {"key": c["key"], "name": c["name"], "region": c["region"],
                        "country": "BR", "radius": RAIO_KM, "distance_unit": "kilometer"}
    for c in r.get("data", []):
        if c.get("country_code") == "BR":
            return {"key": c["key"], "name": c["name"], "region": c.get("region"),
                    "country": "BR", "radius": RAIO_KM, "distance_unit": "kilometer"}
    return None


_UF = {"SP": "sao paulo", "RJ": "rio de janeiro", "DF": "distrito federal",
       "MG": "minas gerais", "CE": "ceara", "PR": "parana", "RS": "rio grande do sul"}


def _uf_bate(region, uf):
    if not region:
        return False
    alvo = _UF.get(uf, "")
    r = region.lower().replace("á", "a").replace("â", "a").replace("ã", "a")
    r = r.replace("é", "e").replace("ê", "e").replace("í", "i").replace("ó", "o")
    return alvo and alvo in r


def achar_alvo(termo, tipo):
    """tipo = adinterest | adTargetingCategory(behaviors)."""
    if tipo == "interesse":
        r = get("search", {"type": "adinterest", "q": termo, "locale": "pt_BR", "limit": 10})
    else:
        r = get("search", {"type": "adTargetingCategory", "class": "behaviors",
                           "q": termo, "locale": "pt_BR", "limit": 10})
    dados = r.get("data", [])
    if not dados:
        return None
    melhor = dados[0]
    return {"id": str(melhor["id"]), "name": melhor["name"],
            "audience": melhor.get("audience_size_lower_bound")
            or melhor.get("audience_size") or 0}


def resolver(com_poa):
    print()
    print("Resolvendo geo...")
    geo = []
    for nome, uf in CIDADES + (CIDADES_EXTRA if com_poa else []):
        c = achar_cidade(nome, uf)
        if c:
            print("  OK  %-18s %s / %s  (raio %skm)" % (nome, c["name"], c["region"], RAIO_KM))
            geo.append(c)
        else:
            print("  !!  %-18s NAO ENCONTRADA — conferir na mao" % nome)

    print()
    print("Resolvendo interesses...")
    ints = []
    for t in INTERESSES:
        a = achar_alvo(t, "interesse")
        if a:
            print("  OK  %-32s -> %s (%s)" % (t, a["name"], a["id"]))
            ints.append({"id": a["id"], "name": a["name"]})
        else:
            print("  --  %-32s sem match" % t)

    print()
    print("Resolvendo comportamentos...")
    behs = []
    for t in COMPORTAMENTOS:
        a = achar_alvo(t, "comportamento")
        if a:
            print("  OK  %-32s -> %s (%s)" % (t, a["name"], a["id"]))
            behs.append({"id": a["id"], "name": a["name"]})
        else:
            print("  --  %-32s sem match" % t)

    return geo, ints, behs


# ---------------------------------------------------------------------------
# Targeting: estrutura clonada do conjunto AMIGOS, publico trocado
# ---------------------------------------------------------------------------


def montar_targeting(geo, ints, behs, estreito):
    modelo = get(ADSET_MODELO, {"fields": "name,targeting,destination_type,optimization_goal,"
                                          "billing_event,bid_strategy,promoted_object,daily_budget"})
    tm = modelo.get("targeting", {})
    print()
    print("Molde estrutural lido de:", modelo.get("name"))
    print("  posicionamentos:", tm.get("publisher_platforms"), tm.get("instagram_positions"))
    print("  exclusao       :", tm.get("excluded_custom_audiences"))

    # Whitelist: so os campos estruturais vem do molde. Copiar o dict inteiro
    # arrasta campos que a API recusa na criacao (ex: age_range com
    # advantage_audience=0, subcode 1487079 — aprendizado 19/07).
    alvo = {
        "geo_locations": {"cities": geo},
        "age_min": IDADE_MIN,
        "age_max": IDADE_MAX,
        # sem "genders" = todos
        "targeting_automation": {"advantage_audience": 0},
    }
    for campo in ("publisher_platforms", "instagram_positions", "device_platforms",
                  "excluded_custom_audiences", "brand_safety_content_filter_levels"):
        if tm.get(campo):
            alvo[campo] = tm[campo]

    if estreito:
        # Bloco E: contexto de celebracao/grupo E poder aquisitivo.
        celebra = [i for i in ints if any(
            k in i["name"].lower() for k in ("anivers", "birthday", "party", "festa", "casam"))]
        luxo = [i for i in ints if i not in celebra] + behs
        alvo["flexible_spec"] = [{"interests": celebra}, {"interests": luxo}]
    else:
        alvo["flexible_spec"] = [{"interests": ints, "behaviors": behs}]

    return alvo, modelo


def estimar(alvo):
    try:
        r = get(CONTA + "/delivery_estimate", {
            "targeting_spec": json.dumps(alvo),
            "optimization_goal": "CONVERSATIONS",
        })
        d = (r.get("data") or [{}])[0]
        lo = d.get("estimate_mau_lower_bound") or d.get("estimate_dau_lower_bound")
        hi = d.get("estimate_mau_upper_bound") or d.get("estimate_dau_upper_bound")
        if lo:
            print()
            print("Tamanho estimado do publico: %s a %s pessoas" % (f"{lo:,}", f"{hi:,}"))
            pressao = (VERBA / 100) / (lo / 1000.0)
            print("Pressao de verba: R$ %.2f por mil pessoas/dia (R$%d/dia)"
                  % (pressao, VERBA / 100))
    except urllib.error.HTTPError as e:
        print("  (estimativa indisponivel:", e.read().decode("utf-8")[:200], ")")


def criar(alvo, modelo):
    print()
    print("Criando conjunto", NOME)
    return post(CONTA + "/adsets", {
        "name": NOME,
        "campaign_id": CAMPANHA,
        "optimization_goal": "CONVERSATIONS",
        "billing_event": "IMPRESSIONS",
        "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
        "destination_type": "INSTAGRAM_DIRECT",
        "promoted_object": {"page_id": PAGINA},
        "daily_budget": VERBA,
        "targeting": alvo,
        "status": "PAUSED",
    }, "conjunto")


# ---------------------------------------------------------------------------

FRASES_PENDENTES = """
FRASES DE OVERLAY — NOVAS, AGUARDANDO APROVACAO DA CLIENTE
(banco de frases da skill: so frase aprovada entra sem checar)

  A) "Algumas datas nao se repetem. Esta merece uma casa inteira."
  B) "Voces so chegam. A casa cuida de todo o resto."

  Alternativas, mesmo status:
  C) "Nada para organizar. Tudo para viver."
  D) "Uma data. Uma casa. Ninguem mais."

Foto: DSCF5426 (casa completa + piscina + palmeiras) para A,
      DSCF5290 (casal na piscina + baia) para B.
Nenhum criativo/anuncio foi criado por este script — depende do ok dela.
"""


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="so resolve e estima, nao escreve")
    ap.add_argument("--com-poa", action="store_true", help="inclui Porto Alegre no geo")
    ap.add_argument("--estreito", action="store_true",
                    help="flexible_spec em 2 blocos (E) em vez de 1 bloco (OU)")
    args = ap.parse_args()

    if not checar():
        sys.exit(1)

    geo, ints, behs = resolver(args.com_poa)
    if not geo or not ints:
        sys.exit("Sem geo ou sem interesse resolvido — abortando.")

    alvo, modelo = montar_targeting(geo, ints, behs, args.estreito)
    print()
    print(json.dumps(alvo, ensure_ascii=False, indent=2))
    estimar(alvo)

    if args.dry:
        print()
        print("--dry: nada foi criado.")
        print(FRASES_PENDENTES)
        sys.exit(0)

    novo = criar(alvo, modelo)
    if novo:
        print()
        print("Conjunto criado PAUSED:", novo)
        print("Conferir:  read.py adset --id %s" % novo)
        print("NAO ativar sem ok da Mileny.")
        print(FRASES_PENDENTES)
