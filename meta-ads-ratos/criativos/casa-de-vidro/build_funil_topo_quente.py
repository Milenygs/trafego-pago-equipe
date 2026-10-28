#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Casa de Vidro Paraty — funil de conversao (26/09/2026).

Pedido da Mileny: "quero criar um funil real de conversao — da forma que estavamos
fazendo nao ta dando certo". Ate aqui a conta ia do frio direto para o WhatsApp.
Agora:
  TOPO 1  [PERFIL]  trafego pro perfil, R$20/dia, bairros alto padrao SP-RJ-MG
  TOPO 2  [VV]      video view (ThruPlay) do "Onde o verao 1", R$20/dia, nos MESMOS
                    pinos da campanha de WhatsApp (impacto antes da conversao)
  FUNDO   [QUENTE]  conjunto novo na GEO-PIN/WHATS, R$50/dia: seguidores + quem
                    interagiu com o IG + quem viu os videos, com o video ja anunciado
  + tirar a exclusao de IG_SEGUIDORES dos conjuntos frios da GEO-PIN/WHATS.

Tudo novo sobe PAUSED. Etapas independentes, para retomar sem duplicar objeto:
    python build_funil_topo_quente.py --so audiencia   # falha (#2654): usar o video da Pagina, ver AUDIENCIA_VIDEO_VERAO
    python build_funil_topo_quente.py --so perfil --post-perfil <ig_media_id>
    python build_funil_topo_quente.py --so vv
    python build_funil_topo_quente.py --so quente
    python build_funil_topo_quente.py --so seguidores
  --campanha / --conjunto reaproveitam objeto ja criado.
  --dry imprime o payload sem escrever.
