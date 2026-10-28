#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cheirin Bao MT — criativos da campanha de outubro (03/10/2026).

9 videos da pasta "CLAUDE CODE\\franquias\\cheirin bao\\criativos campanha outubro":
depoimentos de franqueados e o fundador convidando. Todos de captacao (camada 4).

Blueprint: o criativo do DRE 146k (1092194586544651) — mesma pagina, mesmo IG,
formulario [M] FORMS FRANQUIA (2805248149848936), SIGN_UP, link http://fb.me/,
titulo "Verifique Sua Regiao Agora", descricao "A partir de R$ 300 mil" e os
83 recursos de IA em OPT_OUT (copiados do modelo; ele nao tem standard_enhancements).

Copy: sem numero financeiro no texto (o que aparece no video segue a excecao dos
DRE, decidida pela Mileny). Investimento "a partir de R$ 300 mil" como filtro.

Videos convertidos antes para 1080x1920 H.264 (pasta de upload passada em --pasta).
Upload simples (requests), como recomenda o aprendizado de 19/09 para video grande.

Tudo sobe PAUSED. Quem ativa e a Mileny.

Uso:
    python build_outubro_depoimentos.py --pasta <pasta dos mp4> --dry
    python build_outubro_depoimentos.py --pasta <pasta dos mp4>
