#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cheirin Bao MT — publicos do conjunto novo "quente + LAL" (14/10/2026).

Copia, nesta conta, os publicos de engajamento do Instagram do print da Mileny
(120D). Fontes ig_business tiradas das regras de publicos que ja existem aqui:
- 9317933804989351 = @cheirinbaofranquias (IG_engja_franquiacheirin)
- 934954819849986  = @cheirinbao (IG_ENGAJ_CHERINBAO_*)
O "[IG CHEIRINBAO] Envolvimento todos - 120D" antigo (120216062349100212) esta
"pequeno demais" e expirando: por isso sai um novo.

Video 50% da Cheirin NAO sobe pela API (video organico do IG, subcode 1870049,
aprendizado de 08/09): criar no painel.
Estado salvo em estado_publicos_quente_lal_1410.json (nao recria o que ja existe).
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.abspath(os.path.join(AQUI, "..", ".."))
API = "https://graph.facebook.com/v21.0/"
CONTA = "act_884652616778712"
ESTADO = os.path.join(AQUI, "estado_publicos_quente_lal_1410.json")

IG_FRANQUIAS = 9317933804989351
IG_CHEIRIN = 934954819849986
DIAS = 120

PUBLICOS = [
    ("cbf_engajou", "[IG CB FRANQUIAS] Engajou post - 120D", IG_FRANQUIAS, "ig_business_profile_engaged"),
    ("cbf_mensagem", "[IG CB FRANQUIAS] Enviou mensagem - 120D", IG_FRANQUIAS, "ig_user_messaged_business"),
    ("cbf_todos", "[IG CB FRANQUIAS] Envolvimento todos - 120D", IG_FRANQUIAS, "ig_business_profile_all"),
    ("cbf_salvou", "[IG CB FRANQUIAS] Salvou - 120D", IG_FRANQUIAS, "ig_business_profile_ad_saved"),
    ("cbf_visitou", "[IG CB FRANQUIAS] Visitou - 120D", IG_FRANQUIAS, "ig_business_profile_visit"),
    ("cb_todos", "[IG CHEIRIN BÃO] Envolvimento todos - 120D", IG_CHEIRIN, "ig_business_profile_all"),
]


def token():
    with open(os.path.join(SKILL, ".env"), encoding="utf-8") as f:
        for linha in f:
            if linha.strip().startswith("META_ADS_TOKEN"):
                return linha.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("META_ADS_TOKEN nao encontrado")


TOKEN = token()


def post(path, params, oque):
    corpo = {k: (json.dumps(v) if isinstance(v, (dict, list)) else v) for k, v in params.items()}
    corpo["access_token"] = TOKEN
    try:
        with urllib.request.urlopen(urllib.request.Request(API + path, data=urllib.parse.urlencode(corpo).encode()),
                                    timeout=120) as r:
            saida = json.load(r)
            print("  OK   %-48s %s" % (oque, saida.get("id")), flush=True)
            return saida.get("id")
    except urllib.error.HTTPError as e:
        erro = json.loads(e.read().decode("utf-8")).get("error", {})
        print("  ERRO %-48s %s | sub %s | %s" % (oque, erro.get("message"), erro.get("error_subcode"),
                                                 erro.get("error_user_msg")))
        return None


def regra(fonte, evento):
    return {"inclusions": {"operator": "or", "rules": [{
        "event_sources": [{"type": "ig_business", "id": fonte}],
        "retention_seconds": DIAS * 86400,
        "filter": {"operator": "and", "filters": [{"field": "event", "operator": "eq", "value": evento}]}}]}}


def main():
    e = json.load(open(ESTADO, encoding="utf-8")) if os.path.exists(ESTADO) else {}
    for chave, nome, fonte, evento in PUBLICOS:
        if e.get(chave):
            print("  JA   %-48s %s" % (nome, e[chave]))
            continue
        e[chave] = post("%s/customaudiences" % CONTA, {
            "name": nome,
            "description": "%s (%d dias). Criado em 14/10/2026 para o conjunto quente + LAL." % (evento, DIAS),
            "rule": regra(fonte, evento), "prefill": "true"}, nome)
        json.dump(e, open(ESTADO, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(e, ensure_ascii=False))


if __name__ == "__main__":
    main()
