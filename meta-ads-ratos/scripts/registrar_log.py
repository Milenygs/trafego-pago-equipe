#!/usr/bin/env python3
"""
Registro automatico das mudancas feitas nas contas (log de atividades da Meta).

Pedido da Mileny em 28/10/2026: "todas as nossas acoes nas contas de anuncios
devem ser registradas e compartilhadas entre nos duas" (Mileny e Tainara).

O que a sessao do Claude aplica ja e registrado na hora, pela regra da skill.
Este script e a rede de seguranca para o que e feito direto no PAINEL: le o log
de atividades de cada conta, pega so o que foi feito por pessoa (o ator "Meta"
e cobranca/revisao automatica e fica de fora) e grava no topo do
historico\\AAAA-MM.md do cliente, em OneDrive\\Carteira (pasta compartilhada).

Nao escreve no decisoes.md: ele diz o que vale AGORA e isso e decisao de
quem mexeu. A linha entra com "motivo: a preencher" e o Extrato cobra.

Sem IA e so leitura na Meta. Roda dentro da tarefa das 7h (rodar-diario.ps1).

Uso:
  python registrar_log.py                  # desde a ultima rodada (estado.json)
  python registrar_log.py --desde 2026-10-25
  python registrar_log.py --simular        # mostra o que gravaria, nao grava
"""

import argparse
import datetime as dt
import hashlib
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import init_api

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTAS_PATH = os.path.join(SKILL_DIR, "contas.yaml")
CARTEIRA = os.path.join(os.path.expanduser("~"), "OneDrive", "Carteira")
ESTADO_DIR = os.path.join(CARTEIRA, "_Central", "registro-log")
ESTADO_PATH = os.path.join(ESTADO_DIR, "estado.json")

BRT = dt.timezone(dt.timedelta(hours=-3))  # Brasil sem horario de verao

# slug do contas.yaml -> pasta do cliente em Carteira
PASTAS = {
    "acai-fruit-show": "franquias/acai-fruit-show",
    "bem-querer-donuts": "franquias/bem-querer-donuts",
    "boali": "franquias/boali",
    "cheirin-bao": "franquias/cheirin-bao",
    "cheirin-bao-mkt": "franquias/cheirin-bao",
    "facilmart": "franquias/facilmart",
    "kascao-ca2": "franquias/kascao-ca02",
    "acai-teixeira": "lojas-afs/teixeira-de-freitas",
    "afs-ipatinga-centro": "lojas-afs/ipatinga-centro",
    "afs-osasco": "lojas-afs/osasco",
    "afs-mantena": "lojas-afs/mantena",
    "afs-cidade-nova": "lojas-afs/cidade-nova",
    "acai-loja-fsa": "lojas-afs/mantena",  # conta compartilhada; Tomba sai pelo nome
    "saborazzi": "b2b/saborazzi",
    "trendpel": "b2b/trendpel",
    "acai-fruit-show-industria": "b2b/afs-industria-revendedores",
    "desygn-moveis": "outros/desygn-moveis",
    "casa-de-vidro-paraty": "outros/casa-de-vidro-paraty",
    "ap-ponto": "outros/ap-ponto",
    "bm1-rsp-rayssa-medicina": "outros/bm1-rsp-rayssa-medicina",
}

# Atores que nao sao pessoa
ATORES_IGNORADOS = {"Meta", "Facebook"}
# Mudancas pela API = sessoes do Claude, que ja registram na hora.
# "relatórios-automaçoes" e o usuario do sistema; "ta" aparece nas sessoes da Tai.
ATORES_API = {"relatórios-automaçoes", "relatorios-automacoes", "ta"}

# Eventos que so fazem barulho
EVENTOS_IGNORADOS = {
    "update_ad_run_status_to_be_set_after_review",
    "ad_account_billing_charge",
    "add_images", "edit_images",
    "update_campaign_budget_scheduling_state",
}
# Estados intermediarios de revisao: o que importa e o estado final
INTERMEDIARIOS = {"Processo pendente", "Análise pendente", "Em análise"}

TIPO_OBJETO = [
    ("_campaign", "Campanha"), ("_ad_set", "Conjunto"), ("_ad_", "Anúncio"),
    ("create_ad", "Anúncio"), ("_audience", "Público"), ("_ad_account", "Conta"),
]


def load_clientes():
    import yaml
    with open(CONTAS_PATH, "r", encoding="utf-8") as f:
        return (yaml.safe_load(f) or {}).get("clientes") or {}


