"""Belo 24/09/2026 - campanha de formulario nativo para testar contra a campanha de LP.

Espelho da [BELO] Lançamento | Lead LP | SET26 (120245790359480358): mesmos 3 conjuntos
(targeting copiado por API, com geo e anunciante verificado), mesma verba (350/300/150), mesmos
2 videos. Muda so o destino: formulario instantaneo (LEAD_GENERATION + ON_AD).
Formulario no modelo do ANIV17 (2165262060698307, 169 leads): renda em 10 faixas a partir de
R$2.500, FGTS, sem desqualificar ninguem. Tudo PAUSED.
Uso: python build_belo_form.py [--form-id ID] [--campanha ID]
"""
import json
import os
import sys
import time
from pathlib import Path

import requests

SKILL = Path(os.path.expanduser("~/OneDrive/.claude/skills/meta-ads-ratos"))
env = (SKILL / ".env").read_text(encoding="utf-8")
TOKEN = [l.split("=", 1)[1].strip().strip('"') for l in env.splitlines() if l.startswith("META_ADS_TOKEN")][0]
G = "https://graph.facebook.com/v23.0/"

ACT = "act_1043516946010441"
PAGE = "198169833565944"
IG = "17841401339383360"
CAMP_LP = "120245790359480358"
VIDEOS = {"VID Locucao Lancamento v1": "1532597512229215", "VID UGC Leo v1": "3228123300731106"}
VERBA = {"Interesse": 35000, "LAL": 30000, "Remarketing": 15000}
REGIONAL = {
    "regional_regulated_categories": ["BRAZIL_REGULATION", "VOLUNTARY_VERIFICATION"],
    "regional_regulation_identities": {"universal_beneficiary": "609854092925940",
                                       "universal_payer": "609854092925940"},
}
FAIXAS = ["Até R$2.500 por mês", "De R$2.501 a R$3.500", "De R$3.501 a R$4.500", "De R$4.501 a R$5.500",
          "De R$5.501 a R$6.500", "De R$6.501 a R$7.500", "De R$7.501 a R$8.500", "De R$8.501 a R$9.500",
          "De R$9.501 a R$10.000", "R$10.001 ou mais"]
CONTEXTO = ("Lançamento da AP Ponto em Vespasiano: apartamentos de 2 quartos a partir de R$250 mil, "
            "pelo Minha Casa Minha Vida.\n\n"
            "✅ Entrada parcelada em até 60x direto com a construtora\n"
            "✅ ITBI e registro por conta da AP Ponto\n"
            "✅ Dá para somar a renda da família e usar o FGTS\n"
            "✅ Lazer completo, a 2 minutos do ponto de ônibus\n\n"
            "Preencha e o nosso time te mostra quanto fica o seu apê.\n\n"
            "Consulte condições.")

BODY_1 = """Primeiro apê em Vespasiano.
E a renda da família toda conta.

O Ponto Belo é o lançamento da AP Ponto: apartamentos de 2 quartos a partir de R$250 mil, pelo Minha Casa Minha Vida.

A entrada é parcelada em até 60x direto com a construtora. E o ITBI e o registro ficam por conta da AP Ponto: são de R$10 mil a R$15 mil a menos logo na assinatura.

Dá para somar a renda de quem vai morar com você, em qualquer faixa, inclusive renda familiar até R$5 mil.

Piscina, academia, quadra, churrasqueira e playground dentro do condomínio.

\U0001F4CD Rua Afonso Pena, 685, Santo Antônio, Vespasiano/MG
\U0001F68C A 2 minutos do ponto de ônibus
✈️ A 15 minutos de Confins
*Consulte condições."""

