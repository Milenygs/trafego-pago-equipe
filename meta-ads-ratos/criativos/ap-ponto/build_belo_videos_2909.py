"""Belo 28/09/2026 - videos 3 e 4 (UGC do engenheiro na obra) nas campanhas de LP (ativa) e de formulario (pausada).

Copies de conversao, logica do Belo: facilidades em destaque, minimo de renda so junto de "somar",
sem subsidio, texto nao promete nada que o video/LP nao diga. Abertura de cada video segue o gancho dele.
Anuncios PAUSED, 1 por video em cada conjunto (6 conjuntos).
Uso: python build_belo_videos_2909.py [--dry]
"""
import json
import subprocess
import sys
import time
from pathlib import Path

import requests

AQUI = Path(__file__).parent
sys.path.insert(0, str(AQUI))
import build_belo_lancamento as lp  # noqa: E402

TOKEN, G, ACT, PAGE, IG = lp.TOKEN, lp.G, lp.ACT, lp.PAGE, lp.IG
PASTA = Path(lp.PASTA) / "criativos 2909"
CAMP_LP, CAMP_FORM = "120245790359480358", "120245805859660358"
FORM_BELO = "2287635791803187"
VIDEOS = {"VID Engenheiro Sonho v1": PASTA / "ADS BELO 3.mp4",
          "VID Engenheiro Familia v1": PASTA / "ADS BELO 4.mp4"}

ABERTURA = {
    "VID Engenheiro Sonho v1": ("\"Um dia eu compro o meu apartamento.\"\nE se esse dia for agora?\n\n"
                                "O Ponto Belo acabou de chegar em Vespasiano: 2 quartos a partir de R$250 mil, "
                                "pelo Minha Casa Minha Vida."),
    "VID Engenheiro Familia v1": ("Comprar um apartamento é só uma compra?\nOu é o lugar onde a sua família vai "
                                  "construir as próximas histórias?\n\nO Ponto Belo é o lançamento da AP Ponto em "
                                  "Vespasiano: 2 quartos a partir de R$250 mil, pelo Minha Casa Minha Vida."),
}
CORPO_1 = """

✅ Entrada parcelada em até 60x direto com a construtora
✅ ITBI e registro por nossa conta: é um dinheiro que fica com você
✅ Piscina, área gourmet, churrasqueira, salão de festas, quadra e mini mercado

Renda familiar a partir de R$5.001, e dá para somar com outras pessoas que vão morar com você.
"""
V2 = """Lançamento é quando dá para escolher a sua unidade primeiro. 🏡

No Ponto Belo, em Vespasiano:
📍 2 quartos a partir de R$250 mil
💳 Entrada em até 60x direto com a construtora
📄 Você não paga ITBI nem registro
🏊 Piscina, área gourmet, salão de festas e quadra
🚌 A 2 minutos do ponto de ônibus

O mesmo valor que você paga de aluguel já pode ser a parcela do que é seu.
"""
V3 = """"Minha renda sozinha não dá."
"Não tenho o dinheiro da entrada."
"E ainda tem ITBI e cartório."

No Ponto Belo, a AP Ponto resolve as três:
✔ Renda familiar a partir de R$5.001, e dá para somar com outras pessoas
✔ A entrada é parcelada em até 60x direto com a construtora
✔ ITBI e registro ficam por nossa conta

"Parcelamos a entrada e hoje estamos pagando prestações que cabem no nosso bolso."
Amanda e Fabrício, clientes AP Ponto

17 anos de mercado. Aqui você fala direto com a construtora, sem corretor.
"""
CTA_TXT = {CAMP_LP: "👇 Toque em Saiba mais e simule o seu apê.\n*Consulte condições.",
           CAMP_FORM: "👇 Toque em Cadastre-se e receba a sua simulação.\n*Consulte condições."}


def bodies(ad_name, camp):
    fim = CTA_TXT[camp]
    return [ABERTURA[ad_name] + CORPO_1 + fim, V2 + fim, V3 + fim]


def get(p, **k):
    k["access_token"] = TOKEN
    return requests.get(G + p, params=k, timeout=90).json()


def post(path, data, fatal=True):
    data = {k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v) for k, v in data.items()}
    data["access_token"] = TOKEN
    r = requests.post(G + path, data=data, timeout=180).json()
    if "error" in r:
        e = r["error"]
        print(json.dumps({k: e.get(k) for k in ("code", "error_subcode", "error_user_title", "error_user_msg", "message")},
                         ensure_ascii=False, indent=1))
        if fatal:
            sys.exit(1)
    return r


def main():
    for n in VIDEOS:
        for c in (CAMP_LP, CAMP_FORM):
            for b in bodies(n, c):
                assert "até R$5 mil" not in b and "todas as faixas" not in b and "subsídio" not in b.lower()
    if "--dry" in sys.argv:
        for b in bodies("VID Engenheiro Sonho v1", CAMP_LP) + bodies("VID Engenheiro Familia v1", CAMP_FORM)[:1]:
            print(b, "\n-------")
        return

    conjuntos = {c: {s["name"]: s["id"] for s in get(c + "/adsets", fields="name")["data"]} for c in (CAMP_LP, CAMP_FORM)}
    print("conjuntos:", conjuntos)
    for ad_name, path in VIDEOS.items():
        out = subprocess.run([sys.executable, str(lp.SKILL / "scripts" / "create.py"), "video", "--account", ACT,
                              "--file", str(path), "--name", ad_name.replace(" ", "_")],
                             capture_output=True, text=True, encoding="utf-8")
        txt = out.stdout
        vid = json.loads(txt[txt.find("{"):txt.rfind("}") + 1])["id"]
        for _ in range(60):
            if get(vid, fields="status").get("status", {}).get("video_status") == "ready":
                break
            time.sleep(15)
        thumbs = get(vid + "/thumbnails", fields="uri,is_preferred").get("data", [])
        uri = next((t["uri"] for t in thumbs if t.get("is_preferred")), thumbs[0]["uri"])
        print(ad_name, "video", vid)
        for camp in (CAMP_LP, CAMP_FORM):
            if camp == CAMP_LP:
                cta = {"type": "LEARN_MORE", "value": {"link": lp.LINK}}
                extra = {"url_tags": lp.UTM}
            else:
                cta = {"type": "SIGN_UP", "value": {"lead_gen_form_id": FORM_BELO}}
                extra = {}
            cr = post(ACT + "/adcreatives", {
                "name": f"{ad_name} | BELO {'FORM ' if camp == CAMP_FORM else ''}SET26",
                "object_story_spec": {"page_id": PAGE, "instagram_user_id": IG,
                                      "video_data": {"video_id": vid, "image_url": uri, "call_to_action": cta}},
                "asset_feed_spec": {"bodies": [{"text": b} for b in bodies(ad_name, camp)],
                                    "titles": [{"text": t} for t in lp.TITLES],
                                    "descriptions": [{"text": d} for d in lp.DESCRIPTIONS],
                                    "optimization_type": "DEGREES_OF_FREEDOM"},
                "degrees_of_freedom_spec": {"creative_features_spec": {f: {"enroll_status": "OPT_OUT"} for f in lp.OPT_OUT}},
                **extra})["id"]
            print("  criativo", "LP" if camp == CAMP_LP else "FORM", cr)
            for sname, sid in conjuntos[camp].items():
                ad = post(ACT + "/ads", {"name": ad_name, "adset_id": sid, "creative": {"creative_id": cr},
                                         "status": "PAUSED"}, fatal=False)
                print("    anuncio", sname, ad.get("id"))
                time.sleep(3)


if __name__ == "__main__":
    main()
