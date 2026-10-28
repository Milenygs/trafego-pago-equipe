"""Belo 26/10/2026 - video Leo 3 Motivos (o mesmo do Direct novo) nas campanhas de LP e de Formulario.

LP: conjunto Servidores (melhor R$/Simulacao+ do CV, R$345). Form: LAL Compradores RMBH | Leads Qualificados (QUALITY_LEAD).
Copia os criativos do Leo v1 (LP) e do Engenheiro Sonho v2 (Form): link, UTM dinamica, form TEL, titulos e descricoes.
Troca o video e o 1o corpo de texto (agora o dos 3 motivos); os outros 2 corpos aprovados ficam. Anuncios PAUSED.
Uso: python build_belo_3motivos_lp_form_2610.py
"""
import sys
import time
from pathlib import Path

AQUI = Path(__file__).parent
sys.path.insert(0, str(AQUI))
import build_belo_lancamento as lp  # noqa: E402

ACT, PAGE, IG = lp.ACT, lp.PAGE, lp.IG
VIDEO = "1519046376749269"  # v1.mp4, subido em 26/10 para o Direct novo
ANUNCIO = "VID UGC Leo 3 Motivos v1"  # = utm_content: nao renomear

CORPO = """Você ainda paga aluguel em Vespasiano? Presta atenção nesses 3 motivos para conhecer o Ponto Belo:

1️⃣ A entrada é parcelada em até 60x direto com a construtora
2️⃣ A documentação do imóvel é 100% gratuita: ITBI e registro por conta da AP Ponto
3️⃣ Dá para juntar renda com quem vai morar com você (renda familiar mínima de R$5.000)

Apartamentos de 2 quartos a partir de R$250 mil, a 15 minutos do Shopping Estação.

{cta}
*Consulte condições."""

DESTINOS = {
    "LP / Servidores": {"adset": "120246003834740358", "modelo": "1803407947338068",
                        "cta": "👇 Faça uma simulação agora mesmo."},
    "Form / Leads Qualificados": {"adset": "120245933397060358", "modelo": "963624940133967",
                                  "cta": "👇 Toque em Cadastre-se e receba a sua simulação."},
    # 26/10 (Mileny: "testar em todos os publicos"): os outros conjuntos ativos; o Remarketing segue pausado
    "LP / LAL Compradores": {"adset": "120245790363030358", "modelo": "1803407947338068",
                             "cta": "👇 Faça uma simulação agora mesmo."},
    "LP / Interesse": {"adset": "120245790403680358", "modelo": "1803407947338068",
                       "cta": "👇 Faça uma simulação agora mesmo."},
    "Form / LAL Qualificados CAPI": {"adset": "120245854126000358", "modelo": "963624940133967",
                                     "cta": "👇 Toque em Cadastre-se e receba a sua simulação."},
}


def main():
    h = lp.thumb(VIDEO, "BELO_LEO_3MOTIVOS")
    criados = []
    for nome, d in DESTINOS.items():
        if ANUNCIO in {a["name"] for a in lp.get(d["adset"] + "/ads", fields="name", limit=50).get("data", [])}:
            print(nome, "ja tem o anuncio - pulando")
            continue
        m = lp.get(d["modelo"], fields="url_tags,object_story_spec,asset_feed_spec")
        vd = m["object_story_spec"]["video_data"]
        afs = m["asset_feed_spec"]
        bodies = [{"text": CORPO.format(cta=d["cta"])}] + [{"text": b["text"]} for b in afs["bodies"][1:]]
        dados = {
            "name": f"{ANUNCIO} | BELO OUT26 | {nome}",
            "object_story_spec": {"page_id": PAGE, "instagram_user_id": IG,
                                  "video_data": {"video_id": VIDEO, "image_hash": h, "call_to_action": vd["call_to_action"]}},
            "asset_feed_spec": {"bodies": bodies,
                                "titles": [{"text": t["text"]} for t in afs["titles"]],
                                "descriptions": [{"text": t["text"]} for t in afs["descriptions"]],
                                "optimization_type": "DEGREES_OF_FREEDOM"},
            "degrees_of_freedom_spec": {"creative_features_spec": {f: {"enroll_status": "OPT_OUT"} for f in lp.OPT_OUT}},
        }
        if m.get("url_tags"):
            dados["url_tags"] = m["url_tags"]
        cr = lp.post(ACT + "/adcreatives", dados)["id"]
        ad = lp.post(ACT + "/ads", {"name": ANUNCIO, "adset_id": d["adset"], "creative": {"creative_id": cr},
                                    "status": "PAUSED"})["id"]
        print(nome, "| criativo", cr, "| anuncio", ad)
        criados.append((nome, ad, cr))
        time.sleep(2)

    # validacao: destino, UTM, video, recursos de IA e status
    for nome, ad, cr in criados:
        c = lp.get(cr, fields="url_tags,object_story_spec,asset_feed_spec,degrees_of_freedom_spec")
        v = c["object_story_spec"]["video_data"]
        spec = c.get("degrees_of_freedom_spec", {}).get("creative_features_spec", {})
        print(nome, "| video", v["video_id"], "| CTA", v["call_to_action"], "| UTM", c.get("url_tags"),
              "| corpos", len(c["asset_feed_spec"]["bodies"]), "| IA OPT_OUT",
              sum(1 for x in spec.values() if x.get("enroll_status") == "OPT_OUT"), "de", len(spec))
        print("  ", lp.get(ad, fields="name,adset{name},status,effective_status"))


if __name__ == "__main__":
    main()
