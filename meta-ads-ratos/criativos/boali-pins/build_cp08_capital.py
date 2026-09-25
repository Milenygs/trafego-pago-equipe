#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Boali — CP 08: conjunto novo [PIN LOJAS CAPITAL] com 25 lojas fixas de SP capital.

Por que existe: em 17/09/2026 a Mileny corrigiu a premissa de 10/09. SP capital
(269969) NAO e praca fechada, esta ABERTA. A exclusao foi tirada do conjunto de
pinos da onda 1, e a capital ganha conjunto proprio (ABO) para ter leitura e verba
separadas; misturada aos 10 pinos, ela engoliria a entrega dos satelites.

Lojas: camada "Boali | Brasil" do KML (lista_lojas_capital.py), so lojas fixas
(shopping, rua, clube, academia). Fora: eventos, corporativas, food truck, escola
e pontos de outras cidades (Sao Caetano, Osasco, Guarulhos, Cotia, Santo Andre).

Resto igual ao conjunto de pinos da onda 1: 30-55, mesmo flexible_spec, 4 publicos
excluidos, AC/AM/RO/RR fora, so Instagram sem Explorar, advantage_audience 0.
Anuncios: os 3 que rodam nos pinos (Rodrigo, AD15 Anderson, AD12).

Uso:
    python build_cp08_capital.py --dry
    python build_cp08_capital.py          # cria conjunto + 3 ads, tudo PAUSED
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_cp08_captacao import CONTA, FLEX, PAGE, post  # noqa: E402

CAMPANHA = "120251205701320156"   # CP 08 - [FRIO] [PIN LOJAS] [FORMS] [ONDA 1]
SP_CAPITAL = 269969
RAIO_KM = 2
VERBA = 8000  # R$ 80/dia (ok da Mileny, 17/09)
NOME = "[FRIO] [PIN LOJAS CAPITAL] [FORMS] SP CAPITAL 25 LOJAS 2KM"

EXCLUIR_PUBLICOS = [
    "120224942147330156",   # PEPA - BOALI 180DD
    "120237818661500156",   # CADASTRO REALIZADO
    "120238982678540156",   # PQ ENGAJADO RB
    "120251264895210156",   # CAPI_LEAD_DESQUALIFICADO_180D (CRM)
]

CRIATIVOS = [
    ("1025361703312632", "AD04 - RODRIGO FATURAMENTO"),
    ("1093928739992114", "AD15 - OPERACAO SEM FOGAO ANDERSON"),
    ("902745925926548", "AD12 - MERCADO BILHAO EUA"),
]

# (rotulo, lat, lon) — coordenadas do KML oficial
LOJAS = [
    ("Shopping Light",            -23.54673, -46.63863),
    ("Shopping Frei Caneca",      -23.55405, -46.65268),
    ("Shopping Mega Polo",        -23.53690, -46.61851),
    ("Top Center Shopping",       -23.56581, -46.65080),
    ("Shopping Center 3",         -23.55785, -46.65895),
    ("Jardim Pamplona Shopping",  -23.57038, -46.66142),
    ("Clube Lemon Jardins",       -23.57629, -46.65820),
    ("Shopping Center Norte",     -23.51571, -46.61805),
    ("Perdizes (rua)",            -23.53768, -46.67199),
    ("Shopping Metro Santa Cruz", -23.59909, -46.63721),
    ("Sky Fit Tatuape",           -23.53557, -46.58260),
    ("Vila Madalena (rua)",       -23.55552, -46.68968),
    ("Shopping Metro Tatuape",    -23.54171, -46.57667),
    ("Itaim Bibi (rua)",          -23.58710, -46.67688),
    ("Moema Arapanes (rua)",      -23.60602, -46.66656),
    ("Shopping Vila Olimpia",     -23.59530, -46.68668),
    ("Shopping Ibirapuera",       -23.61028, -46.66664),
    ("Santana Parque Shopping",   -23.48304, -46.64470),
    ("Shopping Metro Tucuruvi",   -23.48025, -46.60274),
    ("Shopping Villa Lobos",      -23.55113, -46.72196),
    ("D&D Shopping",              -23.60899, -46.69662),
    ("Conceicao (rua)",           -23.63406, -46.64113),
    ("Butanta Shopping",          -23.58441, -46.72507),
    ("SPFC Morumbis",             -23.60274, -46.71880),
    ("Continental Shopping",      -23.54744, -46.75707),
]


def targeting():
    return {
        "age_min": 30, "age_max": 55,
        "flexible_spec": FLEX,
        "geo_locations": {
            "custom_locations": [
                {"distance_unit": "kilometer", "latitude": la, "longitude": lo,
                 "radius": RAIO_KM, "primary_city_id": SP_CAPITAL,
                 "region_id": 460, "country": "BR"}
                for _, la, lo in LOJAS
            ],
            # location_types omitido: a Meta grava ["home","recent"] (padrao da onda 1).
        },
        "excluded_geo_locations": {
            "regions": [{"key": k} for k in ("438", "441", "457", "458")],
        },
        "excluded_custom_audiences": [{"id": a} for a in EXCLUIR_PUBLICOS],
        "targeting_automation": {"advantage_audience": 0,
                                 "individual_setting": {"geo": 0}},
        "publisher_platforms": ["instagram"],
        "instagram_positions": ["stream", "story", "reels", "profile_feed", "ig_search"],
        "device_platforms": ["mobile", "desktop"],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()

    print("\n%s" % NOME)
    print("  campanha: %s (CP 08, ABO)" % CAMPANHA)
    print("  verba   : R$ %d/dia · %d pinos de %d km · PAUSED" % (VERBA / 100, len(LOJAS), RAIO_KM))
    for rot, la, lo in LOJAS:
        print("      %-28s %9.5f, %9.5f" % (rot, la, lo))
    print("  criativos: %s\n" % " · ".join(n for _, n in CRIATIVOS))
    if args.dry:
        print("  [dry] nada foi criado.\n")
        return

    adset = post("%s/adsets" % CONTA, {
        "name": NOME,
        "campaign_id": CAMPANHA,
        "daily_budget": VERBA,
        "billing_event": "IMPRESSIONS",
        "optimization_goal": "LEAD_GENERATION",
        "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
        "destination_type": "ON_AD",
        "promoted_object": {"page_id": PAGE},
        "targeting": targeting(),
        "status": "PAUSED",
    }, "conjunto CAPITAL")

    for cid, rotulo in CRIATIVOS:
        post("%s/ads" % CONTA, {
            "name": rotulo,
            "adset_id": adset,
            "creative": {"creative_id": cid},
            "status": "PAUSED",
        }, "  ad %s" % rotulo[:28])

    print("\n  ADSET_ID=%s · tudo PAUSED. Conferir antes de ativar.\n" % adset)


if __name__ == "__main__":
    main()
