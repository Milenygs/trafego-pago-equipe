#!/usr/bin/env python3
"""
Anúncios da campanha "[TRÁFEGO] Cardápio Web | Pedir agora | 12 e 13/09"
Açaí Fruit Show Cidade Nova (act_4213499778794589).

Lê o conjunto de resultado_campanha.json e o vídeo já processado de resultado_video*.json.
Cria o criativo com botão "Pedir agora" (ORDER_NOW) levando ao cardápio web e o anúncio
PAUSED. NÃO ativa: a ativação é da Mileny. Não cria de novo se já existir anúncio com o
mesmo nome no conjunto.

Uso:
  python build_anuncio.py --link URL_DO_CARDAPIO --dry-run            # só valida
  python build_anuncio.py --link URL_DO_CARDAPIO                      # AD01 (O TEU AÇAÍ FAVORITO)
  python build_anuncio.py --link URL_DO_CARDAPIO --video-json resultado_video2.json \
      --nome "AD02 - BANANA E MORANGO [VIDEO]"                        # AD02

Copy: variantes em copy_cardapio_fds.md (endereço e horário pedidos pela loja). Os dois
anúncios usam a mesma variante, para a diferença entre eles ser só o vídeo.
Opt-out das otimizações de IA recurso a recurso (aprendizados 10 e 11/09/2026):
standard_enhancements NÃO pode ir na criação.
"""
import argparse, json, os, sys

SCRIPTS = os.path.join(os.environ["USERPROFILE"], "OneDrive", ".claude", "skills",
                       "meta-ads-ratos", "scripts")
sys.path.insert(0, SCRIPTS)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import requests
from lib import init_api
from facebook_business.api import FacebookAdsApi
from facebook_business.exceptions import FacebookRequestError

AQUI = os.path.dirname(os.path.abspath(__file__))
ACT = "act_4213499778794589"
PAGE_ID = "1063959303475481"
IG_ID = "17841422939839762"                    # @acaifruitshowcidadenova

COPY = {
    "A": {
        "texto": (
            "Sábado e domingo pedem açaí 💜\n\n"
            "Monte o seu do seu jeito, com as frutas, caldas e acompanhamentos que você ama, "
            "e faça o pedido direto pelo nosso cardápio. É só tocar em \"Pedir agora\" 👇\n\n"
            "📍 Av. Antônio Carlos Magalhães (ACM), 133 – Cidade Nova, Feira de Santana\n"
            "🕚 Aberto das 11h às 20h"
        ),
        "titulo": "Açaí Fruit Show Cidade Nova",
        "descricao": "Peça pelo cardápio online",
    },
    "B": {
        "texto": (
            "Bateu a vontade de açaí? A gente resolve 😋\n\n"
            "Escolhe o tamanho, os acompanhamentos e faz o pedido pelo nosso cardápio, "
            "sem fila e sem complicação.\n\n"
            "📍 Av. ACM, 133 – Cidade Nova, Feira de Santana\n"
            "🕚 Hoje, das 11h às 20h"
        ),
        "titulo": "Seu açaí do seu jeito",
        "descricao": "Aberto hoje das 11h às 20h",
    },
}

DOF = {"creative_features_spec": {f: {"enroll_status": "OPT_OUT"} for f in (
    "advantage_plus_creative", "enhance_cta", "inline_comment", "text_optimizations",
    "video_auto_crop", "video_filtering", "video_uncrop")}}

ap = argparse.ArgumentParser()
ap.add_argument("--link", required=True, help="URL do cardápio web da loja")
ap.add_argument("--variante", choices=sorted(COPY), default="A")
ap.add_argument("--nome", default="AD01 - O TEU AÇAÍ FAVORITO [VIDEO]")
ap.add_argument("--video-json", default="resultado_video.json",
                help="vídeo processado a usar (resultado_video.json, resultado_video2.json...)")
ap.add_argument("--dry-run", action="store_true")
args = ap.parse_args()

if not args.link.startswith("https://"):
    raise SystemExit("O link precisa começar com https://")
try:
    r = requests.get(args.link, timeout=20, allow_redirects=True,
                     headers={"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)"})
    print(f"Link respondeu HTTP {r.status_code} (final: {r.url})")
    if r.status_code >= 400:
        raise SystemExit("Link do cardápio não abre — conferir antes de subir.")
except requests.RequestException as e:
    raise SystemExit(f"Link do cardápio não respondeu: {e}")

with open(os.path.join(AQUI, "resultado_campanha.json"), encoding="utf-8") as f:
    adset_id = json.load(f)["adset_id"]
with open(os.path.join(AQUI, args.video_json), encoding="utf-8") as f:
    video = json.load(f)
