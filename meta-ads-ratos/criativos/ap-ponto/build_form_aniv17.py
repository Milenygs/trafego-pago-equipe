#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AP Ponto - formulario nativo na campanha de aniversario (10/09/2026).

Pedido da Mileny: usar formulario instantaneo na campanha dos 17 anos, com os
mesmos valores de renda do formulario unificado, comecando em R$2.500, e
**sem desqualificar ninguem** - no unificado as faixas ate R$4.500 sao marcadas
como "nao sao leads"; aqui todo mundo entra.

O que este script faz:
  1. cria o formulario "AP Ponto | 17 Anos Comprou Ganhou | SET26" na pagina
     (precisa de page access token - o system user tem a pagina no /me/accounts)
  2. cria o conjunto M_ANIV17_FORM dentro da campanha M_ANIV17_SET26,
     LEAD_GENERATION + ON_AD (formulario instantaneo), mesmo publico do
     conjunto de remarketing
  3. clona os 2 criativos de aniversario trocando o destino: em vez de
     "Saiba mais -> LP do Luna", vira "Cadastre-se -> formulario"

Uso:
    python build_form_aniv17.py --dry
    python build_form_aniv17.py --form-only      so cria o formulario
    python build_form_aniv17.py --verba 150      cria tudo, conjunto PAUSED
    python build_form_aniv17.py --verba 150 --ativar
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
PAGINA = "198169833565944"
INSTAGRAM = "17841401339383360"
PIXEL = "211205516600655"

CAMPANHA = "120245550567960358"          # M_ANIV17_SET26 · 09 a 25/09
ADSET_RMKT = "120245550755120358"        # M_ANIV17_RMKT_PRAZO (site)
ADSET_FORM = "120245572529370358"        # M_ANIV17_FORM (formulario instantaneo)
AD_VIDEO = "120245572546340358"          # AD05
AD_IMAGEM = "120245572552200358"         # AD06
FIM = "2026-09-25T23:59:00-0300"

VIDEO_ID = "1950954295574378"
IMAGE_HASH = "d7d7ed255f51382dc73fe4dae3ccdfec"

# Publicos (mesmos do conjunto de remarketing + quente do Instagram)
PUB = ["120245517541240358",   # Qualificados sem venda
       "120245517750200358",   # Site todos 180d
       "120245519551400358",   # MQL site 180d
       "120245519552380358",   # Simulacao 180d
       "120245540043470358",   # IG_ENGAJ_AP_PONTO_180D      32,1k
       "120245540058970358"]   # IG_VIDEO_AP_PONTO_50%_180D 131,2k
EXC = ["120245517540390358",   # Compradores
       "120245517540780358"]   # Exclusao complemento

# Faixas de renda: as mesmas do "AP Ponto | Unificado MQL + FGTS | MAR26",
# comecando em R$2.500 (as duas primeiras do unificado viraram uma so).
FAIXAS = [
    "Até R$2.500 por mês",
    "De R$2.501 a R$3.500",
    "De R$3.501 a R$4.500",
    "De R$4.501 a R$5.500",
    "De R$5.501 a R$6.500",
    "De R$6.501 a R$7.500",
    "De R$7.501 a R$8.500",
    "De R$8.501 a R$9.500",
    "De R$9.501 a R$10.000",
    "R$10.001 ou mais",
]

EMPREENDIMENTOS = [
    "Ponto Lis — pronto para morar, em Contagem",
    "Ponto Luna — em Vespasiano",
    "Quero conhecer os dois",
]

CONTEXTO = (
    "Comprando o seu apartamento até 25/09, você leva um presente para "
    "comemorar com a gente.\n\n"
    "✅ Ponto Lis, pronto para morar em Contagem\n"
    "✅ Ponto Luna, em Vespasiano\n"
    "✅ Entrada facilitada, pode usar o FGTS\n"
    "✅ Financiamento pelo programa Minha Casa Minha Vida\n\n"
    "Preencha e o nosso time entra em contato com as condições da campanha.\n\n"
    "Consulte condições."
)

COPY = (
    "A AP Ponto está fazendo 17 anos — e quem ganha o presente é você.\n\n"
    "Comprando o seu apartamento até 25/09, você leva um presente para comemorar "
    "com a gente. E dá para sair do aluguel com entrada e parcelas a partir de "
    "R$ 1.000.\n\n"
    "✅ Entrada a partir de R$ 1.000\n"
    "✅ Parcelas a partir de R$ 1.000\n"
    "✅ Ponto Lis, pronto para morar em Contagem\n"
    "✅ Ponto Luna, em Vespasiano — entrega em dezembro\n"
    "✅ Use o FGTS e junte a renda de até 3 pessoas\n\n"
    "Preencha em 30 segundos e o nosso time fala com você.\n"
    "*Consulte condições."
)
TITULO = "Entrada e parcela a partir de R$ 1.000"

