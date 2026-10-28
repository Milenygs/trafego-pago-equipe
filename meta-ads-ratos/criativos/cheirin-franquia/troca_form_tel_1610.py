#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cheirin Bao MT — troca para o formulario novo com verificacao de telefone (16/10/2026). Mileny: "pode sim".

Form novo: 1106977512033195 "[M] FORMS FRANQUIA- VERIFICACAO TEL" (Intencao mais alta). Antigo: 2805248149848936.
Para cada um dos 10 anuncios de captacao ainda no antigo: criativo novo com o mesmo video/imagem e texto, so o form
trocado, IA toda em OPT_OUT (dof do modelo DRE 146k), e troca do criativo no proprio anuncio (nome e ID ficam: o CRM
roteia pelo nome). AD41 (imagem por posicionamento) e AD32 (anuncio de post, IA ligada, spec ilegivel) sao refeitos.

Uso:  --dry  (le e monta o plano em estado_troca_form_1610.json, nao grava nada)
      sem flag: aplica o plano (retoma do estado se parar no meio)
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
import build_outubro_depoimentos as b  # noqa: E402
import build_ad41_1510 as a41  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
ESTADO = os.path.join(AQUI, "estado_troca_form_1610.json")
NOVO, ANTIGO = "1106977512033195", "2805248149848936"
FB_ME = "http://fb.me/"

ANUNCIOS = {
    "120257017816030212": "VD01 - franqueada_raissa (VD02 Raissa)",
    "120258142932050212": "[PINO SP] AD38",
    "120258419535120212": "[PINO SP] AD39",
    "120258456784050212": "VD01 - franqueada_raissa (PINO SP)",
    "120258427452430212": "Quente - AD32 (PINO SP, post)",
    "120258456832290212": "AD37 (Q16)",
    "120258418038660212": "Q16 - AD38",
    "120258419509260212": "Q16 - AD40",
    "120258461665020212": "Q16 - AD41 (imagem)",
    "120258418044610212": "VD03 - franqueada_raissa (Q16)",
}
AD32_COPY = next(p["copy"] for p in b.PECAS if p["rotulo"].startswith("AD32"))


def get(path, params, tentativas=4):
    for i in range(tentativas):
        try:
            return b.get(path, params)
        except urllib.error.HTTPError as e:
            corpo = e.read().decode("utf-8")
            if any(c in corpo for c in ('"code":80004', '"code":17', '"code":613', '"code":32')) and i < tentativas - 1:
                print("  ... limite da Meta, esperando %ds" % (60 * (i + 1)))
                time.sleep(60 * (i + 1))
                continue
            return {"erro": corpo[:400]}


def post(path, params, oque, tentativas=4):
    corpo = {k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v) for k, v in params.items()}
    corpo["access_token"] = b.TOKEN
    dados = urllib.parse.urlencode(corpo).encode()
    for i in range(tentativas):
        try:
            with urllib.request.urlopen(urllib.request.Request(b.API + path, data=dados), timeout=120) as r:
                j = json.load(r)
                print("  OK   %-52s %s" % (oque, j.get("id") or j.get("success")))
                return j.get("id") or j.get("success")
        except urllib.error.HTTPError as e:
            err = json.loads(e.read().decode("utf-8")).get("error", {})
            if err.get("code") in (80004, 17, 613, 32) and i < tentativas - 1:
                print("  ... limite da Meta (%s), esperando %ds" % (err.get("code"), 60 * (i + 1)))
                time.sleep(60 * (i + 1))
                continue
            print("  ERRO %-52s %s | %s" % (oque, err.get("error_subcode"), err.get("error_user_msg") or err.get("message")))
            return None


def troca_form(cta):
    cta = json.loads(json.dumps(cta))
    cta.setdefault("value", {})["lead_gen_form_id"] = NOVO
    cta["value"].setdefault("link", FB_ME)
    return cta


