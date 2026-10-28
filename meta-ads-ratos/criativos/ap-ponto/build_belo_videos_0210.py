"""Belo 02/10/2026 - 2 videos novos editados pela Mileny, so na campanha de LP, para testar contra o que deu bom no CV.

- "mulher com nova chamada" (mesma da Locucao campea) -> LAL Compradores + Remarketing 180D
- "Leo, obra e imagens em tela cheia" (Leo so qualificou no Interesse) -> Interesse 25-45
Miniatura propria em cada um (para nao ficarem iguais): mulher = rosto + "Conheca o Ponto Belo!" (0,3s);
Leo = render da piscina (25,5s). Transcricao conferida antes (faster_whisper small).
Copies da logica do Belo: abertura no gancho de cada video, facilidades em destaque, renda minima so junto de
"somar", sem subsidio, CTA igual ao do campeao ("Faca uma simulacao agora mesmo"). Anuncios PAUSED.
Uso: python build_belo_videos_0210.py [--dry]
"""
import json
import sys
import time
from pathlib import Path

import requests

AQUI = Path(__file__).parent
sys.path.insert(0, str(AQUI))
import build_belo_lancamento as lp  # noqa: E402

TOKEN, G, ACT, PAGE, IG = lp.TOKEN, lp.G, lp.ACT, lp.PAGE, lp.IG
PASTA = Path(lp.PASTA) / "criativos editados mileny"
CONJ = {"LAL": "120245790363030358", "RMKT": "120245790367990358", "INTERESSE": "120245790403680358"}

VIDEOS = {
    "VID Locucao Conheca v1": {"arquivo": "PONTO BELO — mulher com nova chamada (1).mp4",
                               "thumb": "thumb_mulher_conheca.jpg", "conjuntos": ["LAL", "RMKT"]},
    "VID UGC Leo Chegou v1": {"arquivo": "PONTO BELO — Leo, obra e imagens em tela cheia (2).mp4",
                              "thumb": "thumb_leo_piscina.jpg", "conjuntos": ["INTERESSE"]},
}

# titulos que estao no ar desde 28/09 (o lp.TITLES ainda tem "A 2 min do onibus...", trocado pelo CTA)
TITLES = ["2 quartos a partir de R$250 mil", "Entrada em até 60x com a construtora", "ITBI e registro por nossa conta",
          "Simule com a renda da sua família", "Faça uma simulação agora mesmo"]
FIM = "\n\n👇 Faça uma simulação agora mesmo.\n*Consulte condições."
RENDA = "Renda familiar mínima de R$5.001, e dá para somar com outras pessoas que vão morar com você."

ABERTURA = {
    "VID Locucao Conheca v1": (
        "Conheça o Ponto Belo: apartamentos na planta pelo Minha Casa Minha Vida, em Vespasiano.\n"
        "Seu primeiro apê pode estar mais perto do que você imagina. 🏡\n\n"
        "📍 Lançamento com unidades de 2 quartos a partir de R$250 mil\n"
        "💳 Entrada parcelada em até 60x direto com a construtora\n"
        "📄 Documentação gratuita: ITBI e registro por conta da AP Ponto\n"
        "🏊 Lazer completo no condomínio\n\n"
        + RENDA + "\n\nNão deixe a sua oportunidade passar."),
    "VID UGC Leo Chegou v1": (
        "O Ponto Belo acabou de chegar em Vespasiano.\n"
        "E pode ser a sua oportunidade de conquistar o seu apê. 🏡\n\n"
        "Apartamentos de 2 quartos a partir de R$250 mil, pelo Minha Casa Minha Vida.\n\n"
        "✅ Entrada parcelada em até 60x direto com a construtora\n"
        "✅ Você não paga documentação: ITBI e registro por conta da AP Ponto\n"
        "✅ Piscina, área gourmet, churrasqueira, salão de festas, quadra e minimercado\n\n"
        + RENDA + "\n\nAquele lugar para chegar no fim do dia e pensar: agora sim, conquistei o que é meu."),
}

