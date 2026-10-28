"""Belo 26/10/2026 - campanha de Direct com o video novo do Leo (3 Motivos), no lugar da Indicacao.

Publico = o do M_ANIV17_SET26_DIRECT (120245571017280358, 111 conversas a R$15): aberto, sem lista, 20-50, so
Instagram (feed, stories, reels, perfil), sem Advantage. Geo = praca de 15/10 (BH cidade + Vespasiano 20 km,
expansao desligada) no lugar de Contagem 21 + Vespasiano 25; idioma pt-BR como trava (Direct de 24/09 entregou
em 73 paises). Mensagem automatica do Belo (boas-vindas + 3 ice breakers "Ponto Belo"). R$100/dia. Tudo PAUSED.
Uso: python build_belo_direct_leo3motivos_2610.py
"""
import json
import sys
import time
from pathlib import Path

import requests

AQUI = Path(__file__).parent
sys.path.insert(0, str(AQUI))
import build_belo_lancamento as lp           # noqa: E402
import build_belo_direct_boasvindas as bv    # noqa: E402

TOKEN, G, ACT, PAGE, IG = lp.TOKEN, lp.G, lp.ACT, lp.PAGE, lp.IG
VIDEO = Path.home() / "OneDrive/Área de Trabalho/CLAUDE CODE/clientes/ap-ponto/criativos belo/criativos 2909/v1.mp4"

CAMPANHA = "[BELO] Direct | Leo 3 Motivos | OUT26"
CONJUNTO = "[BELO] Direct Aberto 20-50 | BH + Vespasiano"
ANUNCIO = "VID UGC Leo 3 Motivos v1 [DIRECT]"
VERBA = 10000  # centavos: R$100/dia (a mesma da Indicacao)

TARGETING = {
    "age_min": 20, "age_max": 50,
    "geo_locations": {"cities": [{"key": "244661"},  # Belo Horizonte (cidade, sem raio)
                                 {"key": "273969", "radius": 20, "distance_unit": "kilometer"}]},  # Vespasiano
    "locales": [16],  # Portugues (Brasil)
    "publisher_platforms": ["instagram"],
    "instagram_positions": ["stream", "story", "reels", "profile_feed"],
    "device_platforms": ["mobile", "desktop"],
    "targeting_automation": {"advantage_audience": 0, "individual_setting": {"geo": 0}},
    "targeting_relaxation_types": {"lookalike": 0, "custom_audience": 0},
}

# Logica de 10/09 e 24/09: facilidades na abertura; renda minima so junto de "somar" (R$5.000 liberado em 26/10).
# So o que o video diz (o "5 minutos do centro" fica de fora ate ter fonte).
TEXTO = """Entrada em até 60x, documentação grátis e renda somada: o seu apê no Ponto Belo, em Vespasiano. 🏡

O mesmo valor que você paga de aluguel já pode ser a parcela do que é seu.

✅ Entrada parcelada em até 60x direto com a construtora
✅ Documentação do imóvel 100% gratuita
✅ Renda familiar mínima de R$5.000, e dá para somar com quem vai morar com você
📍 2 quartos a partir de R$250 mil, a 15 minutos do Shopping Estação

💬 Chama a gente aqui no Direct e faça a sua simulação.
*Consulte condições."""
TITULO = "Ponto Belo: simule pelo Direct"


def get(p, **k):
    k["access_token"] = TOKEN
    return requests.get(G + p, params=k).json()


def post(path, data, fatal=True):
    data = {k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v) for k, v in data.items()}
    data["access_token"] = TOKEN
    r = requests.post(G + path, data=data).json()
    if "error" in r:
        e = r["error"]
        print(json.dumps({k: e.get(k) for k in ("code", "error_subcode", "error_user_title", "error_user_msg", "message")},
                         ensure_ascii=False, indent=1))
        if fatal:
            sys.exit(1)
    return r


def subir_video():
    # envio simples: o upload em partes do create.py falha em video grande (aprendizado 19/09)
    for v in get(ACT + "/advideos", fields="title", limit=100).get("data", []):
        if v.get("title") == ANUNCIO:
            print("video ja existe", v["id"])
            return v["id"]
    with open(VIDEO, "rb") as f:
        r = requests.post(G + ACT + "/advideos", data={"access_token": TOKEN, "title": ANUNCIO, "name": ANUNCIO},
                          files={"source": (VIDEO.name, f, "video/mp4")}, timeout=600).json()
    if "id" not in r:
        sys.exit(f"upload falhou: {r}")
    print("video", r["id"])
    return r["id"]


