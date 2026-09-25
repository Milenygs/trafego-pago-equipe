#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build da INAUGURACAO da loja Acai Fruit Show Tomba (Feira de Santana/BA).
Inauguracao: 14/08/2026 a partir das 12h. Verba total: R$500 (10 a 14/08).

Duas campanhas, tudo criado PAUSED:
  A) [INAUG] Reconhecimento | Tomba   — OUTCOME_AWARENESS / REACH      — R$300
  B) [INAUG] Trafego Perfil | Tomba   — OUTCOME_TRAFFIC / PROFILE_VISIT — R$200

Cada campanha tem 1 conjunto e 3 anuncios (CONVITE, COPO SHOW, TODO MUNDO VAI).
Cada anuncio usa os DOIS formatos: o 1:1 no feed e o 9:16 em stories/reels,
via asset_customization_rules (placement asset customization).

Nada e ativado por este script. Revisar no Ads Manager e ativar os 3 niveis.

Pre-requisito: a conta act_1396372809122061 precisa estar ATIVA. Enquanto estiver
desativada (disable_reason 1) a Meta recusa qualquer criacao e o script para na
checagem inicial, sem criar nada.

Uso:
    python build_inauguracao.py --checar     # so verifica pre-requisitos
    python build_inauguracao.py              # build completo (as 2 campanhas)
    python build_inauguracao.py --so A       # so a campanha de reconhecimento
    python build_inauguracao.py --so B       # so a de trafego pro perfil
    python build_inauguracao.py --sem-custom # 1 anuncio por formato, sem
                                             # placement customization (plano B
                                             # se a Meta recusar as regras)
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone

PASTA_CRIATIVOS = (
    r"C:\Users\MilenyGalvão\OneDrive\Área de Trabalho\CLAUDE CODE"
    r"\franquias\acai-fruit-show\criativos loja tombas"
)

AQUI = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.abspath(os.path.join(AQUI, "..", ".."))
sys.path.insert(0, os.path.join(SKILL, "scripts"))

from lib import init_api  # noqa: E402

# ---------------------------------------------------------------------------
# Conta e ativos
# ---------------------------------------------------------------------------

CONTA = "act_1396372809122061"         # padrao: conta propria do Tomba (bloqueada)

# Plano B: rodar pela conta ATIVA da loja irma FSA, com a pagina do Tomba.
# Usar --conta fsa. A cobranca cai na conta da FSA, nao na do Tomba.
CONTAS = {
    "tomba": "act_1396372809122061",   # BM "Açaí Frui Show Tomba" — DESATIVADA
    "fsa": "act_1441561347702342",     # BM acaifruitshow.fsa (1391827282125899) — ativa
}

PAGINA = "1217373171465383"            # Acai Fruit Show Tomba FSa
INSTAGRAM = "17841441193880089"        # @acaifruitshowtomba
IG_USER = "acaifruitshowtomba"
PERFIL_IG = f"http://instagram.com/{IG_USER}"

FIM = "2026-08-14T23:59:00-0300"       # dia da inauguracao = ultimo dia de verba

# "A partir de hoje": comeca 10 minutos depois de rodar o script. Verba vitalicia
# exige start_time explicito, senao a Meta assume a criacao e pode recusar.
BRT = timezone(timedelta(hours=-3))


