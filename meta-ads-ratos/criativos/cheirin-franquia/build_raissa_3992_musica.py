#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cheirin Bao MT — VD07 - franqueada_raissa: EDIT D com musica (edicao trazida pela Mileny), VD02 Raissa, PAUSED (04/10/2026).

Mileny: "coloquei na pasta uma edicao com musica do mesmo criativo, vamos testar subindo ele".
Teste: VD04 (sem musica) x VD07 (com musica): mesma abertura ("E e por isso que eu escolhi…"), mesma copy, entao a
variavel e so a musica. O nome VD06 ficou de fora porque o conjunto ja tem um "VD06 - FRANQUEADA RAISSA - GANCHO2
CONHECER" antigo (pausado). O nome tem "franqueada_raissa" (rota do CRM para o funil Franqueados).
"""
import json
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_outubro_depoimentos as b  # noqa: E402
from build_raissa_3992 import ADSET, COPY, PASTA  # noqa: E402

NOME = "VD07 - franqueada_raissa"
ARQUIVO = "raissa franqueada edição musica  3992.mp4"
THUMB_SEG = 3.0


def main():
    m = b.modelo()
    mp4 = os.path.join(tempfile.gettempdir(), "%s - 3992 D com musica.mp4" % NOME)
    shutil.copyfile(os.path.join(PASTA, ARQUIVO), mp4)   # nome limpo na biblioteca da conta
    vid = b.sobe_video(mp4)
    thumb = b.sobe_thumb(mp4, THUMB_SEG)
    story = {"page_id": m["page_id"], "instagram_user_id": m["instagram_user_id"],
             "video_data": {"video_id": vid, "image_hash": thumb, "title": m["title"],
                            "link_description": m["link_description"], "message": COPY,
                            "call_to_action": m["cta"]}}
    cr = b.post("%s/adcreatives" % b.CONTA, {"name": "Cheirin — %s (3992 D com musica)" % NOME,
                                             "object_story_spec": story,
                                             "degrees_of_freedom_spec": m["dof"]}, "criativo " + NOME)
    ad = b.post("%s/ads" % b.CONTA, {"name": NOME, "adset_id": ADSET, "creative": {"creative_id": cr},
                                     "status": "PAUSED"}, "anuncio %s (PAUSED)" % NOME)
    print(json.dumps({NOME: {"video": vid, "thumb": thumb, "criativo": cr, "anuncio": ad}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
