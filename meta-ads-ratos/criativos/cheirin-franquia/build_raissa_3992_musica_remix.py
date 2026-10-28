#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cheirin Bao MT — VD07 - franqueada_raissa passa a usar o REMIX (musica 16 dB abaixo da voz, 1080x1920), 04/10/2026.

Mileny: "nao consegue arrumar a musica pra mim?". Na edicao dela a musica ficava ~2-3 dB abaixo da voz e cobria a fala
no trecho em pe; o remix (remix_raissa_3992_musica.py) separa a musica por subtracao da EDIT D e a devolve 16 dB
abaixo da voz. O video do remix e o da EDIT D copiado sem recodificar, entao a capa e a mesma da VD04.
Troca so o criativo do anuncio (continua PAUSED); o criativo anterior (musica alta) fica para reverter: 1429813575943696.
"""
import json
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_outubro_depoimentos as b  # noqa: E402
from build_raissa_3992 import COPY, PASTA  # noqa: E402
from build_raissa_3992_copy_b import THUMB_VD04  # noqa: E402

AD_VD07 = "120258161910470212"
# uso: build_raissa_3992_musica_remix.py [baixa|media|forte]. 04/10: "baixa" (16 dB) primeiro; a Mileny achou baixa demais
# (aparecia o ruido das pessoas na loja) e escolheu a "media" (9 dB abaixo da voz).
NIVEL = sys.argv[1] if len(sys.argv) > 1 else "baixa"
REMIX = "Cheirin Bao - Raissa - 3992 EDIT D musica %s (remix).mp4" % NIVEL


def main():
    m = b.modelo()
    mp4 = os.path.join(tempfile.gettempdir(), "VD07 - franqueada_raissa - 3992 D musica %s.mp4" % NIVEL)
    shutil.copyfile(os.path.join(PASTA, REMIX), mp4)   # nome limpo na biblioteca da conta
    vid = b.sobe_video(mp4)
    story = {"page_id": m["page_id"], "instagram_user_id": m["instagram_user_id"],
             "video_data": {"video_id": vid, "image_hash": THUMB_VD04, "title": m["title"],
                            "link_description": m["link_description"], "message": COPY,
                            "call_to_action": m["cta"]}}
    cr = b.post("%s/adcreatives" % b.CONTA, {"name": "Cheirin — VD07 - franqueada_raissa (3992 D, musica %s 1080p)" % NIVEL,
                                             "object_story_spec": story,
                                             "degrees_of_freedom_spec": m["dof"]}, "criativo VD07 remix")
    b.post(AD_VD07, {"creative": {"creative_id": cr}}, "VD07 - franqueada_raissa -> remix")
    d = b.get(AD_VD07, {"fields": "name,status,effective_status,creative{id,object_story_spec,degrees_of_freedom_spec}"})
    vd = d["creative"]["object_story_spec"]["video_data"]
    feats = d["creative"].get("degrees_of_freedom_spec", {}).get("creative_features_spec", {})
    print(json.dumps({"anuncio": d["name"], "status": d["status"], "effective_status": d["effective_status"],
                      "criativo": d["creative"]["id"], "video": vd["video_id"], "cta": vd["call_to_action"]["type"],
                      "form": vd["call_to_action"]["value"].get("lead_gen_form_id"),
                      "ia_ligada": [k for k, x in feats.items() if x.get("enroll_status") != "OPT_OUT"],
                      "recursos": len(feats)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
