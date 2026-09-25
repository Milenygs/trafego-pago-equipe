#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Casa de Vidro Paraty — 2 videos novos nos conjuntos de GEO-PIN (09/09/2026).

Pedido da Mileny: subir os 2 videos que ela deixou na pasta do desktop
("video guilbert" e "A IA nao vai substituir isso") e PAUSAR o criativo antigo.

Os 2 videos entram nos DOIS conjuntos de pino, para o teste rodar igual nos
dois publicos. O criativo e clonado do que ja roda (1581729363451112): mesma
copy aprovada, mesmo CTA, mesmo destino. So a midia muda — assim o que a
metrica compara e o video, nao a copy.

Uso:
    python build_videos_geopin.py --dry   # mostra o que vai fazer, nao escreve
    python build_videos_geopin.py         # cria os criativos + 4 ads ACTIVE
                                          # e pausa os 2 ads antigos
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.abspath(os.path.join(AQUI, "..", ".."))
API = "https://graph.facebook.com/v21.0/"

CONTA = "act_792396727164193"
PAGINA = "949028168287242"
INSTAGRAM = "17841472733937596"

CAMPANHA = "120249369648020510"          # [GEO-PIN] ALTO PADRAO SP-RJ - 08/09
ADSETS = [
    ("120249369649830510", "PIN MORA"),      # bairros alto padrao SP-RJ
    ("120249369651930510", "PIN DESTINO"),   # Angra/Ilhabela/Buzios/Campos/Paraty
]

CRIATIVO_MODELO = "1581729363451112"     # o que roda hoje — fonte da copy/CTA
ADS_A_PAUSAR = ["120249376195720510", "120249376198040510"]

VIDEOS = [
    {"video_id": "1055776960704207",
     "nome": "CDV - Video Guilbert - 09/09/2026",
     "ad": "AD - Guilbert"},
    {"video_id": "2866427223725338",
     "nome": "CDV - A IA nao vai substituir isso - 09/09/2026",
     "ad": "AD - A IA nao substitui"},
]

# Fallback caso a Meta recuse o spec completo lido do criativo modelo.
# Nomes validos mudam com frequencia — ver aprendizados.md (subcode 3858504).
SEM_ENHANCEMENTS_MIN = {
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
    params = dict(params or {})
    params["access_token"] = TOKEN
    url = API + path + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url) as r:
        return json.load(r)


def post(path, params, oque):
    corpo = {k: (json.dumps(v) if isinstance(v, (dict, list)) else v)
             for k, v in params.items()}
    corpo["access_token"] = TOKEN
    dados = urllib.parse.urlencode(corpo).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(API + path, data=dados)) as r:
            saida = json.load(r)
            print("  OK   %-40s %s" % (oque, saida.get("id") or saida))
            return saida.get("id") or True
    except urllib.error.HTTPError as e:
        erro = json.loads(e.read().decode("utf-8")).get("error", {})
        print("  ERRO %-40s" % oque)
        print("       msg :", erro.get("message"))
        print("       user:", erro.get("error_user_title"), "|", erro.get("error_user_msg"))
        print("       sub :", erro.get("error_subcode"))
        return None


def checar():
    conta = get(CONTA, {"fields": "name,account_status,balance"})
    status = conta.get("account_status")
    print("Conta    :", conta.get("name"))
    print("Status   :", status, "(1=ativa, 3=UNSETTLED)")
    print("Em aberto: R$ %.2f" % (int(conta.get("balance", 0)) / 100))
    if status != 1:
        print("BLOQUEADO — fora do status 1 a Meta recusa /adcreatives (subcode 1487194).")
        return False
    return True


def thumb(video_id):
    """Thumbnail marcada como preferida pela Meta; senao a primeira."""
    dados = get(video_id + "/thumbnails").get("data", [])
    if not dados:
        return None
    for t in dados:
        if t.get("is_preferred"):
            return t["uri"]
    return dados[0]["uri"]


def modelo():
    c = get(CRIATIVO_MODELO, {"fields": "object_story_spec,degrees_of_freedom_spec"})
    vd = c["object_story_spec"]["video_data"]
    return {
        "message": vd["message"],
        "cta": vd["call_to_action"],
        "dof": c.get("degrees_of_freedom_spec", {}).get("creative_features_spec", {}),
    }


def criar_criativo(v, base, dof):
    spec = {
        "page_id": PAGINA,
        "instagram_user_id": INSTAGRAM,
        "video_data": {
            "video_id": v["video_id"],
            "message": base["message"],
            "image_url": v["thumb"],
            "call_to_action": base["cta"],
        },
    }
    return post(CONTA + "/adcreatives", {
        "name": v["nome"],
        "object_story_spec": spec,
        "degrees_of_freedom_spec": {"creative_features_spec": dof},
    }, "criativo " + v["ad"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()

    if not checar():
        sys.exit(1)

    base = modelo()
    print()
    print("Copy herdada do criativo %s (aprovada, ja no ar):" % CRIATIVO_MODELO)
    print("  " + base["message"].replace("\n", "\n  ")[:200] + "...")
    print("CTA:", json.dumps(base["cta"], ensure_ascii=False))
    print("Features de IA no spec do modelo:", len(base["dof"]), "(todas OPT_OUT)")

    for v in VIDEOS:
        v["thumb"] = thumb(v["video_id"])
        print()
        print("Video %s -> %s" % (v["video_id"], v["nome"]))
        print("  thumb:", (v["thumb"] or "SEM THUMB")[:100])

    if args.dry:
        print()
        print("--dry: nada foi criado.")
        print("Criaria %d criativos e %d anuncios ACTIVE, e pausaria %s"
              % (len(VIDEOS), len(VIDEOS) * len(ADSETS), ADS_A_PAUSAR))
        return

    print()
    print("Criando criativos...")
    for v in VIDEOS:
        cid = criar_criativo(v, base, base["dof"] or SEM_ENHANCEMENTS_MIN)
        if not cid and base["dof"]:
            print("       -> repetindo com o subset minimo de opt-out")
            cid = criar_criativo(v, base, SEM_ENHANCEMENTS_MIN)
        v["creative_id"] = cid
        time.sleep(1)

    print()
    print("Criando anuncios (ACTIVE)...")
    for v in VIDEOS:
        if not v.get("creative_id"):
            print("  --   %-40s sem criativo, pulando" % v["ad"])
            continue
        for adset_id, apelido in ADSETS:
            post(CONTA + "/ads", {
                "name": "%s - %s" % (v["ad"], apelido),
                "adset_id": adset_id,
                "creative": {"creative_id": v["creative_id"]},
                "status": "ACTIVE",
            }, "%s - %s" % (v["ad"], apelido))
            time.sleep(1)

    print()
    print("Pausando os anuncios antigos...")
    for ad in ADS_A_PAUSAR:
        post(ad, {"status": "PAUSED"}, "pausar " + ad)
        time.sleep(1)

    print()
    print("Conferir a entrega em 1-2h:")
    print("  read.py ads --account %s --campaign %s" % (CONTA, CAMPANHA))


if __name__ == "__main__":
    main()
