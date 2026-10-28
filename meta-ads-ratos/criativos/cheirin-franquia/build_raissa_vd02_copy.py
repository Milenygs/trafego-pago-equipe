#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cheirin Bao MT — copy personalizada no VD02 - franqueada_raissa (gancho novo), 04/10/2026.

Mileny: "queria uma copy personalizada ao anuncio". O VD02 rodava com a copy generica herdada do criativo antigo
("Nao acredite so em mim… Mais de 1.000 franquias…"), que nao fala da Raissa nem filtra pelo investimento.
O video (15s) diz: "Voce esta procurando um modelo de negocio para investir? Eu sou Raissa, franqueada da Cheirin Bao
desde 2023, com 3 operacoes, duas no Rio de Janeiro e uma em Sao Paulo. Clique aqui no link que eu mesma irei
explicar melhor sobre a marca." -> angulo A04 (quem entra, expande).
Criativo novo com o mesmo video, a mesma capa e o mesmo formulario; o anuncio continua com o mesmo ID e ATIVO
(troca de criativo = volta para revisao). Criativo antigo guardado para reverter: 4059390357700249.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_outubro_depoimentos as b  # noqa: E402

AD = "120258144319940212"
CRIATIVO_ANTIGO = "4059390357700249"
COPY = (
    "Em 2023, a Raissa abriu a primeira Cheirin Bão. Hoje são três operações: duas no Rio de Janeiro e uma em "
    "São Paulo.\n\n"
    "Se você está procurando um modelo de negócio para investir, ninguém explica melhor do que quem já está "
    "dentro da rede.\n\n"
    "Clique e fale direto com a Raissa.\n\n" + b.FIM)


def main():
    if "--dry" in sys.argv:
        print(COPY)
        return
    m = b.modelo()
    o = b.get(CRIATIVO_ANTIGO, {"fields": "object_story_spec"})["object_story_spec"]["video_data"]
    story = {"page_id": m["page_id"], "instagram_user_id": m["instagram_user_id"],
             "video_data": {"video_id": o["video_id"], "image_hash": o["image_hash"], "title": m["title"],
                            "link_description": m["link_description"], "message": COPY,
                            "call_to_action": o["call_to_action"]}}
    cr = b.post("%s/adcreatives" % b.CONTA, {"name": "Cheirin — VD02 - franqueada_raissa (gancho novo, copy Raissa 3 operacoes)",
                                             "object_story_spec": story,
                                             "degrees_of_freedom_spec": m["dof"]}, "criativo VD02 copy personalizada")
    b.post(AD, {"creative": {"creative_id": cr}}, "VD02 - franqueada_raissa -> criativo novo")
    d = b.get(AD, {"fields": "name,status,effective_status,creative{id,object_story_spec,degrees_of_freedom_spec}"})
    vd = d["creative"]["object_story_spec"]["video_data"]
    feats = d["creative"].get("degrees_of_freedom_spec", {}).get("creative_features_spec", {})
    print(json.dumps({"anuncio": AD, "status": d["status"], "effective_status": d["effective_status"],
                      "criativo": d["creative"]["id"], "cta": vd["call_to_action"]["type"],
                      "form": vd["call_to_action"]["value"].get("lead_gen_form_id"),
                      "ia_ligada": [k for k, x in feats.items() if x.get("enroll_status") != "OPT_OUT"],
                      "recursos": len(feats)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
