#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cheirin Bao — video 3992 da Raissa, versoes C e D a partir do ORIGINAL SEM LEGENDA (03/10/2026).

Pedido: o Eduardo sugeriu abrir com "E e por isso que eu escolhi a Cheirin Bao". Duas versoes, iguais em
tudo menos a 1a frase, para o teste medir so o gancho:
  C (sugestao Claude)  "Eu escolhi a Cheirin Bao, a maior rede de cafeterias do Brasil."  (corta "E e por isso que")
  D (pedido Eduardo)   "E e por isso que eu escolhi a Cheirin Bao, a maior rede…"
  depois, nas duas: "Ta em crise ou nao, o brasileiro toma cafe." (sentada) -> "E negocio bom e negocio de
  recorrencia. Vem tomar cafe aqui hoje, volta amanha." (em pe) -> "Quer entender mais…? Clique aqui no link."

Cortes (timeline do original, 30 fps):
  19,667 troca de quadro no vale entre "que" e "eu" (C); o audio da C entra no fundo do vale, 19,683 (-45 dB),
  para nao sobrar a cauda do "que" | 19,033 troca para o plano da fachada (D); o "E" comeca em 19,02 logo apos
  silencio digital, entao o audio da D entra em 19,017 | nas duas o audio adianta 16 ms do video (imperceptivel)
  24,133 fim do plano ("Brasil" acaba em 23,80) | 6,733 inicio de "ta em crise" | 11,620 fim de "cafe" |
  13,267 sentada -> em pe | 19,000 fim de "volta amanha" | 24,167 plano andando (CTA)
