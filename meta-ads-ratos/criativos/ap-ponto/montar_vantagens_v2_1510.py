"""Belo 15/10/2026 (Mileny: "pode editar"): versao 2 da arte "Vantagens 60x".

1. Linha nova sob "Some renda com mais alguem": "e chegue a renda minima de R$5.001" (regra da renda do Belo:
   minimo sempre junto de "da para somar"). Nas duas versoes.
2. 9:16: tudo o que importa dentro da area segura de Stories/Reels (topo 14% livre; lista e selo 60x acima de ~65% da
   altura; selo menor e longe da borda direita, onde ficam os icones do Reels).
Remonta a arte a partir dos PNGs da Mileny (fonte da arte: Outfit). Uso:
  python montar_vantagens_v2_1510.py <feed.png> <stories.png> <Outfit.ttf> <pasta_saida>
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FEED, STORY, FONTE, SAIDA = map(Path, sys.argv[1:5])
GREY = (227, 227, 227)
LAV = (182, 193, 237)
TXT = (61, 65, 86)
SS = 4  # supersampling das mascaras


def fonte(peso, tam):
    f = ImageFont.truetype(str(FONTE), tam)
    f.set_variation_by_name(peso)
    return f


def mask_rrect(w, h, r):
    m = Image.new("L", (w * SS, h * SS), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w * SS - 1, h * SS - 1), r * SS, fill=255)
    return m.resize((w, h), Image.LANCZOS)


def mask_circ(d):
    m = Image.new("L", (d * SS, d * SS), 0)
    ImageDraw.Draw(m).ellipse((0, 0, d * SS - 1, d * SS - 1), fill=255)
    return m.resize((d, d), Image.LANCZOS)


def sombra(canvas, mask, xy, desloc=8, blur=14, cor=(30, 40, 100), opac=0.20):
    pad = blur * 3
    w, h = mask.size
    a = Image.new("L", (w + 2 * pad, h + 2 * pad), 0)
    a.paste(mask, (pad, pad))
    a = a.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * opac))
    camada = Image.new("RGB", a.size, cor)
    canvas.paste(camada, (xy[0] - pad, xy[1] - pad + desloc), a)


def card(canvas, box, r):
    x0, y0, x1, y1 = box
    m = mask_rrect(x1 - x0 + 1, y1 - y0 + 1, r)
    canvas.paste(Image.new("RGB", m.size, LAV), (x0, y0), m)


def foto(canvas, src, ate, r):
    """Foto da fachada de src (linhas 0..ate), com os cantos de baixo refeitos em `ate`."""
    crop = src.crop((0, 0, src.width, ate))
    canvas.paste(crop, (0, 0))
    # cantos inferiores: pinta o fundo fora de um retangulo arredondado
    w = 1043 - 36 + 1
    m = mask_rrect(w, r * 2, r)  # so a metade de baixo importa
    faixa = canvas.crop((36, ate - r, 36 + w, ate))
    fundo = Image.new("RGB", faixa.size, GREY)
    fundo.paste(faixa, (0, 0), m.crop((0, r, w, 2 * r)))
    canvas.paste(fundo, (36, ate - r))


def badge_belo(canvas, src, caixa, r, destino_y):
    x0, y0, x1, y1 = caixa
    peca = src.crop((x0, y0, x1 + 1, y1 + 1))
    m = mask_rrect(peca.width, peca.height, r)
    sombra(canvas, m, (x0, destino_y), desloc=6, blur=12, opac=0.16)
    canvas.paste(peca, (x0, destino_y), m)


def selo_60x(canvas, src, centro, raio, novo_centro, escala):
    cx, cy = centro
    d = 2 * raio + 2
    peca = src.crop((int(cx - raio - 1), int(cy - raio - 1), int(cx - raio - 1) + d, int(cy - raio - 1) + d))
    nd = round(d * escala)
    peca = peca.resize((nd, nd), Image.LANCZOS)
    m = mask_circ(nd)
    pos = (round(novo_centro[0] - nd / 2), round(novo_centro[1] - nd / 2))
    sombra(canvas, m, pos, desloc=10, blur=16, cor=(40, 60, 170), opac=0.28)
    canvas.paste(peca, pos, m)


def azul_negrito(src, caixa):
    """Cor do texto em negrito (linha 'Preco de lancamento', toda em negrito)."""
    a = np.array(src.crop(caixa)).reshape(-1, 3).astype(int)
    a = a[np.abs(a - np.array(LAV)).max(axis=1) > 40]
    escuros = a[np.argsort(a.sum(axis=1))[: max(20, len(a) // 20)]]
    return tuple(int(v) for v in np.median(escuros, axis=0))


def largura(f, t):
    return f.getbbox(t)[2] - f.getbbox(t)[0]


def tamanho_da_linha(src, y0, y1, x_ini, x_lim, texto):
    """Acha o corpo da Outfit Regular que reproduz a largura medida da linha original."""
    a = np.array(src.crop((x_ini, y0, x_lim, y1 + 1))).astype(int)
    tinta = ~np.all(np.abs(a - np.array(LAV)) <= 10, axis=2)
    xs = np.where(tinta.any(axis=0))[0]
    alvo = xs.max() - xs.min() + 1
    for t in range(20, 60):
        if largura(fonte("Regular", t), texto) >= alvo:
            return t, alvo
    return 40, alvo


def linha_renda(canvas, x, base, tam, azul):
    d = ImageDraw.Draw(canvas)
    f_reg, f_bold = fonte("Regular", tam), fonte("Bold", tam)
    t1, t2 = "e chegue à renda mínima de ", "R$5.001"
    d.text((x, base), t1, font=f_reg, fill=TXT, anchor="ls")
    d.text((x + f_reg.getlength(t1), base), t2, font=f_bold, fill=azul, anchor="ls")


# ---------------------------------------------------------------- 9:16
s = Image.open(STORY).convert("RGB")
assert s.size == (1080, 1920), s.size
azul = azul_negrito(s, (140, 1049, 500, 1088))
t_row, w_row = tamanho_da_linha(s, 1205, 1243, 140, 740, "Some renda com mais alguém")
print("story: azul", azul, "| corpo da linha", t_row, "| largura", w_row)

S1 = -140   # sobe foto, selo do Belo, card, titulo, pilulas e itens 1-4
S2 = 48     # espaco da linha nova
S3 = -96    # lazer, botao e aviso
c = Image.new("RGB", (1080, 1920), GREY)
foto(c, s, 700 + S1, 40)
card(c, (36, 740 + S1, 1043, 1883), 44)
c.paste(s.crop((40, 845, 1040, 1020)), (40, 845 + S1))                 # titulo + pilulas
c.paste(s.crop((60, 1040, 740, 1250)), (60, 1040 + S1))                # itens 1-4
linha_renda(c, 143, 1243 + S1 + 30, round(t_row * 0.76), azul)       # linha nova
c.paste(s.crop((60, 1250, 740, 1356)), (60, 1250 + S1 + S2))           # itens 5-6
c.paste(s.crop((40, 1360, 1040, 1630)), (40, 1360 + S3))               # lazer, botao, aviso
badge_belo(c, s, (357, 612, 722, 819), 32, 612 + S1)
topo_lista, fim_lista = 1049 + S1, 1347 + S1 + S2
selo_60x(c, s, (905.5, 1185.5), 134, (836, (topo_lista + fim_lista) / 2), 0.86)
c.save(SAIDA / "IMG_Vantagens_60x_v2_story_1080x1920.png")
print("story: lista", topo_lista, "-", fim_lista, "| aviso termina em", 1618 + S3)

# ---------------------------------------------------------------- 4:5
f = Image.open(FEED).convert("RGB")
assert f.size == (1080, 1350), f.size
azul_f = azul_negrito(f, (140, 802, 500, 836))
tf_row, wf_row = tamanho_da_linha(f, 940, 973, 140, 770, "Some renda com mais alguém")
print("feed: azul", azul_f, "| corpo da linha", tf_row, "| largura", wf_row)
D = -36
g = f.copy()
g.paste(Image.new("RGB", (1080, 980), GREY), (0, 0))                   # refaz o topo (0..980)
foto(g, f, 507 + D, 40)
card(g, (36, 532 + D, 1043, 1312), 44)
g.paste(f.crop((40, 980, 1044, 1313)), (40, 980))                      # parte de baixo intacta
g.paste(Image.new("RGB", (1043 - 760 + 1, 1080 - 980), LAV), (760, 980))  # tira a sombra antiga do selo
g.paste(f.crop((40, 610, 1040, 775)), (40, 610 + D))                   # titulo + pilulas (sem a sombra do selo)
g.paste(f.crop((60, 790, 770, 980)), (60, 790 + D))                    # itens 1-4
linha_renda(g, 143, 973 + D + 28, round(tf_row * 0.76), azul_f)
badge_belo(g, f, (390, 430, 689, 599), 30, 430 + D)
selo_60x(g, f, (907.5, 917.5), 118, (907.5, 917.5), 1.0)
g.save(SAIDA / "IMG_Vantagens_60x_v2_feed_1080x1350.png")
print("ok")
