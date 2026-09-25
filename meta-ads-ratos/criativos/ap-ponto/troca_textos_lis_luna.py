#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AP Ponto - troca de texto nos anuncios do Lis e do Luna (10/09/2026).

Decisao da Mileny com os numeros do dono (Abdo, WhatsApp 10/09):
  - sai o requisito de renda, entra recurso: parcela, entrada e composicao de renda
  - Luna: entrada e parcela a partir de R$ 1.000 (R$ 2.000 e o ideal, mas aceita 1.000),
    entrega em dezembro
  - Lis: fica sem numero de parcela (o R$ 1.000 e do Luna); o ganho dele e "esta pronto,
    a chave e sua agora"
  - abertura de aluguel aprovada por ela: "O mesmo valor que voce paga de aluguel ja pode
    ser a parcela do que e seu" (a versao que ela vetou dizia "no fim do ano voce nao tem
    nada no seu nome")

Criativo e imutavel: cada troca de texto nasce como criativo novo, e o anuncio passa a
apontar para ele (`POST /{ad_id}` com `creative`). Os ids dos anuncios nao mudam.

Uso:
    python troca_textos_lis_luna.py --dry
    python troca_textos_lis_luna.py
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
CONTA = "act_1043516946010441"

# --------------------------------------------------------------------- textos

LIS_TITULOS = [
    "Pronto para morar · a chave é sua agora",
    "✅ Apartamento Pronta Entrega",
]
# a linha de requisito sai; entra o recurso equivalente (composicao de renda)
LIS_TROCA = {
    "✅ Renda familiar a partir de R$5.500": "✅ Junte a renda de até 3 pessoas para aprovar",
}

LUNA_TITULOS = [
    "Entrada e parcela a partir de R$ 1.000",
    "Saia do aluguel · chaves em dezembro",
    "2 quartos em Vespasiano · entrega em dezembro",
]
LUNA_CORPOS = [
    "Já pensou em sair do aluguel pagando parcelas a partir de R$ 1.000 na Caixa "
    "— e o imóvel ser seu?\n\n"
    "É isso que o Ponto Luna faz. A entrada começa em R$ 1.000 e a chave sai em dezembro.\n\n"
    "🔑 Entrega em dezembro de 2026\n"
    "✅ Entrada a partir de R$ 1.000\n"
    "✅ Parcelas a partir de R$ 1.000\n"
    "✅ 2 quartos + vaga, 41m², a 10 minutos da Cidade Administrativa\n"
    "✅ Use o FGTS e junte a renda de até 3 pessoas\n"
    "✅ Até 100% financiado + ITBI e Registro grátis\n\n"
    "📲 Faça a sua simulação e veja quanto fica a sua parcela.\n"
    "*Consulte condições.",

    "O mesmo valor que você paga de aluguel já pode ser a parcela do que é seu.\n\n"
    "No Ponto Luna a entrada começa em R$ 1.000 e as parcelas também. "
    "Em dezembro a chave é sua.\n\n"
    "✅ 41m², 2 quartos + vaga de garagem\n"
    "✅ Lazer completo, a 10 minutos da Cidade Administrativa\n"
    "✅ Use o FGTS na entrada\n"
    "✅ Junte a renda de até 3 pessoas para aprovar\n"
    "✅ Financiamento pelo Minha Casa Minha Vida\n\n"
    "📲 Simule agora, sem compromisso.\n"
    "*Consulte condições.",
]

# --------------------------------------------------------------------- alvos

SEM_IA = {
    "advantage_plus_creative": {"enroll_status": "OPT_OUT"},
    "enhance_cta": {"enroll_status": "OPT_OUT"},
    "text_optimizations": {"enroll_status": "OPT_OUT"},
    "image_touchups": {"enroll_status": "OPT_OUT"},
    "video_auto_crop": {"enroll_status": "OPT_OUT"},
}

LIS_ADS = ["120245536110730358", "120245536110740358"]
LUNA_ADS = ["120245536185530358", "120245536188510358", "120245536190860358",
            "120245536195590358", "120245536173270358", "120245536175560358",
            "120245536167200358"]