"""
import argparse
import json
import sys
import time

from build_geopin_whats import CONTA, PAGINA, INSTAGRAM, get, post

WHATS_CAMPANHA = "120249402919690510"
WHATSAPP = "5511969565817"
IG_SEGUIDORES = "120244196072220510"
IG_INTERACAO_180 = "120240941992860510"
IG_VIDEO50_365 = "120240942126400510"
SITE_120 = "120240942159870510"
VIAJANTE_INTERNACIONAL = "6022788483583"
VIDEO_VERAO = "1938277547122704"          # "Onde o verao 1" (video do anuncio)
CRIATIVO_VERAO_WHATS = "1399576785028475"  # criativo CTWA do "Onde o verao 1" (ja aprovado)
VIDEO_VERAO_PAGINA = "1799657194568531"    # o mesmo video, ligado ao post da Pagina
THUMB_VERAO = "140a2d91c2825de1d2806ba1e9afe7ce"
AUDIENCIA_VIDEO_VERAO = "120249614027790510"  # [IG_VIDEO_VERAO_50%] 180D, criado 26/09
# Copy do anuncio dela, com as 2 adaptacoes de 16/09: sai a linha "servicos sob medida
# com custo a parte:" (abria uma lista que nao vem) e sai o "Reserve sua estadia" (VV nao tem destino).
COPY_VV = (
    "Descubra o Luxo absoluto em Paraty em nossa casa de Vidro!\n\n"
    "A Casa de Vidro é um refúgio exclusivo para quem busca privacidade, conforto e experiências "
    "personalizadas à altura do seu estilo de vida. 🏖️🚤\n\n"
    "⚠️ Observação: Não somos pousada, aluguel por temporada do espaço completo.\n\n"
    "Aqui, cada detalhe foi pensado para proporcionar um descanso impecável:\n\n"
    "• Piscina com borda infinita e vista cinematográfica para o mar;\n"
    "• Sauna seca, deck panorâmico e varanda gourmet;\n"
    "• Gastronomia personalizada, com menus criados especialmente para você;\n"
    "• Praia privativa, estruturada pela nossa equipe;\n"
    "• Concierge exclusivo;\n"
    "• Transporte marítimo direto do cais de Paraty Mirim até a casa;\n\n"
    "Acomoda com excelência até 12 pessoas.\n\n"
    "📍 Localizada em Paraty Mirim - Paraty Rio de Janeiro, a poucos minutos do Centro Histórico e "
    "cercada por natureza preservada, a Casa de Vidro é um convite para viver dias indescritíveis.\n\n"
    "Exclusividade, privacidade e experiências inesquecíveis."
)
PERFIL_URL = "https://www.instagram.com/casadevidro.paraty/"

PIN_MORA = "120249402954240510"
PIN_DESTINO = "120249403004740510"
PIN_LUGARES_BR = "120249403702380510"
PIN_LUGARES = "120249403592920510"  # verba vitalicia encerrada em 24/09

# Bairros alto padrao de MG (BH + Nova Lima). Coordenadas conferidas no OSM/Nominatim.
PINOS_MG = [
    {"latitude": -19.9315, "longitude": -43.9460, "radius": 1, "distance_unit": "kilometer"},    # Lourdes / Santo Agostinho
    {"latitude": -19.9360, "longitude": -43.9320, "radius": 1, "distance_unit": "kilometer"},    # Savassi / Funcionarios
    {"latitude": -19.9460, "longitude": -43.9270, "radius": 1.5, "distance_unit": "kilometer"},  # Sion / Anchieta / Serra
    {"latitude": -19.9554, "longitude": -43.9116, "radius": 1.5, "distance_unit": "kilometer"},  # Mangabeiras
    {"latitude": -19.9500, "longitude": -43.9500, "radius": 1.5, "distance_unit": "kilometer"},  # Cidade Jardim / Sao Bento / Santa Lucia
    {"latitude": -19.9815, "longitude": -43.9425, "radius": 1.5, "distance_unit": "kilometer"},  # Belvedere / Vila da Serra / Vale do Sereno
    {"latitude": -19.8575, "longitude": -43.9780, "radius": 2, "distance_unit": "kilometer"},    # Pampulha (Bandeirantes / Sao Luiz)
]
# Centro de BH (-19.919, -43.940) fica fora de todos os raios.

OPT_OUT_POST_IG = ["advantage_plus_creative", "enhance_cta", "inline_comment", "text_optimizations",
                   "image_touchups", "image_uncrop", "adapt_to_placement", "show_summary",
                   "reveal_details_over_time", "video_auto_crop", "video_filtering", "video_uncrop"]


def dof():
    return {"creative_features_spec": {f: {"enroll_status": "OPT_OUT"} for f in OPT_OUT_POST_IG}}


def pinos(adset_id):
    t = get(adset_id, {"fields": "targeting"})["targeting"]
    saida = []
    for p in t["geo_locations"]["custom_locations"]:
        saida.append({k: p[k] for k in ("latitude", "longitude", "radius", "distance_unit")})
    return saida


def escrever(path, params, oque, dry):
    if dry:
        print("  DRY  %-40s %s" % (oque, json.dumps(params, ensure_ascii=False)[:1500]))
        return "DRY_" + oque.replace(" ", "_")
    novo = post(path, params, oque)
    if not novo:
        sys.exit("parou em: " + oque)
    time.sleep(1.5)
    return novo


def etapa_audiencia(a):
    # formato legado por video especifico (o mesmo dos publicos de video 50% que ja existem na conta)
    params = {
        "name": "[IG_VIDEO_VERAO_50%] 180D",
        "subtype": "ENGAGEMENT",
        "retention_days": 180,
        "prefill": "true",
        "rule": [{"event_name": "video_view_50_percent", "object_id": VIDEO_VERAO}],
    }
    return escrever(CONTA + "/customaudiences", params, "publico video Verao 50% 180D", a.dry)


def etapa_perfil(a):
    if not a.post_perfil:
        sys.exit("--post-perfil obrigatorio")
    camp = a.campanha or escrever(CONTA + "/campaigns", {
        "name": "[TOPO/PERFIL] Trafego pro perfil - ALTO PADRAO SP-RJ-MG - 26/09",
        "objective": "OUTCOME_TRAFFIC", "status": "PAUSED", "special_ad_categories": [],
        "is_adset_budget_sharing_enabled": "false",
    }, "campanha PERFIL", a.dry)
    locs = pinos(PIN_MORA) + PINOS_MG
    targeting = {
        "age_min": 35, "age_max": 65,
        "geo_locations": {"custom_locations": locs, "location_types": ["home"]},
        "flexible_spec": [{"behaviors": [{"id": VIAJANTE_INTERNACIONAL}]}],
        "excluded_custom_audiences": [{"id": IG_SEGUIDORES}],
        "publisher_platforms": ["instagram"],
        "targeting_automation": {"advantage_audience": 0},
    }
    adset = escrever(CONTA + "/adsets", {
        "name": "[PERFIL] BAIRROS ALTO PADRAO SP-RJ-MG + VIAJANTE INTERNACIONAL",
        "campaign_id": camp, "status": "PAUSED", "daily_budget": 2000,
        "billing_event": "IMPRESSIONS", "optimization_goal": "PROFILE_VISIT",
        "destination_type": "INSTAGRAM_PROFILE", "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
        "promoted_object": {"page_id": PAGINA, "smart_pse_enabled": False},
        "targeting": targeting,
    }, "conjunto PERFIL (%d pinos)" % len(locs), a.dry)
    cr = escrever(CONTA + "/adcreatives", {
        "name": "CDV - POST IG %s - Perfil - 26/09/2026" % a.post_perfil,
        "object_id": PAGINA, "instagram_user_id": INSTAGRAM,
        "source_instagram_media_id": a.post_perfil,
        "call_to_action": {"type": "VIEW_INSTAGRAM_PROFILE", "value": {"link": PERFIL_URL}},
        "degrees_of_freedom_spec": dof(),
    }, "criativo PERFIL", a.dry)
    escrever(CONTA + "/ads", {"name": a.nome_ad or "AD - Post IG - PERFIL", "adset_id": adset,
                              "creative": {"creative_id": cr}, "status": "PAUSED"}, "anuncio PERFIL", a.dry)


def etapa_engaj(a):
    """Substituto da visita ao perfil (conta nao qualificada, 2016153), escolhido por ela em 26/09:
    engajamento com o Reel organico, mesmo publico. Quem interage cai no [IG_INTERACAO] do QUENTE."""
    if not a.post_perfil:
        sys.exit("--post-perfil obrigatorio")
    camp = a.campanha or escrever(CONTA + "/campaigns", {
        "name": "[TOPO/ENGAJ] Reel Refugio no paraiso - ALTO PADRAO SP-RJ-MG - 26/09",
        "objective": "OUTCOME_ENGAGEMENT", "status": "PAUSED", "special_ad_categories": [],
        "is_adset_budget_sharing_enabled": "false",
    }, "campanha ENGAJ", a.dry)
    locs = pinos(PIN_MORA) + PINOS_MG
    targeting = {
        "age_min": 35, "age_max": 65,
        "geo_locations": {"custom_locations": locs, "location_types": ["home"]},
        "flexible_spec": [{"behaviors": [{"id": VIAJANTE_INTERNACIONAL}]}],
        "excluded_custom_audiences": [{"id": IG_SEGUIDORES}],
        "publisher_platforms": ["instagram"],
        "targeting_automation": {"advantage_audience": 0},
    }
    adset = escrever(CONTA + "/adsets", {
        "name": "[ENGAJ] BAIRROS ALTO PADRAO SP-RJ-MG + VIAJANTE INTERNACIONAL",
        "campaign_id": camp, "status": "PAUSED", "daily_budget": 2000,
        "billing_event": "IMPRESSIONS", "optimization_goal": "POST_ENGAGEMENT",
        "destination_type": "ON_POST", "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
        "targeting": targeting,
    }, "conjunto ENGAJ (%d pinos)" % len(locs), a.dry)
    # engajamento nao leva botao (regra permanente da Mileny, 21/07)
    cr = escrever(CONTA + "/adcreatives", {
        "name": "CDV - Reel Refugio no paraiso - Engajamento (sem botao) - 26/09/2026",
        "object_id": PAGINA, "instagram_user_id": INSTAGRAM,
        "source_instagram_media_id": a.post_perfil,
        "degrees_of_freedom_spec": dof(),
    }, "criativo ENGAJ", a.dry)
    escrever(CONTA + "/ads", {"name": "AD - Reel Refugio no paraiso - ENGAJ", "adset_id": adset,
                              "creative": {"creative_id": cr}, "status": "PAUSED"}, "anuncio ENGAJ", a.dry)


def etapa_vv(a):
    camp = a.campanha or escrever(CONTA + "/campaigns", {
        "name": "[TOPO/VV] Video view - Onde o verao - pinos da WHATS - 26/09",
        "objective": "OUTCOME_ENGAGEMENT", "status": "PAUSED", "special_ad_categories": [],
        "is_adset_budget_sharing_enabled": "false",
    }, "campanha VV", a.dry)
    locs = pinos(PIN_MORA) + pinos(PIN_DESTINO) + pinos(PIN_LUGARES_BR)
    # mistura bairro (home) com destino/hotel (mora ou esteve): sem location_types, a Meta
    # aplica o padrao atual "mora ou esteve recentemente" (recent/travel_in explicitos dao 1870199)
    targeting = {
        "age_min": 35, "age_max": 65,
        "geo_locations": {"custom_locations": locs},
        "flexible_spec": [{"behaviors": [{"id": VIAJANTE_INTERNACIONAL}]}],
        "excluded_custom_audiences": [{"id": IG_SEGUIDORES}],
        "publisher_platforms": ["instagram"],
        "targeting_automation": {"advantage_audience": 0},
    }
    adset = escrever(CONTA + "/adsets", {
        "name": "[VV] MESMOS PINOS DA WHATS (MORA+DESTINO+HOTEIS BR) + VIAJANTE",
        "campaign_id": camp, "status": "PAUSED", "daily_budget": 2000,
        "billing_event": "IMPRESSIONS", "optimization_goal": "THRUPLAY",
        "destination_type": "ON_VIDEO", "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
        "targeting": targeting,
    }, "conjunto VV (%d pinos)" % len(locs), a.dry)
    # video view nao leva botao (regra permanente da Mileny, 21/07). Usa o video DA PAGINA
    # (1799657194568531), o mesmo do publico [IG_VIDEO_VERAO_50%] — o video do anuncio
    # (1938277547122704) nao tem Pagina e nao aceita publico (#2654).
    cr = escrever(CONTA + "/adcreatives", {
        "name": "CDV - Onde o verao 1 - Video view (sem botao) - 26/09/2026",
        "object_story_spec": {"page_id": PAGINA, "instagram_user_id": INSTAGRAM, "video_data": {
            "video_id": VIDEO_VERAO_PAGINA, "image_hash": THUMB_VERAO, "message": COPY_VV}},
        "degrees_of_freedom_spec": dof(),
    }, "criativo VV", a.dry)
    escrever(CONTA + "/ads", {"name": "AD - Onde o verao 1 - VIDEO VIEW", "adset_id": adset,
                              "creative": {"creative_id": cr}, "status": "PAUSED"}, "anuncio VV", a.dry)


def etapa_quente(a):
    publicos = [IG_SEGUIDORES, IG_INTERACAO_180, IG_VIDEO50_365, SITE_120, AUDIENCIA_VIDEO_VERAO]
    targeting = {
        "age_min": 35, "age_max": 65,
        "geo_locations": {"countries": ["BR"]},  # geo obrigatoria (regra 24/09): publico de IG pega o mundo
        "custom_audiences": [{"id": p} for p in publicos],
        "publisher_platforms": ["instagram"],
        "targeting_automation": {"advantage_audience": 0},
    }
    adset = a.conjunto or escrever(CONTA + "/adsets", {
        "name": "[QUENTE] SEGUIDORES + INTERACAO IG + VIDEO - BR",
        "campaign_id": WHATS_CAMPANHA, "status": "PAUSED", "daily_budget": 5000,
        "billing_event": "IMPRESSIONS", "optimization_goal": "CONVERSATIONS",
        "destination_type": "WHATSAPP", "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
        "promoted_object": {"page_id": PAGINA, "smart_pse_enabled": False,
                            "whatsapp_phone_number": WHATSAPP},
        "targeting": targeting,
    }, "conjunto QUENTE (%d publicos)" % len(publicos), a.dry)
    escrever(CONTA + "/ads", {"name": "AD - Onde o verao 1 - QUENTE", "adset_id": adset,
                              "creative": {"creative_id": CRIATIVO_VERAO_WHATS}, "status": "PAUSED"},
             "anuncio QUENTE", a.dry)


def etapa_seguidores(a):
    for adset_id in (PIN_MORA, PIN_DESTINO, PIN_LUGARES_BR):
        t = get(adset_id, {"fields": "name,targeting"})
        tg = t["targeting"]
        antes = [x["id"] for x in tg.get("excluded_custom_audiences", [])]
        tg.pop("excluded_custom_audiences", None)
        lt = tg["geo_locations"].get("location_types", [])
        if "recent" in lt:
            tg["geo_locations"].pop("location_types")  # reenviar recent da 1870199; omitido volta igual
        else:
            tg["geo_locations"]["location_types"] = ["home"]
        for p in tg["geo_locations"].get("custom_locations", []):
            for k in ("primary_city_id", "region_id", "country"):
                p.pop(k, None)
        print("  %s  exclusoes antes: %s" % (t["name"], antes))
        if not antes:
            continue  # ja estava sem exclusao
        if a.dry:
            escrever(adset_id, {"targeting": tg}, "tira IG_SEGUIDORES " + adset_id, a.dry)
        else:
            post(adset_id, {"targeting": tg}, "tira IG_SEGUIDORES " + adset_id)  # update devolve success, nao id
            time.sleep(1.5)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--so", required=True, choices=["audiencia", "perfil", "engaj", "vv", "quente", "seguidores"])
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--post-perfil")
    ap.add_argument("--post-video")
    ap.add_argument("--nome-ad")
    ap.add_argument("--campanha")
    ap.add_argument("--conjunto")
    ap.add_argument("--audiencia-video")
    a = ap.parse_args()
    {"audiencia": etapa_audiencia, "perfil": etapa_perfil, "engaj": etapa_engaj, "vv": etapa_vv,
     "quente": etapa_quente, "seguidores": etapa_seguidores}[a.so](a)