def miniatura(vid):
    for _ in range(60):
        if get(vid, fields="status").get("status", {}).get("video_status") == "ready":
            break
        time.sleep(10)
    else:
        sys.exit("video nao ficou pronto em 10 min")
    thumbs = get(vid + "/thumbnails", fields="uri,is_preferred").get("data", [])
    return next((t["uri"] for t in thumbs if t.get("is_preferred")), thumbs[0]["uri"])


def main():
    assert len(TITULO) <= 40
    if CAMPANHA in {c["name"] for c in get(ACT + "/campaigns", fields="name", limit=200).get("data", [])}:
        sys.exit("campanha ja existe - conferir no painel antes de rodar de novo")

    vid = subir_video()
    uri = miniatura(vid)

    camp = post(ACT + "/campaigns", {
        "name": CAMPANHA, "objective": "OUTCOME_ENGAGEMENT", "status": "PAUSED",
        "special_ad_categories": [], "is_adset_budget_sharing_enabled": "false",
    })["id"]
    print("campanha", camp)
    time.sleep(1)
    adset = post(ACT + "/adsets", {
        "name": CONJUNTO, "campaign_id": camp, "status": "PAUSED",
        "daily_budget": VERBA, "billing_event": "IMPRESSIONS", "optimization_goal": "CONVERSATIONS",
        "destination_type": "INSTAGRAM_DIRECT", "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
        "promoted_object": {"page_id": PAGE}, "targeting": TARGETING, **lp.REGIONAL,
    })["id"]
    print("conjunto", adset)
    time.sleep(1)
    cr = post(ACT + "/adcreatives", {
        "name": f"{ANUNCIO} | BELO DIRECT OUT26",
        "object_story_spec": {"page_id": PAGE, "instagram_user_id": IG, "video_data": {
            "video_id": vid, "image_url": uri, "message": TEXTO, "title": TITULO,
            "call_to_action": {"type": "INSTAGRAM_MESSAGE",
                               "value": {"app_destination": "INSTAGRAM_DIRECT", "link": "https://www.instagram.com/"}},
            "page_welcome_message": json.dumps(bv.WELCOME, ensure_ascii=False)}},
        "degrees_of_freedom_spec": {"creative_features_spec": {f: {"enroll_status": "OPT_OUT"} for f in lp.OPT_OUT}},
    })["id"]
    print("criativo", cr)
    time.sleep(1)
    ad = post(ACT + "/ads", {"name": ANUNCIO, "adset_id": adset, "creative": {"creative_id": cr}, "status": "PAUSED"})["id"]
    print("anuncio", ad)

    # validacao: geo, idade, posicionamentos, boas-vindas, CTA, recursos de IA e status
    t = get(adset, fields="targeting")["targeting"]
    print("geo:", [(c.get("name"), c.get("radius")) for c in t.get("geo_locations", {}).get("cities", [])],
          "| idade:", t.get("age_min"), "-", t.get("age_max"), "| idioma:", t.get("locales"),
          "| IG:", t.get("instagram_positions"), "| plataformas:", t.get("publisher_platforms"),
          "| automacao:", t.get("targeting_automation"))
    if not t.get("geo_locations", {}).get("cities"):
        sys.exit("CONJUNTO SEM GEO - nao ativar")
    c = get(cr, fields="object_story_spec,degrees_of_freedom_spec")
    vd = c["object_story_spec"]["video_data"]
    spec = c.get("degrees_of_freedom_spec", {}).get("creative_features_spec", {})
    print("boas-vindas:", bool(vd.get("page_welcome_message")), "| CTA:", vd["call_to_action"]["type"],
          "| recursos IA OPT_OUT:", sum(1 for v in spec.values() if v.get("enroll_status") == "OPT_OUT"), "de", len(spec))
    for obj in (camp, adset, ad):
        print("  ", get(obj, fields="name,status,effective_status"))


if __name__ == "__main__":
    main()
