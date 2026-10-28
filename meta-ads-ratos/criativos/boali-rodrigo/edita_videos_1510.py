#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Boali — 2 edicoes de video do Rodrigo (15/10/2026). Nao sobe nada na Meta.

1. AD23 curto: "vender franquia e facil, o dificil e entregar" (44,9s -> ~24s).
   Legenda gravada no video: os cortes caem no quadro em que a legenda troca
   (achado varrendo a faixa da legenda a 30 fps):
     0,00-1,55   "O cara, vender franquia e muito facil."   (1,567 entra "Moleza.")
     11,00-20,40 "E tem muita gente conseguindo vender franquia, o dificil e entregar,
                  o dificil e construir uma companhia que ta ha mais de 19 anos fazendo a
                  mesma coisa."                              (20,40 entra "So como Boali,")
     32,034-fim  "Tem cara no meu mercado vendendo franquia para outros estados... e impossivel."
   Sai: capex/campanha/funil, "so como Boali 11 anos", "crescendo ano contra ano", "quem e bom
   no digital... infraestrutura para te atender". Mesma resolucao (720x1280).

2. IMG_4307 (WhatsApp, 464x832, 60 fps, 2min09): "8 novas Boalis na semana, 188 contratos, meta 200 em outubro".
   Sai: a live de terca 13/10 (ja passou) e a "condicao especial"; "Rio praca fechada / prestes a fechar
   outras pracas" (a Mileny nao gostou desse gatilho na regua, 30/09); Africa do Sul, aeroportos em
   detalhe, a repeticao de Cascavel/Foz e as pausas em que ele escreve no quadro.
   Imagem: 30 fps, denoise leve (artefato do WhatsApp), escala 1080x1920 lanczos, nitidez leve.
   Audio: loudnorm -14 LUFS. Nao recupera detalhe que o WhatsApp jogou fora: o ideal e o arquivo original.

    python edita_videos_1510.py ad23
    python edita_videos_1510.py vendas