Legendas e tarja no estilo da previa do editor (medidas nela, em px de 1080x1920): Verdana Bold branca com
contorno escuro, base da ultima linha em y=1452, frase longa em 2 linhas; tarja RAISSA / FRANQUEADA + caixa
branca "Cheirin Bao" (53-501 x 1665-1754) nos primeiros 4 s. Desenhadas com PIL e sobrepostas pelo ffmpeg.
Saida 1080x1920 H.264 30fps, AAC.
"""
import os
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFilter, ImageFont

PASTA = os.path.expandvars(r"%USERPROFILE%\OneDrive\Área de Trabalho\CLAUDE CODE\franquias\cheirin bao"
                           r"\criativos campanha outubro")
SRC = os.path.join(PASTA, "IMG_3992 video original raissa.MOV")
FIM = 28.033
FADE = 0.035
W, H = 1080, 1920
FONTE = r"C:\Windows\Fonts\verdanab.ttf"
TARJA_ATE = 4.0

# legendas do corpo na timeline do ORIGINAL: (inicio, texto). Cada uma vale ate a proxima ou o fim do trecho.
CORPO_LEG = [
    (6.733, "Tá em crise ou não,"),
    (8.720, "o brasileiro toma café."),
    (12.900, "E negócio bom"),
    (14.250, "é negócio de recorrência."),
    (16.250, "Vem tomar café aqui hoje,"),
    (17.900, "volta amanhã."),
    (24.167, "Quer entender mais"),
    (25.350, "sobre esse modelo de negócio?"),
    (26.700, "Clique aqui no link."),
]
CORPO = [(6.733, 11.620), (13.267, 19.000), (24.167, FIM)]
MAIOR_REDE = (21.550, "a maior rede de cafeterias\ndo Brasil.")
VERSOES = {
    "Cheirin Bao - Raissa - 3992 EDIT C eu escolhi.mp4": {
        "segs": [(19.667, 24.133)] + CORPO, "audio_ini": 19.683, "fade_ini": 0.010,
        "abertura": [(19.667, "Eu escolhi a Cheirin Bão,"), MAIOR_REDE]},
    "Cheirin Bao - Raissa - 3992 EDIT D e por isso (Eduardo).mp4": {
        "segs": [(19.033, 24.133)] + CORPO, "audio_ini": 19.017, "fade_ini": 0.005,
        "abertura": [(19.033, "E é por isso que eu escolhi"), (20.300, "a Cheirin Bão,"), MAIOR_REDE]},
}


def fonte_para_largura(texto, alvo):
    """Tamanho da Verdana Bold cuja largura de tinta mais se aproxima da medida na previa."""
    return min(range(24, 80), key=lambda s: abs(ImageFont.truetype(FONTE, s).getbbox(texto)[2]
                                                  - ImageFont.truetype(FONTE, s).getbbox(texto)[0] - alvo))


F_LEG = ImageFont.truetype(FONTE, fonte_para_largura("tá em crise ou não.", 453))
F_NOME = ImageFont.truetype(FONTE, fonte_para_largura("RAISSA", 246))
F_CARGO = ImageFont.truetype(FONTE, fonte_para_largura("FRANQUEADA", 244))
F_CAIXA = ImageFont.truetype(FONTE, fonte_para_largura("Cheirin Bão", 262))


def texto_contorno(img, xy, texto, fonte, anchor, stroke, sombra=150, blur=4):
    """Branco com contorno escuro e sombra suave, como na previa."""
    camada = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(camada).text((xy[0], xy[1] + 3), texto, font=fonte, anchor=anchor, fill=(0, 0, 0, sombra),
                                stroke_width=stroke + 1, stroke_fill=(0, 0, 0, sombra))
    img.alpha_composite(camada.filter(ImageFilter.GaussianBlur(blur)))
    ImageDraw.Draw(img).text(xy, texto, font=fonte, anchor=anchor, fill=(255, 255, 255, 255),
                             stroke_width=stroke, stroke_fill=(20, 20, 20, 235))


def png_legenda(texto, caminho):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    linhas = texto.split("\n")
    for i, linha in enumerate(linhas):
        base = 1452 - (len(linhas) - 1 - i) * 50
        texto_contorno(img, (W / 2, base), linha, F_LEG, "ms", 3)
    img.save(caminho)


def png_tarja(caminho):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    texto_contorno(img, (59 - F_NOME.getbbox("RAISSA")[0], 1571), "RAISSA", F_NOME, "ls", 3, 170, 6)
    texto_contorno(img, (56 - F_CARGO.getbbox("FRANQUEADA")[0], 1617), "FRANQUEADA", F_CARGO, "ls", 2, 170, 5)
    d = ImageDraw.Draw(img)
    d.rectangle((53, 1665, 501, 1754), fill=(255, 255, 255, 255))
    d.text((77 - F_CAIXA.getbbox("Cheirin Bão")[0], 1718), "Cheirin Bão", font=F_CAIXA, anchor="ls",
           fill=(10, 10, 10, 255))
    img.save(caminho)


def legendas_da_edicao(segs, leg):
    """Leva as legendas da timeline original para a timeline da edicao, cortando cada uma no limite do trecho."""
    leg = sorted(leg)
    out, t_ed = [], 0.0
    for a, b in segs:
        for i, (s, txt) in enumerate(leg):
            e = leg[i + 1][0] if i + 1 < len(leg) else FIM
            ini, fim = max(s, a), min(e, b)
            if fim - ini > 0.05:
                out.append((round(t_ed + ini - a, 3), round(t_ed + fim - a, 3), txt))
        t_ed += b - a
    return out, t_ed


def monta(saida, v, tmp):
    partes, rot = [], []
    for i, (a, b) in enumerate(v["segs"]):
        d = b - a
        a_aud, f_in = (v["audio_ini"], v["fade_ini"]) if i == 0 else (a, FADE)
        partes.append(f"[0:v]trim=start={a}:end={b},setpts=PTS-STARTPTS,scale={W}:{H}:flags=lanczos[v{i}]")
        partes.append(f"[0:a]atrim=start={a_aud}:end={a_aud + d:.3f},asetpts=PTS-STARTPTS,"
                      f"afade=t=in:st=0:d={f_in},afade=t=out:st={d - FADE:.3f}:d={FADE}[a{i}]")
        rot.append(f"[v{i}][a{i}]")
    partes.append("".join(rot) + f"concat=n={len(v['segs'])}:v=1:a=1[base][a]")
    legs, dur = legendas_da_edicao(v["segs"], CORPO_LEG + v["abertura"])
    entradas = ["-i", SRC]
    tarja = os.path.join(tmp, "tarja.png")
    png_tarja(tarja)
    entradas += ["-i", tarja]
    partes.append(f"[base][1:v]overlay=0:0:enable='between(t,0,{TARJA_ATE})'[l0]")
    for j, (ini, fim, txt) in enumerate(legs):
        p = os.path.join(tmp, f"leg_{j}.png")
        png_legenda(txt, p)
        entradas += ["-i", p]
        partes.append(f"[l{j}][{j + 2}:v]overlay=0:0:enable='between(t,{ini},{fim - 0.001})'[l{j + 1}]")
    subprocess.run(["ffmpeg", "-y", "-v", "error"] + entradas +
                   ["-filter_complex", ";".join(partes), "-map", f"[l{len(legs)}]", "-map", "[a]",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", "30",
                    "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-movflags", "+faststart",
                    os.path.join(PASTA, saida)], check=True)
    print(f"OK {saida} ({dur:.2f}s)")
    for ini, fim, txt in legs:
        print(f"    {ini:6.2f}-{fim:6.2f}  {txt.replace(chr(10), ' / ')}")


if __name__ == "__main__":
    print("tamanhos Verdana Bold: legenda", F_LEG.size, "| RAISSA", F_NOME.size, "| FRANQUEADA", F_CARGO.size,
          "| caixa", F_CAIXA.size)
    with tempfile.TemporaryDirectory() as tmp:
        for s, v in VERSOES.items():
            monta(s, v, tmp)
