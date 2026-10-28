#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cheirin Bao MT — VD07 - franqueada_raissa volta para a musica ORIGINAL do editor (09/10/2026).

Mileny: "subir um criativo novo na campanha franqueados, conjunto raissa: raissa usar esse". O arquivo
`raissa usar esse.mp4` e identico (SHA256) a `raissa franqueada edicao musica  3992.mp4`, ja subido em 04/10 como VD07
(criativo 1429813575943696). Escolha dela: "Voltar o VD07" (sem anuncio duplicado). Continua PAUSED; ela ativa.
Para reverter: remix medio 902345639475854 · remix baixo 1425907473017649.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_outubro_depoimentos as b  # noqa: E402

AD = "120258161910470212"
ADSET = "120257017816020212"
ORIGINAL = "1429813575943696"
REMIX_MEDIO = "902345639475854"


def main():
    antes = b.get(AD, {"fields": "name,status,creative{id}"})
    assert antes["creative"]["id"] == REMIX_MEDIO, "VD07 nao esta no remix medio: %s" % antes["creative"]["id"]
    assert antes["status"] == "PAUSED", "VD07 nao esta PAUSED"
    b.post(AD, {"creative": {"creative_id": ORIGINAL}}, "VD07 -> criativo com musica original")
    d = b.get(AD, {"fields": "name,status,effective_status,creative{id,object_story_spec,degrees_of_freedom_spec}"})
    vd = d["creative"]["object_story_spec"]["video_data"]
    feats = d["creative"].get("degrees_of_freedom_spec", {}).get("creative_features_spec", {})
    print(json.dumps({"anuncio": AD, "nome": d["name"], "status": d["status"], "effective_status": d["effective_status"],
                      "criativo": d["creative"]["id"], "video": vd["video_id"], "cta": vd["call_to_action"]["type"],
                      "form": vd["call_to_action"]["value"].get("lead_gen_form_id"),
                      "ia_ligada": [k for k, x in feats.items() if x.get("enroll_status") != "OPT_OUT"],
                      "recursos": len(feats)}, ensure_ascii=False))
    print("--- anuncios ativos no conjunto:")
    for a in b.get(ADSET + "/ads", {"fields": "name,status,effective_status", "limit": 50})["data"]:
        if a["status"] == "ACTIVE":
            print("  ", a["name"], "|", a["effective_status"])


if __name__ == "__main__":
    main()
