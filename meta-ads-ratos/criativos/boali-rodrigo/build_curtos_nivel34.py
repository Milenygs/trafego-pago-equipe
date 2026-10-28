#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Boali — AD23 curto (24s) e AD22 "28 milhoes" curto (24s) com CTA no conjunto nivel 3-4 da CP 10 (15/10/2026).

Pedido da Mileny: "vamos subir esses dois novos na campanha nova" (o "188 contratos" fica de fora ate chegar
o arquivo original do iPhone do Rodrigo).

  AD23: ad NOVO PAUSED com o video curto (o AD23 longo 120251751442780156 ja estava ATIVO, ligado pela Mileny).
        Mesma copy, mesma miniatura (1s: os 1,55s iniciais sao os do original).
  AD22: criativo novo + ad PAUSED. Miniatura do AD22 de VV (0,5s, cartela "Ele recusou R$28 milhoes"):
        o trecho inicial do curto e o mesmo do original.
Form 913523365113250, SIGN_UP, IA toda OPT_OUT, contextual_multi_ads OPT_OUT, sem url_tags (igual ao [NIVEL 4] AD20).

    python build_curtos_nivel34.py --dry
    python build_curtos_nivel34.py            # sobe videos, cria criativos, troca/cria ads PAUSED (retoma pelo JSON)
