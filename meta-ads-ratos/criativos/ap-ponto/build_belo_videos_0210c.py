"""Belo 02/10/2026 (tarde) - Belo 5 com legenda padronizada (mesma mulher da Locucao v1), no LAL e no Remarketing.

Substitui o "Conheca" (mesmo video, abertura antiga e legenda fora do padrao), que segue pausado.
Reaproveita o build_belo_videos_0210 (corpos 2 e 3, titulos, descricoes, CTA de simulacao, upload simples).
Miniatura: fachada com "Seu primeiro ape" (0,6s). Sobe PAUSED; a ativacao vem depois (ok da Mileny).
Uso: python build_belo_videos_0210c.py [--dry]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build_belo_videos_0210 as base  # noqa: E402

base.VIDEOS = {
    "VID Locucao Primeiro Ape v1": {"arquivo": "Belo 5 — legenda padronizada (1).mp4",
                                    "thumb": "thumb_belo5_primeiro_ape.jpg", "conjuntos": ["LAL", "RMKT"]},
}
base.ABERTURA = {
    "VID Locucao Primeiro Ape v1": (
        "Seu primeiro apê pode estar mais perto do que você imagina. 🏡\n\n"
        "Conheça o Ponto Belo: apartamentos na planta pelo Minha Casa Minha Vida, em Vespasiano.\n\n"
        "📍 Lançamento com unidades de 2 quartos a partir de R$250 mil\n"
        "💳 Entrada parcelada em até 60x direto com a construtora\n"
        "📄 Documentação gratuita: ITBI e registro por conta da AP Ponto\n"
        "🏊 Lazer completo no condomínio\n\n"
        + base.RENDA + "\n\nNão deixe a sua oportunidade passar."),
}

if __name__ == "__main__":
    base.main()
