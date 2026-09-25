"""Luna 16/09/2026 - video UGC "3 motivos" (v4.mp4) nos 3 conjuntos M_ da campanha de testes.

Sobe o video, cria 1 criativo (2 textos, 3 titulos, IA desligada) e 3 anuncios PAUSED.
Uso: python build_luna_3motivos.py [--dry]
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
VIDEO = Path(os.path.expanduser("~")) / "OneDrive" / "Área de Trabalho" / "CLAUDE CODE" / "clientes" / "ap-ponto" / "criativos luna" / "v4.mp4"
AD_NAME = "[VIDEO][3MOTIVOS][SET26]"
ADSETS = {
    "M_LUNA_LAL_COMPRADORES": "120245536041310358",
    "M_LUNA_INTERESSES": "120245536103800358",
    "M_LUNA_RMKT": "120245536106540358",
}
# 16/09: a Mileny trocou para a UTM fixa que o CV CRM le (padrao da conta ate mudar o rastreamento)
LINK = "https://luna.apponto.com.br/?utm_source=MetaAds&utm_medium=122&utm_campaign=MetaAds"
UTM = ""

BODY_1 = """Você quer sair do aluguel de uma vez por todas? Então veja 3 motivos para conhecer o Ponto Luna \U0001F447

1️⃣ A chave é sua ainda este ano: entrega prevista para dezembro de 2026, sem anos de espera nem dor de cabeça com obra.

2️⃣ Condições facilitadas: financiamento pelo Minha Casa Minha Vida, parcelamento em até 60x e documentação 100% gratuita. Você não paga ITBI nem registro.

3️⃣ Localização: a 15 minutos do Shopping Estação e a 7 minutos da Linha Verde, perto de comércio, escola e posto de saúde.

\U0001F3CA Lazer completo: piscina adulto e infantil, área gourmet com churrasqueira, playground e academia.

\U0001F4F2 Toque em Saiba mais e faça a sua simulação.
*Consulte condições."""

BODY_2 = """Chave na mão em dezembro, sem esperar anos de obra. \U0001F511

No Ponto Luna, em Vespasiano:
✅ Entrada e parcelas a partir de R$ 1.000
✅ Minha Casa Minha Vida + parcelamento em até 60x
✅ ITBI e registro grátis
✅ Use o FGTS e junte a renda de até 3 pessoas
✅ 15 min do Shopping Estação · 7 min da Linha Verde
✅ Piscina, área gourmet, playground e academia

\U0001F4F2 Simule agora e veja quanto fica a sua parcela.
*Consulte condições."""

TITLES = [
    "3 motivos para conhecer o Ponto Luna",
    "Chaves em dezembro · ITBI e registro grátis",
    "Entrada e parcela a partir de R$ 1.000",
]
DESCRIPTION = "Av. Serra do Contorno, 542 - Serra Dourada, Vespasiano - MG"

OPT_OUT = ["advantage_plus_creative", "enhance_cta", "inline_comment", "text_optimizations",
           "video_auto_crop", "video_filtering", "video_uncrop", "adapt_to_placement",
           "translate_voiceover", "show_summary", "reveal_details_over_time"]


def post(path, data):
    data = {k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v) for k, v in data.items()}
    data["access_token"] = TOKEN
    r = requests.post(G + path, data=data).json()
    if "error" in r:
        print(json.dumps(r["error"], ensure_ascii=False, indent=1))
        sys.exit(1)
    return r


def get(path, **params):
    params["access_token"] = TOKEN
    return requests.get(G + path, params=params).json()


def upload_video():
    out = subprocess.run([sys.executable, str(SKILL / "scripts" / "create.py"), "video",
                          "--account", ACT, "--file", str(VIDEO), "--name", "LUNA_3MOTIVOS_v4"],
                         capture_output=True, text=True, encoding="utf-8")
    txt = out.stdout
    try:
        return json.loads(txt[txt.find("{"):txt.rfind("}") + 1])["id"]
    except Exception:
        print(txt, out.stderr)
        sys.exit("upload falhou - conferir read.py videos antes de repetir")


def main():
    dry = "--dry" in sys.argv
    spec = {
        "page_id": PAGE, "instagram_user_id": IG,
        "video_data": {"video_id": "<VIDEO>", "image_hash": "<THUMB>",
                       "call_to_action": {"type": "LEARN_MORE", "value": {"link": LINK}}},
    }
    feed = {
        "bodies": [{"text": BODY_1}, {"text": BODY_2}],
        "titles": [{"text": t} for t in TITLES],
        "descriptions": [{"text": DESCRIPTION}],
        "optimization_type": "DEGREES_OF_FREEDOM",
    }
    dof = {"creative_features_spec": {f: {"enroll_status": "OPT_OUT"} for f in OPT_OUT}}
    if dry:
        print(BODY_1, "\n----\n", BODY_2, "\n----\n", TITLES)
        return

    # --video ID reaproveita um upload anterior (evita video duplicado na conta)
    vid = sys.argv[sys.argv.index("--video") + 1] if "--video" in sys.argv else upload_video()
    print("video", vid)
    for _ in range(40):
        st = get(vid, fields="status").get("status", {}).get("video_status")
        if st == "ready":
            break
        time.sleep(15)
    print("status", st)

    # miniatura: frame do proprio video, subido como imagem da conta (hash nao expira)
    thumbs = get(vid + "/thumbnails", fields="uri,is_preferred").get("data", [])
    uri = next((t["uri"] for t in thumbs if t.get("is_preferred")), thumbs[0]["uri"])
    # adimages por url da erro #3 neste app: baixar e mandar o arquivo
    jpg = requests.get(uri).content
    img = requests.post(G + ACT + "/adimages", data={"access_token": TOKEN},
                        files={"thumb_3motivos.jpg": ("thumb_3motivos.jpg", jpg, "image/jpeg")}).json()
    if "error" in img:
        sys.exit(json.dumps(img["error"], ensure_ascii=False))
    thumb_hash = list(img["images"].values())[0]["hash"]
    print("thumb", thumb_hash)

    spec["video_data"]["video_id"] = vid
    spec["video_data"]["image_hash"] = thumb_hash
    cr = post(ACT + "/adcreatives", {
        "name": "LUNA 3 motivos v4 SET26",
        "object_story_spec": spec,
        "asset_feed_spec": feed,
        "degrees_of_freedom_spec": dof,
        **({"url_tags": UTM} if UTM else {}),
    })
    print("creative", cr["id"])

    for nome, adset in ADSETS.items():
        ad = post(ACT + "/ads", {"name": AD_NAME, "adset_id": adset,
                                 "creative": {"creative_id": cr["id"]}, "status": "PAUSED"})
        print("ad", nome, ad["id"])
        time.sleep(2)


if __name__ == "__main__":
    main()
