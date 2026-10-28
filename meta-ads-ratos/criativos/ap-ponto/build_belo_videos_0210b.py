"""Belo 02/10/2026 (tarde) - Leo "aluguel" (PONTO BELO 2), versao reeditada pela Mileny, no Interesse 25-45. PAUSED.

Reaproveita o build_belo_videos_0210 (corpos 2 e 3, titulos, descricoes, CTA de simulacao, upload simples).
O video nao fala preco, 60x nem ITBI: o corpo 1 leva a oferta inteira. Aluguel so na frase aprovada
("O mesmo valor que voce paga de aluguel ja pode ser a parcela do que e seu"), sem culpar o leitor.
Miniatura: rosto do Leo + "AINDA PAGANDO ALUGUEL?" (0,3s).
Uso: python build_belo_videos_0210b.py [--dry]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build_belo_videos_0210 as base  # noqa: E402

base.VIDEOS = {
    "VID UGC Leo Aluguel v1": {"arquivo": "PONTO BELO 2 — Leo, aluguel, cópia compatível (1).mp4",
                               "thumb": "thumb_leo_aluguel.jpg", "conjuntos": ["INTERESSE"]},
}
base.ABERTURA = {
    "VID UGC Leo Aluguel v1": (
        "\"Um dia eu vou ter o meu apartamento.\"\n"
        "E se esse dia chegou? 🏡\n\n"
        "O Ponto Belo acabou de chegar em Vespasiano: apartamentos de 2 quartos a partir de R$250 mil, "
        "pelo Minha Casa Minha Vida.\n\n"
        "O mesmo valor que você paga de aluguel já pode ser a parcela do que é seu.\n\n"
        "✅ Entrada parcelada em até 60x direto com a construtora\n"
        "✅ ITBI e registro por conta da AP Ponto\n"
        "✅ Piscina, área gourmet, churrasqueira, salão de festas, quadra e minimercado\n\n"
        + base.RENDA + "\n\nÉ a oportunidade que você esperava batendo na sua porta."),
}

if __name__ == "__main__":
    base.main()