def load_estado():
    try:
        with open(ESTADO_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {"ultima_rodada": None, "vistos": {}}


def save_estado(estado):
    os.makedirs(ESTADO_DIR, exist_ok=True)
    # guarda so os ids dos ultimos 45 dias
    corte = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=45)).isoformat()
    estado["vistos"] = {k: v for k, v in estado["vistos"].items() if v >= corte}
    with open(ESTADO_PATH, "w", encoding="utf-8") as f:
        json.dump(estado, f, ensure_ascii=False, indent=1)


def parse_time(s):
    # "2026-10-27T20:01:00+0000"
    return dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S%z")


def reais(v):
    try:
        return f"R$ {int(v) / 100:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (TypeError, ValueError):
        return str(v)


def tipo_objeto(event_type):
    for chave, nome in TIPO_OBJETO:
        if chave in event_type:
            return nome
    return ""


def descrever(ev):
    """Texto curto do que mudou. None = evento sem informacao util."""
    t = ev.get("event_type") or ""
    try:
        x = json.loads(ev.get("extra_data") or "{}")
    except ValueError:
        x = {}
    if not isinstance(x, dict):
        x = {}

    if t.endswith("_run_status"):
        nv, ov = x.get("new_value"), x.get("old_value")
        if nv in INTERMEDIARIOS:
            return None
        verbo = {"Ativo": "ativado", "Ativa": "ativada", "Inativo": "pausado",
                 "Inativa": "pausada", "Excluído": "excluído", "Excluída": "excluída",
                 "Arquivado": "arquivado"}.get(nv, f"{ov} → {nv}")
        return verbo
    if t.endswith("_budget") or t == "create_ad_set":
        o = (x.get("old_value") or {}) if isinstance(x.get("old_value"), dict) else {}
        n = (x.get("new_value") or {}) if isinstance(x.get("new_value"), dict) else {}
        tipo = n.get("additional_value") or ""
        if t == "create_ad_set":
            return f"criado, verba {reais(n.get('new_value'))} {tipo.lower()}".strip()
        return f"verba {reais(o.get('old_value'))} → {reais(n.get('new_value'))} {tipo.lower()}".strip()
    if t.startswith("create_"):
        return "criado"
    if t.startswith("delete_"):
        return "apagado"
    if t.endswith("_name"):
        return f"renomeado: \"{x.get('old_value')}\" → \"{x.get('new_value')}\""
    if t.endswith("_target_spec"):
        return "segmentação alterada (ver no Gerenciador)"
    if t.endswith("_optimization_goal"):
        return f"otimização: {x.get('new_value')}"
    if t.endswith("_bid_strategy"):
        return f"lance: {x.get('new_value')}"
    traduzido = ev.get("translated_event_type")
    return traduzido or t.replace("update_", "").replace("_", " ")


def buscar_log(account_id, desde_utc):
    from facebook_business.adobjects.adaccount import AdAccount
    campos = ["event_type", "event_time", "actor_name", "object_id", "object_name",
              "extra_data", "translated_event_type"]
    params = {"limit": 100, "since": int(desde_utc.timestamp())}
    cursor = AdAccount(account_id).get_activities(fields=campos, params=params)
    eventos = [dict(cursor[i]) for i in range(len(cursor))]
    while cursor.load_next_page():
        eventos.extend(dict(cursor[i]) for i in range(len(cursor)))
    return [e for e in eventos if parse_time(e["event_time"]) >= desde_utc]


def chave(account_id, ev):
    base = "|".join([account_id, ev.get("event_time", ""), ev.get("event_type", ""),
                     str(ev.get("object_id") or ev.get("object_name") or "")])
    return hashlib.sha1(base.encode("utf-8")).hexdigest()[:16]


def bloco_markdown(data_brt, linhas_painel, n_api):
    d = data_brt.strftime("%d/%m")
    out = [f"## {data_brt.isoformat()} — Mudanças no Gerenciador ({d}), registro automático do log da Meta", ""]
    if linhas_painel:
        out += ["| Hora | Quem | Objeto | O que mudou |", "|---|---|---|---|"]
        for hora, quem, tipo, nome, oque in linhas_painel:
            nome = (nome or "").replace("|", "/")
            out.append(f"| {hora} | {quem} | {tipo} {nome} | {oque} |")
        out += ["", "**Motivo: a preencher por quem fez.** Depois de preencher, atualizar o `decisoes.md` se a mudança vale daqui pra frente."]
    if n_api:
        out += ["", f"_Mais {n_api} mudança(s) pela API (usuário do sistema, sessões do Claude): já devem estar registradas numa entrada acima ou abaixo. Se não estiverem, avisar._"]
    out += ["", "---", ""]
    return "\n".join(out)


