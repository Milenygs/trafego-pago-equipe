"""Belo 24/09/2026 - mensagem automatica do Direct (boas-vindas + 3 ice breakers) no anuncio de post.

O titulo do ice breaker vira a 1a mensagem da pessoa na caixa do Direct: todos levam "Ponto Belo",
para o atendimento separar Belo de Luna. Cria criativo novo (post 18629435476003635) e troca no anuncio.
Uso: python build_belo_direct_boasvindas.py [--dry]
"""
import json
import os
import sys
from pathlib import Path

import requests

SKILL = Path(os.path.expanduser("~/OneDrive/.claude/skills/meta-ads-ratos"))
env = (SKILL / ".env").read_text(encoding="utf-8")
TOKEN = [l.split("=", 1)[1].strip().strip('"') for l in env.splitlines() if l.startswith("META_ADS_TOKEN")][0]
G = "https://graph.facebook.com/v23.0/"

ACT = "act_1043516946010441"
PAGE = "198169833565944"
IG = "17841401339383360"
POST_IG = "18629435476003635"
AD = "120245801242000358"
CRIATIVO_ATUAL = "2306543910100726"

SAUDACAO = ("Olá! 💙 Aqui é a AP Ponto, e essa conversa é sobre o *Ponto Belo*, nosso lançamento "
            "em Vespasiano. Escolha uma opção abaixo que a gente já te ajuda 👇")
ICE_BREAKERS = [
    ("Quero simular meu apê no Ponto Belo",
     "Perfeito! Para a simulação do Ponto Belo, me conta: qual é a renda familiar somada de quem "
     "vai morar com você? Dá para juntar a renda de mais de uma pessoa. 😉"),
    ("Quais as condições do Ponto Belo?",
     "No Ponto Belo você tem apartamentos de 2 quartos a partir de R$250 mil pelo Minha Casa Minha "
     "Vida, entrada parcelada em até 60x direto com a construtora e ITBI e registro por nossa conta. "
     "Qual o melhor horário para o nosso time te chamar?"),
    ("Onde fica o Ponto Belo?",
     "O Ponto Belo fica na Rua Afonso Pena, 685, Santo Antônio, em Vespasiano: a 2 minutos do ponto "
     "de ônibus e a 15 de Confins. Quer que a gente te mande o book completo?"),
]

WELCOME = {
    "type": "VISUAL_EDITOR", "version": 2, "landing_screen_type": "welcome_message", "media_type": "text",
    "text_format": {
        "customer_action_type": "ice_breakers",
        "message": {
            "text": SAUDACAO,
            "automated_greeting_message_cta": {"type": "none", "url": ""},
            "ice_breakers": [{"title": t, "response": r} for t, r in ICE_BREAKERS],
        },
    },
    "user_edit": True, "surface": "visual_editor_new",
}


def get(path, **k):
    k["access_token"] = TOKEN
    return requests.get(G + path, params=k).json()


def post(path, data):
    data = {k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v) for k, v in data.items()}
    data["access_token"] = TOKEN
    r = requests.post(G + path, data=data).json()
    if "error" in r:
        e = r["error"]
        print(json.dumps({k: e.get(k) for k in ("code", "error_subcode", "error_user_title", "error_user_msg", "message")},
                         ensure_ascii=False, indent=1))
        sys.exit(1)
    return r


def main():
    # 24/09: este bloco rodava no import (sem main) e trocou o criativo do anuncio sem querer
    # quando outro script importou WELCOME. Agora so roda direto.
    if "--dry" in sys.argv:
        print(json.dumps(WELCOME, ensure_ascii=False, indent=1))
        return
    dof = get(CRIATIVO_ATUAL, fields="degrees_of_freedom_spec").get("degrees_of_freedom_spec", {})
    cr = post(ACT + "/adcreatives", {
        "name": "POST Lancamento Belo | Direct SET26 | boas-vindas",
        "object_id": PAGE, "instagram_user_id": IG, "source_instagram_media_id": POST_IG,
        "call_to_action": {"type": "INSTAGRAM_MESSAGE",
                           "value": {"app_destination": "INSTAGRAM_DIRECT", "link": "https://www.instagram.com/"}},
        "page_welcome_message": json.dumps(WELCOME, ensure_ascii=False),
        **({"degrees_of_freedom_spec": dof} if dof else {}),
    })["id"]
    print("criativo", cr)
    chk = get(cr, fields="page_welcome_message,object_story_spec")
    print("welcome gravado:", bool(chk.get("page_welcome_message") or
          json.dumps(chk.get("object_story_spec", {})).find("welcome") >= 0))
    post(AD, {"creative": {"creative_id": cr}})
    print("anuncio", AD, "agora com", get(AD, fields="creative")["creative"]["id"])


if __name__ == "__main__":
    main()
