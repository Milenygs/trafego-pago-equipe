"""AFS Industria - Rota Santa: publica os 8 anuncios com o FORMS INDUSTRIA 2.0- ROTA SANTANA.
Criativos ja criados em 14/09/2026 (form 1063174803151896, tudo OPT_OUT). Os ads foram recusados
por falta de forma de pagamento (subcode 1359188). Depois que a forma de pagamento for regularizada,
rodar:  python "$HOME\\OneDrive\\.claude\\skills\\meta-ads-ratos\\scripts\\afs_rotasanta_form20.py"
Cria tudo PAUSED; a ativacao e manual.
"""
import os, json, time, requests

env = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
TOK = [l.split("=", 1)[1].strip().strip('"') for l in open(env, encoding="utf-8") if l.startswith("META_ADS_TOKEN")][0]
G = "https://graph.facebook.com/v23.0/"
ACT, ADSET, NEW = "act_1092055801580226", "120250505784000776", "1063174803151896"

CREATIVES = [
    ("VÍDEO - GREGO", "1759882148586831"),
    ("VD - SE VOCÊ TEM UM FREEZER", "1363192635803533"),
    ("VD - VC QUER SÓ UM FORNECEDOR", "2045747059416441"),
    ("CARD - TENHA MAIS SABOR", "1044787855065101"),
    ("VÍDEO - LOGISTICA SHOW", "4578899489056250"),
    ("CD - SEJA REVENDEDOR [Rota Santa]", "1429314379262871"),
    ("VÍDEO - COOKIES", "1766088794599964"),
    ("CD - QUALIDADE QUE GIRA", "1691948209019379"),
]

created = []
for name, cid in CREATIVES:
    r = requests.post(G + ACT + "/ads", data={"access_token": TOK, "name": f"{name} [FORM RS 2.0]", "adset_id": ADSET,
                                              "creative": json.dumps({"creative_id": cid}), "status": "PAUSED"}, timeout=120).json()
    time.sleep(2)
    if "error" in r:
        e = r["error"]
        print("ERRO |", name, "|", e.get("error_subcode"), e.get("error_user_msg") or e.get("message"))
        if e.get("error_subcode") == 1359188:
            print("Forma de pagamento ainda invalida. Nada mais foi tentado."); break
        continue
    print("OK |", name, "| ad", r["id"])
    created.append(r["id"])

time.sleep(20)
for ad in created:
    d = requests.get(G + ad, params={"access_token": TOK, "fields": "name,status,effective_status,issues_info,creative{object_story_spec,asset_feed_spec{call_to_actions},call_to_action}"}, timeout=60).json()
    s = json.dumps(d.get("creative", {}))
    print(d.get("name"), "|", d.get("status"), "/", d.get("effective_status"), "| form novo:", NEW in s,
          "| issues:", [i.get("error_summary") for i in d.get("issues_info", [])])
