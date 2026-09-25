#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Boali — pedido de 24/09/2026 (Mileny: "vamos subir o 29 sim e tb a inauguracao"):
  AD21 Rodrigo "melhor momento e agora" (29, 18s) -> CP 04 quente + CP 05 LAL
       Mesmo angulo do AD16 ("por que agora"), sem a prova das 400 operacoes.
       A copy traz a prova que o video nao tem. Sem "maior rede" (sem fonte).
  AD18 Inauguracao Vila Olimpia -> CP 05 LAL (no CP 04 ja roda desde 19/09)
       Reusa video e miniatura do AD18; so a copy e fria.

Uso:
    python build_29_inauguracao.py            # cria tudo PAUSED (retoma pelo JSON)
    python build_29_inauguracao.py --ativar   # ativa os ads criados e rele
"""
import argparse
import json
import os

import build_rodrigo_setembro as r

r.ESTADO = os.path.join(r.AQUI, "criados_2026-09-24b.json")

AD21_QUENTE = (
    "Por que agora?\n\n"
    "Você já conhece a Boali. O Rodrigo, dono da rede, explica por que este é o "
    "momento de entrar: a marca já está consolidada, e a maior parte da expansão "
    "ainda está pela frente. A meta é chegar a 400 operações nos próximos 4 a 5 "
    "anos.\n\n"
    "✅ 19 anos de mercado\n"
    "✅ 25 estados e mais de 100 cidades\n"
    + r.INVEST +
    "Se esse investimento faz sentido para o seu momento, fale com um consultor "
    "e veja se a sua região está disponível.\n"
    "👇"
)

AD21_FRIO = (
    "Existe hora certa para investir numa franquia?\n\n"
    "Para o Rodrigo, dono da Boali, é agora: a rede de alimentação saudável já "
    "está em 25 estados e mais de 100 cidades, e ainda tem a maior parte da "
    "expansão pela frente, com meta de 400 operações nos próximos 4 a 5 anos.\n\n"
    "✅ Franquia de alimentação saudável\n"
    "✅ 19 anos de mercado\n"
    + r.INVEST +
    "Se esse investimento faz sentido para o seu momento, veja se a sua cidade "
    "ainda está disponível.\n"
    "👇"
)

AD18_FRIO = (
    "9 operações. E ele quer mais.\n\n"
    "Esse é o Adriano, franqueado da Boali. Na inauguração do Shopping Vila "
    "Olímpia, em São Paulo, o Rodrigo, dono da rede, conta a história: com o food "
    "truck e mais 2 pontos em estudo, o Adriano vai chegar a 12 operações.\n\n"
    "A maioria dos franqueados Boali tem mais de uma operação. O modelo foi feito "
    "para crescer com a rede.\n\n"
    "✅ Franquia de alimentação saudável\n"
    "✅ 25 estados e mais de 100 cidades\n"
    + r.INVEST +
    "Se esse investimento faz sentido para o seu momento, veja se a sua cidade "
    "ainda está disponível.\n"
    "👇"
)

r.PECAS = [
    {
        "chave": "AD21",
        "arquivo": "29 - RODRIGO RB Melhor momento",
        "rotulo": "AD21 [FUNDADOR] [VIDEO] MELHOR MOMENTO E AGORA CURTO RODRIGO",
        # 1s: rosto do Rodrigo com a tarja "Invista em Boali agora: melhor hora".
        "thumb_seg": 1,
        "titulo": "Por que investir agora",
        "grupos": [("A", AD21_QUENTE, [r.CP04]), ("B", AD21_FRIO, [r.CP05])],
    },
    {
        "chave": "AD18",
        "arquivo": "inaugura",
        "rotulo": "AD18 [PROVA] [VIDEO] INAUGURACAO VILA OLIMPIA ADRIANO 12 OPERACOES",
        "thumb_seg": 16,
        "titulo": "Inauguração Boali Vila Olímpia",
        "grupos": [("B", AD18_FRIO, [r.CP05])],
    },
]
r.DESTINOS = [r.CP04, r.CP05]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ativar", action="store_true")
    a = ap.parse_args()
    if a.ativar:
        r.ativa(r.carrega())
        return
    estado = r.carrega()
    if "AD18" not in estado:
        with open(os.path.join(r.AQUI, "criados_2026-09-19.json"), encoding="utf-8") as f:
            antigo = json.load(f)["AD18"]
        estado["AD18"] = {"ads": {}, "video_id": antigo["video_id"], "thumb": antigo["thumb"]}
        r.salva(estado)
    r.cria(estado)
    r.le_conta()


if __name__ == "__main__":
    main()
