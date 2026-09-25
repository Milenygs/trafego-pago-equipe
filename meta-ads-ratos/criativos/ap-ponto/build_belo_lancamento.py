"""Belo 23/09/2026 - lançamento: conjunto de interesse + 2 videos x 3 conjuntos (6 anuncios PAUSED).

Copies em Carteira/outros/ap-ponto/copies_belo_lancamento.md (V1/V2/V3, 5 titulos, 3 descricoes).
UTM dinamica (so no Belo - a LP captura e manda pro CV). Anunciante verificado BR em todo conjunto.
Uso: python build_belo_lancamento.py interesse | anuncios [--video-loc ID --video-leo ID]
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import requests

SKILL = Path(os.path.expanduser("~/OneDrive/.claude/skills/meta-ads-ratos"))
env = (SKILL / ".env").read_text(encoding="utf-8")
TOKEN = [l.split("=", 1)[1].strip().strip('"') for l in env.splitlines() if l.startswith("META_ADS_TOKEN")][0]
G = "https://graph.facebook.com/v23.0/"

ACT = "act_1043516946010441"
PAGE = "198169833565944"
IG = "17841401339383360"
PIXEL = "211205516600655"
CAMP = "120245790359480358"
START = "2026-09-24T06:00:00-0300"
PASTA = Path(os.path.expanduser("~")) / "OneDrive" / "Área de Trabalho" / "CLAUDE CODE" / "clientes" / "ap-ponto" / "criativos belo"
VIDEOS = {  # nome do anuncio = utm_content no CV
    "VID Locucao Lancamento v1": PASTA / "Ads belo!.mp4",
    "VID UGC Leo v1": PASTA / "Ponto Belo ADS LEO.mp4",
}
LINK = "https://belo.apponto.com.br/"
UTM = ("utm_source=meta&utm_medium=paid_social&utm_campaign={{campaign.name}}"
       "&utm_term={{adset.name}}&utm_content={{ad.name}}")
# anunciante verificado (Lei BR) - o mesmo que a Mileny preencheu no painel em 23/09
REGIONAL = {
    "regional_regulated_categories": ["BRAZIL_REGULATION", "VOLUNTARY_VERIFICATION"],
    "regional_regulation_identities": {"universal_beneficiary": "609854092925940",
                                       "universal_payer": "609854092925940"},
}

BODY_1 = """Primeiro apê em Vespasiano.
E a renda da família toda conta.

O Ponto Belo é o lançamento da AP Ponto: apartamentos de 2 quartos a partir de R$250 mil, pelo Minha Casa Minha Vida.

A entrada é parcelada em até 60x direto com a construtora. E o ITBI e o registro ficam por conta da AP Ponto: são de R$10 mil a R$15 mil a menos logo na assinatura.

Dá para somar a renda de quem vai morar com você. A simulação mostra valores para todas as faixas, inclusive renda familiar até R$5 mil.

Piscina, academia, quadra, churrasqueira e playground dentro do condomínio.

\U0001F4CD Rua Afonso Pena, 685, Santo Antônio, Vespasiano/MG
\U0001F68C A 2 minutos do ponto de ônibus
✈️ A 15 minutos de Confins
*Consulte condições."""

BODY_2 = """Quanto fica o seu apê no Ponto Belo?
Dá para ver agora, sem cadastro.

No simulador você escolhe a faixa de renda da família, inclusive até R$5 mil, e vê os dois valores: a prestação da Caixa e a parcela da entrada com a AP Ponto.

\U0001F4CD Lançamento no Santo Antônio, Vespasiano · 2 quartos a partir de R$250 mil
\U0001F68C A 2 minutos do ônibus · a 15 de Confins
\U0001F4B3 Entrada em até 60x direto com a construtora
\U0001F4C4 ITBI e registro por conta da AP Ponto
\U0001F3CA Lazer completo no condomínio

O mesmo valor que você paga de aluguel já pode ser a parcela do que é seu.
Simule e veja como fica para a sua família \U0001F447
*Consulte condições."""

BODY_3 = """"Minha renda sozinha não dá."
"Não tenho o dinheiro da entrada."
"E ainda tem ITBI e cartório."

No Ponto Belo, a AP Ponto resolve as três:
✔ A renda da família soma, e a simulação mostra valores para todas as faixas, inclusive até R$5 mil
✔ A entrada é parcelada em até 60x direto com a construtora
✔ ITBI e registro ficam por nossa conta: de R$10 mil a R$15 mil que ficam com você

"Parcelamos a entrada e hoje estamos pagando prestações que cabem no nosso bolso."
Amanda e Fabrício, clientes AP Ponto

17 anos de mercado. Aqui você fala direto com a construtora, sem corretor.

