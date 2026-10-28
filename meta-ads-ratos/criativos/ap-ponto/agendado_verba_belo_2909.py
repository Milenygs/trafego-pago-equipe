"""Agendado para 29/09/2026 06:00 (Agendador de Tarefas do Windows: "AP Ponto - Verba Belo 29-09").

Troca de verba aprovada pela Mileny em 28/09, depois da leitura do CV (custo por simulacao: LAL R$267 x Interesse R$529):
  [BELO] LAL Compradores RMBH   R$300 -> R$400/dia
  [BELO] Interesse Imovel 25-45 R$350 -> R$250/dia
Total da campanha de LP continua R$800/dia. Grava log, registra no historico da AP Ponto e avisa no Telegram.
"""
import datetime
import json
import os
import subprocess
import sys
from pathlib import Path

import requests

SKILL = Path(os.path.expanduser("~/OneDrive/.claude/skills/meta-ads-ratos"))
env = (SKILL / ".env").read_text(encoding="utf-8")
TOKEN = [l.split("=", 1)[1].strip().strip('"') for l in env.splitlines() if l.startswith("META_ADS_TOKEN")][0]
G = "https://graph.facebook.com/v23.0/"
MUDANCAS = [("120245790363030358", "[BELO] LAL Compradores RMBH", 30000, 40000),
            ("120245790403680358", "[BELO] Interesse Imóvel 25-45", 35000, 25000)]
LOG = Path(__file__).with_suffix(".log")
HIST = Path(os.path.expanduser("~/OneDrive/Carteira/outros/ap-ponto/historico/2026-09.md"))


def log(msg):
    linha = f"{datetime.datetime.now():%d/%m/%Y %H:%M:%S} {msg}"
    print(linha)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(linha + "\n")


resumo = []
for sid, nome, antes, depois in MUDANCAS:
    atual = requests.get(G + sid, params={"access_token": TOKEN, "fields": "daily_budget,status"}, timeout=60).json()
    if "error" in atual:
        log(f"ERRO lendo {nome}: {atual['error'].get('message')}")
        resumo.append(f"❌ {nome}: erro ao ler")
        continue
    if int(atual["daily_budget"]) != antes:
        log(f"PULADO {nome}: verba atual R${int(atual['daily_budget'])/100:.0f} diferente do esperado (R${antes/100:.0f}); alguem mexeu antes")
        resumo.append(f"⚠️ {nome}: não alterado (estava R${int(atual['daily_budget'])/100:.0f}, esperado R${antes/100:.0f})")
        continue
    r = requests.post(G + sid, data={"access_token": TOKEN, "daily_budget": depois}, timeout=60).json()
    conf = requests.get(G + sid, params={"access_token": TOKEN, "fields": "daily_budget"}, timeout=60).json()
    ok = r.get("success") and int(conf.get("daily_budget", 0)) == depois
    log(f"{'OK' if ok else 'FALHOU'} {nome}: R${antes/100:.0f} -> R${depois/100:.0f} | resposta {r}")
    resumo.append(f"{'✅' if ok else '❌'} {nome}: R${antes/100:.0f} → R${int(conf.get('daily_budget', 0))/100:.0f}")

texto = "AP Ponto | Belo | troca de verba programada (29/09 06:00)\n" + "\n".join(resumo)
try:
    subprocess.run([sys.executable, str(SKILL / "scripts" / "notify.py"), "telegram", "--text", texto], timeout=60)
except Exception as e:  # noqa: BLE001
    log(f"telegram falhou: {e}")

try:
    txt = HIST.read_text(encoding="utf-8")
    marca = "---\n\n## "
    entrada = ("---\n\n## 2026-09-29 06:00 - AP Ponto: troca de verba do Belo (agendada em 28/09)\n\n"
               "Aplicada pelo Agendador de Tarefas (`agendado_verba_belo_2909.py`), aprovada pela Mileny em 28/09 com base no CV "
               "(custo por simulação LAL R$267 × Interesse R$529):\n" + "\n".join(f"- {r}" for r in resumo) + "\n\n")
    i = txt.find(marca)
    HIST.write_text(txt[:i] + entrada + txt[i + len("---\n\n"):] if i >= 0 else txt + "\n" + entrada, encoding="utf-8")
except Exception as e:  # noqa: BLE001
    log(f"historico nao atualizado: {e}")