BODY_2 = """Quanto fica o seu apê no Ponto Belo?
Preencha em 30 segundos e a gente te mostra.

Você informa a faixa de renda da família, inclusive até R$5 mil, e o nosso time te passa os dois valores: a prestação da Caixa e a parcela da entrada com a AP Ponto.

\U0001F4CD Lançamento no Santo Antônio, Vespasiano · 2 quartos a partir de R$250 mil
\U0001F68C A 2 minutos do ônibus · a 15 de Confins
\U0001F4B3 Entrada em até 60x direto com a construtora
\U0001F4C4 ITBI e registro por conta da AP Ponto
\U0001F3CA Lazer completo no condomínio

O mesmo valor que você paga de aluguel já pode ser a parcela do que é seu.
Toque em Cadastre-se \U0001F447
*Consulte condições."""

BODY_3 = """"Minha renda sozinha não dá."
"Não tenho o dinheiro da entrada."
"E ainda tem ITBI e cartório."

No Ponto Belo, a AP Ponto resolve as três:
✔ A renda da família soma, em qualquer faixa, inclusive até R$5 mil
✔ A entrada é parcelada em até 60x direto com a construtora
✔ ITBI e registro ficam por nossa conta: de R$10 mil a R$15 mil que ficam com você

"Parcelamos a entrada e hoje estamos pagando prestações que cabem no nosso bolso."
Amanda e Fabrício, clientes AP Ponto

17 anos de mercado. Aqui você fala direto com a construtora, sem corretor.

Lançamento em Vespasiano: 2 quartos a partir de R$250 mil, na Rua Afonso Pena, 685, a 2 minutos do ônibus.
Preencha e receba a sua simulação \U0001F447
*Consulte condições."""

TITLES = ["2 quartos a partir de R$250 mil", "Entrada em até 60x com a construtora",
          "ITBI e registro por nossa conta", "Simule com a renda da sua família",
          "A 2 min do ônibus, a 15 de Confins"]
DESCRIPTIONS = ["Lançamento em Vespasiano", "Minha Casa Minha Vida", "Fale direto com a construtora"]
OPT_OUT = ["advantage_plus_creative", "enhance_cta", "inline_comment", "text_optimizations",
           "video_auto_crop", "video_filtering", "video_uncrop", "adapt_to_placement",
           "translate_voiceover", "show_summary", "reveal_details_over_time"]


def get(p, tok=None, **k):
    k["access_token"] = tok or TOKEN
    return requests.get(G + p, params=k).json()


def post(path, data, tok=None, fatal=True):
    data = {k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v) for k, v in data.items()}
    data["access_token"] = tok or TOKEN
    r = requests.post(G + path, data=data).json()
    if "error" in r:
        e = r["error"]
        print(json.dumps({k: e.get(k) for k in ("code", "error_subcode", "error_user_title", "error_user_msg", "message")},
                         ensure_ascii=False, indent=1))
        if fatal:
            sys.exit(1)
    return r


def page_token():
    for p in get("me/accounts", fields="id,access_token", limit=100).get("data", []):
        if p["id"] == PAGE:
            return p["access_token"]
    sys.exit("pagina nao aparece no /me/accounts")


def criar_form():
    perguntas = [
        {"type": "CUSTOM", "key": "renda_familiar",
         "label": "Qual a renda familiar? (Pode somar a renda de mais de uma pessoa)",
         "options": [{"key": "faixa_%d" % i, "value": f} for i, f in enumerate(FAIXAS)]},
        {"type": "CUSTOM", "key": "fgts", "label": "Você possui FGTS disponível?",
         "options": [{"key": "sim", "value": "Sim!"}, {"key": "nao", "value": "Não."}]},
        {"type": "FULL_NAME"}, {"type": "EMAIL"}, {"type": "PHONE"},
    ]
    utm = "?utm_source=meta&utm_medium=leadform&utm_campaign=belo_lancamento"
    r = post(PAGE + "/leadgen_forms", {
        "name": "AP Ponto | Ponto Belo | Lançamento | SET26",
        "locale": "pt_BR",
        "questions": perguntas,
        "context_card": {"title": "Ponto Belo: seu primeiro apê em Vespasiano", "style": "PARAGRAPH_STYLE",
                         "content": [CONTEXTO], "button_text": "Quero minha simulação"},
        "question_page_custom_headline": "Preencha e o nosso time te mostra quanto fica o seu apê",
        "thank_you_page": {"title": "Recebemos os seus dados!",
                           "body": "O nosso time entra em contato com a simulação do seu apê no Ponto Belo.",
                           "button_text": "Conhecer o Ponto Belo", "button_type": "VIEW_WEBSITE",
                           "website_url": "https://belo.apponto.com.br/" + utm},
        "privacy_policy": {"url": "https://apponto.com.br/politica-de-privacidade",
                           "link_text": "Acesse a Política de Privacidade da Página AP Ponto Construtora."},
        "follow_up_action_url": "https://belo.apponto.com.br/" + utm,
        "block_display_for_non_targeted_viewer": True,
        "allow_organic_lead": True,
    }, tok=page_token())
    print("formulario", r["id"])
    return r["id"]