Lançamento em Vespasiano: 2 quartos a partir de R$250 mil, na Rua Afonso Pena, 685, a 2 minutos do ônibus.
Faça sua simulação \U0001F447
*Consulte condições."""

TITLES = [
    "2 quartos a partir de R$250 mil",
    "Entrada em até 60x com a construtora",
    "ITBI e registro por nossa conta",
    "Simule com a renda da sua família",
    "A 2 min do ônibus, a 15 de Confins",
]
DESCRIPTIONS = ["Lançamento em Vespasiano", "Minha Casa Minha Vida", "Sem cadastro para simular"]

OPT_OUT = ["advantage_plus_creative", "enhance_cta", "inline_comment", "text_optimizations",
           "video_auto_crop", "video_filtering", "video_uncrop", "adapt_to_placement",
           "translate_voiceover", "show_summary", "reveal_details_over_time"]


def post(path, data, fatal=True):
    data = {k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v) for k, v in data.items()}
    data["access_token"] = TOKEN
    r = requests.post(G + path, data=data).json()
    if "error" in r:
        print(json.dumps(r["error"], ensure_ascii=False, indent=1))
        if fatal:
            sys.exit(1)
    return r


def get(path, **params):
    params["access_token"] = TOKEN
    return requests.get(G + path, params=params).json()


def adsets_da_campanha():
    return {a["name"]: a["id"] for a in get(CAMP + "/adsets", fields="name", limit=50).get("data", [])}


def criar_interesse():
    if "[BELO] Interesse Imóvel 25-45" in adsets_da_campanha():
        print("interesse ja existe")
        return
    targeting = {
        "age_min": 25, "age_max": 45,
        "geo_locations": {"cities": [{"key": "273969", "radius": 20, "distance_unit": "kilometer"}]},
        "flexible_spec": [{"interests": [{"id": "6002976176121"}, {"id": "6002986908368"},
                                         {"id": "6003103732434"}, {"id": "6003418314031"}]}],
        "excluded_custom_audiences": [{"id": "120245517540390358"}, {"id": "120245517540780358"}],
        "publisher_platforms": ["instagram"],
        "instagram_positions": ["stream", "explore", "reels", "profile_feed"],
        "device_platforms": ["mobile", "desktop"],
        "targeting_automation": {"advantage_audience": 0},
    }
    r = post(ACT + "/adsets", {
        "name": "[BELO] Interesse Imóvel 25-45", "campaign_id": CAMP, "status": "PAUSED",
        "daily_budget": 35000, "billing_event": "IMPRESSIONS", "optimization_goal": "OFFSITE_CONVERSIONS",
        "bid_strategy": "LOWEST_COST_WITHOUT_CAP", "destination_type": "WEBSITE",
        "promoted_object": {"pixel_id": PIXEL, "custom_event_type": "LEAD"},
        "start_time": START, "targeting": targeting, **REGIONAL,
    })
    print("adset interesse", r["id"])


def upload_video(path, nome):
    out = subprocess.run([sys.executable, str(SKILL / "scripts" / "create.py"), "video",
                          "--account", ACT, "--file", str(path), "--name", nome],
                         capture_output=True, text=True, encoding="utf-8")
    txt = out.stdout
    try:
        return json.loads(txt[txt.find("{"):txt.rfind("}") + 1])["id"]
    except Exception:
        print(txt, out.stderr)
        sys.exit("upload falhou - conferir read.py videos antes de repetir")


def thumb(vid, nome):
    for _ in range(40):
        st = get(vid, fields="status").get("status", {}).get("video_status")
        if st == "ready":
            break
        time.sleep(15)
    thumbs = get(vid + "/thumbnails", fields="uri,is_preferred").get("data", [])
    uri = next((t["uri"] for t in thumbs if t.get("is_preferred")), thumbs[0]["uri"])
    jpg = requests.get(uri).content
    fn = f"thumb_{nome}.jpg"
    img = requests.post(G + ACT + "/adimages", data={"access_token": TOKEN},
                        files={fn: (fn, jpg, "image/jpeg")}).json()
    if "error" in img:
        sys.exit(json.dumps(img["error"], ensure_ascii=False))
    return list(img["images"].values())[0]["hash"]


def criar_anuncios():
    adsets = adsets_da_campanha()
    print("conjuntos:", adsets)
    ids_video = {}
    if "--video-loc" in sys.argv:
        ids_video["VID Locucao Lancamento v1"] = sys.argv[sys.argv.index("--video-loc") + 1]
    if "--video-leo" in sys.argv:
        ids_video["VID UGC Leo v1"] = sys.argv[sys.argv.index("--video-leo") + 1]

    for ad_name, path in VIDEOS.items():
        slug = "BELO_LOCUCAO" if "Locucao" in ad_name else "BELO_LEO"
        vid = ids_video.get(ad_name) or upload_video(path, slug)
        print(ad_name, "video", vid)
        h = thumb(vid, slug)
        cr = post(ACT + "/adcreatives", {
            "name": f"{ad_name} | BELO SET26",
            "object_story_spec": {
                "page_id": PAGE, "instagram_user_id": IG,
                "video_data": {"video_id": vid, "image_hash": h,
                               "call_to_action": {"type": "LEARN_MORE", "value": {"link": LINK}}},
            },
            "asset_feed_spec": {
                "bodies": [{"text": b} for b in (BODY_1, BODY_2, BODY_3)],
                "titles": [{"text": t} for t in TITLES],
                "descriptions": [{"text": d} for d in DESCRIPTIONS],
                "optimization_type": "DEGREES_OF_FREEDOM",
            },
            "degrees_of_freedom_spec": {"creative_features_spec": {f: {"enroll_status": "OPT_OUT"} for f in OPT_OUT}},
            "url_tags": UTM,
        })
        print(ad_name, "creative", cr["id"])
        for set_name, set_id in adsets.items():
            ad = post(ACT + "/ads", {"name": ad_name, "adset_id": set_id,
                                     "creative": {"creative_id": cr["id"]}, "status": "PAUSED"}, fatal=False)
            print("  ad", set_name, ad.get("id"))
            time.sleep(2)


if __name__ == "__main__":
    {"interesse": criar_interesse, "anuncios": criar_anuncios}[sys.argv[1]]()
