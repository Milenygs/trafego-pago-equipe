#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Boali — Sao Paulo capital tem praca de expansao no mapa oficial?

Le o KML do My Maps da Boali e separa as camadas. Depois cruza cada ponto da
camada de PRACAS DE EXPANSAO com o poligono aproximado do municipio de Sao Paulo
(bounding box + checagem de distancia ao centro), para responder uma coisa so:
existe praca ABERTA dentro da capital?

Nao confia em nota anterior — a resposta sai do arquivo.
"""
import os
import re
import xml.etree.ElementTree as ET
from math import asin, cos, radians, sin, sqrt

AQUI = os.path.dirname(os.path.abspath(__file__))
KML = os.path.join(AQUI, "..", "..", "references", "boali-mapa-geral.kml")
NS = {"k": "http://www.opengis.net/kml/2.2"}

SP_CENTRO = (-23.55052, -46.63331)


def dist(a, b):
    la1, lo1 = radians(a[0]), radians(a[1])
    la2, lo2 = radians(b[0]), radians(b[1])
    h = sin((la2 - la1) / 2) ** 2 + cos(la1) * cos(la2) * sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371 * asin(sqrt(h))


def main():
    raiz = ET.parse(KML).getroot()
    print("\nCAMADAS DO MAPA\n" + "-" * 64)
    camadas = []
    for folder in raiz.iter("{http://www.opengis.net/kml/2.2}Folder"):
        nome = folder.find("k:name", NS)
        nome = nome.text.strip() if nome is not None and nome.text else "(sem nome)"
        pontos = []
        for pm in folder.findall("k:Placemark", NS):
            n = pm.find("k:name", NS)
            c = pm.find(".//k:coordinates", NS)
            if c is None or not c.text:
                continue
            partes = c.text.strip().split(",")
            if len(partes) < 2:
                continue
            try:
                lon, lat = float(partes[0]), float(partes[1])
            except ValueError:
                continue
            pontos.append(((n.text.strip() if n is not None and n.text else "?"),
                           lat, lon))
        if pontos:
            camadas.append((nome, pontos))
            print("%-46s %4d pontos" % (nome[:46], len(pontos)))

    # A camada de expansao e a que tem "praca" ou "expansao" no nome.
    alvo = [c for c in camadas
            if re.search(r"expans|pra[cç]a", c[0], re.I)]
    if not alvo:
        print("\nNao achei camada de pracas de expansao pelo nome. Camadas acima.")
        return

    for nome, pontos in alvo:
        print("\n" + "=" * 64)
        print("CAMADA: %s  (%d pontos)" % (nome, len(pontos)))
        print("=" * 64)
        # bounding box generosa do municipio de Sao Paulo
        dentro_bbox = [p for p in pontos
                       if -24.01 <= p[1] <= -23.35 and -46.83 <= p[2] <= -46.36]
        print("dentro da bounding box do municipio de SP: %d" % len(dentro_bbox))
        for n, la, lo in sorted(dentro_bbox, key=lambda p: dist((p[1], p[2]), SP_CENTRO)):
            print("   %-44s %7.2f km do centro de SP" % (n[:44], dist((la, lo), SP_CENTRO)))
        perto = sorted(((dist((la, lo), SP_CENTRO), n) for n, la, lo in pontos))[:8]
        print("\n8 pracas mais proximas do centro de SP:")
        for d, n in perto:
            print("   %7.2f km  %s" % (d, n[:52]))
    print()


if __name__ == "__main__":
    main()
