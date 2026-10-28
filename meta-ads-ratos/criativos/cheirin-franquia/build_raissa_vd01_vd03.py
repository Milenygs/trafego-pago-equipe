#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cheirin Bao MT — 3 anuncios da Raissa no conjunto VD02 com o nome-chave do CRM (03/10/2026).

Mileny: "podemos colocar VD01, VD02 e VD03 e manter o nome" / "nome franqueada_raissa".
O CRM leva para o funil Franqueados o lead cujo anuncio tem "franqueada_raissa" no nome.

  VD01 - franqueada_raissa = anuncio antigo 120257017816030212 (era "VD02 - Franqueada - Raissa"), so renomeado
  VD02 - franqueada_raissa = gancho novo (vinha do Franqueados Geo, anuncio 120257017781570212): criativo REFEITO
                             limpo — mesmo video 3564667067026446, mesma capa e mesma copy, mas SIGN_UP
                             (o original era LEARN_MORE) e os 83 recursos de IA em OPT_OUT (o original tinha
                             video_auto_crop, video_filtering e video_uncrop ligados)
  VD03 - franqueada_raissa = corte curto 120258143483510212 (era "Franqueada- raissa"), so renomeado
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_outubro_depoimentos as b  # noqa: E402

VD02_SET = "120257017816020212"
ANTIGO = "120257017816030212"
CURTO = "120258143483510212"
ORIGEM = "1783054749279413"   # criativo do gancho novo (VD08)


def main():
    m = b.modelo()
    o = b.get(ORIGEM, {"fields": "object_story_spec"})["object_story_spec"]["video_data"]
    cta = {"type": "SIGN_UP", "value": {"lead_gen_form_id": "2805248149848936",
                                        "link": o["call_to_action"]["value"].get("link") or "http://fb.me/"}}
    story = {"page_id": m["page_id"], "instagram_user_id": m["instagram_user_id"],
             "video_data": {"video_id": o["video_id"], "image_hash": o["image_hash"], "title": o["title"],
                            "message": o["message"], "call_to_action": cta}}
    cr = b.post("%s/adcreatives" % b.CONTA, {"name": "Cheirin — VD02 - franqueada_raissa (gancho novo, limpo)",
                                             "object_story_spec": story,
                                             "degrees_of_freedom_spec": m["dof"]}, "criativo gancho novo (limpo)")
    time.sleep(2)
    novo = b.post("%s/ads" % b.CONTA, {"name": "VD02 - franqueada_raissa", "adset_id": VD02_SET,
                                       "creative": {"creative_id": cr}, "status": "PAUSED"},
                  "anuncio VD02 - franqueada_raissa (PAUSED)")
    time.sleep(2)
    b.post(ANTIGO, {"name": "VD01 - franqueada_raissa"}, "renomeado antigo -> VD01 - franqueada_raissa")
    time.sleep(2)
    b.post(CURTO, {"name": "VD03 - franqueada_raissa"}, "renomeado corte curto -> VD03 - franqueada_raissa")
    time.sleep(2)
    b.post(novo, {"status": "ACTIVE"}, "ativado VD02 - franqueada_raissa")
    print(json.dumps({"criativo": cr, "anuncio_vd02": novo}))


if __name__ == "__main__":
    main()
