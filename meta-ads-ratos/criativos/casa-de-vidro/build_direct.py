#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Casa de Vidro Paraty — criativos + anuncios da campanha de DIRECT.

Contexto: a campanha e os 2 conjuntos JA EXISTEM (criados em 12/08, PAUSED).
Este script fecha o que faltou — os 2 carrosseis com CTA de Instagram Direct e
os 2 anuncios — porque em 12-13/08 a conta estava UNSETTLED e a Meta recusava
qualquer POST em /adcreatives com subcode 1487194.

Estrutura ja no ar (PAUSED):
    Campanha 120248795623790510  [ENGAJ] [DIRECT] - Campanha Geral - P_personalizado 12/08
    +- 120248795624060510  [DATACOMEMORATIVA/AMIGOS] [DIRECT]      R$80/dia
    +- 120248795624670510  [COMPORTAMENTO/FERIASFAMILIA] [DIRECT]  R$80/dia

Os carrosseis reaproveitam os MESMOS image_hash e as MESMAS legendas dos
criativos de WhatsApp que ja rodavam (1058479113508257 Amigos, 1999049784332225
Familia). A unica diferenca e o destino: CTA WHATSAPP_MESSAGE -> INSTAGRAM_MESSAGE.

Nada e ativado por este script. Revisar o preview e ativar os 3 niveis.

Uso:
    python build_direct.py --checar   # so verifica se a conta destravou
    python build_direct.py            # cria os 2 criativos + os 2 anuncios
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta

AQUI = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.abspath(os.path.join(AQUI, "..", ".."))
API = "https://graph.facebook.com/v21.0/"

# ---------------------------------------------------------------------------
# Conta e ativos
# ---------------------------------------------------------------------------

CONTA = "act_792396727164193"
PAGINA = "949028168287242"
INSTAGRAM = "17841472733937596"          # @casadevidro.paraty

CAMPANHA = "120248795623790510"
ADSET_AMIGOS = "120248795624060510"
ADSET_FAMILIA = "120248795624670510"

# Campanha antiga de WhatsApp. Decisao da Mileny (13/08): NAO pausar junto —
# rodar as duas em paralelo por 3 dias e so entao pausar esta.
CAMPANHA_WHATS = "120244195893530510"

# Destino do carrossel. Em anuncio de Direct o link nao e clicado — o clique
# abre a conversa —, mas a API exige o campo preenchido no link_data.
LINK = "https://www.instagram.com/casadevidro.paraty/"
CTA = {"type": "INSTAGRAM_MESSAGE"}


def token():
    caminho = os.path.join(SKILL, ".env")
    for linha in open(caminho, encoding="utf-8"):
        if linha.strip().startswith("META_ADS_TOKEN"):
            return linha.split("=", 1)[1].strip().strip('"')
    sys.exit("META_ADS_TOKEN nao encontrado em " + caminho)


TOKEN = token()


def get(path, fields):
    url = API + path + "?" + urllib.parse.urlencode({"access_token": TOKEN, "fields": fields})
    with urllib.request.urlopen(url) as r:
        return json.load(r)


def post(path, params, oque):
    corpo = {k: (json.dumps(v) if isinstance(v, (dict, list)) else v) for k, v in params.items()}
    corpo["access_token"] = TOKEN
    dados = urllib.parse.urlencode(corpo).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(API + path, data=dados)) as r:
            saida = json.load(r)
            print("  OK  %-34s %s" % (oque, saida.get("id")))
            return saida.get("id")
    except urllib.error.HTTPError as e:
        erro = json.loads(e.read().decode("utf-8")).get("error", {})
        print("  ERRO %-33s" % oque)
        print("       msg :", erro.get("message"))
        print("       user:", erro.get("error_user_title"), "|", erro.get("error_user_msg"))
        print("       sub :", erro.get("error_subcode"))
        return None


# ---------------------------------------------------------------------------
# Saudacao automatica do Direct (ice breakers da casa)
# ---------------------------------------------------------------------------

SAUDACAO = "Ola, como vai? Bem-vindo(a) a Casa de Vidro em Paraty. ✨"