def inserir_no_historico(pasta, nome_cliente, data_brt, texto, simular):
    arq = os.path.join(CARTEIRA, pasta, "historico", f"{data_brt:%Y-%m}.md")
    if simular:
        print(f"\n>>> {arq}\n{texto}")
        return arq
    os.makedirs(os.path.dirname(arq), exist_ok=True)
    if os.path.exists(arq):
        with open(arq, "r", encoding="utf-8") as f:
            atual = f.read()
    else:
        atual = f"# Histórico {data_brt:%Y-%m} — {nome_cliente}\n\nMais recente primeiro.\n\n"
    i = atual.find("\n## ")
    novo = atual + "\n" + texto if i < 0 else atual[: i + 1] + texto + atual[i + 1:]
    with open(arq, "w", encoding="utf-8") as f:
        f.write(novo)
    return arq


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--desde", help="AAAA-MM-DD (horario de Brasilia). Padrao: ultima rodada, ou 2 dias atras")
    ap.add_argument("--simular", action="store_true", help="mostra o que gravaria, sem gravar")
    args = ap.parse_args()

    init_api()
    estado = load_estado()
    agora = dt.datetime.now(dt.timezone.utc)
    if args.desde:
        desde = dt.datetime.strptime(args.desde, "%Y-%m-%d").replace(tzinfo=BRT).astimezone(dt.timezone.utc)
    elif estado.get("ultima_rodada"):
        desde = dt.datetime.fromisoformat(estado["ultima_rodada"]) - dt.timedelta(hours=2)
    else:
        desde = agora - dt.timedelta(days=2)

    clientes = load_clientes()
    resumo = {"data": agora.astimezone(BRT).date().isoformat(), "desde": desde.astimezone(BRT).isoformat(),
              "gravados": [], "erros": [], "sem_pasta": []}

    for slug, c in clientes.items():
        if c.get("diario") is False or c.get("ex_cliente"):
            continue
        conta = c.get("conta_anuncio")
        if not conta:
            continue
        pasta = PASTAS.get(slug)
        try:
            eventos = buscar_log(conta, desde)
        except Exception as e:  # conta sem acesso nao derruba as outras
            resumo["erros"].append({"slug": slug, "erro": str(e)[:200]})
            continue

        por_dia = {}
        for ev in eventos:
            if ev.get("actor_name") in ATORES_IGNORADOS or ev.get("event_type") in EVENTOS_IGNORADOS:
                continue
            k = chave(conta, ev)
            if k in estado["vistos"]:
                continue
            oque = descrever(ev)
            estado["vistos"][k] = ev["event_time"][:19]
            if oque is None:
                continue
            quando = parse_time(ev["event_time"]).astimezone(BRT)
            dia = por_dia.setdefault(quando.date(), {"painel": [], "api": 0})
            if ev.get("actor_name") in ATORES_API:
                dia["api"] += 1
                continue
            dia["painel"].append((quando.strftime("%H:%M"), ev.get("actor_name") or "?",
                                  tipo_objeto(ev.get("event_type", "")), ev.get("object_name"), oque))

        if not por_dia:
            continue
        if not pasta:
            resumo["sem_pasta"].append(slug)
            continue
        for data_brt in sorted(por_dia):  # do mais antigo ao mais novo: o mais novo fica no topo
            d = por_dia[data_brt]
            if not d["painel"] and not d["api"]:
                continue
            d["painel"].sort()
            pasta_dia = pasta
            if slug == "acai-loja-fsa" and all("TOMBA" in (n or "").upper() for _, _, _, n, _ in d["painel"]):
                pasta_dia = "lojas-afs/tomba"
            arq = inserir_no_historico(pasta_dia, c.get("nome", slug), data_brt,
                                       bloco_markdown(data_brt, d["painel"], d["api"]), args.simular)
            resumo["gravados"].append({"slug": slug, "data": data_brt.isoformat(), "arquivo": arq,
                                       "painel": [{"hora": h, "quem": q, "objeto": f"{t} {n}", "o_que": o}
                                                  for h, q, t, n, o in d["painel"]],
                                       "api": d["api"]})

    if not args.simular:
        estado["ultima_rodada"] = agora.isoformat()
        save_estado(estado)
        with open(os.path.join(ESTADO_DIR, f"{resumo['data']}.json"), "w", encoding="utf-8") as f:
            json.dump(resumo, f, ensure_ascii=False, indent=1)

    n = sum(len(g["painel"]) for g in resumo["gravados"])
    print(f"registro do log: {n} mudança(s) de painel em {len(resumo['gravados'])} bloco(s); "
          f"erros: {len(resumo['erros'])}; sem pasta: {resumo['sem_pasta'] or '-'}")


if __name__ == "__main__":
    main()