def inicio():
    return (datetime.now(BRT) + timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%S%z")

# Praca Macario Barreto, S/N - Tomba (em frente ao Supermercado da Praca)
LAT, LNG = -12.28243, -38.95731

# Verba por campanha, em centavos
VERBA_ALCANCE = 30000   # R$300 — convite/reconhecimento
VERBA_TRAFEGO = 20000   # R$200 — visita ao perfil

RAIO_ALCANCE = 6        # km — definido pela Mileny (10/08)
RAIO_TRAFEGO = 6        # km

# Nota de dimensionamento: 6km = 450-530 mil pessoas. Com R$300 da para ~37-75 mil
# impressoes, ou seja ~8-15% do publico, 1x cada. Com REACH o Meta espalha para o
# maximo de gente diferente, entao o teto de frequencia abaixo fica sem efeito
# nesse tamanho de publico (a 1km eram 23-27 mil pessoas com ~3x cada).

ENDERECO = ("Praça Macário Barreto, S/N — Tomba "
            "(em frente ao Supermercado da Praça)")

# ---------------------------------------------------------------------------
# Os 3 conceitos. Cada um: arquivo do feed, arquivo de stories e a legenda.
# ---------------------------------------------------------------------------

CONCEITOS = [
    {
        "nome": "CONVITE",
        "feed": "TOMBA - CONVITE FEED.png",
        "stories": "TOMBA - CONVITE STORIES.png",
        "titulo": "Inauguração Açaí Fruit Show Tomba",
        "legenda": (
            "Você está convidado! 💜🎉\n\n"
            "O Açaí Fruit Show chegou no Tomba, e a nossa inauguração é "
            "dia 14 de agosto, a partir das 12h.\n\n"
            "Marca na agenda, chama a galera e vem viver essa experiência "
            "com a gente. Não fique de fora!\n\n"
            f"📍 {ENDERECO}\n"
            "🗓️ 14/08, a partir das 12h\n"
            f"📱 @{IG_USER}"
        ),
    },
    {
        "nome": "COPO SHOW",
        "feed": "TOMBA - COPO SHOW FEED.png",
        "stories": "TOMBA - COPO SHOW STORIES.png",
        "titulo": "100 Copos Show na inauguração",
        "legenda": (
            "100 COPOS SHOW para os primeiros clientes! 🥤💜\n\n"
            "É isso mesmo: na inauguração do Açaí Fruit Show Tomba, os "
            "primeiros clientes ganham um Copo Show.\n\n"
            "Dia 14 de agosto, a partir das 12h. Chega cedo — é por ordem "
            "de chegada!\n\n"
            f"📍 {ENDERECO}\n"
            "🗓️ 14/08, a partir das 12h"
        ),
    },
    {
        "nome": "TODO MUNDO VAI",
        "feed": "TOMBA - TODO MUNDO  VAI FEED.png",
        "stories": "TOMBA - TODO MUNDO  VAI STORIES.png",
        "titulo": "Compre 1 e ganhe outro na inauguração",
        "legenda": (
            "COMPRE 1 E GANHE OUTRO na mega inauguração! 💜🍨\n\n"
            "O Açaí Fruit Show Tomba abre dia 14 de agosto, a partir das "
            "12h — e no dia é compre 1, ganhe outro.\n\n"
            "Chama quem você quer levar e vem com a gente. Todo mundo vai!\n\n"
            f"📍 {ENDERECO}\n"
            "🗓️ 14/08, a partir das 12h\n\n"
            "*Promoção válida no dia da inauguração, conforme regulamento "
            "na loja."
        ),
    },
]

# ---------------------------------------------------------------------------
# Posicionamentos — so Instagram (preferencia permanente da Mileny)
# ---------------------------------------------------------------------------

POS_FEED = ["stream", "explore", "explore_home", "profile_feed"]
POS_STORIES = ["story", "reels"]

# explore_home exige "explore" junto, senao a API rejeita (subcode 2490392)
POS_TODOS = POS_FEED + POS_STORIES

# Enhancements automaticos desligados — regra permanente: anuncio sempre limpo.
# Campos validos confirmados em 2026-07-24 (nao incluir standard_enhancements).
DOF_SPEC = {
    "creative_features_spec": {
        chave: {"enroll_status": "OPT_OUT"}
        for chave in (
            "advantage_plus_creative", "enhance_cta", "text_optimizations",
            "video_auto_crop", "video_uncrop", "pac_relaxation",
        )
    }
}

# CTA da campanha B. Nao usar VIEW_INSTAGRAM_PROFILE: a conta nao e elegivel a
# anuncios de Visita ao Perfil com este perfil (subcode 2016153), e o objetivo de
# reconhecimento tambem recusa esse tipo (1885396). LEARN_MORE com link pro perfil
# entrega o mesmo destino e passa nos dois casos.
CTA_TRAFEGO = "LEARN_MORE"


def targeting(raio_km, posicoes):
    return {
        "age_min": 18,
        "age_max": 65,
        "geo_locations": {
            "custom_locations": [{
                "latitude": LAT,
                "longitude": LNG,
                "radius": raio_km,
                "distance_unit": "kilometer",
                "country": "BR",
            }],
            "location_types": ["home", "recent"],
        },
        "publisher_platforms": ["instagram"],
        "instagram_positions": posicoes,
        "device_platforms": ["mobile", "desktop"],
        # NAO incluir targeting_optimization: a Meta removeu o campo e o conjunto
        # PROFILE_VISIT rejeita com subcode 1870197 (o de REACH ainda aceitava).
        "targeting_automation": {
            "advantage_audience": 0,
            "individual_setting": {"age": 0, "gender": 0},
        },
    }


# ---------------------------------------------------------------------------

init_api()
from facebook_business.api import FacebookAdsApi  # noqa: E402

api = FacebookAdsApi.get_default_api()


def chamar(metodo, caminho, params=None, files=None):
    """Chamada Graph com erro legivel (error_user_msg, nao so o subcode)."""
    try:
        resp = api.call(metodo, caminho, params=params or {}, files=files or {})
        return resp.json()
    except Exception as exc:  # noqa: BLE001
        corpo = getattr(exc, "_body", None) or getattr(exc, "body", None)
        if isinstance(corpo, dict):
            err = corpo.get("error", corpo)
            msg = err.get("error_user_msg") or err.get("message")
            sub = err.get("error_subcode") or err.get("code")
            raise SystemExit(f"\nFALHOU em {'/'.join(caminho)} [{sub}]\n  {msg}\n")
        raise SystemExit(f"\nFALHOU em {'/'.join(caminho)}\n  {exc}\n")


def checar_prerequisitos():
    print("Checando pre-requisitos...\n")

    conta = chamar("GET", (CONTA,), {
        "fields": "name,account_status,disable_reason,balance,is_prepay_account",
    })
    status = conta.get("account_status")
    print(f"  conta     : {conta.get('name')} — status {status}")
    if status != 1:
        raise SystemExit(
            f"\nBLOQUEADO: conta com account_status {status} "
            f"(disable_reason {conta.get('disable_reason')}).\n"
            "So conta ATIVA cria anuncios. Pedir revisao em\n"
            "  business.facebook.com > Central de Contas > Qualidade da conta\n"
            "e rodar de novo quando liberar.\n"
        )

    paginas = chamar("GET", ("me", "accounts"), {"fields": "id", "limit": 200})
    if PAGINA not in {p["id"] for p in paginas.get("data", [])}:
        raise SystemExit(
            f"\nBLOQUEADO: pagina {PAGINA} fora do /me/accounts do system user.\n"
            "Sem acesso de Anunciante na pagina o criativo falha "
            "(erro 10 / subcode 3858749).\n"
        )
    print(f"  pagina    : {PAGINA} OK (system user tem acesso)")

    # NAO usar promote_pages como gate: ele lista so as paginas que o negocio dono
    # da conta POSSUI. Pagina compartilhada por parceiro funciona no anuncio e nao
    # aparece nessa lista (confirmado 10/08: criativo criado na conta da FSA com a
    # pagina do Tomba, que nao consta no promote_pages dela). E so informativo.
    promo = chamar("GET", (CONTA, "promote_pages"), {"fields": "id", "limit": 200})
    if PAGINA in {p["id"] for p in promo.get("data", [])}:
        print(f"  vinculo   : pagina e propria do negocio dono da {CONTA}")
    else:
        print("  vinculo   : pagina vem de parceiro (nao consta em promote_pages "
              "— normal)")

    if conta.get("is_prepay_account") and int(conta.get("balance", 0)) == 0:
        print("  ATENCAO   : conta pre-paga com saldo R$0 — por credito antes "
              "de ativar")

    faltando = []
    for c in CONCEITOS:
        for chave in ("feed", "stories"):
            caminho = os.path.join(PASTA_CRIATIVOS, c[chave])
            if not os.path.isfile(caminho):
                faltando.append(caminho)
    if faltando:
        raise SystemExit("\nArquivos nao encontrados:\n  " +
                         "\n  ".join(faltando) + "\n")
    print(f"  criativos : {len(CONCEITOS) * 2} arquivos OK\n")


_cache_hash = {}


def subir_imagem(nome_arquivo):
    """Sobe a imagem e devolve o hash (cacheado por arquivo)."""
    if nome_arquivo in _cache_hash:
        return _cache_hash[nome_arquivo]
    caminho = os.path.join(PASTA_CRIATIVOS, nome_arquivo)
    with open(caminho, "rb") as fh:
        res = chamar("POST", (CONTA, "adimages"), files={nome_arquivo: fh})
    h = list(res.get("images", {}).values())[0]["hash"]
    _cache_hash[nome_arquivo] = h
    print(f"    imagem subida : {h[:12]}...  {nome_arquivo}")
    return h


def criar_campanha(nome, objetivo):
    c = chamar("POST", (CONTA, "campaigns"), {
        "name": nome,
        "objective": objetivo,
        "status": "PAUSED",
        "special_ad_categories": json.dumps([]),
        "buying_type": "AUCTION",
        # ABO exige este campo explicito (subcode 4834011)
        "is_adset_budget_sharing_enabled": "false",
    })
    print(f"  campanha : {c['id']}  {nome}")
    return c["id"]


def criar_conjunto_alcance(campanha_id):
    nome = f"00 - Feira de Santana | {RAIO_ALCANCE}km | 18-65"
    cj = chamar("POST", (CONTA, "adsets"), {
        "name": nome,
        "campaign_id": campanha_id,
        "status": "PAUSED",
        "optimization_goal": "REACH",
        "billing_event": "IMPRESSIONS",
        "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
        "lifetime_budget": VERBA_ALCANCE,
        "start_time": inicio(),
        "end_time": FIM,
        "targeting": json.dumps(targeting(RAIO_ALCANCE, POS_TODOS)),
        # Convite quer repeticao: ate 2 impressoes por pessoa por dia.
        "frequency_control_specs": json.dumps([
            {"event": "IMPRESSIONS", "interval_days": 1, "max_frequency": 2},
        ]),
    })
    print(f"  conjunto : {cj['id']}  {nome}")
    return cj["id"]


def criar_conjunto_trafego(campanha_id):
    nome = f"00 - Feira de Santana | {RAIO_TRAFEGO}km | 18-65"
    cj = chamar("POST", (CONTA, "adsets"), {
        "name": nome,
        "campaign_id": campanha_id,
        "status": "PAUSED",
        # PROFILE_VISIT + destination INSTAGRAM_PROFILE seria o ideal, mas a conta
        # nao e elegivel a Visita ao Perfil com este perfil novo (subcode 2016153).
        # LINK_CLICKS com o link do perfil e o substituto elegivel.
        "optimization_goal": "LINK_CLICKS",
        "billing_event": "IMPRESSIONS",
        "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
        "lifetime_budget": VERBA_TRAFEGO,
        "start_time": inicio(),
        "end_time": FIM,
        "targeting": json.dumps(targeting(RAIO_TRAFEGO, POS_TODOS)),
    })
    print(f"  conjunto : {cj['id']}  {nome}")
    return cj["id"]


def criar_ad_customizado(conceito, conjunto_id, cta):
    """1 anuncio que serve o 1:1 no feed e o 9:16 em stories/reels."""
    h_feed = subir_imagem(conceito["feed"])
    h_story = subir_imagem(conceito["stories"])

    afs = {
        "images": [
            {"hash": h_feed, "adlabels": [{"name": "img_feed"}]},
            {"hash": h_story, "adlabels": [{"name": "img_story"}]},
        ],
        "bodies": [{"text": conceito["legenda"]}],
        "titles": [{"text": conceito["titulo"]}],
        "link_urls": [{"website_url": PERFIL_IG}],
        "ad_formats": ["SINGLE_IMAGE"],
        "asset_customization_rules": [
            {
                "customization_spec": {
                    "publisher_platforms": ["instagram"],
                    "instagram_positions": POS_FEED,
                },
                "image_label": {"name": "img_feed"},
                "priority": 1,
            },
            {
                "customization_spec": {
                    "publisher_platforms": ["instagram"],
                    "instagram_positions": POS_STORIES,
                },
                "image_label": {"name": "img_story"},
                "priority": 2,
            },
        ],
    }
    if cta:
        afs["call_to_action_types"] = [cta]

    criativo = chamar("POST", (CONTA, "adcreatives"), {
        "name": f"[INAUG] {conceito['nome']} | feed+stories",
        "object_story_spec": json.dumps({
            "page_id": PAGINA,
            "instagram_user_id": INSTAGRAM,
        }),
        "asset_feed_spec": json.dumps(afs),
        "degrees_of_freedom_spec": json.dumps(DOF_SPEC),
    })
    anuncio = chamar("POST", (CONTA, "ads"), {
        "name": f"[INAUG] {conceito['nome']}",
        "adset_id": conjunto_id,
        "creative": json.dumps({"creative_id": criativo["id"]}),
        "status": "PAUSED",
    })
    print(f"    anuncio : {anuncio['id']}  {conceito['nome']} "
          f"(criativo {criativo['id']})")


def criar_ad_simples(conceito, conjunto_id, formato, cta):
    """Plano B: 1 anuncio por formato, sem placement customization."""
    nome_arq = conceito[formato]
    h = subir_imagem(nome_arq)

    # photo_data puro nao roda no Instagram (subcode 2446383) — usar link_data.
    link_data = {
        "image_hash": h,
        "link": PERFIL_IG,
        "message": conceito["legenda"],
        "name": conceito["titulo"],
    }
    if cta:
        link_data["call_to_action"] = {"type": cta, "value": {"link": PERFIL_IG}}

    criativo = chamar("POST", (CONTA, "adcreatives"), {
        "name": f"[INAUG] {conceito['nome']} | {formato}",
        "object_story_spec": json.dumps({
            "page_id": PAGINA,
            "instagram_user_id": INSTAGRAM,
            "link_data": link_data,
        }),
        "degrees_of_freedom_spec": json.dumps(DOF_SPEC),
    })
    anuncio = chamar("POST", (CONTA, "ads"), {
        "name": f"[INAUG] {conceito['nome']} | {formato}",
        "adset_id": conjunto_id,
        "creative": json.dumps({"creative_id": criativo["id"]}),
        "status": "PAUSED",
    })
    print(f"    anuncio : {anuncio['id']}  {conceito['nome']} [{formato}] "
          f"(criativo {criativo['id']})")


def montar(rotulo, nome_campanha, objetivo, criar_conjunto, cta, sem_custom):
    print(f"\n=== {rotulo} ===")
    campanha_id = criar_campanha(nome_campanha, objetivo)
    conjunto_id = criar_conjunto(campanha_id)
    for conceito in CONCEITOS:
        if sem_custom:
            for formato in ("feed", "stories"):
                criar_ad_simples(conceito, conjunto_id, formato, cta)
                time.sleep(1)
        else:
            criar_ad_customizado(conceito, conjunto_id, cta)
            time.sleep(1)
    return campanha_id


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--checar", action="store_true",
                    help="so verifica pre-requisitos, nao cria nada")
    ap.add_argument("--so", choices=["A", "B"],
                    help="A = so reconhecimento, B = so trafego perfil")
    ap.add_argument("--sem-custom", action="store_true",
                    help="1 anuncio por formato (plano B se a Meta recusar as "
                         "regras de placement)")
    ap.add_argument("--conta", choices=sorted(CONTAS), default="tomba",
                    help="de qual conta subir: 'tomba' (propria, bloqueada) ou "
                         "'fsa' (loja irma, ativa). Default: tomba")
    args = ap.parse_args()

    global CONTA
    CONTA = CONTAS[args.conta]
    print(f"Conta de veiculacao: {CONTA} ({args.conta})\n")

    checar_prerequisitos()
    if args.checar:
        print("Pre-requisitos OK — pronto pra rodar o build.")
        return

    criadas = []
    if args.so in (None, "A"):
        criadas.append(montar(
            f"A) RECONHECIMENTO — convite — R$ {VERBA_ALCANCE / 100:.0f}",
            "[INAUG] Reconhecimento | Tomba",
            "OUTCOME_AWARENESS",
            criar_conjunto_alcance,
            # Sem botao: OUTCOME_AWARENESS recusa VIEW_INSTAGRAM_PROFILE em
            # criativo dinamico (subcode 1885396). Alinhado com a regra de que
            # campanha sem destino nao leva CTA.
            cta=None,
            sem_custom=args.sem_custom,
        ))
    if args.so in (None, "B"):
        criadas.append(montar(
            f"B) TRAFEGO PERFIL — R$ {VERBA_TRAFEGO / 100:.0f}",
            "[INAUG] Trafego Perfil | Tomba",
            "OUTCOME_TRAFFIC",
            criar_conjunto_trafego,
            cta=CTA_TRAFEGO,
            sem_custom=args.sem_custom,
        ))

    print("\nTudo criado PAUSED. Antes de ativar:")
    print("  1. conferir preview: read.py preview --creative <id> --format all")
    print("  2. por credito na conta (pre-paga, saldo R$0)")
    print("  3. ativar os 3 niveis: campanha -> conjunto -> anuncios")
    print(f"\nCampanhas: {', '.join(criadas)}")


if __name__ == "__main__":
    main()
