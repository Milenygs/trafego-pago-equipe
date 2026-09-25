#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Boali — reedicao do video de Sinop (24/09/2026, pedido da Mileny: "video tem que
ter acao, troca de cena").

Base: "BoalI Sinop (versao curta) (3).mp4" (sem legenda).
  1. gancho 33,55-38,10 "A maior rede ... agora esta aqui" (equipe + fachada)
  2. 4,65-15,30 Luciana "estou muito feliz ... atraves da alimentacao"
     (sai o "Ola, eu sou Luciana Pereira" sobre o braco; o nome vira texto na tela)
  3. 17,70-18,60 caixa "Aqui tem transformacao" (1s, sem fala; sai o resto do vazio)
  4. 19,25-33,50 "Eu trouxe a Boali para Sinop ... nutritivos"
  5. cartao final "Seja um franqueado!" (ultimos 2,2s do video do Marcos Babi)
Legenda nova: Arial Black, 3 palavras por vez, palavra falada em laranja.

Uso:  python reedita_sinop.py
"""
import os
import subprocess
import tempfile
import unicodedata

PASTA = os.path.expandvars(
    r"%USERPROFILE%\OneDrive\Área de Trabalho\CLAUDE CODE\franquias\boali"
    r"\criativos setembro anderson")
TMP = os.path.join(tempfile.gettempdir(), "boali_sinop")
os.makedirs(TMP, exist_ok=True)


def acha(prefixo, contem=""):
    for a in os.listdir(PASTA):
        n = unicodedata.normalize("NFC", a)
        if n.startswith(prefixo) and contem in n and "reedi" not in n:
            return os.path.join(PASTA, a)
    raise SystemExit("nao achei %s" % prefixo)


SINOP = acha("BoalI Sinop (versão curta) (3)")
MARCOS = acha("BOALI - Marcos Babi.mp4")
SAIDA = os.path.join(PASTA, "BoalI Sinop (reedição com ação).mp4")

# (arquivo, inicio, fim)
TRECHOS = [
    (SINOP, 33.55, 38.10),
    (SINOP, 4.65, 15.30),
    (SINOP, 17.70, 18.60),
    (SINOP, 19.25, 33.50),
    (MARCOS, 35.95, 38.15),
]

CORRIGE = {"sinal": "Sinop", "sinal.": "Sinop.", "s9": "Sinop", "sinovi": "Sinop", "sinop": "Sinop", "trossemos": "Trouxemos",
           "boalha": "Boali", "boalha,": "Boali,", "nutreti.": "nutritivos.", "nutreti": "nutritivos."}


def run(cmd):
    subprocess.run(cmd, check=True)


def monta_sem_legenda(bruto):
    ins, filtros, pares = [], [], ""
    for i, (arq, a, b) in enumerate(TRECHOS):
        ins += ["-i", arq]
        d = b - a
        filtros.append(
            "[%d:v]trim=%.2f:%.2f,setpts=PTS-STARTPTS,scale=1080:1920,setsar=1,fps=30[v%d]"
            % (i, a, b, i))
        filtros.append(
            "[%d:a]atrim=%.2f:%.2f,asetpts=PTS-STARTPTS,aresample=48000,"
            "afade=t=in:d=0.04,afade=t=out:st=%.2f:d=0.06[a%d]" % (i, a, b, d - 0.06, i))
        pares += "[v%d][a%d]" % (i, i)
    filtros.append("%sconcat=n=%d:v=1:a=1[v][a]" % (pares, len(TRECHOS)))
    run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(filtros),
         "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "16", "-preset", "medium",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", bruto])


def palavras(bruto):
    from faster_whisper import WhisperModel
    wav = os.path.join(TMP, "bruto.wav")
    run(["ffmpeg", "-v", "error", "-y", "-i", bruto, "-ac", "1", "-ar", "16000", wav])
    m = WhisperModel("small", compute_type="int8")
    segs, _ = m.transcribe(wav, language="pt", word_timestamps=True)
    fim_fala = sum(b - a for _, a, b in TRECHOS[:-1])  # nada de legenda no cartao
    out = []
    for s in segs:
        for w in s.words:
            if w.start >= fim_fala - 0.1:
                continue
            t = w.word.strip()
            t = CORRIGE.get(t.lower(), t)
            out.append([w.start, w.end, t])
    return out


def ts(s):
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    return "%d:%02d:%05.2f" % (h, m, s)


def ass(ws, caminho):
    cab = (
        "[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\n\n"
        "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
        "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, "
        "Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, "
        "Encoding\n"
        "Style: L,Arial Black,84,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,1,0,0,0,100,100,"
        "0,0,1,7,3,2,80,80,640,1\n"
        "Style: N,Arial Black,58,&H00FFFFFF,&H00FFFFFF,&H00216BF2,&H00216BF2,1,0,0,0,100,100,"
        "0,0,3,18,0,1,70,70,900,1\n\n"
        "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
    ev = []
    laranja = r"{\c&H216BF2&}"
    branco = r"{\c&HFFFFFF&}"
    for i in range(0, len(ws), 3):
        grupo = ws[i:i + 3]
        for j, (a, b, _t) in enumerate(grupo):
            fim = grupo[j + 1][0] if j + 1 < len(grupo) else b + 0.15
            if i + 3 < len(ws) and j == len(grupo) - 1:
                fim = min(fim, ws[i + 3][0])
            txt = " ".join((laranja + g[2].upper() + branco) if k == j else g[2].upper()
                           for k, g in enumerate(grupo))
            ev.append("Dialogue: 0,%s,%s,L,,0,0,0,,%s" % (ts(a), ts(fim), txt))
    # nome da franqueada no inicio do trecho 2
    t2 = TRECHOS[0][2] - TRECHOS[0][1]
    ev.append("Dialogue: 1,%s,%s,N,,0,0,0,,{\\fad(200,200)}LUCIANA PEREIRA\\N"
              "{\\fs40}Franqueada Boali Sinop" % (ts(t2 + 0.9), ts(t2 + 4.2)))
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(cab + "\n".join(ev) + "\n")


def main():
    bruto = os.path.join(TMP, "bruto.mp4")
    monta_sem_legenda(bruto)
    ws = palavras(bruto)
    print("legenda:", " ".join(w[2] for w in ws))
    sub = os.path.join(TMP, "leg.ass")
    ass(ws, sub)
    # caminho do .ass no filtro: relativo, rodando dentro do TMP
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", bruto, "-vf", "subtitles=leg.ass",
                    "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt",
                    "yuv420p", "-c:a", "copy", "-movflags", "+faststart", SAIDA],
                   check=True, cwd=TMP)
    print("salvo:", SAIDA)


if __name__ == "__main__":
    main()
