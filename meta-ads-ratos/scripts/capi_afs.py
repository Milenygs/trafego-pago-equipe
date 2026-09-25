# -*- coding: utf-8 -*-
"""CAPI semanal da Açaí Fruit Show Franquias.

Uso:
    python scripts/capi_afs.py --csv "C:\\caminho\\pipeline.csv"
    python scripts/capi_afs.py --csv "..." --test-code TEST12345   (validar antes)
    python scripts/capi_afs.py --csv "..." --dry-run               (só mostrar)

O que faz:
  1. lê o export do CRM
  2. puxa os leads da Meta (com o leadgen_id e a resposta de capital)
  3. casa CRM x Meta por e-mail e telefone
  4. classifica cada lead em lead_qualificado / lead_desqualificado
  5. descarta o que está fora da janela de 7 dias da Meta
  6. envia pelo capi.py
"""
import argparse
import csv
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIXEL = "1930108940975664"

# formularios da conta (antigos + atuais)
FORMULARIOS = [
    "1372877821349964",  # MT 25/05
    "1980887529298059",  # M 04/08
    "1800556261308285",  # AFS FRANQUIA EXPANSAO QUALIFICADO
    "1385814793614198",  # AFS FRANQUIA EXPANSAO CONTROLE
]

# respostas de capital que ficam ABAIXO do ticket de R$270 mil
ABAIXO_DO_TICKET = ("acima_100", "entre_100mil_e_200", "menos_200", "acima de r$100mil")

# Etapas reais do funil Closer (mapeadas do CRM em 13/08/2026).
# Mapa EXPLICITO — nada de match por trecho, que confundiria
# "3a Reuniao - Falar com o Diretor" com uma primeira reuniao.
ETAPA_EVENTO = {
    # ainda em processo — nao geram sinal
    "leads novos": None,
    "retorno 1º dia": None,
    "retorno 2º dia": None,
    "retorno 3º dia": None,
    "não atendeu": None,
    "atendeu": None,
    "standby": None,
    # marcos de avanço
    "1a reunião": "reuniao_agendada",
    "falar com o franqueado": "reuniao_agendada",
    "2a reunião - cof": "proposta_enviada",   # COF = oferta formal da franquia
    "ficha cadastral": "proposta_enviada",
    "3a reunião - falar com o diretor": "proposta_enviada",
    "disparo de mensagens": "proposta_enviada",
    "ganho": "venda",
    # negativo
    "perda": "lead_desqualificado",
}


def evento_da_etapa(etapa):
    """Casa a etapa do CRM com o evento, tolerando acento e espaço."""
    e = (etapa or "").strip().lower()
    if e in ETAPA_EVENTO:
        return ETAPA_EVENTO[e], True
    # normaliza acentos para tentar de novo
    troca = str.maketrans("áàâãéêíóôõúç", "aaaaeeiooouc")
    e2 = e.translate(troca)
    for k, v in ETAPA_EVENTO.items():
        if k.translate(troca) == e2:
            return v, True
    return None, False          # etapa desconhecida — precisa avisar


def carregar_env():
    caminho = os.path.join(RAIZ, ".env")
    for linha in open(caminho, encoding="utf-8"):
        m = re.match(r'^\s*([A-Z_]+)\s*=\s*"?([^"\n]*)"?\s*$', linha)
        if m:
            os.environ.setdefault(m.group(1), m.group(2))


def norm_email(v):
    return (v or "").strip().lower()


def norm_fone(v):
    d = re.sub(r"\D", "", v or "")
    if not d:
        return ""
    if not d.startswith("55"):
        d = "55" + d
    return d


