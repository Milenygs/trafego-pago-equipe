#!/usr/bin/env python3
"""
Aniversário Teixeira — Açaí Fruit Show Teixeira de Freitas (act_766482893061196)

Solicitação da Mileny (03/09/2026): divulgar a promoção de aniversário da loja,
verba R$ 200 até 11/09, público Teixeira de Freitas, criativo em vídeo.

Sobe conjunto + vídeo + criativo + anúncio e ATIVA os três níveis.
A campanha 120251890940370584 já foi criada antes deste script.

Padrão herdado de corrigir_instagram.py (17/06/2026), que é a versão corrigida:
page 738359459365811 + IG 17841476160771866 (@acaifruitshowtxf). O primeiro
script daquela pasta usava o IG da loja FSA por engano — não copiar dele.
"""
import json, os, sys, time

SCRIPTS = os.path.join(os.environ["USERPROFILE"], "OneDrive", ".claude", "skills",
                       "meta-ads-ratos", "scripts")
sys.path.insert(0, SCRIPTS)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from lib import init_api
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.advideo import AdVideo
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.ad import Ad

ACT = "act_766482893061196"
CAMPANHA = "120251890940370584"
PAGE_ID = "738359459365811"
IG_ACTOR = "17841476160771866"          # @acaifruitshowtxf
IG_URL = "https://www.instagram.com/acaifruitshowtxf/"
GEO_KEY = "2684470"                     # Teixeira de Freitas / BA

VIDEO = os.path.join(os.environ["USERPROFILE"], "OneDrive", "Área de Trabalho",
                     "CLAUDE CODE", "franquias", "acai-fruit-show",
                     "criativos loja teixeira de freitas", "campanha aniversario.mov")

# Endereço e telefone vêm do criativo de junho da própria loja — não inventar oferta:
# o detalhe da promoção está no vídeo.
COPY = (
    "É aniversário do Açaí Fruit Show Teixeira de Freitas!\n\n"
    "Tem promoção especial rolando na loja pra comemorar com você. "
    "Corre que é só até dia 11!\n\n"
    "Rua da Pituba, 180 - Bela Vista, Teixeira de Freitas\n"
    "(73) 98105-2744"
)

# Opt-out das otimizações de IA da Meta (preferência fixa da Mileny).
# standard_enhancements foi descontinuado (erro 100/3858504) — usar features
# individuais.
OPT_OUT = {"creative_features_spec": {
    "standard_enhancements": {"enroll_status": "OPT_OUT"},
}}
OPT_OUT_GRANULAR = {"creative_features_spec": {
    "enhance_cta": {"enroll_status": "OPT_OUT"},
    "text_optimizations": {"enroll_status": "OPT_OUT"},
    "video_auto_crop": {"enroll_status": "OPT_OUT"},
    "image_brightness_and_contrast": {"enroll_status": "OPT_OUT"},
    "media_liquidity_animated_image": {"enroll_status": "OPT_OUT"},
}}

log = []


def passo(msg):
    print(msg, flush=True)
    log.append(msg)


init_api()
acc = AdAccount(ACT)

# --- 1. Upload do vídeo -----------------------------------------------------
passo(f"Subindo vídeo ({round(os.path.getsize(VIDEO)/1024/1024, 1)} MB)...")
vid = acc.create_ad_video(params={"name": "Aniversario Teixeira 09/26",
                                  "source": VIDEO})
video_id = vid["id"]
passo(f"  video_id: {video_id}")

# Meta processa o vídeo em background; criativo com vídeo não pronto falha.
thumb = None
for i in range(40):
    time.sleep(15)
    v = AdVideo(video_id).api_get(fields=["status", "thumbnails"]).export_all_data()
    st = (v.get("status") or {}).get("video_status")
    passo(f"  [{i+1}] status: {st}")
    if st == "ready":
        thumbs = (v.get("thumbnails") or {}).get("data") or []
        pref = [t for t in thumbs if t.get("is_preferred")] or thumbs
        thumb = pref[0]["uri"] if pref else None
        break
    if st == "error":
        raise SystemExit(f"Vídeo falhou no processamento: {v}")
else:
    raise SystemExit("Vídeo não ficou pronto em 10 min — rodar de novo depois.")
