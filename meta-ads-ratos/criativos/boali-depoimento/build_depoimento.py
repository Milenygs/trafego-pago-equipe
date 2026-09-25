#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Boali — sobe UM depoimento novo de franqueado como anuncio nos DOIS conjuntos
de captacao que estao no ar (10/09/2026).

Por que nos dois, e nao em um conjunto novo:
  a regra da casa e conjunto por NIVEL DE CONSCIENCIA, criativo e municao dentro
  do conjunto. Depoimento de franqueado e o formato campeao nas duas temperaturas
  — no quente (CP 04) deu CPL R$71 e R$69; no frio (CP 05) deu R$89 e R$63, os
  dois melhores da conta. Nao e criativo de uma temperatura so, entao entra nas
  duas como anuncio, sem conjunto novo.

Prioridade e o CP 05: em 01-09/09 ele rodou praticamente com UM criativo
([LAL] MERCADO BILHAO), CPM R$180 e frequencia 1,77 sobre um LAL 1% de ~1,4M.
Publico pequeno + criativo unico = fadiga. Criativo novo e o remedio direto.

Blueprint copiado do criativo vencedor 1809873060459195 (AD12 MARY E BRUNO):
mesma pagina, mesmo IG, mesmo formulario, mesmo CTA, e TODOS os enhancements
em OPT_OUT — o painel liga essas IAs sozinho, aqui elas ficam desligadas.

Os anuncios sobem PAUSED. Ativar so com ok da Mileny.

Uso:
    python build_depoimento.py --video "C:\\...\\depoimento.mp4" --rotulo "AD14 - DEPOIMENTO FULANO" --dry
    python build_depoimento.py --video "C:\\...\\depoimento.mp4" --rotulo "AD14 - DEPOIMENTO FULANO"
    python build_depoimento.py --video-id 1046597861672228 --rotulo "..."   # se ja subiu o video
