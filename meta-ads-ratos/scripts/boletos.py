#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Meta Ads Ratos - Calendario de boletos / recargas.

Motor de calendario puro (nao chama a API da Meta): le o bloco `boleto:` de cada
cliente no contas.yaml e responde "o que precisa ser enviado/pago hoje".

Regra do calendario (combinada com a cliente do Grupo TFS / Acai Fruit Show):
  - Pagamento SEMPRE em terca ou quinta.
  - Envio do boleto SEMPRE na quinta, 5 ou 7 dias antes do vencimento.
  - Ciclo de 28 dias (4 semanas exatas) em vez de 30: trava o dia da semana pra
    sempre e deixa ~2 dias de saldo sobrando por ciclo, que e a margem pra conta
    nunca parar de rodar.

Uso:
  python boletos.py hoje                 # o que fazer hoje (usado pelo diario)
  python boletos.py hoje --json
  python boletos.py agenda               # proximos 4 ciclos de cada conta
  python boletos.py agenda --ciclos 6 --data 2026-10-01

Config por cliente no contas.yaml:
  boleto:
    valor: 1500.00
    ciclo_dias: 28
    vencimento_ancora: "2026-09-15"   # uma terca ou quinta
    envio_dias_antes: 5               # 5 = quinta anterior a uma terca
    forma: prepago | cartao           # como o dinheiro entra na conta
