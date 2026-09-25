#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Boali — 4 videos novos da pasta "criativos setembro anderson" (19/09/2026).

Pecas (os 3 marcados "usar este" + o 34, que a Mileny mandou so para os pinos):
  AD16 Rodrigo "melhor momento" (400 operacoes)  -> CP 04 quente + CP 05 LAL
  AD17 Rodrigo "sem fogao e sem chef"            -> CP 05 LAL
       (fora do CP 04: o AD15 Anderson ja cobre o angulo "sem fogao" la)
  AD18 Inauguracao Vila Olimpia (Adriano, 9->12) -> CP 04 quente
       (fora do CP 08: o AD19 usa o mesmo trecho do Adriano la)
  AD19 Rodrigo fala do Adriano                   -> CP 08 onda 1 + CP 08 capital
       (pedido da Mileny: so na campanha dos pinos)

Copy: uma por peca e temperatura. Sem numero financeiro (a ficha da Boali esta
"a definir" = proibido); so o investimento R$359.000, que filtra.
V1/V2 de texto ficam para outra rodada: esta rodada testa VIDEO novo.

Blueprint, form, CTA e opt-out de IA: os do build_depoimento.py.

Uso:
    python build_rodrigo_setembro.py --dry       # le a conta e mostra tudo, nao cria
    python build_rodrigo_setembro.py             # cria tudo PAUSED (retoma pelo JSON)
    python build_rodrigo_setembro.py --ativar    # ativa os ads criados e rele