"""
import argparse
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(AQUI, "..", "boali-depoimento"))
import build_depoimento as base  # noqa: E402
from build_rodrigo_setembro import sobe_video_simples  # noqa: E402
import build_ad23_captacao as ad23  # noqa: E402

PASTA = os.path.join(os.path.expanduser("~"), "OneDrive", "Área de Trabalho", "CLAUDE CODE", "franquias", "boali",
                     "criativos para video viwes")
ESTADO = os.path.join(AQUI, "criados_2026-10-15_curtos.json")
VV = json.load(open(os.path.join(AQUI, "criados_2026-10-02_vv.json"), encoding="utf-8"))
AD23_ESTADO = json.load(open(os.path.join(AQUI, "criados_2026-10-15_ad23.json"), encoding="utf-8"))

NIVEL34 = ad23.NIVEL34
INVEST = "✅ Investimento a partir de R$359.000\n\n"

AD22_COPY = (
    "Ele recusou R$28 milhões para não perder o controle da empresa.\n\n"
    "O fundo exigia 80 lojas em 18 meses. Para o Rodrigo Barros, dono da Boali, esse ritmo não deixava "
    "espaço para manter a qualidade.\n\n"
    "Para quem vai investir, isso importa: a Boali cresce no ritmo em que consegue entregar, com os "
    "fundadores perto da operação e um time de suporte direto aos franqueados.\n\n"
    "✅ 19 anos de mercado\n"
    "✅ Suporte direto ao franqueado\n"
    + INVEST +
    "Se esse investimento faz sentido para o seu momento, fale com um consultor e veja se a sua região "
    "está disponível.\n"
    "👇"
)

PECAS = [
    {
        "chave": "AD23",
        "arquivo": "video rodrigo- vender franquia (curto 24s).mp4",
        "rotulo": "[NIVEL 4] AD23 [FUNDADOR] [VIDEO 24S] VENDER FRANQUIA E FACIL O DIFICIL E ENTREGAR",
        "thumb": VV["AD23"]["thumb"],
        "titulo": ad23.TITULO,
        "copy": ad23.COPY,
        # O AD23 longo (AD23_ESTADO["ad"]) foi ATIVADO pela Mileny em 15/10: nao trocar o criativo de ad
        # ativo (volta para revisao). O curto entra como ad novo PAUSED; ela decide qual fica.
        "ad_existente": None,
    },
    {
        "chave": "AD22",
        "arquivo": "ele recusou 28 milhoes (curto 24s).mp4",
        "rotulo": "[NIVEL 4] AD22 [MARCA] [VIDEO 24S] RECUSOU 28 MILHOES CAPITAL PACIENTE",
        "thumb": VV["AD22"]["thumb"],
        "titulo": "Capital paciente",
        "copy": AD22_COPY,
        "ad_existente": None,
    },
]


def carrega():
    if os.path.exists(ESTADO):
        with open(ESTADO, encoding="utf-8") as f:
            return json.load(f)
    return {}


def salva(estado):
    with open(ESTADO, "w", encoding="utf-8") as f:
        json.dump(estado, f, ensure_ascii=False, indent=2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    print("\nBoali — curtos no nivel 3-4 (%s)" % ("DRY" if a.dry else "cria PAUSED"))
    status, _ = ad23.le_conta()
    for p in PECAS:
        v = os.path.join(PASTA, p["arquivo"])
        print("\n  %s  %s (%.1f MB)  thumb %s" % (p["chave"], p["arquivo"], os.path.getsize(v) / 1048576, p["thumb"]))
        print("  título (%d/40): %s" % (len(p["titulo"]), p["titulo"]))
        print("  antes do 'ver mais': %r" % p["copy"][:125])
        if p["ad_existente"]:
            ad = base.get(p["ad_existente"], {"fields": "name,status,effective_status,creative{id}"})
            print("  ad existente %s  %s/%s  criativo atual %s" % (ad["id"], ad["status"], ad["effective_status"],
                                                                 ad["creative"]["id"]))
    if a.dry:
        print("\n  [dry] nada foi criado.")
        return
    if status != 1:
        sys.exit("conta com account_status %s: nao cria criativo" % status)

    estado = carrega()
    for p in PECAS:
        e = estado.setdefault(p["chave"], {})
        if not e.get("video_id"):
            e["video_id"] = sobe_video_simples(os.path.join(PASTA, p["arquivo"]))
            salva(estado)
        if not e.get("criativo"):
            e["criativo"] = base.post("%s/adcreatives" % base.CONTA, {
                "name": "Boali — %s [CAPTACAO]" % p["rotulo"],
                "object_story_spec": {
                    "page_id": base.PAGE,
                    "instagram_user_id": base.IG,
                    "video_data": {
                        "video_id": e["video_id"],
                        "image_hash": p["thumb"],
                        "title": p["titulo"],
                        "link_description": ad23.DESCRICAO,
                        "message": p["copy"],
                        "call_to_action": {"type": "SIGN_UP",
                                           "value": {"lead_gen_form_id": base.FORM, "link": "http://fb.me/"}},
                    },
                },
                "degrees_of_freedom_spec": base.SEM_IA,
                "contextual_multi_ads": {"enroll_status": "OPT_OUT"},
            }, "criativo %s curto" % p["chave"])
            if not e["criativo"]:
                sys.exit("parou no criativo %s" % p["chave"])
            salva(estado)
        if not e.get("ad"):
            if p["ad_existente"]:
                ok = base.post(p["ad_existente"], {"name": p["rotulo"], "creative": {"creative_id": e["criativo"]}},
                               "troca criativo do ad %s" % p["chave"])
                e["ad"] = p["ad_existente"] if ok else None
            else:
                e["ad"] = base.post("%s/ads" % base.CONTA, {
                    "name": p["rotulo"], "adset_id": NIVEL34,
                    "creative": {"creative_id": e["criativo"]}, "status": "PAUSED",
                }, "ad %s no nivel 3-4" % p["chave"])
            salva(estado)

    print("\n  RELEITURA")
    for p in PECAS:
        e = estado[p["chave"]]
        ad = base.get(e["ad"], {"fields": "name,status,effective_status,issues_info,preview_shareable_link,creative{id}"})
        cr = base.get(e["criativo"], {"fields": "object_story_spec,degrees_of_freedom_spec"})
        vd = cr["object_story_spec"]["video_data"]
        feats = cr.get("degrees_of_freedom_spec", {}).get("creative_features_spec", {})
        print("  %s  %s/%s  criativo=%s  issues=%s" % (ad["id"], ad["status"], ad["effective_status"],
                                                     ad["creative"]["id"], ad.get("issues_info", "-")))
        print("    %s" % ad["name"])
        print("    video=%s  form=%s  cta=%s  IA em OPT_IN: %s" % (
            vd.get("video_id"), vd["call_to_action"]["value"].get("lead_gen_form_id"), vd["call_to_action"]["type"],
            [k for k, v in feats.items() if v.get("enroll_status") == "OPT_IN"] or "nenhuma"))
        print("    preview: %s" % ad.get("preview_shareable_link"))


if __name__ == "__main__":
    main()
