#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cheirin Bao MT — video 3992 da Raissa no conjunto VD02 Raissa, nas duas versoes de gancho (04/10/2026).

Mileny: "deixa sem musica mesmo" / "se puder deixar as duas versoes salvas". As duas sobem PAUSED; ela ativa.
  VD04 - franqueada_raissa = EDIT D, abre com a frase toda "E e por isso que eu escolhi a Cheirin Bao…" (a que ela
                             e o Eduardo preferiram; a abertura da C pareceu corrida)
  VD05 - franqueada_raissa = EDIT C, abre em "Eu escolhi a Cheirin Bao…"
O nome tem "franqueada_raissa" porque o CRM usa o nome do anuncio para mandar o lead ao funil Franqueados.
Mesma copy nas duas (angulo A02, recorrencia), entao o que muda entre elas e so o gancho.
Blueprint do criativo: o do build_outubro_depoimentos (modelo DRE 146k: form, SIGN_UP, recursos de IA em OPT_OUT).
"""
import json
import os
import shutil
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_outubro_depoimentos as b  # noqa: E402

ADSET = "120257017816020212"   # VD02 Raissa, campanha ✅05 [FORM] [FRANQUEADOS]
PASTA = os.path.expandvars(r"%USERPROFILE%\OneDrive\Área de Trabalho\CLAUDE CODE\franquias\cheirin bao"
                           r"\criativos campanha outubro")
PECAS = [
    {"nome": "VD04 - franqueada_raissa", "rotulo": "3992 D, frase toda",
     "arquivo": "Cheirin Bao - Raissa - 3992 EDIT D e por isso (Eduardo).mp4", "thumb": 3.0},
    {"nome": "VD05 - franqueada_raissa", "rotulo": "3992 C, eu escolhi",
     "arquivo": "Cheirin Bao - Raissa - 3992 EDIT C eu escolhi.mp4", "thumb": 2.4},
]
COPY = (
    "“Tá em crise ou não, o brasileiro toma café.”\n\n"
    "Foi por isso que a Raissa, franqueada, escolheu a Cheirin Bão. Café é hábito de todo dia: o cliente toma "
    "hoje e volta amanhã. E, como ela diz, negócio bom é negócio de recorrência.\n\n"
    "Quer entender como funciona esse modelo de negócio? Clique e fale com a gente.\n\n" + b.FIM)


def main():
    if "--dry" in sys.argv:
        print(COPY)
        return
    m = b.modelo()
    s = b.get(ADSET, {"fields": "name,status,campaign{name}"})
    print("Conjunto: %s (%s) | campanha %s | form %s | %d recursos OPT_OUT"
          % (s["name"], s["status"], s["campaign"]["name"], m["cta"]["value"]["lead_gen_form_id"],
             len(m["dof"]["creative_features_spec"])))
    saida = {}
    for i, p in enumerate(PECAS):
        mp4 = os.path.join(tempfile.gettempdir(), "%s - %s.mp4" % (p["nome"], p["rotulo"]))
        shutil.copyfile(os.path.join(PASTA, p["arquivo"]), mp4)   # nome limpo na biblioteca da conta
        vid = b.sobe_video(mp4)
        thumb = b.sobe_thumb(mp4, p["thumb"])
        story = {"page_id": m["page_id"], "instagram_user_id": m["instagram_user_id"],
                 "video_data": {"video_id": vid, "image_hash": thumb, "title": m["title"],
                                "link_description": m["link_description"], "message": COPY,
                                "call_to_action": m["cta"]}}
        cr = b.post("%s/adcreatives" % b.CONTA, {"name": "Cheirin — %s (%s)" % (p["nome"], p["rotulo"]),
                                                 "object_story_spec": story,
                                                 "degrees_of_freedom_spec": m["dof"]}, "criativo " + p["nome"])
        if i:
            time.sleep(40)   # #613: escrita seguida no mesmo conjunto
        ad = b.post("%s/ads" % b.CONTA, {"name": p["nome"], "adset_id": ADSET, "creative": {"creative_id": cr},
                                         "status": "PAUSED"}, "anuncio %s (PAUSED)" % p["nome"])
        saida[p["nome"]] = {"video": vid, "thumb": thumb, "criativo": cr, "anuncio": ad}
    print(json.dumps(saida, ensure_ascii=False))


if __name__ == "__main__":
    main()
