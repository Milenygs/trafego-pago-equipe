#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cheirin Bao MT — criativos "LEADS 1, 2 e 3" (14/10/2026). Mileny: "pode sim, nao e da franqueada Raissa".

- AD40 (LEADS 2, duas franqueadas, superacao) -> 16 QUENTE + LAL, ATIVADO (ok da Mileny).
- AD39 (LEADS 1 CORTADO em 25,04s: o final "como ser um franqueador de sucesso" saiu) -> PINO SP, PAUSED.
  Entra no lugar do AD37 em 16/10 se o AD37 nao qualificar (decisao de 13/10).
- N2 (LEADS 3, cliente indica a experiencia) -> topo 02 Aquecimento (THRUPLAY), PAUSED, sem botao.

Captacao: modelo DRE 146k (form 2805248149848936, SIGN_UP, 83 recursos de IA em OPT_OUT), copy sem numero
financeiro. Topo: modelo 1732633824304507 (titulo "Cheirin Bao", sem CTA, IA em OPT_OUT).
Videos ja preparados em %TEMP%\\cheirin_leads_1410 (LEADS 1 cortado, .mov convertidos para H.264/AAC).
Estado em estado_leads_1410.json (nao recria o que ja existe).
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_outubro_depoimentos as b  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
ESTADO = os.path.join(AQUI, "estado_leads_1410.json")
PASTA = os.path.join(os.environ["TEMP"], "cheirin_leads_1410")
MODELO_TOPO = "1732633824304507"

PECAS = [
    {
        "chave": "ad40", "arquivo": "AD40 - LEADS 2.mp4", "thumb": 3.0, "tipo": "captacao",
        "adset": "120258418032850212", "nome": "Q16 - AD40 [PROVA] franqueadas pensaram em desistir", "ativar": True,
        "copy": (
            "Pensaram em desistir. Hoje, estão crescendo na rede.\n\n"
            "Duas franqueadas Cheirin Bão contam como foi o começo: pouca gente apoiou, os momentos difíceis vieram, "
            "e a franqueadora esteve junto o tempo todo. Uma delas já está indo para a quarta loja.\n\n"
            "“Se eu tivesse hoje que escolher alguma coisa pra fazer, eu faria a mesma coisa.”\n\n" + b.FIM),
    },
    {
        "chave": "ad39", "arquivo": "AD39 - LEADS 1 cortado.mp4", "thumb": 6.0, "tipo": "captacao",
        "adset": "120257337905370212", "nome": "[PINO SP] AD39 [FUNDADOR] ecossistema do pe a xicara", "ativar": False,
        "copy": (
            "Do pé de café à xícara, a Cheirin Bão cuida de toda a cadeia.\n\n"
            "No vídeo, você conhece esse ecossistema por dentro e ouve quem já faz parte dele: franqueados que "
            "aprenderam a tocar o negócio junto com a rede, com apoio em cada dificuldade.\n\n"
            "Quer ver o passo a passo? Clique e fale com a gente.\n\n" + b.FIM),
    },
    {
        "chave": "n2", "arquivo": "N2 - LEADS 3 cliente indica.mp4", "thumb": 6.0, "tipo": "topo",
        "adset": "120256940921410212", "nome": "N2 - cliente indica a experiencia", "ativar": False,
        "copy": (
            "Tem gente que vem pelo café e volta pela experiência.\n\n"
            "Uma cliente conta por que indica a Cheirin Bão: os vários jeitos de passar o café, os grãos, a torra e "
            "um atendimento que faz a pessoa se sentir bem.\n\n"
            "É essa experiência que cada franqueado leva para a sua cidade."),
    },
]


def modelo_topo():
    d = b.get(MODELO_TOPO, {"fields": "object_story_spec,degrees_of_freedom_spec"})
    feats = d["degrees_of_freedom_spec"].get("creative_features_spec", {})
    feats.pop("standard_enhancements", None)
    assert all(v.get("enroll_status") == "OPT_OUT" for v in feats.values()), "modelo do topo com IA ligada"
    oss = d["object_story_spec"]
    return {"page_id": oss["page_id"], "instagram_user_id": oss["instagram_user_id"],
            "title": oss["video_data"]["title"], "dof": {"creative_features_spec": feats}}


def salva(e):
    json.dump(e, open(ESTADO, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def main():
    if "--dry" in sys.argv:
        for p in PECAS:
            print("== %s -> %s\n%s\n" % (p["nome"], p["adset"], p["copy"]))
        return
    e = json.load(open(ESTADO, encoding="utf-8")) if os.path.exists(ESTADO) else {}
    cap, topo = b.modelo(), modelo_topo()
    for p in PECAS:
        k = p["chave"]
        r = e.setdefault(k, {})
        caminho = os.path.join(PASTA, p["arquivo"])
        if not r.get("video"):
            r["video"] = b.sobe_video(caminho); salva(e)
        if not r.get("capa"):
            r["capa"] = b.sobe_thumb(caminho, p["thumb"]); salva(e)
        if not r.get("criativo"):
            if p["tipo"] == "captacao":
                m = cap
                vd = {"video_id": r["video"], "image_hash": r["capa"], "title": m["title"],
                      "link_description": m["link_description"], "message": p["copy"], "call_to_action": m["cta"]}
            else:
                m = topo
                vd = {"video_id": r["video"], "image_hash": r["capa"], "title": m["title"], "message": p["copy"]}
            story = {"page_id": m["page_id"], "instagram_user_id": m["instagram_user_id"], "video_data": vd}
            r["criativo"] = b.post("%s/adcreatives" % b.CONTA, {"name": "Cheirin — %s" % p["nome"],
                                                                 "object_story_spec": story,
                                                                 "degrees_of_freedom_spec": m["dof"]},
                                   "criativo " + p["nome"])
            salva(e)
        if not r.get("anuncio"):
            r["anuncio"] = b.post("%s/ads" % b.CONTA, {"name": p["nome"], "adset_id": p["adset"],
                                                        "creative": {"creative_id": r["criativo"]},
                                                        "status": "PAUSED"}, "anuncio %s (PAUSED)" % p["nome"])
            salva(e)
        if p["ativar"] and not r.get("ativado"):
            time.sleep(35)  # #613
            b.post(r["anuncio"], {"status": "ACTIVE"}, "%s ATIVADO (ok da Mileny)" % p["nome"])
            r["ativado"] = True
            salva(e)
    print("--- conferencia")
    for p in PECAS:
        r = e[p["chave"]]
        d = b.get(r["anuncio"], {"fields": "name,adset_id,status,effective_status,"
                                            "creative{object_story_spec,degrees_of_freedom_spec}"})
        vd = d["creative"]["object_story_spec"]["video_data"]
        feats = d["creative"].get("degrees_of_freedom_spec", {}).get("creative_features_spec", {})
        cta = vd.get("call_to_action") or {}
        print(json.dumps({"nome": d["name"], "anuncio": r["anuncio"], "conjunto": d["adset_id"], "status": d["status"],
                          "effective": d["effective_status"], "video": r["video"], "criativo": r["criativo"],
                          "cta": cta.get("type"), "form": (cta.get("value") or {}).get("lead_gen_form_id"),
                          "recursos_ia": len(feats),
                          "ia_ligada": [x for x, v in feats.items() if v.get("enroll_status") != "OPT_OUT"]},
                         ensure_ascii=False))


if __name__ == "__main__":
    main()
