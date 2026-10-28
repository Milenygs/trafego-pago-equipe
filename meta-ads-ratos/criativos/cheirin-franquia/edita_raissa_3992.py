#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cheirin Bao — reedicao do video 3992 da Raissa (03/10/2026): o original abre parado (Raissa sentada,
frase longa) e a cena com movimento so chega aos 13s. As duas versoes reordenam o proprio material.

Cortes nos quadros exatos de troca de cena/legenda (varredura a 30 fps):
  13,267s sentada -> em pe | 19,000s loja -> plano aberto (legenda "E e por isso") | 6,733s inicio da
  legenda "ta em crise ou nao" (antes dela a faixa da legenda esta vazia) | 11,620s fim de "...toma (pausa) cafe." (o 'cafe' vai de 10,86 a 11,50s)

A (recomendada) "Negocio bom e negocio de recorrencia" -> sentada (com o nome RAISSA FRANQUEADA) ->
  "E e por isso que eu escolhi a Cheirin Bao" -> CTA.            ~26,4s
B "Ta em crise ou nao, o brasileiro toma cafe" -> em pe -> CTA.  ~19,7s
Audio: afade de 35 ms em cada ponta (sem estalo). Saida H.264 720x1280 30fps, AAC.
"""
import os
import subprocess

PASTA = os.path.expandvars(r"%USERPROFILE%\OneDrive\Área de Trabalho\CLAUDE CODE\franquias\cheirin bao"
                           r"\criativos campanha outubro")
SRC = os.path.join(PASTA, "Cheirin Bao - Raissa - previa 3992 (2).mp4")
FIM = 28.033
FADE = 0.035

VERSOES = {
    "Cheirin Bao - Raissa - 3992 EDIT A gancho recorrencia.mp4": [(13.267, 19.000), (0.000, 11.620), (19.000, FIM)],
    "Cheirin Bao - Raissa - 3992 EDIT B gancho crise.mp4": [(6.733, 11.620), (13.267, FIM)],
}


def monta(saida, segs):
    partes, rotulos = [], []
    for i, (a, b) in enumerate(segs):
        d = b - a
        partes.append(f"[0:v]trim=start={a}:end={b},setpts=PTS-STARTPTS[v{i}]")
        partes.append(f"[0:a]atrim=start={a}:end={b},asetpts=PTS-STARTPTS,"
                      f"afade=t=in:st=0:d={FADE},afade=t=out:st={d - FADE:.3f}:d={FADE}[a{i}]")
        rotulos.append(f"[v{i}][a{i}]")
    fc = ";".join(partes) + ";" + "".join(rotulos) + f"concat=n={len(segs)}:v=1:a=1[v][a]"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", SRC, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", "30",
                    "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-movflags", "+faststart",
                    os.path.join(PASTA, saida)], check=True)
    print("OK", saida, f"{sum(b - a for a, b in segs):.1f}s")


if __name__ == "__main__":
    for s, segs in VERSOES.items():
        monta(s, segs)

