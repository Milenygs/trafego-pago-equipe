"""Belo 24/09/2026 - renda familiar minima de R$5.001 (pode somar com outras pessoas) EXPLICITA em tudo.

Decisao da Mileny (24/09): substitui o "inclusive renda familiar ate R$5 mil" das copies de 23/09.
1. Formulario novo com o minimo na tela de abertura e na pergunta, e as MESMAS 7 faixas da LP.
2. Criativos novos (2 videos + 2 imagens) x (LP, formulario) com as copies ajustadas.
3. Troca o criativo nos 24 anuncios existentes (mesmos ids de anuncio).
Uso: python build_belo_renda_minima.py [--dry] [--form-id ID]
"""
import json
import sys
import time
from pathlib import Path

import requests

AQUI = Path(__file__).parent
sys.path.insert(0, str(AQUI))
import build_belo_lancamento as lp  # noqa: E402
import build_belo_form as fm        # noqa: E402

TOKEN, G, ACT, PAGE, IG = lp.TOKEN, lp.G, lp.ACT, lp.PAGE, lp.IG
CAMP_LP, CAMP_FORM = "120245790359480358", "120245805859660358"
VIDEOS = {"VID Locucao Lancamento v1": "1532597512229215", "VID UGC Leo v1": "3228123300731106"}
IMAGENS = {"IMG Lancamento Fachada v1": "c6aaa32c644cfd7966e3222f21f86e4a",
           "IMG Lancamento Azul v1": "ee3413bf03630e75650b72f6f90464fc"}
RENDA = "Renda familiar mínima de R$5.001, e dá para somar com outras pessoas que vão morar com você."

TROCAS = [
    # LP
    ("Dá para somar a renda de quem vai morar com você. A simulação mostra valores para todas as faixas, "
     "inclusive renda familiar até R$5 mil.", RENDA),
    ("No simulador você escolhe a faixa de renda da família, inclusive até R$5 mil, e vê os dois valores",
     "No simulador você informa a renda da família (mínimo de R$5.001, somando com outras pessoas) e vê os dois valores"),
    ("✔ A renda da família soma, e a simulação mostra valores para todas as faixas, inclusive até R$5 mil",
     "✔ Renda familiar mínima de R$5.001, e dá para somar com outras pessoas"),
    # formulario
    ("Dá para somar a renda de quem vai morar com você, em qualquer faixa, inclusive renda familiar até R$5 mil.", RENDA),
    ("Você informa a faixa de renda da família, inclusive até R$5 mil, e o nosso time te passa os dois valores",
     "Você informa a renda da família (mínimo de R$5.001, somando com outras pessoas) e o nosso time te passa os dois valores"),
    ("✔ A renda da família soma, em qualquer faixa, inclusive até R$5 mil",
     "✔ Renda familiar mínima de R$5.001, e dá para somar com outras pessoas"),
]


def ajusta(txt):
    for a, b in TROCAS:
        txt = txt.replace(a, b)
    if "até R$5 mil" in txt or "todas as faixas" in txt or "R$5.001" not in txt:
        sys.exit("texto sem o minimo explicito ou com a frase antiga:\n" + txt)
    return txt


BODIES_LP = [ajusta(b) for b in (lp.BODY_1, lp.BODY_2, lp.BODY_3)]
BODIES_FORM = [ajusta(b) for b in (fm.BODY_1, fm.BODY_2, fm.BODY_3)]
# 24/09 (tarde): a Mileny aplicou a logica de 10/09 - titulo com o minimo sozinho repete o descartado
# "Renda familiar a partir de R$5.500". Com --titulo-facilidade volta "Simule com a renda da sua familia".
if "--titulo-facilidade" in sys.argv:
    TITLES = list(lp.TITLES)
else:
    TITLES = [t if t != "Simule com a renda da sua família" else "Renda familiar mínima R$5.001" for t in lp.TITLES]
assert all(len(t) <= 40 for t in TITLES)
SUFIXO = "facilidades" if "--titulo-facilidade" in sys.argv else "renda min"

FAIXAS_LP = ["Até R$ 5.000", "R$ 5.001 a R$ 6.000", "R$ 6.001 a R$ 7.000", "R$ 7.001 a R$ 8.000",
             "R$ 8.001 a R$ 9.000", "R$ 9.001 a R$ 10.000", "Acima de R$ 10.000"]  # iguais ao formulario da LP
CONTEXTO = ("Lançamento da AP Ponto em Vespasiano: apartamentos de 2 quartos a partir de R$250 mil, "
            "pelo Minha Casa Minha Vida.\n\n"
            "✅ Renda familiar mínima de R$5.001: dá para somar com outras pessoas\n"
            "✅ Entrada parcelada em até 60x direto com a construtora\n"
            "✅ ITBI e registro por conta da AP Ponto\n"
            "✅ Use o seu FGTS\n"
            "✅ Lazer completo, a 2 minutos do ponto de ônibus\n\n"
            "Preencha e o nosso time te mostra quanto fica o seu apê.\n\n"
            "Consulte condições.")
OPT_OUT_VID = lp.OPT_OUT
OPT_OUT_IMG = ["advantage_plus_creative", "enhance_cta", "inline_comment", "text_optimizations", "image_touchups",
               "image_uncrop", "image_templates", "adapt_to_placement", "show_summary", "reveal_details_over_time"]


def get(p, tok=None, **k):
    k["access_token"] = tok or TOKEN
    return requests.get(G + p, params=k).json()


def post(path, data, tok=None, fatal=True):
    data = {k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v) for k, v in data.items()}
    data["access_token"] = tok or TOKEN
    r = requests.post(G + path, data=data).json()
    if "error" in r:
        e = r["error"]
        print(json.dumps({k: e.get(k) for k in ("code", "error_subcode", "error_user_title", "error_user_msg", "message")},
                         ensure_ascii=False, indent=1))
        if fatal:
            sys.exit(1)
    return r