"""

import argparse
import datetime as dt
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTAS_PATH = os.path.join(SKILL_DIR, "contas.yaml")

DIAS_SEMANA = ["segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"]

CICLO_PADRAO = 28
ENVIO_PADRAO = 5


def _br(d):
    """date -> 'DD/MM (quinta)'."""
    return f"{d.strftime('%d/%m')} ({DIAS_SEMANA[d.weekday()]})"


def _moeda(v):
    """1500.0 -> 'R$ 1.500,00' (formato BR, nao o 1,500.00 do padrao Python)."""
    return "R$ " + f"{float(v):,.2f}".replace(",", "@").replace(".", ",").replace("@", ".")


def carregar_boletos():
    """Retorna [(slug, cfg_cliente, cfg_boleto)] dos clientes com bloco `boleto:`."""
    import yaml
    with open(CONTAS_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    saida = []
    for slug, cfg in (data.get("clientes") or {}).items():
        bol = cfg.get("boleto")
        if not bol or not bol.get("vencimento_ancora"):
            continue
        saida.append((slug, cfg, bol))
    return saida


def vencimentos(bol, hoje, quantos=1):
    """Lista os proximos `quantos` vencimentos >= hoje, a partir da ancora."""
    ancora = bol["vencimento_ancora"]
    if isinstance(ancora, str):
        ancora = dt.date.fromisoformat(ancora)
    ciclo = int(bol.get("ciclo_dias") or CICLO_PADRAO)

    venc = ancora
    while venc < hoje:
        venc += dt.timedelta(days=ciclo)
    return [venc + dt.timedelta(days=ciclo * i) for i in range(quantos)]


def situacao(bol, hoje):
    """Estado do boleto vigente. Retorna dict pronto pro digest."""
    ciclo = int(bol.get("ciclo_dias") or CICLO_PADRAO)
    antes = int(bol.get("envio_dias_antes") or ENVIO_PADRAO)

    ancora = bol["vencimento_ancora"]
    if isinstance(ancora, str):
        ancora = dt.date.fromisoformat(ancora)

    venc = vencimentos(bol, hoje, 1)[0]
    envio = venc - dt.timedelta(days=antes)
    # A ancora e o PRIMEIRO vencimento do calendario: antes dela nao existe
    # ciclo nenhum, so aritmetica. Sem isso o checador cobraria um boleto
    # que nunca foi emitido.
    venc_anterior = venc - dt.timedelta(days=ciclo)
    if venc_anterior < ancora:
        venc_anterior = None

    dias_p_envio = (envio - hoje).days
    dias_p_venc = (venc - hoje).days

    forma = bol.get("forma") or "prepago"
    entrada = ("confirmar que o saldo entrou na conta"
               if forma == "prepago" else
               "confirmar que a fatura do cartao foi coberta")

    valor = _moeda(bol["valor"])

    if hoje == envio:
        estado, gravidade = "ENVIAR_HOJE", "critico"
        msg = f"HOJE e dia de enviar o boleto de {valor} - vence em {_br(venc)}."
        acao = f"Gerar e mandar o boleto pro cliente hoje; no vencimento, {entrada}."
    elif hoje == venc:
        estado, gravidade = "VENCE_HOJE", "critico"
        msg = f"Boleto de {valor} VENCE HOJE."
        acao = f"Cobrar o pagamento e {entrada} ainda hoje."
    elif envio < hoje < venc:
        # Janela entre envio e vencimento. O calendario NAO sabe se o boleto
        # saiu mesmo - entao aqui e "aguardando", nao "atrasado". So vira
        # critico na vespera, que e quando ainda da pra correr atras.
        if dias_p_venc <= 1:
            estado, gravidade = "VENCE_AMANHA", "critico"
        else:
            estado, gravidade = "AGUARDANDO_PAGAMENTO", "atencao"
        msg = (f"Boleto de {valor} (envio previsto {_br(envio)}) vence em "
               f"{_br(venc)} - faltam {dias_p_venc} dia(s).")
        acao = (f"Se ainda nao saiu, enviar hoje. Se ja foi, {entrada} "
                f"ate o vencimento.")
    elif dias_p_envio <= 2:
        estado, gravidade = "ENVIO_EM_BREVE", "atencao"
        msg = f"Boleto de {valor} sai em {_br(envio)} (vence {_br(venc)})."
        acao = "Deixar o boleto gerado pra sair na data."
    else:
        estado, gravidade = "AGENDADO", "info"
        msg = (f"Proximo boleto de {valor}: envio {_br(envio)}, "
               f"vencimento {_br(venc)}.")
        acao = None

    return {
        "estado": estado,
        "gravidade": gravidade,
        "msg": msg,
        "acao": acao,
        "valor": float(bol["valor"]),
        "envio": envio.isoformat(),
        "vencimento": venc.isoformat(),
        "vencimento_anterior": venc_anterior.isoformat() if venc_anterior else None,
        "dias_para_envio": dias_p_envio,
        "dias_para_vencimento": dias_p_venc,
        "forma": bol.get("forma") or "prepago",
    }


def checar_ciclo_anterior(sit, ultima_recarga, hoje=None):
    """Cruza o calendario com a recarga real da API.

    Se o vencimento anterior ja passou e a conta nao recebeu recarga depois dele,
    o boleto daquele ciclo nao foi pago - esse e o alerta que o calendario sozinho
    nunca pegaria. `ultima_recarga` vem do digest ('AAAA-MM-DD') ou None.
    """
    if not ultima_recarga or not sit.get("vencimento_anterior"):
        return None
    venc_ant = dt.date.fromisoformat(sit["vencimento_anterior"])
    hoje = hoje or dt.date.today()
    if venc_ant > hoje - dt.timedelta(days=2):
        return None  # ainda dentro da janela de compensacao
    if dt.date.fromisoformat(ultima_recarga) >= venc_ant:
        return None  # recarga entrou depois do vencimento: pago
    return (f"O boleto que vencia em {_br(venc_ant)} nao aparece como pago - a "
            f"ultima recarga da conta foi em {ultima_recarga}.")


def montar_hoje(data_ref=None):
    hoje = data_ref or dt.date.today()
    itens = []
    for slug, cfg, bol in carregar_boletos():
        sit = situacao(bol, hoje)
        sit.update({"slug": slug, "nome": cfg.get("nome"),
                    "conta": cfg.get("conta_anuncio")})
        itens.append(sit)
    ordem = {"critico": 0, "atencao": 1, "info": 2}
    itens.sort(key=lambda i: (ordem.get(i["gravidade"], 9), i["vencimento"]))
    return {"data": hoje.isoformat(), "itens": itens}


def texto_telegram(bloco):
    """Bloco curto pro resumo das 7h. Retorna '' se nao ha nada a fazer."""
    acionaveis = [i for i in bloco["itens"] if i["gravidade"] in ("critico", "atencao")]
    if not acionaveis:
        return ""
    linhas = ["🧾 BOLETOS"]
    for i in acionaveis:
        marca = "🔴" if i["gravidade"] == "critico" else "🟡"
        linhas.append(f"{marca} {i['nome']}: {i['msg']}")
        if i.get("pendencia_ciclo_anterior"):
            linhas.append(f"   ⚠️ {i['pendencia_ciclo_anterior']}")
    return "\n".join(linhas)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def cmd_hoje(args):
    data_ref = dt.date.fromisoformat(args.data) if args.data else None
    bloco = montar_hoje(data_ref)
    if args.json:
        print(json.dumps(bloco, indent=2, ensure_ascii=False))
        return
    print(f"Boletos - situacao em {dt.date.fromisoformat(bloco['data']).strftime('%d/%m/%Y')}\n")
    for i in bloco["itens"]:
        marca = {"critico": "[!]", "atencao": "[~]"}.get(i["gravidade"], "   ")
        print(f"{marca} {i['nome']}: {i['msg']}")


def cmd_agenda(args):
    hoje = dt.date.fromisoformat(args.data) if args.data else dt.date.today()
    n = args.ciclos
    print(f"Agenda de boletos a partir de {hoje.strftime('%d/%m/%Y')} "
          f"({n} ciclos)\n")
    linhas = []
    for slug, cfg, bol in carregar_boletos():
        antes = int(bol.get("envio_dias_antes") or ENVIO_PADRAO)
        for venc in vencimentos(bol, hoje, n):
            linhas.append((venc - dt.timedelta(days=antes), venc,
                           cfg.get("nome"), float(bol["valor"])))
    linhas.sort()
    print(f"{'ENVIO':<20} {'VENCIMENTO':<20} {'CONTA':<28} VALOR")
    for envio, venc, nome, valor in linhas:
        print(f"{_br(envio):<20} {_br(venc):<20} {nome:<28} {_moeda(valor)}")


def main():
    p = argparse.ArgumentParser(description="Calendario de boletos/recargas")
    sub = p.add_subparsers(dest="cmd", required=True)

    ph = sub.add_parser("hoje", help="O que precisa ser enviado/pago hoje")
    ph.add_argument("--data", help="AAAA-MM-DD (padrao: hoje)")
    ph.add_argument("--json", action="store_true")
    ph.set_defaults(func=cmd_hoje)

    pa = sub.add_parser("agenda", help="Proximos vencimentos de cada conta")
    pa.add_argument("--ciclos", type=int, default=4)
    pa.add_argument("--data", help="AAAA-MM-DD (padrao: hoje)")
    pa.set_defaults(func=cmd_agenda)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
