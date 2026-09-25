#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Casa de Vidro — copy nova no Carrossel B e ativacao dos 4 anuncios (16/09/2026).

Pedido dela: ativar o carrossel B com o texto do video "onde o verao 1" (mandado por
ela no chat, porque o video nao esta nesta conta e o app nao le o Instagram dela).

Criativo na Meta e imutavel: a copy nova exige criativo novo. Entao o fluxo e
criar o B2 (mesmas 4 imagens do B) e TROCAR o creative nos 4 ads que ja existem,
em vez de criar ads novos — os 4 nasceram ontem, nunca entregaram, nao ha
aprendizado a preservar e assim a conta nao fica com ad orfao (mesma decisao de
10/09 na troca da V2 para a V3).

Adaptacoes ao texto dela (video -> carrossel), avisadas no chat:
  - tirado "...servicos sob medida com custo a parte:" (abria lista que nao veio);
  - a observacao "nao somos pousada" virou linha de posicionamento;
  - "Reserve sua estadia" -> chamada de WhatsApp (destino do conjunto).

Uso:
    python trocar_copy_e_ativar_carrossel_b.py --dry
    python trocar_copy_e_ativar_carrossel_b.py
"""
import argparse
import time

from build_geopin_whats import CONTA, SEM_ENHANCEMENTS_MIN, post
from build_carrosseis_geopin import CARROSSEIS, base_v3, spec_carrossel

ADS_B = [
    ("120249466671330510", "PIN MORA"),
    ("120249466676740510", "PIN DESTINO"),
    ("120249466680230510", "PIN LUGARES"),
    ("120249466684090510", "PIN LUGARES BR"),
]

COPY_NOVA = (
    "Descubra o luxo absoluto em Paraty, na nossa Casa de Vidro.\n\n"
    "A Casa de Vidro é um refúgio exclusivo para quem busca privacidade, conforto e "
    "experiências personalizadas à altura do seu estilo de vida. 🏖️🚤\n\n"
    "⚠️ Não somos pousada: é o aluguel por temporada do espaço completo — a casa inteira, só sua.\n\n"
    "Aqui, cada detalhe foi pensado para proporcionar um descanso impecável:\n\n"
    "• Piscina com borda infinita e vista cinematográfica para o mar;\n"
    "• Sauna seca, deck panorâmico e varanda gourmet;\n"
    "• Gastronomia personalizada, com menus criados especialmente para você;\n"
    "• Praia privativa, estruturada pela nossa equipe;\n"
    "• Concierge exclusivo;\n"
    "• Transporte marítimo direto do cais de Paraty Mirim até a casa.\n\n"
    "Acomoda com excelência até 12 pessoas.\n\n"
    "📍 Em Paraty Mirim, a poucos minutos do Centro Histórico e cercada por natureza "
    "preservada — um convite para viver dias indescritíveis.\n\n"
    "👇 Chame no WhatsApp e consulte as datas disponíveis."
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--criativo", help="reusar um B2 ja criado")
    args = ap.parse_args()

    car = dict(next(c for c in CARROSSEIS if c["chave"] == "B"))
    car["copy"] = COPY_NOVA

    welcome, dof = base_v3()
    print("Boas-vindas:", "herdado do V3" if welcome else "NENHUM")
    print("Opt-outs   :", len(dof))
    print("\nCopy nova (Carrossel B):")
    print("  " + COPY_NOVA.replace("\n", "\n  "))
    print("\nCards (inalterados):")
    for h, t in car["cards"]:
        print("   -", h, t or "(capa)")
    print("\nAds que vao receber a copy nova e ficar ACTIVE:")
    for ad, apelido in ADS_B:
        print("   -", ad, apelido)

    if args.dry:
        print("\n--dry: nada escrito.")
        return

    criativo = args.criativo
    if not criativo:
        print("\nCriando criativo B2...")
        spec = spec_carrossel(car, welcome)
        nome = "CDV - Carrossel Eventos B2 - Luxo absoluto [WHATS] - 16/09/2026"
        criativo = post(CONTA + "/adcreatives", {
            "name": nome, "object_story_spec": spec,
            "degrees_of_freedom_spec": {"creative_features_spec": dof or SEM_ENHANCEMENTS_MIN},
        }, "criativo B2")
        if not criativo and dof:
            print("       -> repetindo com o subset minimo de opt-out")
            criativo = post(CONTA + "/adcreatives", {
                "name": nome, "object_story_spec": spec,
                "degrees_of_freedom_spec": {"creative_features_spec": SEM_ENHANCEMENTS_MIN},
            }, "criativo B2 (min)")
    if not criativo:
        raise SystemExit("Criativo B2 falhou — nada trocado, nada ativado.")

    print("\nTrocando o criativo e ativando...")
    for ad, apelido in ADS_B:
        post(ad, {
            "creative": {"creative_id": criativo},
            "name": "AD - Carrossel Eventos B2 - Luxo absoluto - " + apelido,
        }, "troca de copy " + apelido)
        time.sleep(1)
        post(ad, {"status": "ACTIVE"}, "ativar " + apelido)
        time.sleep(1)

    print("\nCriativo B2:", criativo)


if __name__ == "__main__":
    main()