def criar_form():
    utm = "?utm_source=meta&utm_medium=leadform&utm_campaign=belo_lancamento"
    r = post(PAGE + "/leadgen_forms", {
        "name": "AP Ponto | Ponto Belo | Lançamento | Renda mín 5001 | SET26",
        "locale": "pt_BR",
        "questions": [
            {"type": "CUSTOM", "key": "renda_familiar",
             "label": "Qual a renda familiar? (Mínimo de R$5.001, pode somar com outras pessoas)",
             "options": [{"key": "faixa_%d" % i, "value": f} for i, f in enumerate(FAIXAS_LP)]},
            {"type": "CUSTOM", "key": "fgts", "label": "Você possui FGTS disponível?",
             "options": [{"key": "sim", "value": "Sim!"}, {"key": "nao", "value": "Não."}]},
            {"type": "FULL_NAME"}, {"type": "EMAIL"}, {"type": "PHONE"},
        ],
        "context_card": {"title": "Ponto Belo: seu primeiro apê em Vespasiano", "style": "PARAGRAPH_STYLE",
                         "content": [CONTEXTO], "button_text": "Quero minha simulação"},
        "question_page_custom_headline": "Preencha e o nosso time te mostra quanto fica o seu apê",
        "thank_you_page": {"title": "Recebemos os seus dados!",
                           "body": "O nosso time entra em contato com a simulação do seu apê no Ponto Belo.",
                           "button_text": "Conhecer o Ponto Belo", "button_type": "VIEW_WEBSITE",
                           "website_url": "https://belo.apponto.com.br/" + utm},
        "privacy_policy": {"url": "https://apponto.com.br/politica-de-privacidade",
                           "link_text": "Acesse a Política de Privacidade da Página AP Ponto Construtora."},
        "follow_up_action_url": "https://belo.apponto.com.br/" + utm,
        "block_display_for_non_targeted_viewer": True,
        "allow_organic_lead": True,
    }, tok=fm.page_token())
    print("formulario novo", r["id"])
    return r["id"]


def feed(bodies):
    return {"bodies": [{"text": b} for b in bodies], "titles": [{"text": t} for t in TITLES],
            "descriptions": [{"text": d} for d in lp.DESCRIPTIONS], "optimization_type": "DEGREES_OF_FREEDOM"}


def dof(lista):
    return {"creative_features_spec": {f: {"enroll_status": "OPT_OUT"} for f in lista}}


def main():
    if "--dry" in sys.argv:
        for b in BODIES_LP + BODIES_FORM:
            print(b, "\n-----")
        print(TITLES)
        return
    form = sys.argv[sys.argv.index("--form-id") + 1] if "--form-id" in sys.argv else criar_form()
    cta_lp = {"type": "LEARN_MORE", "value": {"link": lp.LINK}}
    cta_fm = {"type": "SIGN_UP", "value": {"lead_gen_form_id": form}}

    novos = {}  # (campanha, nome do anuncio) -> criativo
    for nome, vid in VIDEOS.items():
        thumbs = get(vid + "/thumbnails", fields="uri,is_preferred").get("data", [])
        uri = next((t["uri"] for t in thumbs if t.get("is_preferred")), thumbs[0]["uri"])
        for camp, cta, bodies, extra in ((CAMP_LP, cta_lp, BODIES_LP, {"url_tags": lp.UTM}),
                                         (CAMP_FORM, cta_fm, BODIES_FORM, {})):
            novos[(camp, nome)] = post(ACT + "/adcreatives", {
                "name": f"{nome} | BELO {'FORM ' if camp == CAMP_FORM else ''}SET26 | {SUFIXO}",
                "object_story_spec": {"page_id": PAGE, "instagram_user_id": IG,
                                      "video_data": {"video_id": vid, "image_url": uri, "call_to_action": cta}},
                "asset_feed_spec": feed(bodies), "degrees_of_freedom_spec": dof(OPT_OUT_VID), **extra})["id"]
            time.sleep(1)
    for nome, h in IMAGENS.items():
        for camp, cta, bodies, link, extra in ((CAMP_LP, cta_lp, BODIES_LP, lp.LINK, {"url_tags": lp.UTM}),
                                               (CAMP_FORM, cta_fm, BODIES_FORM, "https://fb.me/", {})):
            novos[(camp, nome)] = post(ACT + "/adcreatives", {
                "name": f"{nome} | BELO {'FORM ' if camp == CAMP_FORM else ''}SET26 | {SUFIXO}",
                "object_story_spec": {"page_id": PAGE, "instagram_user_id": IG,
                                      "link_data": {"image_hash": h, "link": link, "call_to_action": cta}},
                "asset_feed_spec": feed(bodies), "degrees_of_freedom_spec": dof(OPT_OUT_IMG), **extra})["id"]
            time.sleep(1)
    print("criativos novos:", {f"{'LP' if c == CAMP_LP else 'FORM'} {n}": i for (c, n), i in novos.items()})

    for camp in (CAMP_LP, CAMP_FORM):
        for a in get(camp + "/ads", fields="name,adset{name}", limit=50)["data"]:
            cr = novos.get((camp, a["name"]))
            if not cr:
                print("  sem criativo novo para", a["name"])
                continue
            r = post(a["id"], {"creative": {"creative_id": cr}}, fatal=False)
            print(f"  troca {'LP' if camp == CAMP_LP else 'FORM'} | {a['adset']['name']} | {a['name']} -> {cr} {r}")
            time.sleep(2)


if __name__ == "__main__":
    main()
