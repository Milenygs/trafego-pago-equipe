#!/usr/bin/env python3
"""
Meta Ads Ratos - Status da integracao CRM -> CAPI

Responde em poucas linhas: os eventos do CRM estao chegando no dataset?
Mostra quanto chegou de cada evento, ha quantos dias cada um nao aparece,
e alerta quando um estagio para de mandar.

Uso:
  python capi_status.py --pixel 1113125670113540
  python capi_status.py --pixel 1113125670113540 --dias 30
  python capi_status.py --pixel 1113125670113540 --alerta 7   # avisa se parado ha 7+ dias
"""

import argparse
import datetime as dt
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import _load_env_file, print_error  # noqa: E402

_load_env_file()

try:
    from facebook_business.adobjects.adspixel import AdsPixel
    from facebook_business.api import FacebookAdsApi
except ImportError:
    print_error("facebook_business nao instalado. Rode: pip install facebook-business")
    sys.exit(2)

# eventos que a gente manda do CRM (mesma lista do capi.py)
EVENTOS_CRM = [
    "lead_qualificado",
    "reuniao_agendada",
    "proposta_enviada",
    "venda",
    "lead_desqualificado",
]


def main():
    p = argparse.ArgumentParser(description="Status da integracao CRM -> CAPI")
    p.add_argument("--pixel", required=True, help="ID do dataset/pixel")
    p.add_argument("--dias", type=int, default=30, help="janela em dias (padrao 30)")
    p.add_argument("--alerta", type=int, default=5,
                   help="alerta se um evento esta parado ha N dias (padrao 5)")
    args = p.parse_args()

    token = os.environ.get("META_ADS_TOKEN")
    if not token:
        print_error("META_ADS_TOKEN nao encontrado no .env da skill.")
        sys.exit(2)
    FacebookAdsApi.init(access_token=token, api_version=os.environ.get("META_GRAPH_VERSION", "v23.0"))

    inicio = dt.datetime.now() - dt.timedelta(days=args.dias)
    hoje = dt.date.today()

    total = defaultdict(int)
    ultimo_dia = {}
    web = 0

    try:
        stats = AdsPixel(args.pixel).get_stats(params={
            "aggregation": "event",
            "start_time": inicio.strftime("%Y-%m-%dT00:00:00+0000"),
        })
        for s in stats:
            dia = str(s.get("start_time"))[:10]
            for d in (s.get("data") or []):
                evento = d.get("value")
                n = int(d.get("count", 0))
                if evento in EVENTOS_CRM:
                    total[evento] += n
                    if evento not in ultimo_dia or dia > ultimo_dia[evento]:
                        ultimo_dia[evento] = dia
                else:
                    web += n
    except Exception as e:
        print_error(f"nao consegui ler o dataset: {str(e)[:200]}")
        sys.exit(1)

    print(f"\nCAPI / CRM — dataset {args.pixel} — ultimos {args.dias} dias")
    print("=" * 62)

    problemas = []
    for evento in EVENTOS_CRM:
        n = total.get(evento, 0)
        ultimo = ultimo_dia.get(evento)
        if ultimo:
            parado = (hoje - dt.date.fromisoformat(ultimo)).days
            situacao = "hoje" if parado == 0 else f"ha {parado}d"
            marca = ""
            if parado >= args.alerta:
                marca = "   <<< PAROU"
                problemas.append((evento, parado))
            print(f"  {evento:22} {n:>6} eventos   ultimo: {ultimo} ({situacao}){marca}")
        else:
            print(f"  {evento:22} {0:>6} eventos   nunca chegou   <<< VERIFICAR")
            problemas.append((evento, None))

    print(f"\n  (eventos de site/pixel no periodo: {web})")

    print("\n" + "=" * 62)
    if not problemas:
        print("  OK — todos os estagios do CRM estao chegando.")
    else:
        print("  ATENCAO:")
        for evento, parado in problemas:
            if parado is None:
                print(f"    - {evento}: nunca chegou neste periodo")
            else:
                print(f"    - {evento}: sem novos eventos ha {parado} dias")
        print("\n  Antes de mexer, confirme com o comercial se o estagio de fato")
        print("  nao aconteceu. Evento parado nem sempre e integracao quebrada —")
        print("  as vezes e so a operacao que nao teve aquele movimento.")
    print()


if __name__ == "__main__":
    main()
