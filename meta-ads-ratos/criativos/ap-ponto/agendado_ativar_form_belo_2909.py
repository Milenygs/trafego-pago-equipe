"""Agendado para 29/09/2026 06:02 (Agendador de Tarefas: "AP Ponto - Ativar Form Belo 29-09").

Pedido da Mileny em 28/09: ativar a campanha de formulario do Belo so com 3 conjuntos (R$100/dia cada, ja configurados):
  [BELO][FORM] Momento de Vida 25-45, [BELO][FORM] LAL Compradores RMBH, [BELO][FORM] LAL Qualificados CAPI
Ativa campanha -> conjuntos -> anuncios de VIDEO (imagens ficam pausadas). Base Quente, Interesse antigo e Remarketing
continuam pausados. Grava log, registra no historico e avisa no Telegram.
"""
import datetime
import os
import subprocess
import sys
import time
from pathlib import Path

import requests

SKILL = Path(os.path.expanduser("~/OneDrive/.claude/skills/meta-ads-ratos"))
env = (SKILL / ".env").read_text(encoding="utf-8")
TOKEN = [l.split("=", 1)[1].strip().strip('"') for l in env.splitlines() if l.startswith("META_ADS_TOKEN")][0]
G = "https://graph.facebook.com/v23.0/"
CAMP = "120245805859660358"
CONJUNTOS = {"120245855388890358": "Momento de Vida 25-45", "120245805860620358": "LAL Compradores RMBH",
             "120245854126000358": "LAL Qualificados CAPI"}
LOG = Path(__file__).with_suffix(".log")
HIST = Path(os.path.expanduser("~/OneDrive/Carteira/outros/ap-ponto/historico/2026-09.md"))


def log(msg):
    linha = f"{datetime.datetime.now():%d/%m/%Y %H:%M:%S} {msg}"
    print(linha)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(linha + "\n")


def ativar(obj):
    for tentativa in range(3):
        r = requests.post(G + obj, data={"access_token": TOKEN, "status": "ACTIVE"}, timeout=60).json()
        if r.get("success"):
            return True
        log(f"tentativa {tentativa + 1} falhou em {obj}: {r.get('error', {}).get('message')}")
        time.sleep(20)
    return False


resumo = []
ok = ativar(CAMP)
resumo.append(f"{'✅' if ok else '❌'} Campanha [BELO] Lançamento | Lead Form")
for sid, nome in CONJUNTOS.items():
    ok_s = ativar(sid)
    ads = requests.get(G + sid + "/ads", params={"access_token": TOKEN, "fields": "id,name"}, timeout=60).json().get("data", [])
    vids = [a for a in ads if a["name"].startswith("VID")]
    ok_a = sum(ativar(a["id"]) for a in vids)
    resumo.append(f"{'✅' if ok_s else '❌'} {nome}: R$100/dia · {ok_a}/{len(vids)} vídeos ativos")
    time.sleep(2)

# conferencia
for sid, nome in CONJUNTOS.items():
    s = requests.get(G + sid, params={"access_token": TOKEN, "fields": "status,effective_status,daily_budget"}, timeout=60).json()
    log(f"{nome}: {s.get('status')}/{s.get('effective_status')} R${int(s.get('daily_budget', 0))/100:.0f}")
c = requests.get(G + CAMP, params={"access_token": TOKEN, "fields": "status,effective_status"}, timeout=60).json()
log(f"campanha: {c.get('status')}/{c.get('effective_status')}")
for r in resumo:
    log(r)

texto = "AP Ponto | Belo | formulário ativado (29/09 06:00)\n" + "\n".join(resumo) + \
        "\nBase Quente, Interesse antigo e Remarketing seguem pausados. Imagens pausadas."
try:
    subprocess.run([sys.executable, str(SKILL / "scripts" / "notify.py"), "telegram", "--text", texto], timeout=60)
except Exception as e:  # noqa: BLE001
    log(f"telegram falhou: {e}")
try:
    txt = HIST.read_text(encoding="utf-8")
    entrada = ("---\n\n## 2026-09-29 06:02 - AP Ponto: campanha de formulário do Belo ativada (agendada em 28/09)\n\n"
               "Pedido da Mileny: R$100/dia em cada um de 3 conjuntos, só vídeos. Script `agendado_ativar_form_belo_2909.py`.\n"
               + "\n".join(f"- {r}" for r in resumo) + "\n\n")
    i = txt.find("---\n\n## ")
    HIST.write_text(txt[:i] + entrada + txt[i + len("---\n\n"):] if i >= 0 else txt + "\n" + entrada, encoding="utf-8")
except Exception as e:  # noqa: BLE001
    log(f"historico nao atualizado: {e}")