SEM_IA = {
    "advantage_plus_creative": {"enroll_status": "OPT_OUT"},
    "enhance_cta": {"enroll_status": "OPT_OUT"},
    "text_optimizations": {"enroll_status": "OPT_OUT"},
    "image_touchups": {"enroll_status": "OPT_OUT"},
    "video_auto_crop": {"enroll_status": "OPT_OUT"},
}


def token():
    for linha in open(os.path.join(SKILL, ".env"), encoding="utf-8"):
        if linha.strip().startswith("META_ADS_TOKEN"):
            return linha.split("=", 1)[1].strip().strip('"')
    sys.exit("META_ADS_TOKEN nao encontrado")


TOKEN = token()


def get(path, params=None, tok=None):
    p = dict(params or {})
    p["access_token"] = tok or TOKEN
    with urllib.request.urlopen(API + path + "?" + urllib.parse.urlencode(p)) as r:
        return json.load(r)


def post(path, params, oque, tok=None):
    corpo = {k: (json.dumps(v) if isinstance(v, (dict, list)) else v)
             for k, v in params.items()}
    corpo["access_token"] = tok or TOKEN
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


def page_token():
    for p in get("me/accounts", {"fields": "id,access_token", "limit": 100}).get("data", []):
        if p.get("id") == PAGINA:
            return p.get("access_token")
    sys.exit("pagina da AP Ponto nao aparece no /me/accounts do system user")


def criar_formulario(privacidade):
    # cada option precisa de key E value - so com value a Meta devolve
    # "An unknown error has occurred", sem dizer o campo (testado em 10/09)
    perguntas = [
        {"type": "CUSTOM",
         "key": "empreendimento",
         "label": "Qual empreendimento você quer conhecer?",
         "options": [{"key": "empr_%d" % i, "value": e}
                     for i, e in enumerate(EMPREENDIMENTOS)]},
        {"type": "CUSTOM",
         "key": "renda_familiar",
         "label": "Qual sua renda familiar? (Pode juntar até 3 pessoas)",
         "options": [{"key": "faixa_%d" % i, "value": f} for i, f in enumerate(FAIXAS)]},
        {"type": "CUSTOM",
         "key": "fgts",
         "label": "Você possui FGTS disponível?",
         "options": [{"key": "sim", "value": "Sim!"}, {"key": "nao", "value": "Não."}]},
        {"type": "FULL_NAME"},
        {"type": "EMAIL"},
        {"type": "PHONE"},
    ]
    return post(PAGINA + "/leadgen_forms", {
        "name": "AP Ponto | 17 Anos Comprou Ganhou | Lis e Luna | SET26",
        "locale": "pt_BR",
        "questions": perguntas,
        "context_card": {
            "title": "17 anos de AP Ponto. Quem ganha o presente é você.",
            "style": "PARAGRAPH_STYLE",
            "content": [CONTEXTO],
            "button_text": "Quero saber as condições",
        },
        "question_page_custom_headline": "Preencha e o nosso time entra em contato",
        "thank_you_page": {
            "title": "Recebemos os seus dados!",
            "body": "O nosso time entra em contato para mostrar as condições do aniversário.",
            "button_text": "Conhecer os empreendimentos",
            "button_type": "VIEW_WEBSITE",
            "website_url": ("https://apponto.com.br/?utm_source=meta"
                            "&utm_medium=leadform&utm_campaign=ANIV17"),
        },
        "privacy_policy": privacidade,
        "follow_up_action_url": ("https://luna.apponto.com.br/?utm_source=meta"
                                 "&utm_medium=leadform&utm_campaign=ANIV17"),
        "block_display_for_non_targeted_viewer": True,
        "allow_organic_lead": True,
    }, "formulario 17 anos", tok=page_token())


def criar_conjunto(verba, status):
    targeting = {
        "age_min": 25, "age_max": 60,
        "custom_audiences": [{"id": p} for p in PUB],
        "excluded_custom_audiences": [{"id": e} for e in EXC],
        "publisher_platforms": ["instagram"],
        "instagram_positions": ["stream", "reels", "explore", "profile_feed"],
        "device_platforms": ["mobile", "desktop"],
        "targeting_relaxation_types": {"lookalike": 0, "custom_audience": 0},
        "targeting_automation": {"advantage_audience": 0},
    }
    return post(CONTA + "/adsets", {
        "name": "M_ANIV17_FORM",
        "campaign_id": CAMPANHA,
        "optimization_goal": "LEAD_GENERATION",
        "billing_event": "IMPRESSIONS",
        "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
        "destination_type": "ON_AD",
        "promoted_object": {"page_id": PAGINA},
        "daily_budget": int(round(verba * 100)),
        "end_time": FIM,
        "status": status,
        "targeting": targeting,
        # lead form nativo so aceita (clique 1 dia, visualizacao 0) - a Meta
        # recusa qualquer outra combinacao com subcode 1885501. Sem o campo
        # ela aplica esse padrao sozinha.
    }, "conjunto M_ANIV17_FORM")