ICE_BREAKERS = [
    {
        "title": "Vim do anuncio da Casa de Vidro em Paraty e gostaria de saber mais informacoes",
        "response": (
            "⬇️A Casa de Vidro e uma residencia costeira de alto luxo em Paraty, com "
            "vista panoramica para o mar, 5 suites, piscina com borda infinita, sauna, deck e "
            "servicos personalizados, em absoluta privacidade. Capacidade para ate 12 pessoas."
            "\n\n\U0001f343Diarias a partir de R$ 10 mil - minimo 2 noites"
        ),
    },
    {
        "title": "Quais servicos voces oferecem durante a estadia?",
        "response": (
            "Exclusivos e personalizados:\n- Concierge 24/7\n- Barqueiro\n- Turn-down\n"
            "- Limpeza diaria\n- Servico de compras\n- Servico de praia completo\n"
            "- Cozinheiro + Cardapio personalizado"
        ),
    },
    {
        "title": "Qual a localizacao da Casa de Vidro?",
        "response": (
            "Localizada na regiao de Paraty Mirim, uma das vilas mais antigas da regiao!\n"
            "A Casa de Vidro fica em uma costeira privativa.\n"
            "(acesso exclusivo por 3 min de barco - proprio da casa)."
        ),
    },
]

WELCOME = json.dumps(
    {
        "type": "VISUAL_EDITOR",
        "version": 2,
        "landing_screen_type": "welcome_message",
        "media_type": "text",
        "text_format": {
            "customer_action_type": "ice_breakers",
            "message": {
                "text": SAUDACAO,
                "automated_greeting_message_cta": {"type": "none", "url": ""},
                "ice_breakers": ICE_BREAKERS,
            },
        },
        "user_edit": True,
        "surface": "visual_editor_new",
        "ice_breakers_edited": True,
        "welcome_message_edited": True,
    },
    ensure_ascii=False,
)

# ---------------------------------------------------------------------------
# Os 2 carrosseis (mesmos hashes e legendas dos criativos de WhatsApp)
# ---------------------------------------------------------------------------

CARROSSEIS = [
    {
        "adset": ADSET_AMIGOS,
        "nome": "Casa de Vidro — Carrossel Amigos [DIRECT]",
        "ad": "Casa de Vidro — Carrossel Amigos [DIRECT]",
        "legenda": (
            "Aquela viagem que o grupo sempre quis fazer — mas nunca encontrava o lugar "
            "certo.\n\nCasa inteira, privativa, com piscina e vista para o mar em Paraty Mirim. "
            "Disponibilidade limitada."
        ),
        "cards": [
            ("2b0a046e052196ae605c8ab1f5c6e7be", "Onde cada momento vira história."),
            ("7369f473411a93eb85c2ad55e54376c1", "O mar pertinho."),
            ("d4d182a2a88f06101c942a24099b88b8", "Paraty Mirim ao amanhecer."),
            ("6c66f20bd2072751ffd316a9a64f1bc2", "Detalhes pensados."),
            ("ff842608ffbd032742dfb5074338944d", "Vista exclusiva."),
            ("304c3ae4e117e32211ac742add99ab85", "Alto padrão."),
            ("1ca2baff36bb207ca59f646c94739a3e", "Piscina privativa."),
            ("dc98fd3b5dca3a465edceb82c22d4808", "Conforto elevado."),
            ("7d6d3aa78e93e27790c9655b46a86fc5", "Espaços exclusivos."),
            ("c59536d5c870c7f7271b3a2114a0fba9", "Natureza e privacidade."),
        ],
    },
    {
        "adset": ADSET_FAMILIA,
        "nome": "Casa de Vidro — Carrossel Família [DIRECT]",
        "ad": "Casa de Vidro — Carrossel Família [DIRECT]",
        "legenda": (
            "Para quem escolhe experiências, não apenas destinos.\n\nUma casa inteira "
            "só de vocês, com piscina privativa, natureza e privacidade total em "
            "Paraty Mirim. Consulte disponibilidade."
        ),
        "cards": [
            ("5a3e2f289afbf5a5e9c227d81acd49b0", "Férias que a família vai lembrar para sempre."),
            ("7d6d3aa78e93e27790c9655b46a86fc5", "Espaços exclusivos para vocês."),
            ("c59536d5c870c7f7271b3a2114a0fba9", "Natureza e privacidade."),
            ("1ca2baff36bb207ca59f646c94739a3e", "Piscina privativa."),
            ("ff842608ffbd032742dfb5074338944d", "Vista exclusiva."),
            ("304c3ae4e117e32211ac742add99ab85", "Alto padrão."),
            ("dc98fd3b5dca3a465edceb82c22d4808", "Conforto elevado."),
            ("6c66f20bd2072751ffd316a9a64f1bc2", "Detalhes pensados."),
            ("d4d182a2a88f06101c942a24099b88b8", "Paraty Mirim ao amanhecer."),
            ("7369f473411a93eb85c2ad55e54376c1", "O mar pertinho."),
        ],
    },
]