def data_br(v):
    """Converte '08/08/2026 13:24' em datetime."""
    v = (v or "").strip()
    for fmt in ("%d/%m/%Y %H:%M", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y"):
        try:
            return datetime.strptime(v, fmt)
        except ValueError:
            continue
    return None


def puxar_leads_meta(api):
    """Devolve índices por e-mail e por telefone -> dados do lead na Meta."""
    por_email, por_fone = {}, {}
    for fid in FORMULARIOS:
        try:
            r = api.call("GET", (fid, "leads"),
                         params={"fields": "id,created_time,field_data", "limit": 200}).json()
        except Exception as e:
            print(f"  aviso: formulário {fid} não lido ({str(e)[:70]})")
            continue
        for l in r.get("data", []):
            c = {x["name"]: (x.get("values") or [""])[0] for x in l.get("field_data", [])}
            capital = ""
            for chave in ("capital_disponivel", "quanto_você_tem_para_investir?_"):
                if c.get(chave):
                    capital = c[chave]
                    break
            reg = {"lead_id": l["id"], "capital": capital,
                   "email": norm_email(c.get("email")),
                   "phone": norm_fone(c.get("phone_number")),
                   "nome": c.get("full_name", "")}
            if reg["email"]:
                por_email[reg["email"]] = reg
            if reg["phone"]:
                por_fone[reg["phone"]] = reg
        time.sleep(1)
    return por_email, por_fone


def classificar(linha, capital):
    """Devolve o nome do evento, ou None se ainda não dá pra classificar.

    Combinado com a Mileny/Gleice em 11/08:
      - tag `qualificado` = julgamento humano (R$200 mil+, falou, confirmou interesse).
        A tag é permanente, então não se perde quando o card anda no funil.
      - etapas de reunião em diante = marcos objetivos, sinal mais forte.
      - o julgamento humano tem precedência sobre o capital declarado
        (pode haver financiamento, sócio, etc).
    """
    status = (linha.get("Status") or "").lower()
    tags = (linha.get("Tags") or "").lower()
    cap = (capital or "").lower()

    # 1) marco objetivo pela etapa do funil (mapa explícito)
    evento, conhecida = evento_da_etapa(linha.get("Etapa"))
    if not conhecida:
        return "__ETAPA_DESCONHECIDA__"
    if evento and evento != "lead_desqualificado":
        return evento

    # 2) julgamento humano — a tag vence o capital declarado
    if "qualificado" in tags:
        return "lead_qualificado"

    # 3) negativos
    if evento == "lead_desqualificado" or status == "lost":
        return "lead_desqualificado"
    if any(t in cap for t in ABAIXO_DO_TICKET):
        return "lead_desqualificado"          # declarou menos que o ticket

    return None


def main():
    ap = argparse.ArgumentParser(description="CAPI semanal da AFS Franquias")
    ap.add_argument("--csv", required=True, help="export do CRM (pipeline)")
    ap.add_argument("--test-code", help="test_event_code do Events Manager")
    ap.add_argument("--dry-run", action="store_true", help="não envia, só mostra")
    ap.add_argument("--dias", type=int, default=6,
                    help="janela em dias (a Meta aceita 7; padrão 6 por segurança)")
    args = ap.parse_args()

    carregar_env()
    from facebook_business.api import FacebookAdsApi
    api = FacebookAdsApi.init(access_token=os.environ["META_ADS_TOKEN"],
                              api_version="v21.0")

    print("puxando leads da Meta...")
    por_email, por_fone = puxar_leads_meta(api)
    print(f"  {len(set(r['lead_id'] for r in list(por_email.values()) + list(por_fone.values())))} leads com leadgen_id\n")

    # eventos já enviados antes (evita mandar o mesmo sinal duas vezes)
    log_path = os.path.join(RAIZ, "relatorios", "capi_afs_enviados.json")
    try:
        enviados = set(tuple(x) for x in json.load(open(log_path, encoding="utf-8")))
    except Exception:
        enviados = set()

    corte = datetime.now() - timedelta(days=args.dias)
    eventos = []
    etapas_novas = set()
    sem_match = fora_janela = sem_classe = ja_enviado = outro_funil = 0

    with open(args.csv, encoding="utf-8-sig") as f:
        for linha in csv.DictReader(f):
            # só o funil Closer — o export traz Trendpel e indústria junto
            if (linha.get("Pipeline") or "").strip().lower() != "closer":
                outro_funil += 1
                continue

            email = norm_email(linha.get("Email"))
            fone = norm_fone(linha.get("Telefone"))
            meta = por_email.get(email) or por_fone.get(fone)
            if not meta:
                sem_match += 1
                continue

            evento = classificar(linha, meta["capital"])
            if evento == "__ETAPA_DESCONHECIDA__":
                etapas_novas.add((linha.get("Etapa") or "?").strip())
                sem_classe += 1
                continue
            if not evento:
                sem_classe += 1
                continue

            if (meta["lead_id"], evento) in enviados:
                ja_enviado += 1
                continue

            # o timestamp certo é o da MUDANÇA de estágio, não o da criação do lead
            quando = data_br(linha.get("Última Interação")) or data_br(linha.get("Data Cadastro Lead"))
            if not quando or quando < corte:
                fora_janela += 1
                continue

            eventos.append({
                "event_name": evento,
                "event_time": int(quando.timestamp()),
                "lead_id": meta["lead_id"],
                "email": meta["email"],
                "phone": meta["phone"],
                "_nome": meta["nome"],
            })

    print(f"eventos prontos ....... {len(eventos)}")
    print(f"fora do funil Closer .. {outro_funil}")
    print(f"sem match na Meta ..... {sem_match}  (lead de outra origem ou sem e-mail/telefone)")
    print(f"fora da janela ........ {fora_janela}  (mudança de estágio há mais de {args.dias} dias)")
    print(f"sem classificação ..... {sem_classe}  (ainda em aberto no funil)")
    print(f"já enviados antes ..... {ja_enviado}\n")

    if etapas_novas:
        print("!! ETAPA DESCONHECIDA NO FUNIL — atualizar ETAPA_EVENTO no script:")
        for e in sorted(etapas_novas):
            print(f"     \"{e}\"")
        print()

    if not eventos:
        print("nada a enviar.")
        return

    for e in eventos:
        print(f"  {e['event_name']:22} {e['_nome'][:26]:26} lead_id={e['lead_id']}")

    if args.dry_run:
        print("\n--dry-run: nada foi enviado.")
        return

    saida = os.path.join(RAIZ, "relatorios",
                         f"capi_afs_{datetime.now():%Y-%m-%d}.csv")
    os.makedirs(os.path.dirname(saida), exist_ok=True)
    with open(saida, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["event_name", "event_time", "lead_id",
                                          "email", "phone"])
        w.writeheader()
        for e in eventos:
            w.writerow({k: e[k] for k in w.fieldnames})

    cmd = [sys.executable, os.path.join(RAIZ, "scripts", "capi.py"), "batch",
           "--pixel", PIXEL, "--csv", saida, "--crm", "rd_station"]
    if args.test_code:
        cmd += ["--test-code", args.test_code]

    print(f"\nenviando ({os.path.basename(saida)})...")
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(r.stdout or r.stderr)

    # registra o que foi enviado, pra não repetir na próxima rodada
    if "events_received" in (r.stdout or "") and not args.test_code:
        for e in eventos:
            enviados.add((e["lead_id"], e["event_name"]))
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(sorted(enviados), f, ensure_ascii=False, indent=1)
        print(f"registrados {len(eventos)} envios em capi_afs_enviados.json")


if __name__ == "__main__":
    main()
