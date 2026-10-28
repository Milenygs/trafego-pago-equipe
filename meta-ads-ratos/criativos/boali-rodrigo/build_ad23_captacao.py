#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Boali — AD23 "vender franquia e facil, o dificil e entregar" em versao de CAPTACAO (15/10/2026).

Pedido da Mileny: "poderia editar o AD23 em formato com CTA", para entrar no conjunto
nivel 3-4 da CP 10 no lugar dos videos que rodam la (AD20 Marcos e AD14 loja cheia).

O AD23 original (CP 03, ThruPlay) nao tem botao. Criativo e imutavel, entao sobe um criativo
novo com o MESMO video e a mesma miniatura (1s, rosto do Rodrigo) + formulario 913523365113250,
CTA SIGN_UP, IA toda OPT_OUT, e um ad PAUSED no conjunto nivel 3-4.
Copy sem numero financeiro (so o investimento R$359.000, que filtra).

    python build_ad23_captacao.py --dry      # le a conta e mostra a copy, nao cria
    python build_ad23_captacao.py            # cria criativo + ad PAUSED (retoma pelo JSON)
"""
import argparse
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "boali-depoimento"))
import build_depoimento as base  # noqa: E402

ESTADO = os.path.join(AQUI, "criados_2026-10-15_ad23.json")
VV = json.load(open(os.path.join(AQUI, "criados_2026-10-02_vv.json"), encoding="utf-8"))["AD23"]

NIVEL34 = "120251732899150156"          # [NIVEL 3-4] [VIDEOS FUNIL ESPIRAL 75% + ABRIU FORM] [FORMS] 30-55
REFERENCIA = "1450917803590212"         # criativo do [NIVEL 4] AD20 no mesmo conjunto (url_tags)

ROTULO = "[NIVEL 4] AD23 [FUNDADOR] [VIDEO] VENDER FRANQUIA E FACIL O DIFICIL E ENTREGAR"
TITULO = "O difícil é entregar"
DESCRICAO = "A partir de R$359 mil"

COPY = (
    "Vender franquia é fácil. O difícil é entregar.\n\n"
    "Se você está comparando franquias, faça a pergunta que quase ninguém faz: "
    "quem vai abastecer a sua loja?\n\n"
    "Na Boali, a rede padroniza a própria comida. É o que garante o mesmo prato, o mesmo "
    "padrão e o mesmo preço em 25 estados, com uma estrutura que continua atendendo depois "
    "da assinatura. Quem explica é o Rodrigo, dono da Boali.\n\n"
    "✅ 19 anos de mercado\n"
    "✅ Operação padronizada pela própria rede\n"
    "✅ Investimento a partir de R$359.000\n\n"
    "Se esse investimento faz sentido para o seu momento, fale com um consultor e veja se "
    "a sua região está disponível.\n"
    "👇"
)


def carrega():
    if os.path.exists(ESTADO):
        with open(ESTADO, encoding="utf-8") as f:
            return json.load(f)
    return {}


def salva(estado):
    with open(ESTADO, "w", encoding="utf-8") as f:
        json.dump(estado, f, ensure_ascii=False, indent=2)


def le_conta():
    c = base.get(base.CONTA, {"fields": "account_status,balance,currency"})
    print("  conta: account_status=%s  balance=R$%.2f" % (c["account_status"], int(c["balance"]) / 100))
    a = base.get(NIVEL34, {"fields": "name,status,effective_status,daily_budget"})
    print("  conjunto %s  %s/%s  R$%.0f/dia  %s" % (NIVEL34, a["status"], a["effective_status"],
                                                 int(a["daily_budget"]) / 100, a["name"]))
    for ad in base.get("%s/ads" % NIVEL34, {"fields": "name,status,effective_status", "limit": 50})["data"]:
        print("    %-9s %-16s %s" % (ad["status"], ad["effective_status"], ad["name"]))
    ref = base.get(REFERENCIA, {"fields": "url_tags"})
    return c["account_status"], ref.get("url_tags")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    print("\nBoali — AD23 captacao (%s)" % ("DRY" if a.dry else "cria PAUSED"))
    print("  video %s · miniatura %s" % (VV["video_id"], VV["thumb"]))
    print("  título (%d/40): %s · descrição (%d/30): %s" % (len(TITULO), TITULO, len(DESCRICAO), DESCRICAO))
    print("  antes do 'ver mais' (125): %r" % COPY[:125])
    status, url_tags = le_conta()
    print("  url_tags da referência: %r" % url_tags)
    if a.dry:
        print("\n%s\n\n  [dry] nada foi criado." % COPY)
        return
    if status != 1:
        sys.exit("conta com account_status %s: nao cria criativo (subcode 1487194)" % status)

    estado = carrega()
    if not estado.get("criativo"):
        params = {
            "name": "Boali — %s [CAPTACAO]" % ROTULO,
            "object_story_spec": {
                "page_id": base.PAGE,
                "instagram_user_id": base.IG,
                "video_data": {
                    "video_id": VV["video_id"],
                    "image_hash": VV["thumb"],
                    "title": TITULO,
                    "link_description": DESCRICAO,
                    "message": COPY,
                    "call_to_action": {"type": "SIGN_UP",
                                       "value": {"lead_gen_form_id": base.FORM, "link": "http://fb.me/"}},
                },
            },
            "degrees_of_freedom_spec": base.SEM_IA,
            "contextual_multi_ads": {"enroll_status": "OPT_OUT"},
        }
        if url_tags:
            params["url_tags"] = url_tags
        estado["criativo"] = base.post("%s/adcreatives" % base.CONTA, params, "criativo AD23 captacao")
        if not estado["criativo"]:
            sys.exit("parou no criativo")
        salva(estado)
    if not estado.get("ad"):
        estado["ad"] = base.post("%s/ads" % base.CONTA, {
            "name": ROTULO, "adset_id": NIVEL34,
            "creative": {"creative_id": estado["criativo"]}, "status": "PAUSED",
        }, "ad AD23 no nivel 3-4")
        salva(estado)

    print("\n  RELEITURA")
    ad = base.get(estado["ad"], {"fields": "name,status,effective_status,issues_info,preview_shareable_link"})
    print("  %s  %s/%s  issues=%s" % (ad["id"], ad["status"], ad["effective_status"], ad.get("issues_info", "-")))
    print("  preview: %s" % ad.get("preview_shareable_link"))
    cr = base.get(estado["criativo"], {"fields": "object_story_spec,degrees_of_freedom_spec,url_tags"})
    vd = cr["object_story_spec"]["video_data"]
    print("  form=%s  cta=%s  url_tags=%r" % (vd["call_to_action"]["value"].get("lead_gen_form_id"),
                                            vd["call_to_action"]["type"], cr.get("url_tags")))
    feats = cr.get("degrees_of_freedom_spec", {}).get("creative_features_spec", {})
    print("  IA em OPT_IN: %s" % ([k for k, v in feats.items() if v.get("enroll_status") == "OPT_IN"] or "nenhuma"))


if __name__ == "__main__":
    main()