# Anuncio limpo: sem os aprimoramentos automaticos da Meta (regra permanente da
# Mileny). Campos validos mudam com frequencia — se der subcode 3858504, ler um
# criativo recente e funcional da conta e copiar os nomes atuais.
SEM_ENHANCEMENTS = {
    "creative_features_spec": {
        "advantage_plus_creative": {"enroll_status": "OPT_OUT"},
        "enhance_cta": {"enroll_status": "OPT_OUT"},
        "text_optimizations": {"enroll_status": "OPT_OUT"},
    }
}


# ---------------------------------------------------------------------------


def checar():
    """A conta precisa estar fora de UNSETTLED, senao /adcreatives recusa tudo."""
    conta = get(CONTA, "name,account_status,balance,amount_spent")
    status = conta.get("account_status")
    saldo = int(conta.get("balance", 0)) / 100
    print("Conta   :", conta.get("name"))
    print("Status  :", status, "(1=ativa, 2=desativada, 3=UNSETTLED)")
    print("Em aberto: R$ %.2f" % saldo)
    if status != 1:
        print()
        print("BLOQUEADO. Com a conta fora do status 1 a Meta recusa /adcreatives")
        print("com subcode 1487194 ('erro de permissao', mensagem enganosa).")
        print("Quitar o valor em aberto no gerenciador de pagamentos e rodar de novo.")
        return False
    print("OK — pode criar criativo.")
    return True


def build():
    for c in CARROSSEIS:
        print()
        print(c["nome"])
        cards = [
            {"link": LINK, "image_hash": h, "name": n, "call_to_action": CTA}
            for h, n in c["cards"]
        ]
        criativo = post(
            CONTA + "/adcreatives",
            {
                "name": c["nome"],
                "object_story_spec": {
                    "page_id": PAGINA,
                    "instagram_user_id": INSTAGRAM,
                    "link_data": {
                        "link": LINK,
                        "message": c["legenda"],
                        "call_to_action": CTA,
                        "child_attachments": cards,
                        # end card exige URL de destino e nao ha site aqui
                        "multi_share_end_card": False,
                        "multi_share_optimized": False,
                        "page_welcome_message": WELCOME,
                    },
                },
            },
            "criativo",
        )
        if not criativo:
            print("       -> pulando o anuncio deste carrossel")
            continue
        time.sleep(1)
        post(
            CONTA + "/ads",
            {
                "name": c["ad"],
                "adset_id": c["adset"],
                "creative": {"creative_id": criativo},
                "degrees_of_freedom_spec": SEM_ENHANCEMENTS,
                "status": "PAUSED",
            },
            "anuncio",
        )
        time.sleep(1)

    hoje = datetime.now()
    print()
    print("Feito. Conferir o preview antes de ativar:")
    print("  read.py preview --creative <ID> --format all")
    print("Ativar os 3 niveis: campanha %s -> conjuntos -> anuncios." % CAMPANHA)
    print()
    print("DECISAO DA MILENY (13/08): rodar Direct e WhatsApp EM PARALELO por 3 dias")
    print("e so entao pausar a de WhatsApp, comparando custo por conversa.")
    print("  Campanha de WhatsApp a pausar: %s" % CAMPANHA_WHATS)
    print("  Se ativar hoje, pausar a partir de %s:" % (hoje + timedelta(days=3)).strftime("%d/%m"))
    print("    update.py campaign --id %s --status PAUSED" % CAMPANHA_WHATS)
    print("  Comparativo antes de pausar (custo por conversa nas duas):")
    print("    insights.py campaign --id %s --date-preset last_3d" % CAMPANHA)
    print("    insights.py campaign --id %s --date-preset last_3d" % CAMPANHA_WHATS)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--checar", action="store_true", help="so verifica se a conta destravou")
    args = ap.parse_args()

    if not checar():
        sys.exit(1)
    if not args.checar:
        build()
