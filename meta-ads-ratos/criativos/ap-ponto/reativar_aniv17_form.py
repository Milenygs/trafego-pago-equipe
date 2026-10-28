"""ANIV17 28/09/2026 - reativar o M_ANIV17_FORM ate 30/09 (promocao estendida ate o fim de setembro).

1. Formulario novo = copia do 1841350694665488 (o que os anuncios usam), tela com "ate 30/09" no lugar de 25/09.
2. Criativos novos dos anuncios ATIVOS (mesmo video, textos, titulo e opt-outs) apontando pro form novo; troca no anuncio.
3. Geo no conjunto (estava SEM geo): BH 17 + Contagem 17 + Vespasiano 20 + anunciante verificado.
4. Fim programado: conjunto end_time e campanha stop_time = 30/09 23:59.
Uso: python reativar_aniv17_form.py [--form-id ID]
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
ACT, PAGE = "act_1043516946010441", "198169833565944"
CAMP, ADSET = "120245550567960358", "120245572529370358"
FORM_ANTIGO = "1841350694665488"
FIM = "2026-09-30T23:59:00-0300"
GEO = {"cities": [{"key": "244661", "radius": 17, "distance_unit": "kilometer"},
                  {"key": "249756", "radius": 17, "distance_unit": "kilometer"},
                  {"key": "273969", "radius": 20, "distance_unit": "kilometer"}]}
REGIONAL = {"regional_regulated_categories": ["BRAZIL_REGULATION", "VOLUNTARY_VERIFICATION"],
            "regional_regulation_identities": {"universal_beneficiary": "609854092925940",
                                               "universal_payer": "609854092925940"}}


def get(p, tok=None, **k):
    k["access_token"] = tok or TOKEN
    return requests.get(G + p, params=k, timeout=60).json()


def post(path, data, tok=None, fatal=True):
    data = {k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v) for k, v in data.items()}
    data["access_token"] = tok or TOKEN
    r = requests.post(G + path, data=data, timeout=120).json()
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


def novo_form():
    f = get(FORM_ANTIGO, fields="name,locale,questions,context_card,thank_you_page,question_page_custom_headline,"
                                "block_display_for_non_targeted_viewer,follow_up_action_url")
    perguntas = []
    for q in f["questions"]:
        if q["type"] == "CUSTOM":
            perguntas.append({"type": "CUSTOM", "key": q["key"], "label": q["label"],
                              "options": [{"key": o["key"], "value": o["value"]} for o in q["options"]]})
        else:
            perguntas.append({"type": q["type"]})  # padrao nao aceita label/key na criacao
    cc = f["context_card"]
    texto = cc["content"][0].replace("até 25/09", "até 30/09")
    assert "30/09" in texto and "25/09" not in texto
    ty = f["thank_you_page"]
    r = post(PAGE + "/leadgen_forms", {
        "name": "AP Ponto | 17 Anos Comprou Ganhou | até 30/09 | SET26",
        "locale": f.get("locale", "pt_BR"),
        "questions": perguntas,
        "context_card": {"title": cc["title"], "style": cc.get("style", "PARAGRAPH_STYLE"), "content": [texto],
                         **({"button_text": cc["button_text"]} if cc.get("button_text") else {})},
        **({"question_page_custom_headline": f["question_page_custom_headline"]}
           if f.get("question_page_custom_headline") else {}),
        "thank_you_page": {k: ty[k] for k in ("title", "body", "button_text", "button_type", "website_url") if ty.get(k)},
        "privacy_policy": {"url": "https://apponto.com.br/politica-de-privacidade",
                           "link_text": "Acesse a Política de Privacidade da Página AP Ponto Construtora."},
        "follow_up_action_url": f.get("follow_up_action_url") or ty.get("website_url"),
        "block_display_for_non_targeted_viewer": True,
        "allow_organic_lead": True,
    }, tok=page_token())
    print("form novo", r["id"])
    return r["id"]


def main():
    form = sys.argv[sys.argv.index("--form-id") + 1] if "--form-id" in sys.argv else novo_form()

    # criativos novos so para os anuncios ATIVOS (o AD06 pausado fica como esta)
    for a in get(ADSET + "/ads", fields="id,name,status,creative{id}")["data"]:
        if a["status"] != "ACTIVE":
            print("pula (pausado):", a["name"])
            continue
        c = get(a["creative"]["id"], fields="object_story_spec,degrees_of_freedom_spec")
        oss = c["object_story_spec"]
        d = oss.get("video_data") or oss.get("link_data")
        if "até 25/09" in (d.get("message") or ""):
            d["message"] = d["message"].replace("até 25/09", "até 30/09")
        d["call_to_action"] = {"type": "SIGN_UP", "value": {"lead_gen_form_id": form}}
        d.pop("image_url", None)  # fica o image_hash
        novo = post(ACT + "/adcreatives", {
            "name": f"{a['name']} | ate 30/09",
            "object_story_spec": {k: v for k, v in oss.items() if k in ("page_id", "instagram_user_id", "video_data", "link_data")},
            **({"degrees_of_freedom_spec": c["degrees_of_freedom_spec"]} if c.get("degrees_of_freedom_spec") else {}),
        })["id"]
        print(a["name"], "-> criativo", novo, post(a["id"], {"creative": {"creative_id": novo}}))
        time.sleep(2)

    # conjunto: geo + fim 30/09
    t = get(ADSET, fields="targeting")["targeting"]
    t["geo_locations"] = GEO
    t.pop("age_range", None)
    print("conjunto:", post(ADSET, {"targeting": t, "end_time": FIM, **REGIONAL}))
    print("campanha:", post(CAMP, {"stop_time": FIM, "status": "ACTIVE"}))
    time.sleep(2)

    # conferencia
    s = get(ADSET, fields="status,effective_status,end_time,targeting{geo_locations}")
    print("conjunto agora:", s["status"], s["effective_status"], s["end_time"],
          [(x["name"], x["radius"]) for x in s["targeting"]["geo_locations"].get("cities", [])])
    print("campanha agora:", get(CAMP, fields="status,effective_status,stop_time"))
    for a in get(ADSET + "/ads", fields="name,status,effective_status,creative{object_story_spec}")["data"]:
        d = a["creative"]["object_story_spec"]
        d = d.get("video_data") or d.get("link_data") or {}
        print("  ", a["name"], a["status"], a["effective_status"], "| form:",
              d.get("call_to_action", {}).get("value", {}).get("lead_gen_form_id"),
              "| texto 30/09:", "30/09" in (d.get("message") or ""))


if __name__ == "__main__":
    main()
