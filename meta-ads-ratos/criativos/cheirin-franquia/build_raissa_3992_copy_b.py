#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cheirin Bao MT — VD08 - franqueada_raissa: mesmo video da VD04 (EDIT D, sem musica) com a copy B, PAUSED (04/10/2026).

Mileny: "queria testar uma copy diferente tb — algo sobre negocio rentavel, recorrencia".
Desenho do teste no VD02 Raissa (VD04 e o controle; cada anuncio muda uma coisa so):
  VD04 = D sem musica + copy A (recorrencia) · VD07 = D com musica + copy A · VD08 = D sem musica + copy B
Copy B: "rentavel" como caracteristica de negocio com cliente que volta (angulo A02), sem numero e sem promessa;
mesmo titulo e descricao do modelo. Reaproveita o video e a capa ja enviados para a VD04.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_outubro_depoimentos as b  # noqa: E402
from build_raissa_3992 import ADSET  # noqa: E402

NOME = "VD08 - franqueada_raissa"
VIDEO_VD04 = "2154306735459096"
THUMB_VD04 = "dfe14f3d0e79a5f7ca4aebd1f1b379a8"
COPY_B = (
    "Todo negócio rentável tem uma coisa em comum: o cliente volta.\n\n"
    "Café é hábito de todo dia. O cliente toma hoje e volta amanhã, com crise ou sem crise. Foi essa recorrência "
    "que fez a Raissa escolher a Cheirin Bão para ter a própria cafeteria.\n\n"
    "Quer entender como funciona esse modelo de negócio? Clique e fale com a gente.\n\n" + b.FIM)


def main():
    if "--dry" in sys.argv:
        print(COPY_B)
        return
    m = b.modelo()
    story = {"page_id": m["page_id"], "instagram_user_id": m["instagram_user_id"],
             "video_data": {"video_id": VIDEO_VD04, "image_hash": THUMB_VD04, "title": m["title"],
                            "link_description": m["link_description"], "message": COPY_B,
                            "call_to_action": m["cta"]}}
    cr = b.post("%s/adcreatives" % b.CONTA, {"name": "Cheirin — %s (3992 D, copy B rentavel/recorrencia)" % NOME,
                                             "object_story_spec": story,
                                             "degrees_of_freedom_spec": m["dof"]}, "criativo " + NOME)
    time.sleep(40)   # #613: a VD07 acabou de entrar no mesmo conjunto
    ad = b.post("%s/ads" % b.CONTA, {"name": NOME, "adset_id": ADSET, "creative": {"creative_id": cr},
                                     "status": "PAUSED"}, "anuncio %s (PAUSED)" % NOME)
    print(json.dumps({NOME: {"criativo": cr, "anuncio": ad}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