# corpos 2 e 3: os mesmos da Locucao v2 / Leo v1 que estao no ar (CTA de simulacao desde 28/09)
V2 = """Quanto fica o seu apê no Ponto Belo?
Dá para ver agora, sem cadastro.

No simulador você informa a renda da família (mínimo de R$5.001, somando com outras pessoas) e vê os dois valores: a prestação da Caixa e a parcela da entrada com a AP Ponto.

📍 Lançamento no Santo Antônio, Vespasiano · 2 quartos a partir de R$250 mil
🚌 A 2 minutos do ônibus · a 15 de Confins
💳 Entrada em até 60x direto com a construtora
📄 ITBI e registro por conta da AP Ponto
🏊 Lazer completo no condomínio

O mesmo valor que você paga de aluguel já pode ser a parcela do que é seu."""
V3 = """"Minha renda sozinha não dá."
"Não tenho o dinheiro da entrada."
"E ainda tem ITBI e cartório."

No Ponto Belo, a AP Ponto resolve as três:
✔ Renda familiar mínima de R$5.001, e dá para somar com outras pessoas
✔ A entrada é parcelada em até 60x direto com a construtora
✔ ITBI e registro ficam por nossa conta: de R$10 mil a R$15 mil que ficam com você

"Parcelamos a entrada e hoje estamos pagando prestações que cabem no nosso bolso."
Amanda e Fabrício, clientes AP Ponto

17 anos de mercado. Aqui você fala direto com a construtora, sem corretor.

Lançamento em Vespasiano: 2 quartos a partir de R$250 mil, na Rua Afonso Pena, 685, a 2 minutos do ônibus."""


def bodies(ad_name):
    return [ABERTURA[ad_name] + FIM, V2 + FIM, V3 + FIM]


def get(p, **k):
    k["access_token"] = TOKEN
    return requests.get(G + p, params=k, timeout=90).json()


def post(path, data, files=None, fatal=True):
    data = {k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v) for k, v in data.items()}
    data["access_token"] = TOKEN
    r = requests.post(G + path, data=data, files=files, timeout=600).json()
    if "error" in r:
        e = r["error"]
        print(json.dumps({k: e.get(k) for k in ("code", "error_subcode", "error_user_title", "error_user_msg", "message")},
                         ensure_ascii=False, indent=1))
        if fatal:
            sys.exit(1)
    return r


def main():
    for n in VIDEOS:
        for b in bodies(n):
            low = b.lower()
            assert "até r$5 mil" not in low and "todas as faixas" not in low and "subsídio" not in low
            assert "5.001" in b and "soma" in b  # minimo sempre junto de somar/somando
    if "--dry" in sys.argv:
        for n in VIDEOS:
            print("=====", n, "\n" + bodies(n)[0], "\n")
        return

    for ad_name, v in VIDEOS.items():
        with open(PASTA / v["thumb"], "rb") as f:
            img = post(ACT + "/adimages", {}, files={"filename": (v["thumb"], f, "image/jpeg")})
        thumb_hash = list(img["images"].values())[0]["hash"]
        with open(PASTA / v["arquivo"], "rb") as f:  # envio simples (aprendizados 19/09)
            vid = post(ACT + "/advideos", {"name": ad_name.replace(" ", "_")},
                       files={"source": (v["arquivo"], f, "video/mp4")})["id"]
        for _ in range(60):
            if get(vid, fields="status").get("status", {}).get("video_status") == "ready":
                break
            time.sleep(10)
        print(ad_name, "| video", vid, "| miniatura", thumb_hash)
        cr = post(ACT + "/adcreatives", {
            "name": f"{ad_name} | BELO SET26 | CTA simulacao",
            "object_story_spec": {"page_id": PAGE, "instagram_user_id": IG,
                                  "video_data": {"video_id": vid, "image_hash": thumb_hash,
                                                 "call_to_action": {"type": "LEARN_MORE", "value": {"link": lp.LINK}}}},
            "asset_feed_spec": {"bodies": [{"text": b} for b in bodies(ad_name)],
                                "titles": [{"text": t} for t in TITLES],
                                "descriptions": [{"text": d} for d in lp.DESCRIPTIONS],
                                "optimization_type": "DEGREES_OF_FREEDOM"},
            "degrees_of_freedom_spec": {"creative_features_spec": {f: {"enroll_status": "OPT_OUT"} for f in lp.OPT_OUT}},
            "url_tags": lp.UTM})["id"]
        print("  criativo", cr)
        for c in v["conjuntos"]:
            ad = post(ACT + "/ads", {"name": ad_name, "adset_id": CONJ[c], "creative": {"creative_id": cr},
                                     "status": "PAUSED"}, fatal=False)
            print("    anuncio", c, ad.get("id"))
            time.sleep(3)


if __name__ == "__main__":
    main()