def thumb():
    dados = get(VIDEO_ID + "/thumbnails").get("data", [])
    for t in dados:
        if t.get("is_preferred"):
            return t["uri"]
    return dados[0]["uri"] if dados else None


def criativo_video(form_id, t):
    return post(CONTA + "/adcreatives", {
        "name": "ANIV17 - UGC 17 anos - formulario - set2026",
        "object_story_spec": {
            "page_id": PAGINA, "instagram_user_id": INSTAGRAM,
            "video_data": {
                "video_id": VIDEO_ID, "message": COPY, "title": TITULO, "image_url": t,
                "call_to_action": {"type": "SIGN_UP",
                                   "value": {"lead_gen_form_id": form_id}},
            },
        },
        "degrees_of_freedom_spec": {"creative_features_spec": SEM_IA},
    }, "criativo video/formulario")


def criativo_imagem(form_id):
    return post(CONTA + "/adcreatives", {
        "name": "ANIV17 - Estatico comprou ganhou - formulario - set2026",
        "object_story_spec": {
            "page_id": PAGINA, "instagram_user_id": INSTAGRAM,
            "link_data": {
                "image_hash": IMAGE_HASH, "message": COPY, "name": TITULO,
                "link": "https://fb.me/",
                "call_to_action": {"type": "SIGN_UP",
                                   "value": {"lead_gen_form_id": form_id}},
            },
        },
        "degrees_of_freedom_spec": {"creative_features_spec": SEM_IA},
    }, "criativo imagem/formulario")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--form-only", action="store_true")
    ap.add_argument("--form-id", help="usa um formulario ja criado")
    ap.add_argument("--verba", type=float, default=150.0, help="R$/dia do conjunto")
    ap.add_argument("--ativar", action="store_true")
    ap.add_argument("--trocar", action="store_true",
                    help="troca o criativo dos anuncios que ja existem, em vez de criar conjunto")
    ap.add_argument("--arquivar-form", help="id do formulario antigo a arquivar")
    ap.add_argument("--privacidade", default="https://apponto.com.br/politica-de-privacidade")
    args = ap.parse_args()

    conta = get(CONTA, {"fields": "name,account_status"})
    print("Conta:", conta.get("name"), "| status", conta.get("account_status"))

    if args.dry:
        print()
        print("Formulario: AP Ponto | 17 Anos Comprou Ganhou | SET26")
        print("  perguntas: renda (%d faixas, a partir de R$2.500) · FGTS · nome · e-mail · telefone"
              % len(FAIXAS))
        print("  ninguem e desqualificado - todas as faixas viram lead")
        print("  privacidade:", args.privacidade)
        print("Conjunto  : M_ANIV17_FORM · LEAD_GENERATION + ON_AD · R$%.0f/dia · ate 25/09"
              % args.verba)
        print("Criativos : video + estatico do aniversario, CTA Cadastre-se")
        return

    form = args.form_id
    if not form:
        form = criar_formulario({
            "url": args.privacidade,
            # mesmo texto do formulario unificado, ja aprovado pela Meta
            "link_text": "Acesse a Política de Privacidade da Página AP Ponto Construtora.",
        })
        if not form:
            sys.exit("formulario nao criado")
    print("  form_id:", form)
    if args.form_only:
        return

    status = "ACTIVE" if args.ativar else "PAUSED"

    t = thumb()
    cv = criativo_video(form, t)
    ci = criativo_imagem(form)
    time.sleep(1)

    if args.trocar:
        # formulario e criativo sao imutaveis na Meta: para mudar a pergunta,
        # nasce formulario novo, criativo novo, e o anuncio aponta para ele.
        for ad_id, cid in [(AD_VIDEO, cv), (AD_IMAGEM, ci)]:
            if cid:
                post(ad_id, {"creative": {"creative_id": cid}}, "trocar criativo do " + ad_id)
                time.sleep(1)
        if args.arquivar_form:
            post(args.arquivar_form, {"status": "ARCHIVED"},
                 "arquivar form antigo", tok=page_token())
        return

    adset = criar_conjunto(args.verba, status)
    if not adset:
        sys.exit("conjunto nao criado")
    for nome, cid in [("AD05 - ANIV17 UGC 17 anos [VIDEO][FORM]", cv),
                      ("AD06 - ANIV17 comprou ganhou [IMAGEM][FORM]", ci)]:
        if cid:
            post(CONTA + "/ads", {"name": nome, "adset_id": adset,
                                  "creative": {"creative_id": cid},
                                  "status": status}, "ad " + nome)
            time.sleep(1)

    print()
    print("Conferir: read.py ads-by-campaign --campaign " + CAMPANHA)


if __name__ == "__main__":
    main()
