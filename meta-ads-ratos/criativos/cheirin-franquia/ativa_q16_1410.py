#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cheirin Bao MT — ativacao do 16 QUENTE + LAL (14/10/2026). Mileny: "criei um publico
video 50% - 120 dias, vamos usar ele e ai vc pode ativar".

1. Inclui IG_VIDEO_SELECAONIVEL3_120D (120258418286650212, criado pela Mileny no painel)
   no targeting do 16 (o targeting vai inteiro: o update substitui o anterior).
2. Ativa o conjunto 16 e os 2 anuncios (os dois ja aprovados).
3. Pausa o 04 LAL (decisao dela de 14/10: os publicos dele estao no 16).
>=35s entre escritas no mesmo conjunto (#613).
"""
import time

import build_q16_quente_lal_1410 as b

ADSET = "120258418032850212"
ADS = ["120258418038660212", "120258418044610212"]  # Q16 - AD38, VD03 - franqueada_raissa
LAL04 = "120256940815900212"
VIDEO_CHEIRIN = "120258418286650212"


def main():
    targeting = {
        "age_min": 30, "age_max": 55,
        "geo_locations": {"cities": [{"key": k} for k in b.CIDADES], "regions": [{"key": "460"}],
                          "location_types": ["home", "recent"]},
        "custom_audiences": [{"id": i} for i in b.INCLUIR + [VIDEO_CHEIRIN]],
        "excluded_custom_audiences": [{"id": i} for i in b.EXCLUIR],
        "publisher_platforms": ["instagram"],
        "instagram_positions": ["stream", "story", "explore", "reels", "explore_home", "profile_feed"],
        "device_platforms": ["mobile", "desktop"],
        "targeting_relaxation_types": {"lookalike": 0, "custom_audience": 0},
        "targeting_automation": {"advantage_audience": 0, "individual_setting": {"geo": 0}},
    }
    b.post(ADSET, {"targeting": targeting}, "16: + video 50% Cheirin 120D")
    time.sleep(35)
    b.post(ADSET, {"status": "ACTIVE"}, "16: conjunto ATIVO")
    for ad in ADS:
        time.sleep(35)
        b.post(ad, {"status": "ACTIVE"}, "16: anuncio %s ATIVO" % ad)
    time.sleep(2)
    b.post(LAL04, {"status": "PAUSED"}, "04 LAL PAUSADO")


if __name__ == "__main__":
    main()