def token():
    for linha in open(os.path.join(SKILL, ".env"), encoding="utf-8"):
        if linha.strip().startswith("META_ADS_TOKEN"):
            return linha.split("=", 1)[1].strip().strip('"')
    sys.exit("META_ADS_TOKEN nao encontrado")


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
    try:
        with urllib.request.urlopen(urllib.request.Request(
                API + path, data=urllib.parse.urlencode(corpo).encode())) as r:
            saida = json.load(r)
            print("  OK   %-46s %s" % (oque, saida.get("id") or saida))
            return saida.get("id") or True
    except urllib.error.HTTPError as e:
        erro = json.loads(e.read().decode("utf-8")).get("error", {})
        print("  ERRO %-46s" % oque)
        print("       msg :", erro.get("message"))
        print("       user:", erro.get("error_user_title"), "|", erro.get("error_user_msg"))
        print("       sub :", erro.get("error_subcode"))
        return None


def ler_ad(ad_id):
    return get(ad_id, {"fields": "id,name,creative{id,name,object_story_spec,"
                                 "asset_feed_spec,degrees_of_freedom_spec,url_tags,"
                                 "instagram_user_id}"})


def novo_criativo(base, titulos, corpos, sufixo):
    """Clona o criativo trocando so os textos do asset_feed_spec."""
    c = base["creative"]
    afs = dict(c.get("asset_feed_spec") or {})
    afs["titles"] = [{"text": t} for t in titulos]
    afs["bodies"] = [{"text": b} for b in corpos]

    # a leitura devolve image_url E image_hash no video_data; a criacao aceita
    # so um dos dois (subcode 1443051). Fica o hash, que nao expira.
    oss = json.loads(json.dumps(c.get("object_story_spec") or {}))
    midia = oss.get("video_data") or oss.get("link_data") or {}
    if midia.get("image_hash") and midia.get("image_url"):
        midia.pop("image_url")

    params = {
        "name": (c.get("name") or "criativo")[:60] + " " + sufixo,
        "object_story_spec": oss,
        "asset_feed_spec": afs,
    }
    # o spec herdado vem com standard_enhancements OPT_IN, que a Meta descontinuou
    # (subcode 3858504) - e que a Mileny nao quer de qualquer forma. Entra o subset
    # de opt-out feature a feature.
    params["degrees_of_freedom_spec"] = {"creative_features_spec": SEM_IA}
    if c.get("url_tags"):
        params["url_tags"] = c["url_tags"]
    return post(CONTA + "/adcreatives", params, "criativo " + sufixo)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()

    # um criativo serve varios anuncios; cria uma vez e reaproveita
    feitos = {}

    print("PONTO LIS")
    for ad in LIS_ADS:
        base = ler_ad(ad)
        c = base["creative"]
        afs = c.get("asset_feed_spec") or {}
        corpos = []
        for b in afs.get("bodies", []):
            texto = b["text"]
            for de, para in LIS_TROCA.items():
                texto = texto.replace(de, para)
            corpos.append(texto)
        print("  %s | criativo atual %s" % (base["name"][:40], c["id"]))
        if args.dry:
            print("     titulos ->", LIS_TITULOS)
            print("     corpos  -> %d (linha de renda trocada)" % len(corpos))
            continue
        if c["id"] not in feitos:
            feitos[c["id"]] = novo_criativo(base, LIS_TITULOS, corpos, "TEXTO SET26")
            time.sleep(1)
        if feitos[c["id"]]:
            post(ad, {"creative": {"creative_id": feitos[c["id"]]}}, "trocar no ad " + ad)
            time.sleep(1)

    print()
    print("PONTO LUNA")
    for ad in LUNA_ADS:
        base = ler_ad(ad)
        c = base["creative"]
        print("  %s | criativo atual %s" % (base["name"][:40], c["id"]))
        if args.dry:
            print("     titulos ->", LUNA_TITULOS)
            print("     corpos  -> 2 novos")
            continue
        if c["id"] not in feitos:
            feitos[c["id"]] = novo_criativo(base, LUNA_TITULOS, LUNA_CORPOS, "TEXTO SET26")
            time.sleep(1)
        if feitos[c["id"]]:
            post(ad, {"creative": {"creative_id": feitos[c["id"]]}}, "trocar no ad " + ad)
            time.sleep(1)

    print()
    print("criativos novos:", json.dumps(feitos, ensure_ascii=False))


if __name__ == "__main__":
    main()
