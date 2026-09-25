#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Boali — lojas da camada "Boali | Brasil" dentro da capital de SP (bounding box).

Saida: nome, descricao curta, lat/lon e distancia ao centro, para montar os pinos
do conjunto da capital. A bounding box pega bordas de cidades vizinhas: conferir
os nomes antes de usar.
"""
import csv
import os
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from checa_sp_capital import KML, NS, SP_CENTRO, dist  # noqa: E402

K = "{http://www.opengis.net/kml/2.2}"


def texto(el, tag):
    x = el.find("k:" + tag, NS)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", x.text)).strip() if x is not None and x.text else ""


def main():
    raiz = ET.parse(KML).getroot()
    lojas = []
    for folder in raiz.iter(K + "Folder"):
        nome = texto(folder, "name")
        if not re.fullmatch(r"Boali \| Brasil", nome):
            continue
        for pm in folder.findall("k:Placemark", NS):
            c = pm.find(".//k:coordinates", NS)
            if c is None or not c.text:
                continue
            lon, lat = map(float, c.text.strip().split(",")[:2])
            if -24.01 <= lat <= -23.35 and -46.83 <= lon <= -46.36:
                lojas.append((dist((lat, lon), SP_CENTRO), texto(pm, "name"),
                              texto(pm, "description")[:110], lat, lon))
    lojas.sort()
    saida = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lojas_capital_bbox.csv")
    with open(saida, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["km_centro", "nome", "descricao", "lat", "lon"])
        for d, n, desc, la, lo in lojas:
            w.writerow([round(d, 2), n, desc, la, lo])
    for d, n, desc, la, lo in lojas:
        print("%5.1f km | %-40s | %.5f,%.5f | %s" % (d, n[:40], la, lo, desc[:70]))
    print("\n%d pontos na bounding box -> %s" % (len(lojas), saida))


if __name__ == "__main__":
    main()
