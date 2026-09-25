#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Meta Ads Ratos - Pendencias agendadas ("o que fazer hoje").

Motor de agenda puro (nao chama a API da Meta): le `tarefas.yaml` e responde o
que esta marcado para hoje. Mesma ideia do boletos.py — por nao depender da API,
o lembrete sai mesmo quando a varredura falha por rate limit ou token.

Serve para bloco de acao combinado para um dia especifico (ex: "amanha de manha
ativamos tudo junto"), que o calendario de boleto nao cobre.

Uso:
  python tarefas.py hoje                 # o que esta marcado para hoje
  python tarefas.py hoje --data 2026-09-03
  python tarefas.py hoje --json
  python tarefas.py agenda               # tudo que esta em aberto
  python tarefas.py concluir --id afs-ativacao-form-v2
"""

import argparse
import datetime as dt
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Desde 25/09/2026 a agenda fica na Carteira (OneDrive compartilhado com a
# estagiaria), para a lista ser a mesma em todas as maquinas. Antes ficava
# dentro desta skill, que cada maquina tem a sua copia.
TAREFAS_PATH = os.environ.get("TAREFAS_PATH") or os.path.join(
    os.path.expanduser("~"), "OneDrive", "Carteira", "_Central", "tarefas.yaml")

DIAS = ["segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"]


def _br(d):
    return f"{d.strftime('%d/%m')} ({DIAS[d.weekday()]})"


def carregar():
    import yaml
    if not os.path.exists(TAREFAS_PATH):
        print(f"AVISO: agenda nao encontrada em {TAREFAS_PATH} "
              "(a pasta Carteira sincronizou nesta maquina?)", file=sys.stderr)
        return []
    with open(TAREFAS_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("tarefas") or []


def _data(t):
    d = t.get("data")
    return dt.date.fromisoformat(d) if isinstance(d, str) else d


def montar_hoje(hoje=None):
    hoje = hoje or dt.date.today()
    itens = []
    for t in carregar():
        if t.get("concluida"):
            continue
        d = _data(t)
        if d is None:
            continue
        atraso = (hoje - d).days
        if atraso < 0:
            estado, grav = "AGENDADA", "info"
        elif atraso == 0:
            estado, grav = "HOJE", "critico"
        else:
            estado, grav = "ATRASADA", "critico"
        itens.append({
            "id": t.get("id"),
            "titulo": t.get("titulo", ""),
            "cliente": t.get("cliente", ""),
            "conta": t.get("conta", ""),
            "data": d.isoformat(),
            "estado": estado,
            "gravidade": grav,
            "dias_atraso": max(atraso, 0),
            "passos": t.get("passos") or [],
            "observacao": t.get("observacao", ""),
        })
    ordem = {"critico": 0, "info": 1}
    itens.sort(key=lambda i: (ordem[i["gravidade"]], i["data"]))
    return {"data": hoje.isoformat(), "itens": itens}


def acionaveis(bloco):
    return [i for i in bloco["itens"] if i["gravidade"] == "critico"]


def texto_telegram(bloco):
    """Bloco curto pro resumo das 7h. '' se nao ha nada para hoje."""
    itens = acionaveis(bloco)
    if not itens:
        return ""
    linhas = ["📌 PARA HOJE"]
    for i in itens:
        atraso = f" (ATRASADA {i['dias_atraso']}d)" if i["estado"] == "ATRASADA" else ""
        alvo = f" [{i['cliente']}]" if i.get("cliente") else ""
        linhas.append(f"🔴{alvo} {i['titulo']}{atraso}")
        for p in i["passos"][:8]:
            linhas.append(f"   • {p}")
        if i.get("observacao"):
            linhas.append(f"   ⚠️ {i['observacao']}")
    return "\n".join(linhas)


def cmd_hoje(args):
    hoje = dt.date.fromisoformat(args.data) if args.data else None
    bloco = montar_hoje(hoje)
    if args.json:
        print(json.dumps(bloco, indent=2, ensure_ascii=False))
        return
    d = dt.date.fromisoformat(bloco["data"])
    itens = acionaveis(bloco)
    if not itens:
        print(f"Nada marcado para {_br(d)}.")
        return
    print(f"Pendencias para {_br(d)}\n")
    for i in itens:
        atraso = f"  (ATRASADA {i['dias_atraso']} dia(s))" if i["estado"] == "ATRASADA" else ""
        print(f"[{i['cliente'] or '-'}] {i['titulo']}{atraso}")
        for p in i["passos"]:
            print(f"   - {p}")
        if i.get("observacao"):
            print(f"   ! {i['observacao']}")
        print()


def cmd_agenda(args):
    bloco = montar_hoje()
    if not bloco["itens"]:
        print("Nenhuma tarefa em aberto.")
        return
    print("TAREFAS EM ABERTO\n")
    for i in bloco["itens"]:
        d = dt.date.fromisoformat(i["data"])
        print(f"  {_br(d):20} [{i['estado']:9}] {i['cliente'] or '-':16} {i['titulo'][:52]}")
        print(f"  {'':20} id: {i['id']}")


def cmd_concluir(args):
    import yaml
    with open(TAREFAS_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    achou = False
    for t in data.get("tarefas") or []:
        if t.get("id") == args.id:
            t["concluida"] = True
            t["concluida_em"] = dt.date.today().isoformat()
            achou = True
    if not achou:
        print(f"Tarefa '{args.id}' nao encontrada.", file=sys.stderr)
        sys.exit(1)
    with open(TAREFAS_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
    print(f"Tarefa '{args.id}' marcada como concluida.")


def main():
    p = argparse.ArgumentParser(description="Pendencias agendadas")
    sub = p.add_subparsers(dest="cmd", required=True)

    ph = sub.add_parser("hoje", help="O que esta marcado para hoje")
    ph.add_argument("--data", help="AAAA-MM-DD (padrao: hoje)")
    ph.add_argument("--json", action="store_true")
    ph.set_defaults(func=cmd_hoje)

    pa = sub.add_parser("agenda", help="Tudo que esta em aberto")
    pa.set_defaults(func=cmd_agenda)

    pc = sub.add_parser("concluir", help="Marca uma tarefa como concluida")
    pc.add_argument("--id", required=True)
    pc.set_defaults(func=cmd_concluir)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
