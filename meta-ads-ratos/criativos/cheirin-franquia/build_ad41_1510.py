#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cheirin Bao MT — estatico "Muito mais que uma CAFETERIA." (15/10/2026). Mileny: "pode ativar".

Um anuncio so no 16 QUENTE + LAL, com a imagem 4:5 em feed/explorar/perfil e a 9:16 em stories/reels
(asset_customization_rules). Story com o logo descido 125px (fora da barra do perfil), arte original intacta.
Captacao: modelo DRE 146k (form 2805248149848936, SIGN_UP, titulo e descricao do modelo, IA toda em OPT_OUT),
copy sem numero financeiro. A peca ja traz qualificado na conta do outro gestor (Mileny, 15/10).
Estado em estado_ad41_1510.json (nao recria o que ja existe).
"""
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
import build_outubro_depoimentos as b  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
ESTADO = os.path.join(AQUI, "estado_ad41_1510.json")
ARTE = os.path.join(os.path.expanduser("~"), "OneDrive", "Área de Trabalho", "CLAUDE CODE", "franquias", "cheirin bao")
FEED = os.path.join(ARTE, "ads-01-1080x1350.png")
STORY = os.path.join(ARTE, "ads-01-1080x1920-logo-ajustado.png")
Q16 = "120258418032850212"
NOME = "Q16 - AD41 [MARCA] muito mais que uma cafeteria"
FORM = "2805248149848936"
FB_ME = "http://fb.me/"
ATIVAR = True  # ok da Mileny: "pode ativar"

COPY = (
    "Muito mais que uma cafeteria.\n\n"
    "Ser franqueado Cheirin Bão é abrir uma loja com cardápio completo, uma marca que o cliente já reconhece, "
    "marketing forte e um ecossistema que vai do pé de café à xícara: a rede cuida da cadeia inteira até a sua loja.\n\n"
    "Quer conhecer o modelo por dentro? Clique e fale com a gente.\n\n" + b.FIM)

REGRAS = [
    {"customization_spec": {"publisher_platforms": ["instagram"], "instagram_positions": ["story", "reels"]},
     "image_label": {"name": "img_story"}, "priority": 1},
    {"customization_spec": {"publisher_platforms": ["instagram"],
                            "instagram_positions": ["stream", "explore", "explore_home", "profile_feed"]},
     "image_label": {"name": "img_feed"}, "priority": 2},
]


def tenta(path, params, oque):
    """POST que devolve (id, erro) em vez de encerrar, para poder cair na segunda forma."""
    corpo = {k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v) for k, v in params.items()}
    corpo["access_token"] = b.TOKEN
    try:
        with urllib.request.urlopen(urllib.request.Request(b.API + path, data=urllib.parse.urlencode(corpo).encode()),
                                    timeout=120) as r:
            i = json.load(r).get("id")
            print("  OK   %-58s %s" % (oque, i))
            return i, None
    except urllib.error.HTTPError as e:
        err = json.loads(e.read().decode("utf-8")).get("error", {})
        print("  RECUSADO %-54s %s | %s" % (oque, err.get("error_subcode"), err.get("error_user_msg") or err.get("message")))
        return None, err


def sobe_imagem(caminho):
    with open(caminho, "rb") as f:
        corpo = urllib.parse.urlencode({"bytes": base64.b64encode(f.read()).decode(), "name": os.path.basename(caminho),
                                        "access_token": b.TOKEN}).encode()
    with urllib.request.urlopen(urllib.request.Request(b.API + "%s/adimages" % b.CONTA, data=corpo), timeout=120) as r:
        h = next(iter(json.load(r)["images"].values()))["hash"]
    print("  OK   %-58s %s" % ("imagem " + os.path.basename(caminho), h))
    return h


def form_no_criativo(cid):
    """Confere se o formulario ficou preso ao criativo (em qualquer das duas formas)."""
    d = b.get(cid, {"fields": "asset_feed_spec,object_story_spec,call_to_action_type"})
    txt = json.dumps(d, ensure_ascii=False)
    return FORM in txt, d


def salva(e):
    json.dump(e, open(ESTADO, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def main():
    if "--dry" in sys.argv:
        print("== %s -> %s\n%s" % (NOME, Q16, COPY))
        return
    e = json.load(open(ESTADO, encoding="utf-8")) if os.path.exists(ESTADO) else {}
    nomes = [a["name"] for a in b.get(Q16 + "/ads", {"fields": "name", "limit": 100}).get("data", [])]
    if NOME in nomes and not e.get("anuncio"):
        sys.exit("%s ja existe no 16 (criado fora deste script): nada feito" % NOME)
    m = b.modelo()
    if not e.get("feed"):
        e["feed"] = sobe_imagem(FEED); salva(e)
    if not e.get("story"):
        e["story"] = sobe_imagem(STORY); salva(e)

    if not e.get("criativo"):
        imagens = [{"hash": e["feed"], "adlabels": [{"name": "img_feed"}]},
                   {"hash": e["story"], "adlabels": [{"name": "img_story"}]}]
        base_afs = {"images": imagens, "bodies": [{"text": COPY}], "titles": [{"text": m["title"]}],
                    "descriptions": [{"text": m["link_description"]}], "link_urls": [{"website_url": FB_ME}],
                    "call_to_action_types": ["SIGN_UP"], "ad_formats": ["SINGLE_IMAGE"],
                    "asset_customization_rules": REGRAS, "optimization_type": "PLACEMENT"}
        formas = [
            ("A: formulario no asset_feed_spec",
             {"page_id": m["page_id"], "instagram_user_id": m["instagram_user_id"]},
             dict(base_afs, call_to_actions=[{"type": "SIGN_UP", "value": {"lead_gen_form_id": FORM, "link": FB_ME}}])),
            ("B: link_data com formulario + asset_feed_spec espelhado",
             {"page_id": m["page_id"], "instagram_user_id": m["instagram_user_id"],
              "link_data": {"image_hash": e["feed"], "message": COPY, "name": m["title"],
                            "description": m["link_description"], "link": FB_ME, "call_to_action": m["cta"]}},
             base_afs),
        ]
        for rotulo, oss, afs in formas:
            cid, _ = tenta("%s/adcreatives" % b.CONTA, {"name": "Cheirin — %s (feed 4x5 + story 9x16)" % NOME,
                                                        "object_story_spec": oss, "asset_feed_spec": afs,
                                                        "degrees_of_freedom_spec": m["dof"]}, "criativo " + rotulo[:1])
            if not cid:
                time.sleep(3)
                continue
            ok, _ = form_no_criativo(cid)
            if ok:
                e["criativo"], e["forma"] = cid, rotulo
                salva(e)
                break
            print("  ATENCAO criativo %s aceito sem o formulario: descartado, tentando a outra forma" % cid)
            time.sleep(3)
        if not e.get("criativo"):
            sys.exit("nenhuma forma aceita com o formulario: nada de anuncio criado")

    if not e.get("anuncio"):
        aid, err = tenta("%s/ads" % b.CONTA, {"name": NOME, "adset_id": Q16, "creative": {"creative_id": e["criativo"]},
                                              "status": "PAUSED"}, "anuncio (PAUSED)")
        if not aid:
            sys.exit("anuncio recusado: nada ativado")
        e["anuncio"] = aid
        salva(e)

    if ATIVAR and not e.get("ativado"):
        time.sleep(35)  # #613
        b.post(e["anuncio"], {"status": "ACTIVE"}, "%s ATIVADO (ok da Mileny)" % NOME)
        e["ativado"] = True
        salva(e)

    print("--- conferencia")
    time.sleep(3)
    ok, c = form_no_criativo(e["criativo"])
    afs = c.get("asset_feed_spec") or {}
    d = b.get(e["anuncio"], {"fields": "name,adset_id,status,effective_status,issues_info,"
                                       "creative{degrees_of_freedom_spec}"})
    feats = d["creative"].get("degrees_of_freedom_spec", {}).get("creative_features_spec", {})
    print(json.dumps({
        "anuncio": e["anuncio"], "nome": d["name"], "conjunto": d["adset_id"], "status": d["status"],
        "effective": d["effective_status"], "issues": d.get("issues_info"), "criativo": e["criativo"], "forma": e.get("forma"),
        "form_presente": ok, "imagens": [(i.get("hash"), [l.get("name") for l in i.get("adlabels", [])]) for i in afs.get("images", [])],
        "regras": [(r.get("image_label", {}).get("name"), r.get("customization_spec", {}).get("instagram_positions"))
                   for r in afs.get("asset_customization_rules", [])],
        "cta": afs.get("call_to_action_types"), "recursos_ia": len(feats),
        "ia_ligada": [x for x, v in feats.items() if v.get("enroll_status") != "OPT_OUT"],
    }, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
