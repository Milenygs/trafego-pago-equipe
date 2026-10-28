#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cheirin Bao MT — publicos quentes de alta intencao que a conta nao tinha (03/10/2026).

1. M | FORM ABRIU E NAO ENVIOU 90D — lead_generation_dropoff no formulario ATUAL
   (2805248149848936, [M] FORMS FRANQUIA) e no FORM Bl 2 (3282443085242041). Os
   publicos antigos de "nao enviaram" nao incluem o form atual (por isso < 1.000).
2. M | FORM ENVIOU 90D — lead_generation_submitted nos mesmos forms. Exclusao.
3. M | VIDEO FRANQUIA ANUNCIOS 75% 180D — quem viu 75% dos videos de franquia que
   rodaram em anuncio. Usa o video_id DE TOPO do criativo (copia na Pagina), como
   manda o aprendizado de 26/09. Ficam de fora os videos so de produto/experiencia.

Formato do 3 (legado): subtype ENGAGEMENT, retention_days, prefill, rule = lista.
Lead form: no maximo 90 dias de retencao.
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
PAGE = 639778989482866
FORMS = [2805248149848936, 3282443085242041]

# video_id de topo (Pagina) dos anuncios de franquia nas campanhas 09, 05 e 14,
# lidos em 03/10/2026. Fora: experiencia-cliente-produto v1/v2 (curtos e longos),
# criativo-3-final e waltinho-degustacao (so produto).
VIDEOS = [
    2311049673084094, 1775582683594076, 2490855301411837, 939179849244995, 1132181326155840,
    968991919584476, 3550632418444621, 4087479881551066, 929772892851992, 1937108796963443,
    1806466700358889, 2381435379139589, 1643205300747385, 4487542438184164, 930148180163575,
    1511560307657314, 1448843840421372, 1870743307245059, 3607637529394458, 1436711341695627,
    2982991625383862, 1123363050168331, 1718557416531367, 1132000522510844, 1082560624385444,
    1116854777484491, 1401275134763195, 1577055963351135, 950584478088484, 1825938745453942,
    2515010528971232, 3256832567855127, 2011539042855413, 1307884259076007, 1697207174707113,
    1057004090430194, 1391180149876890, 1378863073862932, 2213089292601092, 2158745541742029,
    4334085160174077, 2965642263788861, 1084456674130688, 1795074258294093, 1034295026334577,
    4421225068131194, 1355927346655168, 1059786280093344, 4586299914987514, 1025106987189248,
    1466589528561583, 1614360887104866, 1576256877574775, 2540080516506172, 2127254448203651,
    2158428691408842, 1610530274010284, 1774269280438981, 2265075371003181, 1541222010651045,
    1022692723919374, 1102442109460908, 1007478755454166, 882953947975636, 1034366832727407,
    1617169986749709, 1051618307647563, 1895187091456259, 2068298457388397, 1758634098804956,
    1454206033481518, 1749070016210123,
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


def regra_form(evento):
    fontes = []
    for f in FORMS:
        fontes.append({"type": "lead", "id": f, "owner_id": PAGE})
        fontes.append({"type": "ig_lead_generation", "id": f, "owner_id": PAGE})
    return {"inclusions": {"operator": "or", "rules": [{
        "event_sources": fontes, "retention_seconds": 90 * 86400,
        "filter": {"operator": "and", "filters": [{"field": "event", "operator": "eq", "value": evento}]}}]}}


def main():
    ids = {}
    ids["abriu"] = post("%s/customaudiences" % CONTA, {
        "name": "M | FORM ABRIU E NAO ENVIOU 90D",
        "description": "Abriu o form [M] FORMS FRANQUIA ou FORM Bl 2 e nao enviou. Criado em 03/10/2026.",
        "rule": regra_form("lead_generation_dropoff"), "prefill": "true"}, "M | FORM ABRIU E NAO ENVIOU 90D")
    ids["enviou"] = post("%s/customaudiences" % CONTA, {
        "name": "M | FORM ENVIOU 90D",
        "description": "Enviou o form [M] FORMS FRANQUIA ou FORM Bl 2. Para exclusao. Criado em 03/10/2026.",
        "rule": regra_form("lead_generation_submitted"), "prefill": "true"}, "M | FORM ENVIOU 90D")
    ids["video"] = post("%s/customaudiences" % CONTA, {
        "name": "M | VIDEO FRANQUIA ANUNCIOS 75% 180D",
        "description": "Viu 75%% de %d videos de franquia que rodaram em anuncio (sem os so de produto). 03/10/2026." % len(VIDEOS),
        "subtype": "ENGAGEMENT", "retention_days": 180, "prefill": "true",
        "rule": [{"event_name": "video_view_75_percent", "object_id": v} for v in VIDEOS]},
        "M | VIDEO FRANQUIA ANUNCIOS 75% 180D")
    print(json.dumps(ids))


if __name__ == "__main__":
    main()
