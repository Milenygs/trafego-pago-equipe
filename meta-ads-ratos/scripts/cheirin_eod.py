# -*- coding: utf-8 -*-
"""Relatorio de fim de dia da Cheirin Bao -> Telegram.
Roda via Agendador de Tarefas do Windows (20h). Puxa as 3 camadas do funil
(Leads Quente, Lookalike, Feed/Aquecimento) do dia e manda o resumo no Telegram.
"""
import sys, os, subprocess, datetime
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
NOTIFY = os.path.join(HERE, "notify.py")
REL_DIR = os.path.join(SKILL, "relatorios")
os.makedirs(REL_DIR, exist_ok=True)

sys.path.insert(0, HERE)
from lib import init_api
from facebook_business.adobjects.adset import AdSet

init_api()

LAYERS = [
    ("Feed/Aquecimento", "120253539693080212", "video"),
    ("Leads Quente", "120255934999460212", "leads"),
    ("Lookalike",    "120255896539410212", "leads"),
    ("BOFU (leads existentes)", "120256270802500212", "leads"),
]

def n(x):
    try: return float(x or 0)
    except Exception: return 0.0

def metrics(adset_id):
    try:
        ins = AdSet(adset_id).get_insights(
            params={"date_preset": "today"},
            fields=["spend","impressions","reach","frequency","clicks","ctr","actions"])
    except Exception as e:
        return {"erro": str(e).splitlines()[0]}
    if not ins:
        return None
    r = ins[0]
    acts = {a["action_type"]: n(a["value"]) for a in (r.get("actions") or [])}
    return {
        "spend": n(r.get("spend")), "impr": int(n(r.get("impressions"))),
        "reach": int(n(r.get("reach"))), "freq": n(r.get("frequency")),
        "ctr": n(r.get("ctr")),
        "leads": int(acts.get("lead") or acts.get("onsite_conversion.lead_grouped") or 0),
        "video": int(acts.get("video_view") or 0),
        "conversas": int(acts.get("onsite_conversion.messaging_conversation_started_7d") or 0),
    }

hoje = datetime.date.today().strftime("%d/%m/%Y")
L = [f"CHEIRIN BAO — Relatorio do dia {hoje}", "(Funil Espiral, teste R$800/dia)", ""]
tot_spend = tot_leads = 0.0
for label, aid, tipo in LAYERS:
    m = metrics(aid)
    if m and m.get("erro"):
        L.append(f"• {label}: erro ({m['erro']})"); L.append(""); continue
    if not m or m["spend"] == 0:
        L.append(f"• {label}: sem entrega ainda hoje"); L.append(""); continue
    tot_spend += m["spend"]
    L.append(f"• {label}")
    L.append(f"   Investido R$ {m['spend']:.2f} | Alcance {m['reach']} | Freq {m['freq']:.2f}")
    if tipo == "video":
        L.append(f"   Video-views: {m['video']} | CTR {m['ctr']:.2f}%")
    else:
        tot_leads += m["leads"]
        cpl = f"R$ {m['spend']/m['leads']:.2f}" if m["leads"] else "—"
        L.append(f"   Leads: {m['leads']} | CPL {cpl} | CTR {m['ctr']:.2f}%")
        if m["conversas"]:
            L.append(f"   Conversas: {m['conversas']}")
    L.append("")

L.append("————————————————")
cpl_geral = f"R$ {tot_spend/tot_leads:.2f}" if tot_leads else "—"
L.append(f"TOTAL: R$ {tot_spend:.2f} investido | {int(tot_leads)} leads | CPL medio {cpl_geral}")

report = "\n".join(L)
path = os.path.join(REL_DIR, f"cheirin_eod_{datetime.date.today().isoformat()}.txt")
with open(path, "w", encoding="utf-8") as f:
    f.write(report)

subprocess.run([sys.executable, NOTIFY, "telegram", "--file", path], check=False)
print(report)