def plano_video(ad_id, cid, m):
    d = get(cid, {"fields": "object_story_spec,url_tags"})
    if "erro" in d:
        return None, d["erro"]
    oss = d["object_story_spec"]
    vd = oss.get("video_data")
    if not vd:
        return None, "criativo sem video_data"
    novo_vd = {k: vd[k] for k in ("video_id", "title", "message", "link_description") if vd.get(k)}
    if vd.get("image_hash"):
        novo_vd["image_hash"] = vd["image_hash"]
    elif vd.get("image_url"):
        novo_vd["image_url"] = vd["image_url"]
    if (vd.get("call_to_action") or {}).get("value", {}).get("lead_gen_form_id") != ANTIGO:
        return None, "form atual nao e o antigo: %s" % json.dumps(vd.get("call_to_action"))
    novo_vd["call_to_action"] = troca_form(vd["call_to_action"])
    spec = {"object_story_spec": {"page_id": oss["page_id"], "instagram_user_id": oss.get("instagram_user_id") or m["instagram_user_id"],
                                  "video_data": novo_vd},
            "degrees_of_freedom_spec": m["dof"]}
    if d.get("url_tags"):
        spec["url_tags"] = d["url_tags"]
    return spec, None


def sem_ids(x):
    """Copia o spec lido tirando os 'id' dos rótulos (a Meta gera de novo)."""
    if isinstance(x, dict):
        return {k: sem_ids(v) for k, v in x.items() if k != "id"}
    if isinstance(x, list):
        return [sem_ids(v) for v in x]
    return x


def plano_afs_painel(cid, m):
    """Criativo do painel com 2 vídeos por posicionamento (asset_feed_spec): copia fiel, só troca o form, IA em OPT_OUT."""
    d = get(cid, {"fields": "asset_feed_spec,object_story_spec,url_tags"})
    s = d.get("asset_feed_spec")
    if not s or not s.get("videos"):
        return None, "sem video_data e sem videos no asset_feed_spec"
    forms = re.findall(r'"lead_gen_form_id":\s*"(\d+)"', json.dumps(s.get("call_to_actions")))
    if forms != [ANTIGO]:
        return None, "form atual inesperado: %s" % forms
    afs = {k: sem_ids(s[k]) for k in ("ad_formats", "optimization_type", "bodies", "titles", "link_urls",
                                       "call_to_action_types", "asset_customization_rules") if k in s}
    afs["descriptions"] = [x for x in sem_ids(s.get("descriptions", [])) if x.get("text")]
    if not afs["descriptions"]:
        afs.pop("descriptions")
    for lu in afs["link_urls"]:
        if not lu.get("display_url"):
            lu.pop("display_url", None)
    videos = []
    for v in s["videos"]:
        th = sorted(get(v["video_id"] + "/thumbnails", {"fields": "uri,is_preferred"}).get("data", []),
                    key=lambda t: not t.get("is_preferred"))
        if not th:
            return None, "video %s sem capa" % v["video_id"]
        videos.append({"video_id": v["video_id"], "thumbnail_url": th[0]["uri"], "adlabels": sem_ids(v.get("adlabels", []))})
    afs["videos"] = videos
    afs["call_to_actions"] = [dict(sem_ids(c), value={"lead_gen_form_id": NOVO, "link": FB_ME}) for c in s["call_to_actions"]]
    oss = d["object_story_spec"]
    spec = {"object_story_spec": {"page_id": oss["page_id"], "instagram_user_id": oss.get("instagram_user_id") or m["instagram_user_id"]},
            "asset_feed_spec": afs, "degrees_of_freedom_spec": m["dof"]}
    if d.get("url_tags"):
        spec["url_tags"] = d["url_tags"]
    return spec, None


def plano_ad32(cid, m):
    d = get(cid, {"fields": "video_id,call_to_action"})
    vid = d.get("video_id")
    if not vid or (d.get("call_to_action") or {}).get("value", {}).get("lead_gen_form_id") != ANTIGO:
        return None, "AD32: video ou form inesperado: %s" % json.dumps(d)[:200]
    th = get(vid + "/thumbnails", {"fields": "uri,is_preferred"}).get("data", [])
    th = sorted(th, key=lambda t: not t.get("is_preferred"))
    if not th:
        return None, "AD32: video sem capa"
    vd = {"video_id": vid, "image_url": th[0]["uri"], "title": m["title"], "link_description": m["link_description"],
          "message": AD32_COPY, "call_to_action": troca_form(m["cta"])}
    return {"object_story_spec": {"page_id": m["page_id"], "instagram_user_id": m["instagram_user_id"], "video_data": vd},
            "degrees_of_freedom_spec": m["dof"]}, None