"""
import argparse
import base64
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

import requests

AQUI = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.abspath(os.path.join(AQUI, "..", ".."))
API = "https://graph.facebook.com/v21.0/"

CONTA = "act_884652616778712"
MODELO = "1092194586544651"      # criativo do Quente - DRE 146k

QUENTE = ("120256940806870212", "Quente - ")
PINO = ("120257337905370212", "[PINO SP] ")
LAL = ("120256940815900212", "LAL - ")

FIM = "Investimento a partir de R$ 300 mil.\nVerifique se a sua região ainda está disponível."

PECAS = [
    {
        "arquivo": "Depoimento franqueado 5.mp4", "thumb": 4.2,
        "rotulo": "AD30 [PROVA] multifranqueado 4 lojas",
        "destinos": [QUENTE, PINO, LAL],
        "copy": (
            "Eram duas lojas. Agora são quatro.\n\n"
            "Neste vídeo, um franqueado Cheirin Bão conta como virou multifranqueado. Para ele, o trabalho "
            "é a quatro mãos: a franqueadora entra com informação e ferramentas, e o franqueado coloca em prática.\n\n"
            "Para quem quer crescer junto com a rede.\n\n" + FIM),
    },
    {
        "arquivo": "dono-falando por ai sobre franquia.mp4", "thumb": 1.5,
        "rotulo": "AD31 [FUNDADOR] franquia tira seu dinheiro",
        "destinos": [QUENTE],
        "copy": (
            "Já ouviu alguém dizer que franquia só serve para tirar o seu dinheiro?\n\n"
            "O fundador da Cheirin Bão responde. E diz a quem ele credita o resultado da rede: ao franqueado "
            "que faz a parte dele, todos os dias.\n\n"
            "Se você quer entender o modelo antes de decidir, a reunião é direto com ele.\n\n" + FIM),
    },
    {
        "arquivo": "Depoimento franqueado 2.mp4", "thumb": 16.0,
        "rotulo": "AD32 [PROVA] como e ser franqueado",
        "destinos": [QUENTE],
        "copy": (
            "Como é ser franqueado Cheirin Bão? Quem responde são os franqueados.\n\n"
            "Eles falam de crescer mês a mês, de planejar o próximo passo e de uma franqueadora que acompanha "
            "cada loja, porque o sucesso dela depende do sucesso do franqueado.\n\n" + FIM),
    },
    {
        "arquivo": "franqueados alexandre e raissa.mp4", "thumb": 10.0,
        "rotulo": "AD33 [PROVA] Alexandre e Raissa premiados",
        "destinos": [QUENTE],
        "copy": (
            "Premiados pela rede. E já a caminho da segunda e da terceira loja.\n\n"
            "O Alexandre e a Raissa contam por que escolheram a Cheirin Bão: se identificaram com a marca e "
            "com as pessoas por trás dela.\n\n" + FIM),
    },
    {
        "arquivo": "franqueado cleber.mp4", "thumb": 4.4,
        "rotulo": "AD34 [EMOCIONAL] Cleber do emprego para a loja",
        "destinos": [PINO],
        "copy": (
            "Do emprego no setor privado para a própria cafeteria.\n\n"
            "O Cleber decidiu empreender, foi atrás de uma franquia e, quando conheceu a Cheirin Bão, se "
            "identificou com o produto e com a marca. Hoje a família inteira vive da loja, e o plano é crescer.\n\n"
            "Você conhece a cafeteria. Na reunião, conhece o negócio.\n\n" + FIM),
    },
    {
        "arquivo": "dono- voce que quer conhcer um negocio.mp4", "thumb": 7.0,
        "rotulo": "AD35 [FUNDADOR] do pe de cafe a xicara",
        "destinos": [PINO],
        "copy": (
            "Do pé de café até a sua xícara.\n\n"
            "A Cheirin Bão cuida do processo inteiro, da fazenda à loja. No vídeo, o fundador apresenta o "
            "negócio e franqueados contam onde chegaram: da primeira loja para a terceira, e agora a quarta.\n\n"
            "Para quem procura um negócio consolidado.\n\n" + FIM),
    },
    {
        "arquivo": "Depoimento franqueado 3.mp4", "thumb": 11.5,
        "rotulo": "AD36 [PROVA] padronizacao e apoio da rede",
        "destinos": [PINO],
        "copy": (
            "O que faz uma loja crescer em oito meses?\n\n"
            "Um franqueado Cheirin Bão responde: seguir a padronização da rede, adaptar à realidade da própria "
            "loja e contar com o apoio da franqueadora no dia a dia.\n\n" + FIM),
    },
    {
        "arquivo": "Depoimento 4 Criativo.mp4", "thumb": 15.5,
        "rotulo": "AD37 [EMOCIONAL] segunda loja em 8 meses",
        "destinos": [PINO],
        "copy": (
            "Oito meses depois da primeira loja, ele já está na segunda.\n\n"
            "Um franqueado Cheirin Bão conta como a franquia mudou o horizonte dele, e por que agora o plano "
            "é crescer na rede.\n\n" + FIM),
    },
    {
        "arquivo": "venha conhecer a maior rede de cafeterias do brasil.mp4", "thumb": 1.2,
        "rotulo": "AD38 [FUNDADOR] cadeia de ponta a ponta",
        "destinos": [PINO, LAL],
        "copy": (
            "Quem apresenta o negócio é o fundador.\n\n"
            "A Cheirin Bão produz, entrega e distribui tudo o que chega à loja do franqueado, de ponta a ponta. "
            "Na reunião, o time explica o modelo inteiro, e o fundador faz questão de participar.\n\n" + FIM),
    },
]


def token():
    with open(os.path.join(SKILL, ".env"), encoding="utf-8") as f:
        for linha in f:
            if linha.strip().startswith("META_ADS_TOKEN"):
                return linha.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("META_ADS_TOKEN nao encontrado no .env")


TOKEN = token()


def get(path, params):
    params = dict(params)
    params["access_token"] = TOKEN
    with urllib.request.urlopen(API + path + "?" + urllib.parse.urlencode(params), timeout=60) as r:
        return json.load(r)


def post(path, params, oque):
    corpo = {k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v)
             for k, v in params.items()}
    corpo["access_token"] = TOKEN
    dados = urllib.parse.urlencode(corpo).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(API + path, data=dados), timeout=120) as r:
            saida = json.load(r)
            print("  OK   %-58s %s" % (oque, saida.get("id")), flush=True)
            return saida.get("id")
    except urllib.error.HTTPError as e:
        erro = json.loads(e.read().decode("utf-8")).get("error", {})
        print("  ERRO %-58s" % oque)
        print("       msg :", erro.get("message"), "| subcode", erro.get("error_subcode"))
        print("       user:", erro.get("error_user_title"), "|", erro.get("error_user_msg"))
        sys.exit(1)


def modelo():
    d = get(MODELO, {"fields": "object_story_spec,degrees_of_freedom_spec"})
    vd = d["object_story_spec"]["video_data"]
    dof = d["degrees_of_freedom_spec"]
    feats = dof.get("creative_features_spec", {})
    feats.pop("standard_enhancements", None)   # aprendizado 10/09: nao reenviar
    assert all(v.get("enroll_status") == "OPT_OUT" for v in feats.values()), "modelo com IA ligada"
    return {
        "page_id": d["object_story_spec"]["page_id"],
        "instagram_user_id": d["object_story_spec"]["instagram_user_id"],
        "title": vd["title"],
        "link_description": vd.get("link_description"),
        "cta": vd["call_to_action"],
        "dof": {"creative_features_spec": feats},
    }


def sobe_video(caminho):
    mb = os.path.getsize(caminho) / (1024 * 1024)
    print("  ... video %s (%.1f MB)" % (os.path.basename(caminho), mb), flush=True)
    with open(caminho, "rb") as f:
        r = requests.post(API + "%s/advideos" % CONTA,
                          data={"access_token": TOKEN, "name": os.path.splitext(os.path.basename(caminho))[0]},
                          files={"source": f}, timeout=900)
    j = r.json()
    if "id" not in j:
        sys.exit("upload falhou: %s" % j)
    vid = j["id"]
    for _ in range(60):                       # espera o processamento (ate ~10 min)
        st = get(vid, {"fields": "status"}).get("status", {}).get("video_status")
        if st == "ready":
            break
        if st == "error":
            sys.exit("video %s com erro de processamento" % vid)
        time.sleep(10)
    print("  OK   %-58s %s" % ("video pronto", vid), flush=True)
    return vid


def sobe_thumb(caminho, seg):
    jpg = os.path.join(tempfile.gettempdir(), "cheirin_thumb_%d.jpg" % int(time.time() * 1000))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(seg), "-i", caminho,
                    "-frames:v", "1", "-q:v", "2", jpg], check=True)
    with open(jpg, "rb") as f:
        corpo = urllib.parse.urlencode({"bytes": base64.b64encode(f.read()).decode(),
                                        "access_token": TOKEN}).encode()
    with urllib.request.urlopen(urllib.request.Request(API + "%s/adimages" % CONTA, data=corpo), timeout=120) as r:
        h = next(iter(json.load(r)["images"].values()))["hash"]
    print("  OK   %-58s %s" % ("capa (%.1fs)" % seg, h), flush=True)
    return h


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pasta", required=True)
    ap.add_argument("--so", help="rotulos ADxx separados por virgula (retomar)")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    m = modelo()
    print("\nCheirin MT — outubro (tudo PAUSED). Modelo %s: form %s, %d recursos OPT_OUT"
          % (MODELO, m["cta"]["value"]["lead_gen_form_id"], len(m["dof"]["creative_features_spec"])))
    pecas = [p for p in PECAS if not a.so or p["rotulo"].split()[0] in a.so.split(",")]
    for p in pecas:
        caminho = os.path.join(a.pasta, p["arquivo"])
        if not os.path.exists(caminho):
            sys.exit("falta o arquivo: %s" % caminho)
        print("\n== %s  ->  %s" % (p["rotulo"], ", ".join(d[1].strip() for d in p["destinos"])))
        for l in p["copy"].splitlines():
            print("     | " + l)
    if a.dry:
        print("\n[dry] nada foi criado.")
        return

    resumo = []
    for p in pecas:
        caminho = os.path.join(a.pasta, p["arquivo"])
        print("\n== %s" % p["rotulo"], flush=True)
        vid = sobe_video(caminho)
        thumb = sobe_thumb(caminho, p["thumb"])
        story = {
            "page_id": m["page_id"],
            "instagram_user_id": m["instagram_user_id"],
            "video_data": {
                "video_id": vid,
                "image_hash": thumb,
                "title": m["title"],
                "link_description": m["link_description"],
                "message": p["copy"],
                "call_to_action": m["cta"],
            },
        }
        cr = post("%s/adcreatives" % CONTA, {"name": "Cheirin — %s" % p["rotulo"],
                                             "object_story_spec": story,
                                             "degrees_of_freedom_spec": m["dof"]}, "criativo")
        for adset, prefixo in p["destinos"]:
            ad = post("%s/ads" % CONTA, {"name": prefixo + p["rotulo"], "adset_id": adset,
                                         "creative": {"creative_id": cr}, "status": "PAUSED"},
                      "anuncio %s" % prefixo.strip())
            resumo.append((p["rotulo"], prefixo.strip(), ad, cr, vid))
            time.sleep(2)
    print("\nRESUMO")
    for r in resumo:
        print("  %-48s %-11s ad %s | criativo %s | video %s" % r)
    print("\nTudo PAUSED. Conferir preview antes de ativar.")


if __name__ == "__main__":
    main()
