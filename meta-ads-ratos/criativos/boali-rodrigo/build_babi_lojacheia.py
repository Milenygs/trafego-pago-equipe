#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Boali — pedido de 24/09/2026 na campanha dos pinos (CP 08):
  AD20 Marcos Babi (franqueado: loja de rua -> shopping -> corporativa)
       -> CP 08 capital + CP 08 onda 1 (onda 1 esta PAUSED: fica esperando o conjunto)
  AD14 Depoimento loja cheia 691 -> CP 08 capital
       (reusa o criativo 1959958101342539, o mesmo que ja roda na onda 1)

Copy do AD20 sem numero financeiro e SEM a fala de perda de peso (15-20s do video).
Miniatura aos 3s: o quadro 0 e a fachada.

Uso:
    python build_babi_lojacheia.py            # cria tudo PAUSED (retoma pelo JSON)
    python build_babi_lojacheia.py --ativar   # ativa os ads criados e rele
"""
import argparse
import os

import build_rodrigo_setembro as r
from build_rodrigo_setembro import base

r.ESTADO = os.path.join(r.AQUI, "criados_2026-09-24.json")

AD20_PINOS = (
    "De loja de rua a loja corporativa.\n\n"
    "Esse é o Marcos, franqueado Boali. Começou com uma loja de rua, passou para "
    "o shopping e hoje está na loja corporativa, crescendo junto com a rede.\n\n"
    "Você já conhece a Boali do lado do cliente. O Marcos mostra o lado de quem "
    "investe.\n\n"
    "✅ 19 anos de mercado\n"
    "✅ Processo testado e suporte do franqueador\n"
    + r.INVEST +
    "Ainda há praças abertas na sua região. Se esse investimento faz sentido "
    "para o seu momento, fale com um consultor.\n"
    "👇"
)

r.PECAS = [{
    "chave": "AD20",
    "arquivo": "BOALI - Marcos Babi",
    "rotulo": "AD20 [FRANQUEADO] [VIDEO] MARCOS BABI RUA SHOPPING CORPORATIVA",
    "thumb_seg": 3,
    "titulo": "De loja de rua a corporativa",
    "grupos": [("A", AD20_PINOS, [r.CP08_CAPITAL, r.CP08_ONDA1])],
}]
r.DESTINOS = [r.CP08_CAPITAL, r.CP08_ONDA1]

AD14_CRIATIVO = "1959958101342539"
AD14_NOME = "AD14 - DEPOIMENTO LOJA CHEIA 691"


def cria_ad14(estado):
    e = estado.setdefault("AD14", {"ads": {}})
    adset_id, nome, _p = r.CP08_CAPITAL
    if adset_id not in e["ads"]:
        e["ads"][adset_id] = base.post("%s/ads" % base.CONTA, {
            "name": AD14_NOME,
            "adset_id": adset_id,
            "creative": {"creative_id": AD14_CRIATIVO},
            "status": "PAUSED",
        }, "ad AD14 em %s" % nome)
        r.salva(estado)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ativar", action="store_true")
    a = ap.parse_args()
    if a.ativar:
        r.PECAS.append({"chave": "AD14"})
        r.ativa(r.carrega())
        return
    estado = r.carrega()
    r.cria(estado)
    cria_ad14(estado)
    r.le_conta()


if __name__ == "__main__":
    main()