if (video.get("status") or {}).get("video_status") != "ready":
    raise SystemExit(f"Vídeo {video.get('video_id')} ainda não está pronto: {video.get('status')}")
if not video.get("thumbnail"):
    raise SystemExit(f"Vídeo {video.get('video_id')} sem miniatura — pegar pelo edge /thumbnails.")
saida = os.path.join(AQUI, os.path.basename(args.video_json)
                     .replace("resultado_video", "resultado_anuncio"))

init_api()
api = FacebookAdsApi.get_default_api()


def chamar(metodo, path, params):
    try:
        return api.call(metodo, path, params=params).json()
    except FacebookRequestError as e:
        err = (e.body() or {}).get("error", {})
        raise SystemExit(f"ERRO {metodo} {'/'.join(path)}: {err.get('message')} | "
                         f"subcode {err.get('error_subcode')} | "
                         f"{err.get('error_user_title')} — {err.get('error_user_msg')}")


c = COPY[args.variante]
story = {"page_id": PAGE_ID, "instagram_user_id": IG_ID, "video_data": {
    "video_id": video["video_id"],
    "image_url": video["thumbnail"],
    "message": c["texto"],
    "title": c["titulo"],
    "link_description": c["descricao"],
    "call_to_action": {"type": "ORDER_NOW", "value": {"link": args.link}},
}}

if args.dry_run:
    for fmt in ("INSTAGRAM_STANDARD", "INSTAGRAM_STORY", "INSTAGRAM_REELS"):
        prev = chamar("GET", (ACT, "generatepreviews"), {
            "creative": {"object_story_spec": story, "degrees_of_freedom_spec": DOF},
            "ad_format": fmt, "locale": "pt_BR"})
        print(f"Preview {fmt}: {'ok' if prev.get('data') else prev}")
    print(f"Dry-run ({args.nome}, vídeo {video['video_id']}): nada criado.")
    sys.exit(0)

# --- 0. Não duplicar ------------------------------------------------------------
existentes = chamar("GET", (adset_id, "ads"), {"fields": "name", "limit": 50}).get("data", [])
if any(a.get("name") == args.nome for a in existentes):
    raise SystemExit(f"Já existe o anúncio '{args.nome}' no conjunto {adset_id} — nada criado.")

# --- 1. Criativo ----------------------------------------------------------------
creative_id = chamar("POST", (ACT, "adcreatives"), {
    "name": f"Cardapio Web | {args.nome} | copy {args.variante}",
    "object_story_spec": story,
    "degrees_of_freedom_spec": DOF,
})["id"]
print(f"Criativo criado: {creative_id}")

# --- 2. Anúncio (PAUSED) --------------------------------------------------------
ad_id = chamar("POST", (ACT, "ads"), {
    "name": args.nome,
    "adset_id": adset_id,
    "creative": {"creative_id": creative_id},
    "status": "PAUSED",
})["id"]
print(f"Anúncio criado: {ad_id}")

# --- 3. Conferência -------------------------------------------------------------
cr = chamar("GET", (creative_id,), {
    "fields": "call_to_action_type,object_story_spec,degrees_of_freedom_spec,instagram_user_id"})
ad = chamar("GET", (ad_id,), {"fields": "name,status,effective_status,issues_info"})
feats = ((cr.get("degrees_of_freedom_spec") or {}).get("creative_features_spec") or {})
cta = ((cr.get("object_story_spec") or {}).get("video_data") or {}).get("call_to_action") or {}
checks = {
    "botao_pedir_agora": cr.get("call_to_action_type") == "ORDER_NOW",
    "link_cardapio": (cta.get("value") or {}).get("link") == args.link,
    "ig_da_loja": cr.get("instagram_user_id") == IG_ID,
    "ia_desligada": bool(feats) and all(v.get("enroll_status") == "OPT_OUT" for v in feats.values()),
    "recursos_opt_out": len(feats),
    "anuncio_pausado": ad.get("status") == "PAUSED",
}
previews = {}
for fmt in ("INSTAGRAM_STANDARD", "INSTAGRAM_STORY", "INSTAGRAM_REELS"):
    p = chamar("GET", (creative_id, "previews"), {"ad_format": fmt, "locale": "pt_BR"})
    previews[fmt] = bool(p.get("data"))
checks["previews"] = previews
print(json.dumps(checks, ensure_ascii=False, indent=2))

with open(saida, "w", encoding="utf-8") as f:
    json.dump({"creative_id": creative_id, "ad_id": ad_id, "nome": args.nome,
               "video_id": video["video_id"], "variante": args.variante,
               "link": args.link, "checks": checks, "anuncio": ad},
              f, ensure_ascii=False, indent=2)
print("\n=> " + saida)
