#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Boali — 24/09/2026 (Mileny: "vamos subir o depoimento Marcos Babi tb"):
  AD20 Marcos Babi -> CP 04 quente + CP 05 LAL
  (nos pinos ja foi criado mais cedo, build_babi_lojacheia.py)
Reusa video e miniatura do AD20. Copy sem numero financeiro e sem a fala de
perda de peso (15-20s do video).

Uso:
    python build_babi_quente_lal.py            # cria PAUSED (retoma pelo JSON)
    python build_babi_quente_lal.py --ativar   # ativa e rele
"""
import argparse
import json
import os

import build_rodrigo_setembro as r

r.ESTADO = os.path.join(r.AQUI, "criados_2026-09-24c.json")

AD20_QUENTE = (
    "De loja de rua a loja corporativa.\n\n"
    "Esse é o Marcos, franqueado Boali. Começou com uma loja de rua, passou para "
    "o shopping e hoje está na loja corporativa, crescendo junto com a rede.\n\n"
    "Você já conhece a Boali. Talvez não conheça quem está do outro lado do "
    "balcão.\n\n"
    "✅ 19 anos de mercado\n"
    "✅ Processo testado e suporte do franqueador\n"
    + r.INVEST +
    "Se esse investimento faz sentido para o seu momento, fale com um consultor "
    "e veja se a sua região está disponível.\n"
    "👇"
)

AD20_FRIO = (
    "Está na dúvida sobre qual negócio abrir?\n\n"
    "O Marcos, franqueado Boali, também já esteve. Começou com uma loja de rua, "
    "passou para o shopping e hoje está na loja corporativa. O conselho dele: "
    "entre numa rede com processo testado e um franqueador que ajuda a crescer.\n\n"
    "✅ Franquia de alimentação saudável\n"
    "✅ 19 anos de mercado, 25 estados\n"
    + r.INVEST +
    "Se esse investimento faz sentido para o seu momento, veja se a sua cidade "
    "ainda está disponível.\n"
    "👇"
)

r.PECAS = [{
    "chave": "AD20",
    "arquivo": "BOALI - Marcos Babi",
    "rotulo": "AD20 [FRANQUEADO] [VIDEO] MARCOS BABI RUA SHOPPING CORPORATIVA",
    "thumb_seg": 3,
    "titulo": "De loja de rua a corporativa",
    "grupos": [("Q", AD20_QUENTE, [r.CP04]), ("F", AD20_FRIO, [r.CP05])],
}]
r.DESTINOS = [r.CP04, r.CP05]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ativar", action="store_true")
    a = ap.parse_args()
    if a.ativar:
        r.ativa(r.carrega())
        return
    estado = r.carrega()
    if "AD20" not in estado:
        with open(os.path.join(r.AQUI, "criados_2026-09-24.json"), encoding="utf-8") as f:
            antigo = json.load(f)["AD20"]
        estado["AD20"] = {"ads": {}, "video_id": antigo["video_id"], "thumb": antigo["thumb"]}
        r.salva(estado)
    r.cria(estado)
    r.le_conta()


if __name__ == "__main__":
    main()
