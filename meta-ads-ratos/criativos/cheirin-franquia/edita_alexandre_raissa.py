#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cheirin Bao — "franqueados alexandre e raissa.mp4" (AD33) com o gancho invertido (05/10/2026).

Mileny: abrir com "Escolhemos a Cheirin Bao…" (do 8s), encaixar a pergunta do 1s em outro momento e excluir o inicio.
Original (24 fps, legendas gravadas no video):
  0-1,67   fundador em tela dividida: "Olha esse depoimento. Escuta." + transicao de luz  -> SAI
  1,67-7,62  pergunta "Qual o faturamento que levou voces a premiacao?" + "Foi 1 milhao 574 mil" (tela preta)
  7,62-7,75  transicao de luz laranja (rosto apagado)  -> SAI
  7,75-20,46 "Escolhemos a Cheirin Bao por ser uma empresa… (Raissa) nos identificamos… e isso foi fundamental para
             a gente poder escolher. E assim, ja deu certo."
  20,46-fim  Raissa "Ja estamos aqui indo para a 2a e a 3a" + CTA do fundador
Nova ordem: porque escolheram -> pergunta do faturamento/premio -> expansao -> CTA. Cortes no quadro exato de troca de
cena e nos vales da fala (7,62: -34 dB; 20,46: -31 dB). Fade de 35 ms, exceto 10 ms na entrada da Raissa ("Ja" comeca
~20 ms depois do corte). Saida 1080x1920, 24 fps.
"""
import os
import subprocess

PASTA = os.path.expandvars(r"%USERPROFILE%\OneDrive\Área de Trabalho\CLAUDE CODE\franquias\cheirin bao"
                           r"\criativos campanha outubro")
SRC = os.path.join(PASTA, "franqueados alexandre e raissa.mp4")
SAIDA = os.path.join(PASTA, "Cheirin Bao - Alexandre e Raissa - gancho escolhemos.mp4")
FIM = 28.583
# (inicio, fim, fade de entrada)
SEGS = [(7.750, 20.458, 0.035), (1.667, 7.625, 0.035), (20.458, FIM, 0.010)]
FADE = 0.035


def main():
    partes, rot = [], []
    for i, (a, b, f_in) in enumerate(SEGS):
        d = b - a
        partes.append("[0:v]trim=start=%.3f:end=%.3f,setpts=PTS-STARTPTS[v%d]" % (a, b, i))
        partes.append("[0:a]atrim=start=%.3f:end=%.3f,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=%.3f,"
                      "afade=t=out:st=%.3f:d=%.3f[a%d]" % (a, b, f_in, d - FADE, FADE, i))
        rot.append("[v%d][a%d]" % (i, i))
    fc = ";".join(partes) + ";" + "".join(rot) + "concat=n=%d:v=1:a=1[v][a]" % len(SEGS)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", SRC, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", "24",
                    "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-movflags", "+faststart", SAIDA], check=True)
    print("OK %s (%.2fs)" % (os.path.basename(SAIDA), sum(b - a for a, b, _ in SEGS)))


if __name__ == "__main__":
    main()
