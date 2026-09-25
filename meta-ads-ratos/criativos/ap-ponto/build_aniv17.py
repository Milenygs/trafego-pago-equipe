#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AP Ponto - campanha de aniversario 17 anos (M_ANIV17_SET26), 09/09/2026.

Dois criativos que a Mileny deixou em
  Area de Trabalho/CLAUDE CODE/clientes/ap-ponto/criativos aniversario
  - WhatsApp Image ... .jpeg  -> estatico 1080x1350 (4:5) "Comprou, ganhou"
  - WhatsApp Video ... .mp4   -> UGC vertical 1080x1920, 27,7s, colaborador falando
                                 dos 17 anos e do presente

Entram nos dois conjuntos da campanha:
  M_ANIV17_RMKT_PRAZO   R$150/dia · conversao no site (agradecimento_lps_rmbh) -> LP do Luna
  [DIRECT_+INDICACAO]   R$ 50/dia · lead pelo Direct do Instagram (LEAD_FROM_IG_DIRECT),
                        rodando para o publico quente do Instagram

Decisao dela em 09/09: a parte de INDICACAO (publico de compradores) fica para depois;
o conjunto roda agora so como Direct para quem ja engajou com o perfil.

Regras permanentes aplicadas:
  - so Instagram (feed, reels, explorar, perfil). Stories fora: R$42 contra R$22 do reels
    no historico da conta. Facebook e Audience Network desligados.
  - todas as features de IA do criativo em OPT_OUT
  - UTM dinamica por anuncio nos criativos de site (achado #4 do diagnostico:
    UTM certa nasce com o anuncio novo, nunca trocada em criativo que ja roda)
  - geo Contagem + Vespasiano, 20 km, so quem mora ou esteve

Uso:
    python build_aniv17.py --dry          mostra o plano, nao escreve
    python build_aniv17.py --conjuntos    so arruma geo/posicionamento/publicos
    python build_aniv17.py                conjuntos + criativos + anuncios PAUSED
    python build_aniv17.py --ativar       idem, com anuncios/conjuntos/campanha ACTIVE
