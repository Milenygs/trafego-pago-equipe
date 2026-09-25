"""Belo 24/09/2026 - os 2 videos do Belo no Direct (conjunto CONVERSATIONS 120245801239900358).

Texto de conversao para o Direct (logica de 10/09: facilidades em destaque, minimo so junto de "somar"),
CTA Enviar mensagem + a mesma mensagem automatica do Belo (boas-vindas + 3 ice breakers "Ponto Belo").
Cria os anuncios PAUSED; --ativar liga os anuncios + conjunto + campanha depois de validar geo.
Uso: python build_belo_direct_videos.py [--ativar]
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
CAMP = "120245801239270358"
ADSET = "120245801239900358"  # [BELO] Direct Publico Quente 180D (BH 17 + Contagem 17 + Vespasiano 20)
VIDEOS = {"VID Locucao Lancamento v1 [DIRECT]": "1532597512229215", "VID UGC Leo v1 [DIRECT]": "3228123300731106"}

TEXTO = """Seu primeiro apê em Vespasiano pode estar mais perto do que você imagina. 🏡

Ponto Belo, o lançamento da AP Ponto: 2 quartos a partir de R$250 mil, pelo Minha Casa Minha Vida.

✅ Entrada parcelada em até 60x direto com a construtora
✅ ITBI e registro por conta da AP Ponto
✅ Renda familiar a partir de R$5.001, e dá para somar com outras pessoas
✅ Lazer completo, a 2 minutos do ponto de ônibus

💬 Chama a gente aqui no Direct: te mostramos quanto fica a sua parcela.
*Consulte condições."""
TITULO = "Ponto Belo: fale com a gente no Direct"


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


def main():
    assert len(TITULO) <= 40
    existentes = {a["name"]: a["id"] for a in get(ADSET + "/ads", fields="name").get("data", [])}
    ads = []
    for nome, vid in VIDEOS.items():
        if nome in existentes:
            ads.append(existentes[nome]); print(nome, "ja existe"); continue
        thumbs = get(vid + "/thumbnails", fields="uri,is_preferred").get("data", [])
        uri = next((t["uri"] for t in thumbs if t.get("is_preferred")), thumbs[0]["uri"])
        cr = post(ACT + "/adcreatives", {
            "name": f"{nome} | BELO DIRECT SET26",
            "object_story_spec": {"page_id": PAGE, "instagram_user_id": IG, "video_data": {
                "video_id": vid, "image_url": uri, "message": TEXTO, "title": TITULO,
                "call_to_action": {"type": "INSTAGRAM_MESSAGE",
                                   "value": {"app_destination": "INSTAGRAM_DIRECT", "link": "https://www.instagram.com/"}},
                "page_welcome_message": json.dumps(bv.WELCOME, ensure_ascii=False)}},
            "degrees_of_freedom_spec": {"creative_features_spec": {f: {"enroll_status": "OPT_OUT"} for f in lp.OPT_OUT}},
        })["id"]
        ad = post(ACT + "/ads", {"name": nome, "adset_id": ADSET, "creative": {"creative_id": cr}, "status": "PAUSED"})["id"]
        ads.append(ad)
        print(nome, "criativo", cr, "anuncio", ad)
        time.sleep(2)

    # validacao: geo no conjunto e boas-vindas nos criativos
    g = get(ADSET, fields="targeting{geo_locations}")["targeting"].get("geo_locations", {})
    cidades = [(c.get("name"), c.get("radius")) for c in g.get("cities", [])]
    print("geo do conjunto:", cidades)
    if not cidades:
        sys.exit("CONJUNTO SEM GEO - nao ativar")
    for a in ads:
        c = get(a, fields="creative{object_story_spec}")["creative"]["object_story_spec"]["video_data"]
        print("  ", a, "boas-vindas:", bool(c.get("page_welcome_message")), "| CTA:", c["call_to_action"]["type"])

    if "--ativar" in sys.argv:
        for obj in [CAMP, ADSET] + ads:
            print("ativar", obj, post(obj, {"status": "ACTIVE"}, fatal=False))
            time.sleep(2)
        for obj in [CAMP, ADSET] + ads:
            print("  ", get(obj, fields="name,status,effective_status"))


if __name__ == "__main__":
    main()
