"""Belo 24/09/2026 - 2 estaticos (Belo.png e belo 22.png, 1080x1920) nas campanhas de LP e de formulario.

As imagens trazem "Renda minima familiar: R$ 5.001,00": as copies dos estaticos saem SEM a frase
"inclusive renda familiar ate R$5 mil" (continua o "da para somar a renda"). Mesmos titulos/descricoes.
LP: Saiba mais -> belo.apponto.com.br + UTM dinamica. Form: Cadastre-se -> formulario 1028699846879881.
2 anuncios novos por conjunto, PAUSED.
Uso: python build_belo_imagens.py [--dry]
"""
import json
import os
import sys
import time
from pathlib import Path

import requests

AQUI = Path(__file__).parent
sys.path.insert(0, str(AQUI))
import build_belo_lancamento as lp  # noqa: E402  (textos e UTM da campanha de LP)
import build_belo_form as fm        # noqa: E402  (textos da campanha de formulario)

TOKEN, G, ACT, PAGE, IG = lp.TOKEN, lp.G, lp.ACT, lp.PAGE, lp.IG
PASTA = lp.PASTA
IMAGENS = {"IMG Lancamento Fachada v1": PASTA / "Belo.png", "IMG Lancamento Azul v1": PASTA / "belo 22.png"}
CAMP_LP = "120245790359480358"
CAMP_FORM = "120245805859660358"
FORM_ID = "1028699846879881"

TROCAS = [
    ("Dá para somar a renda de quem vai morar com você. A simulação mostra valores para todas as faixas, "
     "inclusive renda familiar até R$5 mil.", "Dá para somar a renda com mais alguém que vai morar com você."),
    ("Dá para somar a renda de quem vai morar com você, em qualquer faixa, inclusive renda familiar até R$5 mil.",
     "Dá para somar a renda com mais alguém que vai morar com você."),
    ("No simulador você escolhe a faixa de renda da família, inclusive até R$5 mil, e vê os dois valores",
     "No simulador você informa a renda da família (dá para somar com mais alguém) e vê os dois valores"),
    ("Você informa a faixa de renda da família, inclusive até R$5 mil, e o nosso time te passa os dois valores",
     "Você informa a renda da família (dá para somar com mais alguém) e o nosso time te passa os dois valores"),
    ("✔ A renda da família soma, e a simulação mostra valores para todas as faixas, inclusive até R$5 mil",
     "✔ A renda da família soma: dá para juntar com mais alguém"),
    ("✔ A renda da família soma, em qualquer faixa, inclusive até R$5 mil",
     "✔ A renda da família soma: dá para juntar com mais alguém"),
]


def adapta(txt):
    for a, b in TROCAS:
        txt = txt.replace(a, b)
    if "até R$5 mil" in txt:
        sys.exit("sobrou 'até R$5 mil' num texto de estatico:\n" + txt)
    return txt


BODIES_LP = [adapta(b) for b in (lp.BODY_1, lp.BODY_2, lp.BODY_3)]
BODIES_FORM = [adapta(b) for b in (fm.BODY_1, fm.BODY_2, fm.BODY_3)]


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


def sobe_imagem(path):
    with open(path, "rb") as f:
        r = requests.post(G + ACT + "/adimages", data={"access_token": TOKEN},
                          files={path.name: (path.name, f.read(), "image/png")}).json()
    if "error" in r:
        sys.exit(json.dumps(r["error"], ensure_ascii=False))
    return list(r["images"].values())[0]["hash"]


OPT_OUT = ["advantage_plus_creative", "enhance_cta", "inline_comment", "text_optimizations", "image_touchups",
           "image_uncrop", "image_templates", "adapt_to_placement", "show_summary", "reveal_details_over_time"]


def criativo(nome, h, bodies, titles, descs, cta, link, url_tags=None):
    return post(ACT + "/adcreatives", {
        "name": nome,
        "object_story_spec": {"page_id": PAGE, "instagram_user_id": IG,
                              "link_data": {"image_hash": h, "link": link, "call_to_action": cta}},
        "asset_feed_spec": {"bodies": [{"text": b} for b in bodies], "titles": [{"text": t} for t in titles],
                            "descriptions": [{"text": d} for d in descs], "optimization_type": "DEGREES_OF_FREEDOM"},
        "degrees_of_freedom_spec": {"creative_features_spec": {f: {"enroll_status": "OPT_OUT"} for f in OPT_OUT}},
        **({"url_tags": url_tags} if url_tags else {}),
    })["id"]


def main():
    if "--dry" in sys.argv:
        for b in BODIES_LP + BODIES_FORM:
            print(b, "\n-----")
        return
    for ad_name, path in IMAGENS.items():
        h = sobe_imagem(path)
        print(ad_name, "hash", h)
        cr_lp = criativo(f"{ad_name} | BELO SET26", h, BODIES_LP, lp.TITLES, lp.DESCRIPTIONS,
                         {"type": "LEARN_MORE", "value": {"link": lp.LINK}}, lp.LINK, lp.UTM)
        cr_fm = criativo(f"{ad_name} | BELO FORM SET26", h, BODIES_FORM, fm.TITLES, fm.DESCRIPTIONS,
                         {"type": "SIGN_UP", "value": {"lead_gen_form_id": FORM_ID}}, "https://fb.me/")
        print("  criativos LP", cr_lp, "| form", cr_fm)
        for camp, cr in ((CAMP_LP, cr_lp), (CAMP_FORM, cr_fm)):
            for s in get(camp + "/adsets", fields="name")["data"]:
                ad = post(ACT + "/ads", {"name": ad_name, "adset_id": s["id"], "creative": {"creative_id": cr},
                                         "status": "PAUSED"}, fatal=False)
                print("   anuncio", s["name"], ad.get("id"))
                time.sleep(2)


if __name__ == "__main__":
    main()