"""
import argparse
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

AQUI = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.abspath(os.path.join(AQUI, "..", ".."))
API = "https://graph.facebook.com/v21.0/"

CONTA = "act_1043516946010441"
PAGINA = "198169833565944"
INSTAGRAM = "17841401339383360"

CAMPANHA = "120245550567960358"          # M_ANIV17_SET26 · 09 a 25/09
ADSET_RMKT = "120245550755120358"        # M_ANIV17_RMKT_PRAZO   R$150/dia
ADSET_DIRECT = "120245559079980358"      # [DIRECT_+INDICACAO]   R$ 50/dia

IMAGEM = os.path.join(AQUI, "aniv17_estatico.jpg")
VIDEO_ID = "1950954295574378"            # UGC subido em 09/09/2026
POST_IG_ANIV = "17906654199473799"       # post do feed 09/09 16h34, 20 curtidas, 7 comentarios

LP = "https://luna.apponto.com.br/"
UTM = ("utm_source=meta&utm_medium=paid&utm_campaign={{campaign.name}}"
       "&utm_content={{ad.name}}&utm_term={{adset.name}}&fbid={{ad.id}}")

# Publicos
PUB_QUALIFICADOS = "120245517541240358"
PUB_SITE_TODOS = "120245517750200358"
PUB_MQL = "120245519551400358"
PUB_SIMULACAO = "120245519552380358"
PUB_IG_ENGAJ = "120245540043470358"       # IG_ENGAJ_AP_PONTO_180D      ~32.100
PUB_IG_VIDEO = "120245540058970358"       # IG_VIDEO_AP_PONTO_50%_180D ~131.200
EXC_COMPRADORES = "120245517540390358"
EXC_COMPLEMENTO = "120245517540780358"

GEO = {
    "cities": [
        {"key": "249756", "radius": 20, "distance_unit": "kilometer", "country": "BR"},
        {"key": "273969", "radius": 20, "distance_unit": "kilometer", "country": "BR"},
    ],
    # sem location_types: `recent` descontinuado em 10/09/2026 (aprendizados 11/09)
}
POSICOES_IG = ["stream", "reels", "explore", "profile_feed"]

# Copy. Recurso, nunca requisito: nada de "renda a partir de R$ X" - o gabarito
# que ensina a resposta do formulario (achado de 31/08).
COPY_SITE = (
    "A AP Ponto está fazendo 17 anos — e quem ganha o presente é você.\n\n"
    "Comprando o seu apartamento até 25/09, você leva um presente para comemorar "
    "com a gente.\n\n"
    "✅ 2 quartos com vaga, em Vespasiano\n"
    "✅ Entrada facilitada, com FGTS\n"
    "✅ Financiamento pelo Minha Casa Minha Vida\n\n"
    "Veja quanto fica a sua parcela e garanta o presente antes de 25/09.\n"
    "Consulte condições."
)
TITULO_SITE = "17 anos de AP Ponto · comprou, ganhou"
DESC_SITE = "Ponto Luna · Vespasiano · até 25/09"

COPY_DIRECT = (
    "A AP Ponto está fazendo 17 anos — e quem ganha o presente é você.\n\n"
    "Até 25/09, quem fecha o apartamento leva um presente para comemorar com a gente.\n\n"
    "Chama aqui no direct: a gente te conta as condições e mostra quanto fica "
    "a sua parcela.\n"
    "Consulte condições."
)

# A conta tem criativos antigos com standard_enhancements / show_summary /
# reveal_details_over_time em OPT_IN (vieram do painel). Aqui tudo sai OPT_OUT.
# standard_enhancements foi descontinuado no spec (erro 100) - opt-out e feature a feature.
SEM_IA = {
    "advantage_plus_creative": {"enroll_status": "OPT_OUT"},
    "enhance_cta": {"enroll_status": "OPT_OUT"},
    "text_optimizations": {"enroll_status": "OPT_OUT"},
    "image_touchups": {"enroll_status": "OPT_OUT"},
    "image_brightness_and_contrast": {"enroll_status": "OPT_OUT"},
    "video_auto_crop": {"enroll_status": "OPT_OUT"},
    "video_uncrop": {"enroll_status": "OPT_OUT"},
    "cv_transformation": {"enroll_status": "OPT_OUT"},
    "site_extensions": {"enroll_status": "OPT_OUT"},
    "ads_with_benefits": {"enroll_status": "OPT_OUT"},
}
SEM_IA_MIN = {
    "advantage_plus_creative": {"enroll_status": "OPT_OUT"},
    "enhance_cta": {"enroll_status": "OPT_OUT"},
    "text_optimizations": {"enroll_status": "OPT_OUT"},
    "image_touchups": {"enroll_status": "OPT_OUT"},
    "video_auto_crop": {"enroll_status": "OPT_OUT"},
}


def token():
    caminho = os.path.join(SKILL, ".env")
    for linha in open(caminho, encoding="utf-8"):
        if linha.strip().startswith("META_ADS_TOKEN"):
            return linha.split("=", 1)[1].strip().strip('"')
    sys.exit("META_ADS_TOKEN nao encontrado em " + caminho)


TOKEN = token()


def get(path, params=None):
    p = dict(params or {})
    p["access_token"] = TOKEN
    with urllib.request.urlopen(API + path + "?" + urllib.parse.urlencode(p)) as r:
        return json.load(r)


def post(path, params, oque):
    corpo = {k: (json.dumps(v) if isinstance(v, (dict, list)) else v)
             for k, v in params.items()}
    corpo["access_token"] = TOKEN
    dados = urllib.parse.urlencode(corpo).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(API + path, data=dados)) as r:
            saida = json.load(r)
            print("  OK   %-44s %s" % (oque, saida.get("id") or saida))
            return saida.get("id") or True
    except urllib.error.HTTPError as e:
        erro = json.loads(e.read().decode("utf-8")).get("error", {})
        print("  ERRO %-44s" % oque)
        print("       msg :", erro.get("message"))
        print("       user:", erro.get("error_user_title"), "|", erro.get("error_user_msg"))
        print("       sub :", erro.get("error_subcode"))
        return None


def post_arquivo(path, campo, caminho, oque):
    """Upload multipart - o create.py image --file esta quebrado (bug do SDK)."""
    limite = uuid.uuid4().hex
    nome = os.path.basename(caminho)
    tipo = mimetypes.guess_type(nome)[0] or "application/octet-stream"
    corpo = [
        ("--%s\r\nContent-Disposition: form-data; name=\"access_token\"\r\n\r\n%s\r\n"
         % (limite, TOKEN)).encode(),
        ("--%s\r\nContent-Disposition: form-data; name=\"%s\"; filename=\"%s\"\r\n"
         "Content-Type: %s\r\n\r\n" % (limite, campo, nome, tipo)).encode(),
        open(caminho, "rb").read(),
        ("\r\n--%s--\r\n" % limite).encode(),
    ]
    req = urllib.request.Request(API + path, data=b"".join(corpo))
    req.add_header("Content-Type", "multipart/form-data; boundary=" + limite)
    try:
        with urllib.request.urlopen(req) as r:
            saida = json.load(r)
            print("  OK   %-44s %s" % (oque, json.dumps(saida)[:140]))
            return saida
    except urllib.error.HTTPError as e:
        print("  ERRO %-44s %s" % (oque, e.read().decode("utf-8")[:400]))
        return None


def checar():
    c = get(CONTA, {"fields": "name,account_status,balance"})
    print("Conta    : %s | status %s | em aberto R$ %.2f"
          % (c.get("name"), c.get("account_status"), int(c.get("balance", 0)) / 100))
    if c.get("account_status") != 1:
        print("BLOQUEADO - fora do status 1 a Meta recusa /adcreatives.")
        return False
    return True


def thumb(video_id):
    dados = get(video_id + "/thumbnails").get("data", [])
    for t in dados:
        if t.get("is_preferred"):
            return t["uri"]
    return dados[0]["uri"] if dados else None


def subir_imagem():
    saida = post_arquivo(CONTA + "/adimages", "filename", IMAGEM, "upload imagem")
    if not saida:
        return None
    imgs = saida.get("images", {})
    return list(imgs.values())[0]["hash"] if imgs else None


# ---------------------------------------------------------------- conjuntos

def targeting_base(publicos):
    """Reescrita completa: a Meta substitui o targeting inteiro, mandar parcial apaga o resto."""
    return {
        "age_min": 25,
        "age_max": 60,
        "geo_locations": GEO,
        "custom_audiences": [{"id": p} for p in publicos],
        "excluded_custom_audiences": [{"id": EXC_COMPRADORES}, {"id": EXC_COMPLEMENTO}],
        "publisher_platforms": ["instagram"],
        "instagram_positions": POSICOES_IG,
        "device_platforms": ["mobile", "desktop"],
        "targeting_relaxation_types": {"lookalike": 0, "custom_audience": 0},
        "targeting_automation": {"advantage_audience": 0, "individual_setting": {"geo": 0}},
    }


def ajustar_conjuntos():
    print()
    print("Conjuntos - geo RMBH, Instagram-only, publicos...")
    post(ADSET_RMKT, {"targeting": targeting_base(
        [PUB_QUALIFICADOS, PUB_SITE_TODOS, PUB_MQL, PUB_SIMULACAO])},
        "targeting RMKT_PRAZO")
    time.sleep(1)
    post(ADSET_DIRECT, {"targeting": targeting_base(
        [PUB_IG_ENGAJ, PUB_IG_VIDEO, PUB_QUALIFICADOS, PUB_SITE_TODOS, PUB_MQL, PUB_SIMULACAO])},
        "targeting DIRECT (+ quente do IG)")


# ---------------------------------------------------------------- criativos

def criar_criativo(nome, params, oque):
    params = dict(params)
    params["name"] = nome
    params["degrees_of_freedom_spec"] = {"creative_features_spec": SEM_IA}
    cid = post(CONTA + "/adcreatives", params, oque)
    if not cid:
        print("       -> repetindo com o subset minimo de opt-out")
        params["degrees_of_freedom_spec"] = {"creative_features_spec": SEM_IA_MIN}
        cid = post(CONTA + "/adcreatives", params, oque + " (min)")
    return cid


def criativo_video_site(t):
    return criar_criativo("ANIV17 - UGC 17 anos - site Luna - set2026", {
        "object_story_spec": {
            "page_id": PAGINA, "instagram_user_id": INSTAGRAM,
            "video_data": {
                "video_id": VIDEO_ID, "message": COPY_SITE, "title": TITULO_SITE,
                "link_description": DESC_SITE, "image_url": t,
                "call_to_action": {"type": "LEARN_MORE", "value": {"link": LP}},
            },
        },
        "url_tags": UTM,
    }, "criativo video/site")


def criativo_imagem_site(img):
    return criar_criativo("ANIV17 - Estatico comprou ganhou - site Luna - set2026", {
        "object_story_spec": {
            "page_id": PAGINA, "instagram_user_id": INSTAGRAM,
            "link_data": {
                "image_hash": img, "link": LP, "message": COPY_SITE,
                "name": TITULO_SITE, "description": DESC_SITE,
                "call_to_action": {"type": "LEARN_MORE", "value": {"link": LP}},
            },
        },
        "url_tags": UTM,
    }, "criativo imagem/site")


def criativo_video_direct(t):
    return criar_criativo("ANIV17 - UGC 17 anos - direct - set2026", {
        "object_story_spec": {
            "page_id": PAGINA, "instagram_user_id": INSTAGRAM,
            "video_data": {
                "video_id": VIDEO_ID, "message": COPY_DIRECT, "title": TITULO_SITE,
                "image_url": t,
                "call_to_action": {"type": "INSTAGRAM_MESSAGE",
                                   "value": {"app_destination": "INSTAGRAM_DIRECT"}},
            },
        },
    }, "criativo video/direct")


def criativo_post_ig_direct():
    """Post organico do feed (leva as curtidas e comentarios do post para o anuncio)."""
    return criar_criativo("ANIV17 - Post feed 17 anos - direct - set2026", {
        "object_story_spec": {"page_id": PAGINA, "instagram_user_id": INSTAGRAM},
        "source_instagram_media_id": POST_IG_ANIV,
        "call_to_action": {"type": "INSTAGRAM_MESSAGE",
                           "value": {"app_destination": "INSTAGRAM_DIRECT"}},
    }, "criativo post-IG/direct")


def criativo_imagem_direct(img):
    """Plano B se a Meta recusar o post organico: mesma arte, midia nova."""
    return criar_criativo("ANIV17 - Estatico comprou ganhou - direct - set2026", {
        "object_story_spec": {
            "page_id": PAGINA, "instagram_user_id": INSTAGRAM,
            "link_data": {
                "image_hash": img, "link": "https://www.instagram.com/apponto",
                "message": COPY_DIRECT, "name": TITULO_SITE,
                "call_to_action": {"type": "INSTAGRAM_MESSAGE",
                                   "value": {"app_destination": "INSTAGRAM_DIRECT"}},
            },
        },
    }, "criativo imagem/direct")


def criar_ad(nome, adset, creative_id, status):
    return post(CONTA + "/ads", {
        "name": nome, "adset_id": adset,
        "creative": {"creative_id": creative_id}, "status": status,
    }, "ad " + nome)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--conjuntos", action="store_true", help="so arruma os conjuntos")
    ap.add_argument("--ativar", action="store_true", help="sobe tudo ACTIVE")
    ap.add_argument("--image-hash", help="pula o upload e usa este hash")
    args = ap.parse_args()

    if not checar():
        sys.exit(1)

    if args.dry:
        print()
        print("Video  :", VIDEO_ID, "1080x1920, 27,7s -> reels/stories nativo")
        print("Imagem :", IMAGEM, "1080x1350 -> feed")
        print("Post IG:", POST_IG_ANIV, "(criativo do Direct, leva a prova social)")
        print("LP     :", LP)
        print("UTM    :", UTM)
        print()
        print("RMKT_PRAZO R$150/dia : video + estatico, CTA Saiba mais -> LP do Luna")
        print("DIRECT     R$ 50/dia : post do feed + video, CTA mensagem no Direct")
        print("Publicos do Direct   : IG_ENGAJ 32,1k + IG_VIDEO50% 131,2k + site/MQL")
        return

    ajustar_conjuntos()
    if args.conjuntos:
        return

    img = args.image_hash or subir_imagem()
    if not img:
        sys.exit("upload da imagem falhou")
    print("  image_hash:", img)

    t = thumb(VIDEO_ID)
    print("  thumb do video:", (t or "SEM THUMB")[:90])

    status = "ACTIVE" if args.ativar else "PAUSED"
    print()
    print("Criativos...")
    cv_site = criativo_video_site(t)
    ci_site = criativo_imagem_site(img)
    cv_dir = criativo_video_direct(t)
    cp_dir = criativo_post_ig_direct() or criativo_imagem_direct(img)

    print()
    print("Anuncios (%s)..." % status)
    if cv_site:
        criar_ad("AD01 - ANIV17 UGC 17 anos [VIDEO]", ADSET_RMKT, cv_site, status)
        time.sleep(1)
    if ci_site:
        criar_ad("AD02 - ANIV17 comprou ganhou [IMAGEM]", ADSET_RMKT, ci_site, status)
        time.sleep(1)
    if cv_dir:
        criar_ad("AD03 - ANIV17 UGC 17 anos [VIDEO][DIRECT]", ADSET_DIRECT, cv_dir, status)
        time.sleep(1)
    if cp_dir:
        criar_ad("AD04 - ANIV17 post 17 anos [DIRECT]", ADSET_DIRECT, cp_dir, status)

    if args.ativar:
        print()
        print("Ligando conjuntos e campanha...")
        post(ADSET_RMKT, {"status": "ACTIVE"}, "ativar RMKT_PRAZO")
        post(ADSET_DIRECT, {"status": "ACTIVE"}, "ativar DIRECT")
        post(CAMPANHA, {"status": "ACTIVE"}, "ativar campanha")

    print()
    print("Conferir: read.py ads-by-campaign --campaign " + CAMPANHA)


if __name__ == "__main__":
    main()