passo(f"  thumbnail: {'ok' if thumb else 'sem thumb (Meta gera sozinha)'}")

# --- 2. Conjunto ------------------------------------------------------------
targeting = {
    "geo_locations": {
        "cities": [{"key": GEO_KEY, "radius": 0, "distance_unit": "kilometer"}],
        "location_types": ["home", "recent"],
    },
    "age_min": 18,
    "age_max": 55,
    "publisher_platforms": ["instagram"],
    "instagram_positions": ["stream", "story", "reels", "explore"],
    "targeting_automation": {"advantage_audience": 0},
}

adset = acc.create_ad_set(params={
    "name": "Teixeira de Freitas Cidade | 18-55 | IG",
    "campaign_id": CAMPANHA,
    "lifetime_budget": 20000,                       # R$ 200,00
    "start_time": "2026-09-03T18:00:00-0300",
    "end_time": "2026-09-11T23:59:00-0300",
    "optimization_goal": "LINK_CLICKS",
    "billing_event": "IMPRESSIONS",
    "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
    "destination_type": "INSTAGRAM_PROFILE",
    "targeting": targeting,
    "status": "PAUSED",
})
adset_id = adset["id"]
passo(f"Conjunto criado: {adset_id}")

# --- 3. Criativo ------------------------------------------------------------
video_data = {
    "video_id": video_id,
    "message": COPY,
    "call_to_action": {"type": "LEARN_MORE", "value": {"link": IG_URL}},
}
if thumb:
    video_data["image_url"] = thumb

base = {
    "name": "Creative - Aniversario Teixeira",
    "object_story_spec": {"page_id": PAGE_ID, "video_data": video_data},
    "instagram_user_id": IG_ACTOR,
}

creative = None
for tentativa, dof in (("standard", OPT_OUT), ("granular", OPT_OUT_GRANULAR),
                       ("sem opt-out", None)):
    params = dict(base)
    if dof:
        params["degrees_of_freedom_spec"] = dof
    try:
        creative = acc.create_ad_creative(params=params)
        passo(f"Criativo criado ({tentativa}): {creative['id']}")
        if dof is None:
            passo("  ATENCAO: opt-out das otimizacoes de IA NAO aplicado via API "
                  "— desmarcar no painel.")
        break
    except Exception as e:
        passo(f"  opt-out {tentativa} recusado: {str(e)[:160]}")
        time.sleep(2)
if creative is None:
    raise SystemExit("Criativo não subiu.")

# --- 4. Anúncio -------------------------------------------------------------
ad = acc.create_ad(params={
    "name": "AD01 - Aniversario Teixeira [VIDEO]",
    "adset_id": adset_id,
    "creative": {"creative_id": creative["id"]},
    "status": "PAUSED",
})
passo(f"Anúncio criado: {ad['id']}")

# --- 5. Ativar os três níveis (campanha -> conjunto -> anúncio) -------------
for nome, obj in (("campanha", CAMPANHA), ("conjunto", adset_id), ("anúncio", ad["id"])):
    time.sleep(2)
    from facebook_business.adobjects.abstractcrudobject import AbstractCrudObject
    o = AbstractCrudObject(obj)
    o.get_api().call("POST", (obj,), params={"status": "ACTIVE"})
    passo(f"Ativado: {nome} {obj}")

# --- 6. Conferência ---------------------------------------------------------
time.sleep(5)
conf = {}
conf["campanha"] = acc.get_api().call(
    "GET", (CAMPANHA,), params={"fields": "name,status,effective_status"}).json()
conf["conjunto"] = AdSet(adset_id).api_get(fields=[
    "name", "status", "effective_status", "lifetime_budget", "budget_remaining",
    "start_time", "end_time", "destination_type", "optimization_goal",
    "targeting"]).export_all_data()
conf["anuncio"] = Ad(ad["id"]).api_get(fields=[
    "name", "status", "effective_status"]).export_all_data()

dest = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "resultado_aniversario.json")
with open(dest, "w", encoding="utf-8") as f:
    json.dump({"video_id": video_id, "creative_id": creative["id"],
               "adset_id": adset_id, "ad_id": ad["id"],
               "confirmacao": conf, "log": log}, f, ensure_ascii=False, indent=2)
print("\n=> " + dest)