def main():
    form = sys.argv[sys.argv.index("--form-id") + 1] if "--form-id" in sys.argv else criar_form()
    camp = sys.argv[sys.argv.index("--campanha") + 1] if "--campanha" in sys.argv else post(ACT + "/campaigns", {
        "name": "[BELO] Lançamento | Lead Form | SET26", "objective": "OUTCOME_LEADS", "status": "PAUSED",
        "special_ad_categories": [], "is_adset_budget_sharing_enabled": "false"})["id"]
    print("campanha", camp)

    # conjuntos: targeting copiado dos conjuntos da LP (inclui geo, exclusoes e publicos novos)
    fonte = get(CAMP_LP + "/adsets", fields="name,targeting")["data"]
    existentes = {a["name"]: a["id"] for a in get(camp + "/adsets", fields="name").get("data", [])}
    conjuntos = {}
    for s in fonte:
        chave = next(k for k in VERBA if k in s["name"])
        nome = s["name"].replace("[BELO]", "[BELO][FORM]")
        if nome in existentes:
            conjuntos[nome] = existentes[nome]
            continue
        t = s["targeting"]
        for k in ("age_range",):
            t.pop(k, None)
        r = post(ACT + "/adsets", {
            "name": nome, "campaign_id": camp, "status": "PAUSED", "daily_budget": VERBA[chave],
            "billing_event": "IMPRESSIONS", "optimization_goal": "LEAD_GENERATION",
            "bid_strategy": "LOWEST_COST_WITHOUT_CAP", "destination_type": "ON_AD",
            "promoted_object": {"page_id": PAGE}, "targeting": t, **REGIONAL})
        conjuntos[nome] = r["id"]
        print("conjunto", nome, r["id"])
        time.sleep(1)

    for ad_name, vid in VIDEOS.items():
        thumbs = get(vid + "/thumbnails", fields="uri,is_preferred").get("data", [])
        uri = next((t["uri"] for t in thumbs if t.get("is_preferred")), thumbs[0]["uri"])
        cta = {"type": "SIGN_UP", "value": {"lead_gen_form_id": form}}
        cr = post(ACT + "/adcreatives", {
            "name": f"{ad_name} | BELO FORM SET26",
            "object_story_spec": {"page_id": PAGE, "instagram_user_id": IG,
                                  "video_data": {"video_id": vid, "image_url": uri, "call_to_action": cta}},
            "asset_feed_spec": {
                "bodies": [{"text": b} for b in (BODY_1, BODY_2, BODY_3)],
                "titles": [{"text": t} for t in TITLES],
                "descriptions": [{"text": d} for d in DESCRIPTIONS],
                "optimization_type": "DEGREES_OF_FREEDOM",
            },
            "degrees_of_freedom_spec": {"creative_features_spec": {f: {"enroll_status": "OPT_OUT"} for f in OPT_OUT}},
        })
        print(ad_name, "criativo", cr["id"])
        for nome, sid in conjuntos.items():
            ad = post(ACT + "/ads", {"name": ad_name, "adset_id": sid, "creative": {"creative_id": cr["id"]},
                                     "status": "PAUSED"}, fatal=False)
            print("  anuncio", nome, ad.get("id"))
            time.sleep(2)


if __name__ == "__main__":
    main()
