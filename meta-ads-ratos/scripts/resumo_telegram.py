#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Meta Ads Ratos - Resumo diario no Telegram (sem IA, deterministico).

Le o digest do dia (relatorios/diario-AAAA-MM-DD.json) e envia um resumo
compacto no Telegram. Feito para rodar agendado (Task Scheduler) logo apos
o `diario.py varrer`.

Uso:
  python resumo_telegram.py            # digest de hoje
  python resumo_telegram.py --data 2026-07-16
"""

import argparse
import json
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import _load_env_file  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _enviar(texto):
    import urllib.request
    _load_env_file()
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID nao configurados.", file=sys.stderr)
        sys.exit(2)
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = json.dumps({"chat_id": chat_id, "text": texto[:4000],
                       "disable_web_page_preview": True}).encode("utf-8")
    req = urllib.request.Request(url, data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        r.read()


def _texto_tarefas():
    """Pendencias marcadas para hoje. Nao depende da API nem do digest."""
    try:
        import tarefas as agenda
        return agenda.texto_telegram(agenda.montar_hoje())
    except Exception:
        return ""


def _texto_boletos(bloco):
    """Bloco de boletos do dia. Aceita o bloco do digest ou None (recalcula)."""
    try:
        import boletos as calendario
        if not bloco or not bloco.get("itens"):
            bloco = calendario.montar_hoje()
        return calendario.texto_telegram(bloco)
    except Exception:
        return ""


def montar_resumo(digest):
    resumo = digest.get("resumo", {})
    clientes = digest.get("clientes", [])
    ref = digest.get("referencia", "")

    linhas = [f"📊 Diário Meta Ads ({ref})", ""]
    linhas.append(
        f"R$ {resumo.get('gasto_total_ontem', 0):,.2f} gastos · "
        f"{resumo.get('leads_total_ontem', 0)} leads · "
        f"{resumo.get('clientes_varridos', 0)} contas varridas"
    )

    # Boletos vem ANTES dos alertas de campanha: e a unica parte do resumo com
    # prazo externo (o cliente precisa receber e pagar), entao nao pode ficar
    # soterrada no meio de 12 alertas de CPL.
    bloco = _texto_boletos(digest.get("boletos"))
    if bloco:
        linhas += ["", bloco]

    # Pendencia marcada para hoje vem junto: e acao combinada com data, nao
    # diagnostico — se ficar depois dos alertas, passa batido.
    pend = _texto_tarefas()
    if pend:
        linhas += ["", pend]

    criticos, atencao, erros = [], [], []
    for c in clientes:
        nome = c.get("nome") or c.get("slug")
        if c.get("erro"):
            erros.append(f"• {nome}: {c['erro']}")
            continue
        for a in c.get("alertas", []):
            linha = f"• {nome}: {a.get('msg', '')}"
            if a.get("gravidade") == "critico":
                criticos.append(linha)
            else:
                atencao.append(linha)

    if criticos:
        linhas += ["", f"🔴 CRÍTICOS ({len(criticos)}):"] + criticos[:12]
        if len(criticos) > 12:
            linhas.append(f"  ... e mais {len(criticos) - 12}")
    if atencao:
        linhas += ["", f"🟡 Atenção ({len(atencao)}):"] + atencao[:8]
        if len(atencao) > 8:
            linhas.append(f"  ... e mais {len(atencao) - 8}")
    if erros:
        linhas += ["", f"⚠️ Sem acesso/erro ({len(erros)}):"] + erros[:5]
    if not criticos and not atencao and not erros:
        linhas += ["", "🟢 Nenhum alerta hoje."]

    linhas += ["", "Detalhes e ações: abrir o Claude Code e rodar /ads-diario."]
    return "\n".join(linhas)


def main():
    p = argparse.ArgumentParser(description="Resumo diario no Telegram")
    p.add_argument("--data", help="AAAA-MM-DD (padrao: hoje)")
    args = p.parse_args()

    dia = args.data or date.today().isoformat()
    caminho = os.path.join(BASE, "relatorios", f"diario-{dia}.json")
    if not os.path.exists(caminho):
        # O calendario de boletos nao depende da API: mesmo com a varredura
        # quebrada, o aviso do dia tem que sair.
        msg = (f"⚠️ Diário {dia}: varredura FALHOU — nenhum relatório gerado. "
               f"Rodar /ads-diario manualmente no Claude Code.")
        for bloco in (_texto_boletos(None), _texto_tarefas()):
            if bloco:
                msg += "\n\n" + bloco
        _enviar(msg)
        print(f"Digest {caminho} nao existe; alerta de falha enviado.")
        sys.exit(1)

    with open(caminho, encoding="utf-8") as f:
        digest = json.load(f)
    _enviar(montar_resumo(digest))
    print("Resumo enviado no Telegram.")


if __name__ == "__main__":
    main()