"""
import argparse
import base64
import json
import os
import subprocess
import sys
import tempfile
import unicodedata
import urllib.parse
import urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "boali-depoimento"))
import build_depoimento as base  # noqa: E402

PASTA = os.path.expandvars(
    r"%USERPROFILE%\OneDrive\Área de Trabalho\CLAUDE CODE\franquias\boali"
    r"\criativos setembro anderson")
ESTADO = os.path.join(AQUI, "criados_2026-09-19.json")

CP04 = ("120249949945780156", "CP 04 · QUENTE 180D FORMS", "")
CP05 = ("120250111279470156", "CP 05 · LAL 1%", "[LAL] ")
CP08_ONDA1 = ("120251217473750156", "CP 08 · PIN LOJA+CIDADE ONDA 1", "")
CP08_CAPITAL = ("120251313225380156", "CP 08 · PIN LOJAS CAPITAL", "")

INVEST = "✅ Investimento a partir de R$359.000\n\n"
DESCRICAO = "A partir de R$359 mil"

AD16_QUENTE = (
    "Você já conhece a Boali. Talvez não conheça o plano.\n\n"
    "A meta é chegar a 400 operações nos próximos 4 a 5 anos. Hoje a rede está "
    "entre 30% e 50% desse caminho. Quem explica é o Rodrigo, dono da Boali.\n\n"
    "Quer dizer: você entra numa marca consolidada, com mais da metade da "
    "expansão ainda pela frente.\n\n"
    "✅ 19 anos de mercado\n"
    "✅ 25 estados e mais de 100 cidades\n"
    + INVEST +
    "Se esse investimento faz sentido para o seu momento, fale com um consultor "
    "e veja se a sua região está disponível.\n"
    "👇"
)

AD16_FRIO = (
    "Rede nova tem espaço. Rede grande tem estrutura.\n\n"
    "A Boali está no meio do caminho: já são 25 estados e mais de 100 cidades, "
    "e a meta é chegar a 400 operações nos próximos 4 a 5 anos. Quem explica é "
    "o Rodrigo, dono da Boali.\n\n"
    "✅ Franquia de alimentação saudável\n"
    "✅ 19 anos de mercado\n"
    + INVEST +
    "Se esse investimento faz sentido para o seu momento, veja se a sua cidade "
    "ainda está disponível.\n"
    "👇"
)

AD17_FRIO = (
    "Sem fogão. Sem chef.\n\n"
    "Numa rede de alimentação, soa estranho. Na Boali, é o que faz o modelo "
    "funcionar: a própria rede padroniza a comida e serve o mesmo prato, com o "
    "mesmo padrão e o mesmo preço, em mais de 100 cidades de 25 estados.\n\n"
    "Para o franqueado, isso significa uma loja sem cozinha pesada e sem "
    "depender de chef. Quem explica é o Rodrigo, dono da Boali.\n\n"
    "✅ 19 anos de mercado\n"
    "✅ Operação padronizada\n"
    + INVEST +
    "Se esse investimento faz sentido para o seu momento, veja se a sua cidade "
    "ainda está disponível.\n"
    "👇"
)

AD18_QUENTE = (
    "9 operações. E ele quer mais.\n\n"
    "Esse é o Adriano, franqueado da Boali do Shopping Vila Olímpia, em São "
    "Paulo. Com o food truck e mais 2 pontos em estudo, ele vai chegar a 12 "
    "operações.\n\n"
    "Não é exceção: a maioria dos franqueados Boali tem mais de uma operação. "
    "O modelo foi feito para investir, empreender e crescer com a rede, que já "
    "abre lojas em Portugal e em Miami.\n\n"
    "✅ 19 anos de mercado\n"
    "✅ 25 estados e mais de 100 cidades\n"
    + INVEST +
    "Se esse investimento faz sentido para o seu momento, fale com um consultor "
    "e veja se a sua região está disponível.\n"
    "👇"
)

AD19_PINOS = (
    "Uma loja. 6, no máximo 7 funcionários.\n\n"
    "O Rodrigo, dono da Boali, mostra como a operação é enxuta. E conta o caso "
    "do Adriano, franqueado da Vila Olímpia: 9 operações, e a caminho de 12.\n\n"
    "Você já conhece a Boali do lado do cliente. Este vídeo mostra o lado de "
    "quem investe.\n\n"
    "✅ 19 anos de mercado\n"
    "✅ Equipe enxuta por loja\n"
    + INVEST +
    "Ainda há praças abertas na sua região. Se esse investimento faz sentido "
    "para o seu momento, fale com um consultor.\n"
    "👇"
)

PECAS = [
    {
        "chave": "AD16",
        "arquivo": "30 - Rodrigo RB Melhor investimento 2",
        "rotulo": "AD16 [FUNDADOR] [VIDEO] MELHOR MOMENTO 400 OPERACOES RODRIGO",
        "thumb_seg": 1,
        "titulo": "A meta: 400 operações",
        "grupos": [("A", AD16_QUENTE, [CP04]), ("B", AD16_FRIO, [CP05])],
    },
    {
        "chave": "AD17",
        "arquivo": "BOALI 33 Rodrigo RB",
        "rotulo": "AD17 [FUNDADOR] [VIDEO] SEM FOGAO SEM CHEF PADRONIZACAO RODRIGO",
        "thumb_seg": 2,
        "titulo": "Franquia sem fogão e sem chef",
        "grupos": [("A", AD17_FRIO, [CP05])],
    },
    {
        "chave": "AD18",
        "arquivo": "inaugura",
        "rotulo": "AD18 [PROVA] [VIDEO] INAUGURACAO VILA OLIMPIA ADRIANO 12 OPERACOES",
        # O quadro 0 e vista aerea da cidade. Aos 16s e o Rodrigo com "12 operacoes".
        "thumb_seg": 16,
        "titulo": "Inauguração Boali Vila Olímpia",
        "grupos": [("A", AD18_QUENTE, [CP04])],
    },
    {
        "chave": "AD19",
        "arquivo": "34 - rodrigo fala sobre o Adriano",
        "rotulo": "AD19 [PROVA] [VIDEO] RODRIGO FALA DO ADRIANO LOJA ENXUTA",
        # Nao usar 2-4s: mostram "150.000R$" na tela. Aos 5,5s: "no maximo sete?".
        "thumb_seg": 5.5,
        "titulo": "Loja enxuta, várias unidades",
        "grupos": [("A", AD19_PINOS, [CP08_ONDA1, CP08_CAPITAL])],
    },
]

DESTINOS = [CP04, CP05, CP08_ONDA1, CP08_CAPITAL]


def acha_video(prefixo):
    achados = [a for a in os.listdir(PASTA)
               if unicodedata.normalize("NFC", a).startswith(prefixo)]
    if len(achados) != 1:
        sys.exit("prefixo %r achou %r" % (prefixo, achados))
    return os.path.join(PASTA, achados[0])


def carrega():
    if os.path.exists(ESTADO):
        with open(ESTADO, encoding="utf-8") as f:
            return json.load(f)
    return {}


def salva(estado):
    with open(ESTADO, "w", encoding="utf-8") as f:
        json.dump(estado, f, ensure_ascii=False, indent=2)


def le_conta():
    print("\n  ESTADO DOS CONJUNTOS DE DESTINO")
    for adset_id, nome, _p in DESTINOS:
        a = base.get(adset_id, {"fields": "name,status,effective_status,daily_budget,"
                                          "campaign{name,status,effective_status}"})
        c = a.get("campaign", {})
        verba = int(a["daily_budget"]) / 100 if a.get("daily_budget") else None
        print("\n  %s  %s" % (adset_id, nome))
        print("    conjunto %s/%s · verba %s" % (a["status"], a["effective_status"],
                                                "R$%.0f/dia" % verba if verba else "CBO"))
        print("    campanha %s/%s · %s" % (c.get("status"), c.get("effective_status"),
                                           c.get("name")))
        ads = base.get("%s/ads" % adset_id,
                       {"fields": "name,status,effective_status", "limit": 50})["data"]
        for ad in ads:
            if ad["effective_status"] not in ("ARCHIVED", "DELETED"):
                print("      %-9s %-15s %s" % (ad["status"], ad["effective_status"],
                                              ad["name"]))


def sobe_thumb(video, seg, chave):
    jpg = os.path.join(tempfile.gettempdir(), "boali_%s_thumb.jpg" % chave)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(seg), "-i", video,
                    "-frames:v", "1", "-q:v", "2", jpg], check=True)
    # scripts/create.py image quebra no SDK atual (16/09): vai direto em /adimages.
    with open(jpg, "rb") as f:
        corpo = urllib.parse.urlencode({
            "bytes": base64.b64encode(f.read()).decode(),
            "access_token": base.TOKEN,
        }).encode()
    req = urllib.request.Request(base.API + "%s/adimages" % base.CONTA, data=corpo)
    with urllib.request.urlopen(req, timeout=120) as r:
        imagens = json.load(r)["images"]
    h = next(iter(imagens.values()))["hash"]
    print("  OK   %-52s %s" % ("miniatura %s (%ss)" % (chave, seg), h))
    return h


def sobe_video_simples(video):
    """Envio simples (sem partes) em /advideos. O chunked do create.py falhou 2x no
    video de 56 MB com code 1 "Please reduce the amount of data" (19/09/2026)."""
    import requests
    mb = os.path.getsize(video) / (1024 * 1024)
    print("  ... subindo video (%.1f MB, envio simples), pode demorar" % mb)
    with open(video, "rb") as f:
        r = requests.post(base.API + "%s/advideos" % base.CONTA,
                          data={"access_token": base.TOKEN,
                                "name": os.path.splitext(os.path.basename(video))[0]},
                          files={"source": (os.path.basename(video), f, "video/mp4")},
                          timeout=900)
    saida = r.json()
    if "id" not in saida:
        sys.exit("falhou o upload: %s" % saida.get("error", saida))
    print("  OK   %-52s %s" % ("video", saida["id"]))
    return saida["id"]


def cria(estado):
    for p in PECAS:
        e = estado.setdefault(p["chave"], {"ads": {}})
        video = acha_video(p["arquivo"])
        print("\n  %s — %s" % (p["chave"], os.path.basename(video)))
        if not e.get("video_id"):
            e["video_id"] = sobe_video_simples(video)
            salva(estado)
        if not e.get("thumb"):
            e["thumb"] = sobe_thumb(video, p["thumb_seg"], p["chave"])
            salva(estado)
        for letra, copy, destinos in p["grupos"]:
            ck = "criativo_" + letra
            if not e.get(ck):
                story = {
                    "page_id": base.PAGE,
                    "instagram_user_id": base.IG,
                    "video_data": {
                        "video_id": e["video_id"],
                        "image_hash": e["thumb"],
                        "title": p["titulo"],
                        "link_description": DESCRICAO,
                        "message": copy,
                        "call_to_action": {
                            "type": "SIGN_UP",
                            "value": {"lead_gen_form_id": base.FORM,
                                      "link": "http://fb.me/"},
                        },
                    },
                }
                e[ck] = base.post("%s/adcreatives" % base.CONTA, {
                    "name": "Boali — %s [%s]" % (p["rotulo"], letra),
                    "object_story_spec": story,
                    "degrees_of_freedom_spec": base.SEM_IA,
                }, "criativo %s %s" % (p["chave"], letra))
                salva(estado)
            for adset_id, nome, prefixo in destinos:
                if adset_id in e["ads"]:
                    continue
                e["ads"][adset_id] = base.post("%s/ads" % base.CONTA, {
                    "name": prefixo + p["rotulo"],
                    "adset_id": adset_id,
                    "creative": {"creative_id": e[ck]},
                    "status": "PAUSED",
                }, "ad %s em %s" % (p["chave"], nome))
                salva(estado)
    print("\n  Tudo criado PAUSED. Estado em %s" % ESTADO)


def ativa(estado):
    for p in PECAS:
        for adset_id, ad_id in estado.get(p["chave"], {}).get("ads", {}).items():
            base.post(ad_id, {"status": "ACTIVE"}, "ativa %s em %s" % (p["chave"], adset_id))
    print("\n  RELEITURA")
    for p in PECAS:
        for adset_id, ad_id in estado.get(p["chave"], {}).get("ads", {}).items():
            ad = base.get(ad_id, {"fields": "name,status,effective_status,issues_info,"
                                            "creative{id}"})
            print("  %s  %-9s %-16s %s  issues=%s" % (
                ad_id, ad["status"], ad["effective_status"], ad["name"],
                ad.get("issues_info", "-")))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--ativar", action="store_true")
    a = ap.parse_args()

    if a.ativar:
        ativa(carrega())
        return

    print("\nBoali — 4 videos de setembro (%s)" % ("DRY" if a.dry else "cria PAUSED"))
    for p in PECAS:
        print("\n  %s · %s" % (p["chave"], os.path.basename(acha_video(p["arquivo"]))))
        print("    título (%d/40): %s · descrição (%d/30): %s" % (
            len(p["titulo"]), p["titulo"], len(DESCRICAO), DESCRICAO))
        for letra, copy, destinos in p["grupos"]:
            print("    [%s] -> %s" % (letra, ", ".join(d[1] for d in destinos)))
            print("        antes do 'ver mais' (125): %r" % copy[:125])
    le_conta()
    if a.dry:
        print("\n  [dry] nada foi criado.")
        return
    cria(carrega())


if __name__ == "__main__":
    main()