"""
import os
import subprocess
import sys

B = os.path.join(os.path.expanduser("~"), "OneDrive", "Área de Trabalho", "CLAUDE CODE", "franquias", "boali")
AD23_IN = os.path.join(B, "criativos para video viwes", "video rodrigo- vender franquia.mp4")
AD23_OUT = os.path.join(B, "criativos para video viwes", "video rodrigo- vender franquia (curto 24s).mp4")
VENDAS_IN = os.path.join(B, "IMG_4307.MP4")
VENDAS_OUT = os.path.join(B, "RODRIGO - 8 novas Boalis 188 contratos (editado).mp4")

AD23_CORTES = [(0.0, 1.55), (11.0, 20.40), (32.034, 44.90)]

# AD22 "Ele recusou 28 milhoes" (criador de terceiros, 25 fps, legenda palavra a palavra) -> ~24s.
# Cortes no quadro sem legenda ou na troca (varridos de 0,08 em 0,08 s). Sai tudo que tem numero de
# faturamento ou superlativo sem fonte: "maior franquia... hemisferio sul", "faturamento combinado de
# R$400 milhoes" (tambem na tela), "perdeu mais de 30% do faturamento", Salad Creations, aquisicoes e a pergunta final.
AD22_IN = os.path.join(B, "criativos para video viwes", "ele recusou 28 milhoes.mp4")
AD22_OUT = os.path.join(B, "criativos para video viwes", "ele recusou 28 milhoes (curto 24s).mp4")
AD22_CORTES = [
    (0.00, 4.82),      # "Ele recusou R$28 milhoes para nao perder o controle da propria empresa de salada."
    (38.94, 44.44),    # "O fundo exigia abrir 80 lojas em 18 meses, o ritmo que ele considerava insustentavel para manter a qualidade."
    (59.00, 61.46),    # "A Boali manteve a estrutura enxuta de proposito."
    (69.90, 75.27),    # "A gestao gira em torno desse nucleo pequeno, mais um time de suporte direto para os franqueados."
    (99.98, 105.58),   # "O proprio Rodrigo resume... capital paciente vale mais que capital grande."
]

# (inicio, fim) no original. Pontos conferidos no volume do audio (RMS a cada 50 ms): o whisper
# esticou palavras nas pausas em que ele escreve no quadro, e a 1a versao comeu "Cascavel" e "entao".
VENDAS_CORTES = [
    (3.00, 19.90),     # "cara, que semana... Guarulhos, Santos Dumont, Brasilia, Niteroi, Jundiai e BH. E hoje acabei de assinar Cascavel"
                       # (ele repete "Cascavel" de 20,55 a 21,3 enquanto escreve: fica fora)
    (23.36, 24.95),    # "Foz do"
    (26.38, 27.07),    # "Iguacu"
    (35.60, 40.42),    # "Entao, uma, duas... oito novas Boalis"
    (66.99, 68.70),    # "o mes de outubro comecou com tudo" (66,80 trazia o "-ces" de "voces", que soa "seis")
    (89.30, 100.10),   # "A gente bateu o numero de 188 contratos. Olha so, 188 contratos."
    (106.36, 111.70),  # "eu quero em outubro bater a marca de 200 contratos."
    (112.45, 116.45),  # "Quem e que vem bater essa marca com a gente?"
    (121.60, 128.51),  # "E o numero que a gente tem pra fechar o nosso mes de outubro, entao vem com a gente. Bora boalizar o Brasil e o mundo."
]
FADE = 0.035


def duracao(v):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", v],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


def palavras(v, ss=0.0):
    from faster_whisper import WhisperModel
    m = WhisperModel("small", compute_type="int8")
    segs, _ = m.transcribe(v, language="pt", word_timestamps=True, clip_timestamps=[ss] if ss else "0")
    return [(w.start, w.end, w.word.strip()) for s in segs for w in s.words]


def filtro(cortes, pos_video, pos_audio):
    partes, rotulos = [], []
    for i, (a, b) in enumerate(cortes):
        d = b - a
        partes.append("[0:v]trim=%.3f:%.3f,setpts=PTS-STARTPTS[v%d]" % (a, b, i))
        partes.append("[0:a]atrim=%.3f:%.3f,asetpts=PTS-STARTPTS,afade=t=in:d=%.3f,afade=t=out:st=%.3f:d=%.3f[a%d]"
                      % (a, b, FADE, d - FADE, FADE, i))
        rotulos.append("[v%d][a%d]" % (i, i))
    partes.append("%sconcat=n=%d:v=1:a=1[vc][ac]" % ("".join(rotulos), len(cortes)))
    partes.append("[vc]%s[vo]" % pos_video)
    partes.append("[ac]%s[ao]" % pos_audio)
    return ";".join(partes)


def render(entrada, saida, cortes, pos_video, pos_audio):
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", entrada, "-filter_complex", filtro(cortes, pos_video, pos_audio),
           "-map", "[vo]", "-map", "[ao]", "-c:v", "libx264", "-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", saida]
    subprocess.run(cmd, check=True)
    print("OK  %s  (%.1fs)" % (saida, duracao(saida)))


def confere(saida, cortes):
    """Transcreve o arquivo final trecho a trecho: no arquivo inteiro o whisper embaralha as emendas."""
    import tempfile
    from faster_whisper import WhisperModel
    m = WhisperModel("small", compute_type="int8")
    wav = os.path.join(tempfile.gettempdir(), "boali_confere.wav")
    print("\nTRANSCRICAO DO ARQUIVO FINAL, POR TRECHO:")
    t = 0.0
    for a, b in cortes:
        d = b - a
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "%.3f" % t, "-t", "%.3f" % d, "-i", saida,
                        "-ac", "1", "-ar", "16000", wav], check=True)
        segs, _ = m.transcribe(wav, language="pt", vad_filter=False)
        print("  %5.1fs  %s" % (t, " ".join(s.text.strip() for s in segs)))
        t += d


def ad23():
    render(AD23_IN, AD23_OUT, AD23_CORTES, "fps=30,format=yuv420p", "aresample=48000")
    confere(AD23_OUT, AD23_CORTES)


def vendas():
    render(VENDAS_IN, VENDAS_OUT, VENDAS_CORTES,
           "fps=30,hqdn3d=1.2:1.2:5:5,scale=1080:1920:flags=lanczos,unsharp=5:5:0.55:5:5:0.0,"
           "eq=contrast=1.03:saturation=1.04,format=yuv420p",
           "highpass=f=70,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000")
    confere(VENDAS_OUT, VENDAS_CORTES)


# v2 (pedido da Mileny): abre em "a gente bateu 188 contratos". Mesmos trechos, outra ordem.
VENDAS2_OUT = os.path.join(B, "RODRIGO - 188 contratos (editado v2).mp4")
VENDAS2_CORTES = [
    (89.30, 100.10),   # "A gente bateu o numero de 188 contratos. Olha so, 188 contratos."
    (106.36, 111.70),  # "eu quero em outubro bater a marca de 200 contratos."
    (3.00, 19.90),     # "cara, que semana... acabei de assinar Cascavel"
    (23.36, 24.95),    # "e Foz do"
    (26.38, 27.07),    # "Iguacu"
    (35.60, 40.42),    # "Entao, uma, duas... oito novas Boalis"
    (66.99, 68.70),    # "o mes de outubro comecou com tudo"
    (112.45, 116.45),  # "Quem e que vem bater essa marca com a gente?"
    (121.60, 128.51),  # "E o numero que a gente tem pra fechar o nosso mes de outubro, entao vem com a gente. Bora boalizar..."
]


def vendas2():
    render(VENDAS_IN, VENDAS2_OUT, VENDAS2_CORTES,
           "fps=30,hqdn3d=1.5:1.5:6:6,scale=1080:1920:flags=lanczos,unsharp=5:5:0.6:5:5:0.0,"
           "eq=contrast=1.04:saturation=1.05,format=yuv420p",
           # ruido de fundo e eco da sala: denoise FFT + corte de grave/agudo + compressao leve, depois -14 LUFS
           "highpass=f=90,lowpass=f=11000,afftdn=nr=14:nf=-42:tn=1,"
           "acompressor=threshold=-22dB:ratio=3:attack=8:release=160:makeup=2,"
           "loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000")
    confere(VENDAS2_OUT, VENDAS2_CORTES)


def ad22():
    render(AD22_IN, AD22_OUT, AD22_CORTES, "format=yuv420p", "aresample=48000")
    confere(AD22_OUT, AD22_CORTES)


if __name__ == "__main__":
    {"ad23": ad23, "ad22": ad22, "vendas": vendas, "vendas2": vendas2}[sys.argv[1]]()