"""
import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.abspath(os.path.join(AQUI, "..", ".."))
API = "https://graph.facebook.com/v21.0/"

CONTA = "act_295475086762368"
PAGE = "110751468238380"
IG = "17841452681323339"
FORM = "913523365113250"          # formulario nativo que os vencedores usam

# Conjuntos ATIVOS de captacao (conferidos na conta em 10/09/2026).
DESTINOS = [
    ("120249949945780156", "CP 04 · [QUENTE 180D] [FORMS - CADASTROS] [ON_AD]", ""),
    ("120250111279470156", "CP 05 · [FRIO] LAL 1% QUALIFICADOS+VENDAS 30-55", "[LAL] "),
]

TITULO = "Franquia Boali"

# Copy do criativo vencedor (AD12 Mary e Bruno). Fica aqui como referencia.
# NAO e mais o padrao: em 10/09 a Mileny avisou que o Mary e Bruno comecou a
# trazer lead ruim, e essa copy nao tem nenhum filtro de investimento — ela
# convida todo mundo a se cadastrar. CPL baixo com copy sem filtro e exatamente
# o padrao de quem atrai curioso num ticket de R$300 mil.
COPY_ORIGINAL = (
    "Quem já é franqueado Boali conta na prática por que investiu — e por que "
    "faria tudo de novo.\n\n"
    "Um modelo validado: 19 anos de mercado, 98% dos franqueados recomendam, "
    "operação simples e suporte completo.\n\n"
    'Toque em "Cadastre-se" e receba a apresentação completa da franquia.'
)

# Padrao novo: mesma prova social, com o filtro de investimento na copy.
# O video mostra o painel da loja em 691 pedidos — a prova de giro esta na
# imagem, entao a copy pode gastar as linhas dela qualificando.
#
# VALOR: R$ 359.000, confirmado pela Mileny em 10/09. E o mesmo numero da copy do
# AD04 Rodrigo faturamento (criativo 1025361703312632), que e o anuncio de maior
# taxa de avanco da conta. NAO usar "a partir de R$300 mil" (nota antiga do
# contas.yaml e faixa mais baixa do formulario) — e menos especifico e filtra menos.
#
# A estrutura da copy copia o que funciona no Rodrigo: preco cedo, beneficios em
# lista curta, e CTA de conversa em vez de "receba a apresentacao". Copy que nao
# diz preco + CTA sem compromisso foi o que produziu 1 avanco em 99 leads no quente.
COPY = (
    "691 pedidos no painel num dia comum. Quem já é franqueado Boali conta o "
    "que sustenta esse movimento.\n\n"
    "✅ 19 anos de mercado\n"
    "✅ Investimento a partir de R$359.000\n"
    "✅ Operação simples\n"
    "✅ 98% dos franqueados recomendam\n"
    "✅ Média de 3 lojas por franqueado\n\n"
    "👇 Fale com um de nossos consultores"
)

# O painel sobe criativo com essas IAs ligadas. Preferencia da casa: todas OFF.
#
# ATENCAO (10/09/2026): `standard_enhancements` NAO pode mais ser enviado na
# criacao. A Meta responde "O criativo nao deve incluir aprimoramentos padrao —
# o recurso foi descontinuado, defina recursos individuais". Criativos antigos
# da conta ainda mostram o campo quando lidos (o 1809873060459195 mostra), mas
# copiar dali pra um POST quebra. Opt-out agora e recurso por recurso.
SEM_IA = {
    "creative_features_spec": {
        "advantage_plus_creative": {"enroll_status": "OPT_OUT"},
        "enhance_cta": {"enroll_status": "OPT_OUT"},
        "inline_comment": {"enroll_status": "OPT_OUT"},
        "text_optimizations": {"enroll_status": "OPT_OUT"},
        "video_auto_crop": {"enroll_status": "OPT_OUT"},
        "video_filtering": {"enroll_status": "OPT_OUT"},
        "video_uncrop": {"enroll_status": "OPT_OUT"},
    }
}


def token():
    with open(os.path.join(SKILL, ".env"), encoding="utf-8") as f:
        for linha in f:
            if linha.strip().startswith("META_ADS_TOKEN"):
                return linha.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("META_ADS_TOKEN nao encontrado no .env")


TOKEN = token()


def get(path, params):
    params = dict(params)
    params["access_token"] = TOKEN
    with urllib.request.urlopen(API + path + "?" + urllib.parse.urlencode(params),
                                timeout=60) as r:
        return json.load(r)


def post(path, params, oque):
    corpo = {k: (json.dumps(v) if isinstance(v, (dict, list)) else v)
             for k, v in params.items()}
    corpo["access_token"] = TOKEN
    dados = urllib.parse.urlencode(corpo).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(API + path, data=dados),
                                    timeout=120) as r:
            saida = json.load(r)
            print("  OK   %-52s %s" % (oque, saida.get("id")))
            return saida.get("id")
    except urllib.error.HTTPError as e:
        erro = json.loads(e.read().decode("utf-8")).get("error", {})
        print("  ERRO %-52s" % oque)
        print("       msg :", erro.get("message"))
        print("       user:", erro.get("error_user_title"), "|", erro.get("error_user_msg"))
        sys.exit(1)


def sobe_video(caminho):
    """Delega pro scripts/create.py, que ja faz chunked upload pelo SDK."""
    if not os.path.exists(caminho):
        sys.exit("arquivo nao encontrado: %s" % caminho)
    mb = os.path.getsize(caminho) / (1024 * 1024)
    print("  ... subindo video (%.1f MB), pode demorar" % mb)
    r = subprocess.run(
        [sys.executable, os.path.join(SKILL, "scripts", "create.py"), "video",
         "--account", CONTA, "--file", caminho,
         "--name", os.path.splitext(os.path.basename(caminho))[0]],
        capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout)
        print(r.stderr, file=sys.stderr)
        sys.exit("falhou o upload do video")
    # O create.py imprime "Token carregado ..." antes do JSON, e o JSON sai
    # identado em varias linhas — nao da pra pegar so a ultima linha.
    inicio = r.stdout.rfind("{")
    fim = r.stdout.rfind("}")
    if inicio == -1 or fim == -1:
        print(r.stdout)
        sys.exit("nao achei o id do video na saida do create.py")
    vid = json.loads(r.stdout[inicio:fim + 1])["id"]
    print("  OK   %-52s %s" % ("video", vid))
    return vid


def thumb(video_id):
    """Pega a thumbnail preferida do video. Sem isso a Meta escolhe sozinha."""
    try:
        dados = get("%s/thumbnails" % video_id, {"fields": "uri,is_preferred"})["data"]
    except Exception:
        return None
    if not dados:
        return None
    for t in dados:
        if t.get("is_preferred"):
            return t["uri"]
    return dados[0]["uri"]


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--video", help="caminho do .mp4 do depoimento")
    g.add_argument("--video-id", help="video ja subido na conta")
    ap.add_argument("--rotulo", required=True,
                    help='nome do anuncio, ex: "AD14 - DEPOIMENTO JOAO E ANA"')
    ap.add_argument("--copy", help="sobrescreve a copy padrao")
    ap.add_argument("--trocar-em", help="IDs de ads existentes (virgula) — cria o "
                                        "criativo e troca neles, em vez de criar ads novos")
    ap.add_argument("--dry", action="store_true", help="so mostra o que faria")
    args = ap.parse_args()

    corpo = args.copy or COPY

    print("\nBoali — depoimento novo")
    print("  conta   :", CONTA)
    print("  rotulo  :", args.rotulo)
    print("  form    :", FORM, "(SIGN_UP)")
    print("  destinos: %d conjuntos ativos" % len(DESTINOS))
    for _, nome, _p in DESTINOS:
        print("            -", nome)
    print("  IA      : tudo OPT_OUT")
    print("  status  : PAUSED (ativar so com ok)\n")

    if args.dry:
        print("  [dry] nada foi criado.")
        print("  [dry] copy:")
        for linha in corpo.splitlines():
            print("        " + linha)
        return

    video_id = args.video_id or sobe_video(args.video)

    story = {
        "page_id": PAGE,
        "instagram_user_id": IG,
        "video_data": {
            "video_id": video_id,
            "title": TITULO,
            "message": corpo,
            "call_to_action": {
                "type": "SIGN_UP",
                "value": {"lead_gen_form_id": FORM, "link": "http://fb.me/"},
            },
        },
    }
    uri = thumb(video_id)
    if uri:
        story["video_data"]["image_url"] = uri

    criativo = post("%s/adcreatives" % CONTA, {
        "name": "Boali — %s" % args.rotulo,
        "object_story_spec": story,
        "degrees_of_freedom_spec": SEM_IA,
    }, "criativo")

    if args.trocar_em:
        # Copy de criativo publicado nao se edita — cria um novo e aponta o ad
        # existente pra ele. O ad mantem id, historico e status.
        for ad_id in [x.strip() for x in args.trocar_em.split(",") if x.strip()]:
            post(ad_id, {"creative": {"creative_id": criativo}},
                 "criativo trocado no ad %s" % ad_id)
        print("\n  Criativo trocado. O ad mantem o status que ja tinha.")
        return

    for adset_id, nome, prefixo in DESTINOS:
        post("%s/ads" % CONTA, {
            "name": prefixo + args.rotulo,
            "adset_id": adset_id,
            "creative": {"creative_id": criativo},
            "status": "PAUSED",
        }, "ad em %s" % nome.split(" · ")[0])

    print("\n  Tudo PAUSED. Conferir preview antes de ativar.")


if __name__ == "__main__":
    main()
