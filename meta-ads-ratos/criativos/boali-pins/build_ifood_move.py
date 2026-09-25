#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Boali — captacao no iFood Move (Sao Paulo Expo, 16-17/09/2026). Pedido da Mileny em 16/09:
o Rodrigo (franqueado) palestra no evento em 17/09. Publico: 12 mil+ pessoas de food service.

- Campanha nova, OUTCOME_LEADS, ABO, tudo PAUSED (ativacao e da Mileny).
- 1 conjunto: pino de 1 km no Sao Paulo Expo (o mesmo da Fesqua), ate 18/09 23h59 —
  o default "mora ou esteve recentemente" pega quem passou pelo evento.
- SP capital NAO e excluida: o Expo fica dentro dela. Sem flexible_spec: o evento ja
  filtra, e 1 km cruzado com interesse zera o publico.
- Mesmo formulario/CTA/opt-out de IA dos vencedores; copy fala do evento.

Uso: python build_ifood_move.py --dry | python build_ifood_move.py
"""
import argparse
import copy
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "boali-depoimento"))
import build_depoimento as b  # noqa: E402

MODELO = "120251217473750156"     # CP 08 pinos (forms) — config de conjunto
VERBA = 15000                     # R$150/dia
FIM = "2026-09-18T23:59:00-0300"
CAMPANHA = "CP 09 - [FRIO] [PIN EVENTO] [FORMS] IFOOD MOVE SPE 16-17/09"
CONJUNTO = "[FRIO] [PIN 1KM SAO PAULO EXPO] [FORMS] IFOOD MOVE 30-60"

PINO = {"name": "Rodovia dos Imigrantes, São Paulo, SP, Brasil",
        "address_string": "Rodovia dos Imigrantes, São Paulo, SP, Brasil",
        "latitude": -23.63143, "longitude": -46.62992,
        "radius": 1, "distance_unit": "kilometer"}

LISTA = ("✅ 19 anos de mercado\n"
         "✅ Investimento a partir de R$359.000\n"
         "✅ Operação simples, sem fogão\n"
         "✅ 98% dos franqueados recomendam\n\n"
         "Ainda há praças disponíveis em várias regiões. Fale com um de nossos consultores 👇")

ADS = [
    ("EV01 - RODRIGO PALESTRANTE IFOOD MOVE", "1674897687181888", "165ac89e0bd0b0bee2d26319076f2685",
     "Está no iFood Move? O Rodrigo, franqueado Boali, é um dos palestrantes do evento. "
     "Aqui ele conta como é ter uma Boali.\n\n" + LISTA),
    ("EV02 - LOJA CHEIA 691 IFOOD MOVE", "28842510918712787", "ec87b6fbb193691406a330406fb3ae78",
     "Está no iFood Move? Então você sabe o que são 691 pedidos no painel num dia comum. "
     "Quem já é franqueado Boali conta o que sustenta esse movimento.\n\n" + LISTA),
    ("EV03 - ANDERSON SEM FOGAO IFOOD MOVE", "2223358894903816", "719689eb069c5ef780cbd8de52bffc52",
     "Está no iFood Move? Uma loja que abre em uma hora e não tem fogão. Quem conta é o Anderson, "
     "do time de operações da Boali desde 2008.\n\n" + LISTA),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    m = b.get(MODELO, {"fields": "billing_event,optimization_goal,destination_type,bid_strategy,targeting"})
    t = copy.deepcopy(m["targeting"])
    t["geo_locations"] = {"custom_locations": [PINO]}
    t.pop("excluded_geo_locations", None)
    t.pop("flexible_spec", None)
    t["age_min"], t["age_max"] = 30, 60
    # ig_search quebra video em formulario (2446429, aprendizados 17/08 e 10/09)
    t["instagram_positions"] = ["stream", "story", "reels", "profile_feed"]
    for k in ("publisher_platforms", "instagram_positions", "targeting_automation"):
        print("  %s: %s" % (k, t.get(k)))
    print("  excl_aud:", [x["name"] for x in t.get("excluded_custom_audiences", [])])

    conj = {
        "name": CONJUNTO, "daily_budget": VERBA, "end_time": FIM,
        "billing_event": m["billing_event"], "optimization_goal": m["optimization_goal"],
        "destination_type": m["destination_type"], "bid_strategy": m["bid_strategy"],
        "promoted_object": {"page_id": b.PAGE}, "targeting": t, "status": "PAUSED",
    }
    for nome, _v, _h, msg in ADS:
        print("\n  " + nome + "\n    " + msg.replace("\n", "\n    "))
    if a.dry:
        print("\n  [dry] nada criado")
        return

    camp = b.post("%s/campaigns" % b.CONTA, {
        "name": CAMPANHA, "objective": "OUTCOME_LEADS", "status": "PAUSED",
        "special_ad_categories": [], "is_adset_budget_sharing_enabled": False,
    }, "campanha")
    conj["campaign_id"] = camp
    adset = b.post("%s/adsets" % b.CONTA, conj, "conjunto")
    for nome, video, thumb, msg in ADS:
        cr = b.post("%s/adcreatives" % b.CONTA, {
            "name": "Boali — " + nome,
            "object_story_spec": {"page_id": b.PAGE, "instagram_user_id": b.IG, "video_data": {
                "video_id": video, "image_hash": thumb, "title": b.TITULO, "message": msg,
                "call_to_action": {"type": "SIGN_UP",
                                   "value": {"lead_gen_form_id": b.FORM, "link": "http://fb.me/"}}}},
            "degrees_of_freedom_spec": b.SEM_IA,
        }, "criativo " + nome[:4])
        b.post("%s/ads" % b.CONTA, {"name": nome, "adset_id": adset,
                                    "creative": {"creative_id": cr}, "status": "PAUSED"}, "ad " + nome[:4])
    print("\n  campanha", camp, "| conjunto", adset, "| tudo PAUSED")


if __name__ == "__main__":
    main()