def plano_ad41(m):
    e41 = json.load(open(a41.ESTADO, encoding="utf-8"))
    imagens = [{"hash": e41["feed"], "adlabels": [{"name": "img_feed"}]},
               {"hash": e41["story"], "adlabels": [{"name": "img_story"}]}]
    afs = {"images": imagens, "bodies": [{"text": a41.COPY}], "titles": [{"text": m["title"]}],
           "descriptions": [{"text": m["link_description"]}], "link_urls": [{"website_url": FB_ME}],
           "call_to_action_types": ["SIGN_UP"], "ad_formats": ["SINGLE_IMAGE"],
           "asset_customization_rules": a41.REGRAS, "optimization_type": "PLACEMENT",
           "call_to_actions": [{"type": "SIGN_UP", "value": {"lead_gen_form_id": NOVO, "link": FB_ME}}]}
    return {"object_story_spec": {"page_id": m["page_id"], "instagram_user_id": m["instagram_user_id"]},
            "asset_feed_spec": afs, "degrees_of_freedom_spec": m["dof"]}, None


def salva(e):
    json.dump(e, open(ESTADO, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def monta_plano():
    m = b.modelo()
    e = {}
    for ad_id, rot in ANUNCIOS.items():
        a = get(ad_id, {"fields": "name,adset_id,effective_status,creative{id}"})
        if "erro" in a:
            e[ad_id] = {"rotulo": rot, "erro": a["erro"]}
            continue
        cid = a["creative"]["id"]
        if ad_id == "120258461665020212":
            spec, err = plano_ad41(m)
        elif ad_id == "120258427452430212":
            spec, err = plano_ad32(cid, m)
        else:
            spec, err = plano_video(ad_id, cid, m)
            if err == "criativo sem video_data":
                spec, err = plano_afs_painel(cid, m)
        e[ad_id] = {"rotulo": rot, "nome": a["name"], "conjunto": a["adset_id"], "status": a["effective_status"],
                    "criativo_antigo": cid, "spec": spec, "erro": err}
        print("%-40s | %s | criativo %s | %s" % (rot, a["effective_status"], cid, err or "pronto"))
        time.sleep(0.5)
    salva(e)
    return e


def aplica(e):
    ultimo_por_conjunto = {}
    for ad_id, r in e.items():
        if r.get("erro") or not r.get("spec"):
            print("PULADO %s: %s" % (r["rotulo"], r.get("erro")))
            continue
        print("\n== %s" % r["rotulo"])
        if not r.get("criativo_novo"):
            r["criativo_novo"] = post("%s/adcreatives" % b.CONTA,
                                      dict(r["spec"], name="Cheirin — %s (form verificacao tel 16-10)" % r["nome"]), "criativo novo")
            salva(e)
            if not r["criativo_novo"]:
                continue
            time.sleep(3)
        if not r.get("trocado"):
            espera = 35 - (time.time() - ultimo_por_conjunto.get(r["conjunto"], 0))
            if espera > 0:
                time.sleep(espera)  # #613: 35s entre escritas no mesmo conjunto
            ok = post(ad_id, {"creative": {"creative_id": r["criativo_novo"]}}, "anuncio com o criativo novo")
            ultimo_por_conjunto[r["conjunto"]] = time.time()
            if ok:
                r["trocado"] = True
                salva(e)
            time.sleep(3)


def confere(e):
    print("\n--- conferencia")
    for ad_id, r in e.items():
        d = get(ad_id, {"fields": "name,status,effective_status,creative{id,degrees_of_freedom_spec}"})
        if "erro" in d:
            print("%-40s | erro na leitura" % r["rotulo"]); continue
        cid = d["creative"]["id"]
        c = get(cid, {"fields": "object_story_spec" if ad_id != "120258461665020212" else "asset_feed_spec"})
        forms = sorted(set(re.findall(r'"lead_gen_form_id":\s*"(\d+)"', json.dumps(c))))
        feats = (d["creative"].get("degrees_of_freedom_spec") or {}).get("creative_features_spec", {})
        ligada = [k for k, v in feats.items() if v.get("enroll_status") != "OPT_OUT"]
        print("%-40s | %-6s/%-14s | criativo %s | form %s | IA ligada: %s" % (
            r["rotulo"], d["status"], d["effective_status"], cid, ",".join(forms) or "?", ligada or "nenhuma"))
        time.sleep(0.5)


if __name__ == "__main__":
    if "--dry" in sys.argv:
        monta_plano()
    else:
        est = json.load(open(ESTADO, encoding="utf-8")) if os.path.exists(ESTADO) else monta_plano()
        aplica(est)
        confere(est)
