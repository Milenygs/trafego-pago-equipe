#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cheirin Bao MT — VD09 - franqueada_raissa: "Alexandre e Raissa" com o gancho invertido, no VD02 Raissa (05/10/2026).

Mileny: "gostei muito dele, onde podemos colocar?" -> conjunto da Raissa na ✅05 (depoimento dela; o nome-chave manda o
lead ao funil Franqueados; CRM de 30d: depoimento na ✅05 qualifica ~13%, Quente 3,8%) -> "pode subir e ativar entao".
Sobe PAUSED e e ativado em seguida (ok explicito). O teste do 3992 (VD04/VD07/VD08) fica pausado ate a leitura de 10/10,
para o conjunto (R$160) nao dividir a verba entre 7 anuncios.
"""
import json
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_outubro_depoimentos as b  # noqa: E402
from otimiza_0510 import tenta  # noqa: E402

ADSET = "120257017816020212"
NOME = "VD09 - franqueada_raissa"
PASTA = os.path.expandvars(r"%USERPROFILE%\OneDrive\Área de Trabalho\CLAUDE CODE\franquias\cheirin bao"
                           r"\criativos campanha outubro")
ARQUIVO = "Cheirin Bao - Alexandre e Raissa - gancho escolhemos.mp4"
THUMB_SEG = 0.5
COPY = (
    "Por que o Alexandre e a Raissa escolheram a Cheirin Bão?\n\n"
    "No vídeo, eles respondem e contam o faturamento que levou a loja deles à premiação da rede. Hoje, já estão a "
    "caminho da segunda e da terceira loja.\n\n"
    "Clique e fale direto com a Raissa.\n\n" + b.FIM)


def main():
    if "--dry" in sys.argv:
        print(COPY)
        return
    m = b.modelo()
    mp4 = os.path.join(tempfile.gettempdir(), "%s - Alexandre e Raissa gancho escolhemos.mp4" % NOME)
    shutil.copyfile(os.path.join(PASTA, ARQUIVO), mp4)   # nome limpo na biblioteca da conta
    vid = b.sobe_video(mp4)
    thumb = b.sobe_thumb(mp4, THUMB_SEG)
    story = {"page_id": m["page_id"], "instagram_user_id": m["instagram_user_id"],
             "video_data": {"video_id": vid, "image_hash": thumb, "title": m["title"],
                            "link_description": m["link_description"], "message": COPY,
                            "call_to_action": m["cta"]}}
    cr = b.post("%s/adcreatives" % b.CONTA, {"name": "Cheirin — %s (Alexandre e Raissa, gancho escolhemos)" % NOME,
                                             "object_story_spec": story,
                                             "degrees_of_freedom_spec": m["dof"]}, "criativo " + NOME)
    ad = b.post("%s/ads" % b.CONTA, {"name": NOME, "adset_id": ADSET, "creative": {"creative_id": cr},
                                     "status": "PAUSED"}, "anuncio %s (PAUSED)" % NOME)
    tenta(ad, {"status": "ACTIVE"}, "%s ATIVADO (ok da Mileny)" % NOME)
    d = b.get(ad, {"fields": "name,status,effective_status,creative{object_story_spec,degrees_of_freedom_spec}"})
    vd = d["creative"]["object_story_spec"]["video_data"]
    feats = d["creative"].get("degrees_of_freedom_spec", {}).get("creative_features_spec", {})
    print(json.dumps({"anuncio": ad, "nome": d["name"], "status": d["status"], "effective_status": d["effective_status"],
                      "video": vid, "capa": thumb, "criativo": cr, "cta": vd["call_to_action"]["type"],
                      "form": vd["call_to_action"]["value"].get("lead_gen_form_id"),
                      "ia_ligada": [k for k, x in feats.items() if x.get("enroll_status") != "OPT_OUT"],
                      "recursos": len(feats)}, ensure_ascii=False))
    print("--- anuncios ativos no conjunto:")
    for a in b.get(ADSET + "/ads", {"fields": "name,status,effective_status", "limit": 50})["data"]:
        if a["status"] == "ACTIVE":
            print("  ", a["name"], "|", a["effective_status"])


if __name__ == "__main__":
    main()
