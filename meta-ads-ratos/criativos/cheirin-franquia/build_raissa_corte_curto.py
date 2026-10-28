#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cheirin Bao MT — "Franqueada- raissa" (corte curto 3993) no conjunto VD02 Raissa (03/10/2026).

Pedido da Mileny: subir na campanha ✅05 Forms Franqueados, no conjunto que trouxe mais leads
(VD02 Raissa: 96 leads desde 17/08, CPL R$53). O NOME DO ANUNCIO tem que ser exatamente
"Franqueada- raissa": o CRM usa o nome do anuncio para mandar o lead ao funil Franqueados.

Antes do anuncio, o conjunto (PAUSADO) e corrigido para as regras da conta:
  - targeting_relaxation_types custom_audience 1 -> 0 (expansao desligada);
  - targeting_automation.individual_setting.geo 1 -> 0 (sem expandir localizacao);
  - sem ig_search (erro 2446429 com video em formulario);
  - exclusoes da regra de lead: + BASE LEADS RD e SITE_LEADDESQUALIFICADO_90D.
Blueprint do criativo: o mesmo do build_outubro_depoimentos (modelo DRE 146k). Tudo PAUSED.
"""
import json
import os
import subprocess
import sys
import tempfile
import urllib.request
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_outubro_depoimentos as b  # noqa: E402

ADSET = "120257017816020212"
NOME = "Franqueada- raissa"
VIDEO = os.path.expandvars(r"%USERPROFILE%\OneDrive\Área de Trabalho\CLAUDE CODE\franquias\cheirin bao"
                           r"\criativos campanha outubro\Cheirin Bao - Raissa - 3993 corte curto.mp4")
THUMB_SEG = 1.0

COPY = (
    "Funcionária pública, sem experiência com negócio.\n\n"
    "Era assim que a Raissa estava antes de abrir a franquia Cheirin Bão. O que ela tinha era a vontade de "
    "ter o próprio negócio. No vídeo, ela conta como foi o começo.\n\n"
    "Se o que te trava é não ter experiência, clique e fale com a gente. Na conversa, você entende como a "
    "rede acompanha quem está começando.\n\n" + b.FIM)


def corrige_conjunto():
    t = b.get(ADSET, {"fields": "targeting"})["targeting"]
    t["targeting_relaxation_types"] = {"lookalike": 0, "custom_audience": 0}
    t["targeting_automation"] = {"advantage_audience": 0, "individual_setting": {"geo": 0}}
    t["instagram_positions"] = [p for p in t.get("instagram_positions", []) if p != "ig_search"]
    exc = {c["id"] for c in t.get("excluded_custom_audiences", [])}
    for extra in ("120234070196910212", "120257459142480212"):   # BASE LEADS RD, SITE_LEADDESQUALIFICADO_90D
        if extra not in exc:
            t.setdefault("excluded_custom_audiences", []).append({"id": extra})
    b.post(ADSET, {"targeting": t}, "conjunto VD02 corrigido (relax 0, geo 0, sem ig_search)")


def converte():
    mp4 = os.path.join(tempfile.gettempdir(), "Franqueada-raissa-corte-curto.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", VIDEO, "-map", "0:v:0", "-map", "0:a:0",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", "30",
                    "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-movflags", "+faststart", mp4], check=True)
    return mp4


def main():
    if "--dry" in sys.argv:
        print(COPY)
        return
    m = b.modelo()
    corrige_conjunto()
    mp4 = converte()
    vid = b.sobe_video(mp4)
    thumb = b.sobe_thumb(mp4, THUMB_SEG)
    story = {"page_id": m["page_id"], "instagram_user_id": m["instagram_user_id"],
             "video_data": {"video_id": vid, "image_hash": thumb, "title": m["title"],
                            "link_description": m["link_description"], "message": COPY,
                            "call_to_action": m["cta"]}}
    cr = b.post("%s/adcreatives" % b.CONTA, {"name": "Cheirin — Franqueada- raissa (corte curto 3993)",
                                             "object_story_spec": story,
                                             "degrees_of_freedom_spec": m["dof"]}, "criativo")
    ad = b.post("%s/ads" % b.CONTA, {"name": NOME, "adset_id": ADSET, "creative": {"creative_id": cr},
                                     "status": "PAUSED"}, "anuncio " + NOME)
    print(json.dumps({"video": vid, "thumb": thumb, "criativo": cr, "anuncio": ad}))


if __name__ == "__main__":
    main()
