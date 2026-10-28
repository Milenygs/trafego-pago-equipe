#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cheirin Bao — remix da edicao com musica do 3992 (04/10/2026): a mesma musica, mais baixa, sobre a EDIT D em 1080p.

Na edicao que a Mileny trouxe (720x1280), a musica fica so ~2 dB abaixo da voz e, no trecho em pe ("E negocio bom…
volta amanha"), acima dela; a transcricao errou "Vem tomar cafe aqui hoje" ali. Sem o arquivo da musica, ela e
separada por subtracao: a voz da edicao e a da EDIT D (mesmo audio, defasado ~46 ms), entao
  musica = edicao - g * voz_D_alinhada        (g por minimos quadrados, conferido por janela)
e volta por baixo da voz original da D a ALVO_DB abaixo dela. Video da D (1080x1920) copiado sem recodificar.
"""
import os
import subprocess
import sys
import tempfile

import numpy as np

PASTA = os.path.expandvars(r"%USERPROFILE%\OneDrive\Área de Trabalho\CLAUDE CODE\franquias\cheirin bao"
                           r"\criativos campanha outubro")
MIX = os.path.join(PASTA, "raissa franqueada edição musica  3992.mp4")
D = os.path.join(PASTA, "Cheirin Bao - Raissa - 3992 EDIT D e por isso (Eduardo).mp4")
SR = 48000
# uso: remix_raissa_3992_musica.py [dB abaixo da voz] [rotulo]   (padrao 16 "baixa"; 04/10 a Mileny achou baixa
# demais: sobra o ruido das pessoas ao redor, entao ha tambem a versao "media")
ALVO_DB = float(sys.argv[1]) if len(sys.argv) > 1 else 16.0   # musica abaixo da voz, medida durante a fala
SAIDA = os.path.join(PASTA, "Cheirin Bao - Raissa - 3992 EDIT D musica %s (remix).mp4"
                     % (sys.argv[2] if len(sys.argv) > 2 else "baixa"))


def audio(f):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64).reshape(-1, 2)


def db(x):
    return 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-12)


def main():
    mix, voz = audio(MIX), audio(D)
    mm, vm = mix.mean(axis=1), voz.mean(axis=1)
    n = 1 << int(np.ceil(np.log2(len(mm) + len(vm))))
    xc = np.fft.irfft(np.fft.rfft(mm, n) * np.conj(np.fft.rfft(vm, n)), n)
    xc = np.r_[xc[-len(vm):], xc[:len(mm)]]
    lag = int(np.argmax(xc)) - len(vm)
    print("defasagem: %d amostras (%+.1f ms)" % (lag, 1000 * lag / SR))

    # voz da D na timeline da edicao
    va = np.zeros_like(mix)
    if lag >= 0:
        k = min(len(mix) - lag, len(voz)); va[lag:lag + k] = voz[:k]
    else:
        k = min(len(mix), len(voz) + lag); va[:k] = voz[-lag:-lag + k]
    vam = va.mean(axis=1)
    g = (mm @ vam) / (vam @ vam)
    jan = [(mm[i:i + SR * 2] @ vam[i:i + SR * 2]) / (vam[i:i + SR * 2] @ vam[i:i + SR * 2] + 1e-12)
           for i in range(0, len(mm) - SR, SR * 2)]
    print("ganho da voz: global %.3f | por janela de 2 s: %s" % (g, " ".join("%.2f" % x for x in jan)))
    mus = mix - g * va
    print("vazamento de voz na musica separada (correlacao): %.3f" % np.corrcoef(mus.mean(axis=1), vam)[0, 1])

    # musica de volta na timeline da D
    mus_d = np.zeros_like(voz)
    if lag >= 0:
        k = min(len(voz), len(mus) - lag); mus_d[:k] = mus[lag:lag + k]
    else:
        k = min(len(voz) + lag, len(mus)); mus_d[-lag:-lag + k] = mus[:k]

    w = SR // 20
    env = np.array([db(vm[i:i + w]) for i in range(0, len(vm) - w, w)])
    fala = np.r_[np.repeat(env > -30, w), np.zeros(len(vm) - len(env) * w, bool)]
    antes = db(voz[fala]) - db(mus_d[fala])
    alfa = 10 ** (-(ALVO_DB - antes) / 20)
    out = voz + alfa * mus_d
    pico = np.abs(out).max()
    if pico > 0.97:
        out *= 0.97 / pico
    print("musica abaixo da voz: antes %.1f dB -> agora %.1f dB (alfa %.3f, pico %.2f)"
          % (antes, db(voz[fala]) - db(alfa * mus_d[fala]), alfa, pico))
    print("nas pausas: ruido do ambiente (D) %.1f dB | musica %.1f dB (%+.1f dB sobre o ruido)"
          % (db(voz[~fala]), db(alfa * mus_d[~fala]), db(alfa * mus_d[~fala]) - db(voz[~fala])))

    wav = os.path.join(tempfile.gettempdir(), "remix3992.wav")
    pcm = (np.clip(out, -1, 1) * 32767).astype(np.int16)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", "-", wav],
                   input=pcm.tobytes(), check=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", D, "-i", wav, "-map", "0:v:0", "-map", "1:a:0",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-ar", str(SR), "-shortest",
                    "-movflags", "+faststart", SAIDA], check=True)
    os.remove(wav)
    print("OK", os.path.basename(SAIDA))


if __name__ == "__main__":
    sys.exit(main())
