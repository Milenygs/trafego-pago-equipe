#!/usr/bin/env python3
"""
Meta Ads Ratos - Criar objetos (campaigns, adsets, ads, creatives, audiences)
Todas as criações defaultam para status=PAUSED.
"""
import os, sys, json, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import (init_api, resolve_account, print_json, handle_fb_error,
                 print_error, parse_fields, parse_json_arg, add_account_arg,
                 add_fields_arg, safe_delay)

from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.adobjects.customaudience import CustomAudience
from facebook_business.adobjects.advideo import AdVideo


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------

@handle_fb_error
def cmd_campaign(args):
    """⚠️ WRITE — Cria campanha (status PAUSED por padrao).

    Objetivos: OUTCOME_SALES, OUTCOME_LEADS, OUTCOME_ENGAGEMENT,
    OUTCOME_AWARENESS, OUTCOME_TRAFFIC, OUTCOME_APP_PROMOTION
    Orcamento em centavos: 5000 = R$50,00
    """
    init_api()
    account_id = resolve_account(args.account)

    params = {
        'name': args.name,
        'objective': args.objective,
        'status': args.status or 'PAUSED',
        'special_ad_categories': [args.special_ad_categories] if args.special_ad_categories != 'NONE' else [],
        'buying_type': args.buying_type or 'AUCTION',
    }
    if args.daily_budget:
        params['daily_budget'] = args.daily_budget
    if args.lifetime_budget:
        params['lifetime_budget'] = args.lifetime_budget
    if args.bid_strategy:
        params['bid_strategy'] = args.bid_strategy
    if args.start_time:
        params['start_time'] = args.start_time
    if args.stop_time:
        params['stop_time'] = args.stop_time
    if args.spend_cap:
        params['spend_cap'] = args.spend_cap
    if not args.daily_budget and not args.lifetime_budget:
        # ABO (orcamento no adset, nao na campanha) exige este campo explicito (subcode 4834011)
        params['is_adset_budget_sharing_enabled'] = args.adset_budget_sharing

    account = AdAccount(account_id)
    result = account.create_campaign(params=params)
    safe_delay(1)

    print(f"Criado campaign com ID: {result['id']} (status: {params['status']})", file=sys.stderr)
    print_json(result)


@handle_fb_error
def cmd_adset(args):
    """⚠️ WRITE — Cria ad set (status PAUSED por padrao).

    Requer: campaign_id, optimization_goal, targeting (JSON), billing_event.
    Orcamento em centavos: daily_budget 5000 = R$50,00/dia
    """
    init_api()
    account_id = resolve_account(args.account)

    targeting = parse_json_arg(args.targeting, '--targeting')
    if not targeting:
        print_error("--targeting e obrigatorio (JSON string)")
        sys.exit(1)

    params = {
        'name': args.name,
        'campaign_id': args.campaign,
        'optimization_goal': args.optimization_goal,
        'billing_event': args.billing_event or 'IMPRESSIONS',
        'targeting': targeting,
        'status': args.status or 'PAUSED',
    }
    if args.daily_budget:
        params['daily_budget'] = args.daily_budget
    if args.lifetime_budget:
        params['lifetime_budget'] = args.lifetime_budget
    if args.bid_amount:
        params['bid_amount'] = args.bid_amount
    if args.bid_strategy:
        params['bid_strategy'] = args.bid_strategy
    if args.start_time:
        params['start_time'] = args.start_time
    if args.end_time:
        params['end_time'] = args.end_time
    if args.promoted_object:
        params['promoted_object'] = parse_json_arg(args.promoted_object, '--promoted-object')
    if args.destination_type:
        params['destination_type'] = args.destination_type
    if args.adset_schedule:
        params['adset_schedule'] = parse_json_arg(args.adset_schedule, '--adset-schedule')
    if args.pacing_type:
        params['pacing_type'] = [args.pacing_type]

    account = AdAccount(account_id)
    result = account.create_ad_set(params=params)
    safe_delay(1)

    print(f"Criado adset com ID: {result['id']} (status: {params['status']})", file=sys.stderr)
    print_json(result)


@handle_fb_error
def cmd_ad(args):
    """⚠️ WRITE — Cria ad (status PAUSED por padrao).

    Requer: adset_id, creative (JSON: {"creative_id":"123"}).
    """
    init_api()
    account_id = resolve_account(args.account)

    creative = parse_json_arg(args.creative, '--creative')
    if not creative:
        print_error("--creative e obrigatorio (JSON string, ex: '{\"creative_id\":\"123\"}')")
        sys.exit(1)

    params = {
        'name': args.name,
        'adset_id': args.adset,
        'creative': creative,
        'status': args.status or 'PAUSED',
    }
    if args.tracking_specs:
        params['tracking_specs'] = parse_json_arg(args.tracking_specs, '--tracking-specs')
    if args.conversion_domain:
        params['conversion_domain'] = args.conversion_domain
    if args.degrees_of_freedom_spec:
        params['degrees_of_freedom_spec'] = parse_json_arg(args.degrees_of_freedom_spec, '--degrees-of-freedom-spec')

    account = AdAccount(account_id)
    result = account.create_ad(params=params)
    safe_delay(1)

    print(f"Criado ad com ID: {result['id']} (status: {params['status']})", file=sys.stderr)
    print_json(result)


@handle_fb_error
def cmd_creative(args):
    """⚠️ WRITE — Cria criativo. Criativos sao IMUTAVEIS apos criacao.

    Para trocar url_tags de um criativo existente, use advanced.py swap-url-tags.
    """
    init_api()
    account_id = resolve_account(args.account)

    params = {'name': args.name}

    if args.instagram_user_id:
        params['instagram_user_id'] = args.instagram_user_id
    if args.source_ig_media_id:
        # Criativo a partir de post orgânico existente do Instagram
        params['source_instagram_media_id'] = args.source_ig_media_id
        if args.instagram_user_id:
            params['instagram_actor_id'] = args.instagram_user_id
    if args.object_story_spec:
        params['object_story_spec'] = parse_json_arg(args.object_story_spec, '--object-story-spec')
    if args.asset_feed_spec:
        params['asset_feed_spec'] = parse_json_arg(args.asset_feed_spec, '--asset-feed-spec')
    if args.url_tags:
        params['url_tags'] = args.url_tags
    if args.call_to_action_type:
        params['call_to_action_type'] = args.call_to_action_type
    if args.image_hash:
        params['image_hash'] = args.image_hash
    if args.image_url:
        params['image_url'] = args.image_url
    if args.video_id:
        params['video_id'] = args.video_id
    if args.link_url:
        params['link_url'] = args.link_url
    if args.title:
        params['title'] = args.title
    if args.body:
        params['body'] = args.body

    account = AdAccount(account_id)
    result = account.create_ad_creative(params=params)
    safe_delay(1)

    print(f"Criado creative com ID: {result['id']}", file=sys.stderr)
    print_json(result)


@handle_fb_error
def cmd_image(args):
    init_api()
    import requests
    import tempfile

    account_id = resolve_account(args.account)

    if args.file:
        # Arquivo local — usa direto
        if not os.path.exists(args.file):
            print(f"Erro: arquivo não encontrado: {args.file}", file=sys.stderr)
            sys.exit(1)
        params = {}
        if args.name:
            params['name'] = args.name
        account = AdAccount(account_id)
        result = account.create_ad_image(params=params, files={'filename': args.file})
        safe_delay(1)
        print(f"Imagem enviada com sucesso", file=sys.stderr)
        print_json(result)
    else:
        # Download da URL para arquivo temp
        print("Baixando imagem...", file=sys.stderr)
        response = requests.get(args.url, stream=True)
        response.raise_for_status()

        ext = '.jpg'
        content_type = response.headers.get('content-type', '')
        if 'png' in content_type or args.url.lower().endswith('.png'):
            ext = '.png'
        elif 'webp' in content_type or args.url.lower().endswith('.webp'):
            ext = '.webp'

        tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        try:
            for chunk in response.iter_content(chunk_size=8192):
                tmp.write(chunk)
            tmp.close()

            params = {}
            if args.name:
                params['name'] = args.name

            account = AdAccount(account_id)
            result = account.create_ad_image(params=params, files={'filename': tmp.name})
            safe_delay(1)

            print(f"Imagem enviada com sucesso", file=sys.stderr)
            print_json(result)
        finally:
            os.unlink(tmp.name)


@handle_fb_error
def cmd_video(args):
    init_api()
    account_id = resolve_account(args.account)

    if args.file:
        # Upload de arquivo local via AdVideo (suporte a chunked upload)
        if not os.path.exists(args.file):
            print(f"Erro: arquivo não encontrado: {args.file}", file=sys.stderr)
            sys.exit(1)
        video = AdVideo(parent_id=account_id)
        video[AdVideo.Field.filepath] = args.file
        if args.name:
            video[AdVideo.Field.name] = args.name
        if args.title:
            video[AdVideo.Field.title] = args.title
        if args.description:
            video[AdVideo.Field.description] = args.description
        video.remote_create()
        safe_delay(1)
        print(f"Video enviado com ID: {video['id']}", file=sys.stderr)
        print_json({'id': video['id']})
    else:
        params = {'file_url': args.url}
        if args.name:
            params['name'] = args.name
        if args.title:
            params['title'] = args.title
        if args.description:
            params['description'] = args.description
        account = AdAccount(account_id)
        result = account.create_ad_video(params=params)
        safe_delay(1)
        print(f"Video enviado com ID: {result['id']}", file=sys.stderr)
        print_json(result)


@handle_fb_error
def cmd_custom_audience(args):
    init_api()
    account_id = resolve_account(args.account)

    params = {
        'name': args.name,
        'subtype': args.subtype or 'CUSTOM',
    }
    if args.description:
        params['description'] = args.description
    if args.customer_file_source:
        params['customer_file_source'] = args.customer_file_source

    account = AdAccount(account_id)
    result = account.create_custom_audience(params=params)
    safe_delay(1)

    print(f"Criado custom audience com ID: {result['id']}", file=sys.stderr)
    print_json(result)


@handle_fb_error
def cmd_video_audience(args):
    """Cria público de engajamento com vídeo.

    Modos:
      --video-ids  → vídeos específicos da biblioteca da conta (type: video)
      --page-ids   → todas as páginas do Facebook (type: page) — todos os vídeos da página
      --ig-ids     → contas do Instagram Business (type: instagram_business)

    Pode combinar --page-ids e --ig-ids no mesmo público.
    Use read.py videos --account act_XXX para listar IDs de vídeos avulsos.

    Percentuais válidos: 25, 50, 75, 95
    Retenção em dias: 1 a 365
    """
    init_api()
    account_id = resolve_account(args.account)

    retention_seconds = args.retention_days * 86400
    event_sources = []

    if args.video_ids:
        for vid in args.video_ids.split(','):
            vid = vid.strip()
            if vid:
                event_sources.append({"id": vid, "type": "video"})

    if args.page_ids:
        for pid in args.page_ids.split(','):
            pid = pid.strip()
            if pid:
                event_sources.append({"id": pid, "type": "page"})

    if args.ig_ids:
        for igid in args.ig_ids.split(','):
            igid = igid.strip()
            if igid:
                event_sources.append({"id": igid, "type": "instagram_business"})

    if not event_sources:
        print("Erro: informe --video-ids, --page-ids ou --ig-ids", file=sys.stderr)
        sys.exit(1)

    rule = {
        "inclusions": {
            "operator": "or",
            "rules": [
                {
                    "event_sources": event_sources,
                    "retention_seconds": retention_seconds,
                    "filter": {
                        "operator": "and",
                        "filters": [
                            {
                                "field": "video_watched_percentage",
                                "operator": "gt",
                                "value": args.percentage
                            }
                        ]
                    }
                }
            ]
        }
    }

    params = {
        'name': args.name,
        'subtype': 'ENGAGEMENT',
        'rule': rule,
        'description': args.description or f"Video {args.percentage}% | {args.retention_days} dias | {len(event_sources)} fonte(s)",
    }

    account = AdAccount(account_id)
    result = account.create_custom_audience(params=params)
    safe_delay(1)

    print(f"Publico de video criado com ID: {result['id']}", file=sys.stderr)
    print(f"  Nome: {args.name}", file=sys.stderr)
    print(f"  Percentual: {args.percentage}%  |  Retencao: {args.retention_days} dias", file=sys.stderr)
    print(f"  Fontes: {len(event_sources)} evento(s)", file=sys.stderr)
    print_json(result)


@handle_fb_error
def cmd_lookalike(args):
    init_api()
    account_id = resolve_account(args.account)

    spec = parse_json_arg(args.spec, '--spec')
    if not spec:
        print_error("--spec e obrigatorio (JSON string, ex: '{\"country\":\"BR\",\"ratio\":0.01}')")
        sys.exit(1)

    params = {
        'name': args.name,
        'subtype': 'LOOKALIKE',
        'origin_audience_id': args.source,
        'lookalike_spec': spec,
    }

    account = AdAccount(account_id)
    result = account.create_custom_audience(params=params)
    safe_delay(1)

    print(f"Criado lookalike audience com ID: {result['id']}", file=sys.stderr)
    print_json(result)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Meta Ads - Criar objetos")
    sub = parser.add_subparsers(dest="command", required=True)

    # --- campaign ---
    p = sub.add_parser("campaign", help="Criar campanha")
    add_account_arg(p)
    p.add_argument("--name", required=True, help="Nome da campanha")
    p.add_argument("--objective", required=True,
                   help="Objetivo (OUTCOME_LEADS, OUTCOME_TRAFFIC, OUTCOME_SALES, OUTCOME_AWARENESS, OUTCOME_ENGAGEMENT)")
    p.add_argument("--status", default="PAUSED", help="Status (default: PAUSED)")
    p.add_argument("--special-ad-categories", default="NONE",
                   help="Categoria especial (NONE, EMPLOYMENT, HOUSING, CREDIT, ISSUES_ELECTIONS_POLITICS)")
    p.add_argument("--daily-budget", help="Orcamento diario em centavos (ex: 5000 = R$50)")
    p.add_argument("--lifetime-budget", help="Orcamento vitalicio em centavos")
    p.add_argument("--bid-strategy",
                   help="Estrategia de lance (LOWEST_COST_WITHOUT_CAP, LOWEST_COST_WITH_BID_CAP, COST_CAP)")
    p.add_argument("--buying-type", default="AUCTION", help="Tipo de compra (default: AUCTION)")
    p.add_argument("--start-time", help="Data/hora de inicio (ISO 8601)")
    p.add_argument("--stop-time", help="Data/hora de fim (ISO 8601)")
    p.add_argument("--spend-cap", help="Limite de gasto em centavos")
    p.add_argument("--adset-budget-sharing", type=lambda v: v.lower() == 'true', default=False,
                   help="is_adset_budget_sharing_enabled p/ campanhas ABO (default: false, padrao da Mileny)")

    # --- adset ---
    p = sub.add_parser("adset", help="Criar ad set")
    add_account_arg(p)
    p.add_argument("--name", required=True, help="Nome do ad set")
    p.add_argument("--campaign", required=True, help="ID da campanha")
    p.add_argument("--optimization-goal", required=True,
                   help="Goal (LINK_CLICKS, IMPRESSIONS, REACH, LEAD_GENERATION, OFFSITE_CONVERSIONS, LANDING_PAGE_VIEWS)")
    p.add_argument("--billing-event", default="IMPRESSIONS", help="Evento de cobranca (default: IMPRESSIONS)")
    p.add_argument("--targeting", required=True, help="Targeting como JSON string")
    p.add_argument("--status", default="PAUSED", help="Status (default: PAUSED)")
    p.add_argument("--daily-budget", help="Orcamento diario em centavos")
    p.add_argument("--lifetime-budget", help="Orcamento vitalicio em centavos")
    p.add_argument("--bid-amount", help="Valor do lance em centavos")
    p.add_argument("--bid-strategy", help="Estrategia de lance")
    p.add_argument("--start-time", help="Data/hora de inicio (ISO 8601)")
    p.add_argument("--end-time", help="Data/hora de fim (ISO 8601)")
    p.add_argument("--promoted-object", help="Objeto promovido como JSON string")
    p.add_argument("--destination-type", help="Tipo de destino")
    p.add_argument("--adset-schedule", help='Dayparting como JSON string (ex: \'[{"start_minute":660,"end_minute":1260,"days":[0],"timezone_type":"USER"}]\'). Requer lifetime_budget.')
    p.add_argument("--pacing-type", help="Pacing type (ex: day_parting) - exigido quando --adset-schedule e usado")

    # --- ad ---
    p = sub.add_parser("ad", help="Criar anuncio")
    add_account_arg(p)
    p.add_argument("--name", required=True, help="Nome do anuncio")
    p.add_argument("--adset", required=True, help="ID do ad set")
    p.add_argument("--creative", required=True, help='Creative como JSON (ex: \'{"creative_id":"123"}\')')
    p.add_argument("--status", default="PAUSED", help="Status (default: PAUSED)")
    p.add_argument("--tracking-specs", help="Tracking specs como JSON string")
    p.add_argument("--conversion-domain", help="Dominio de conversao")
    p.add_argument("--degrees-of-freedom-spec", help="Controle de format options como JSON string")

    # --- creative ---
    p = sub.add_parser("creative", help="Criar creative")
    add_account_arg(p)
    p.add_argument("--name", required=True, help="Nome do creative")
    p.add_argument("--instagram-user-id", help="ID da conta Instagram (obrigatorio para ads no Instagram)")
    p.add_argument("--source-ig-media-id", help="ID de post orgânico do Instagram para usar como criativo (obtido via read.py instagram-posts)")
    p.add_argument("--object-story-spec", help="Object story spec como JSON string")
    p.add_argument("--asset-feed-spec", help="Asset feed spec como JSON string")
    p.add_argument("--url-tags", help="URL tags para tracking")
    p.add_argument("--call-to-action-type",
                   help="CTA (LEARN_MORE, SHOP_NOW, SIGN_UP, DOWNLOAD, GET_OFFER, SUBSCRIBE)")
    p.add_argument("--image-hash", help="Hash da imagem")
    p.add_argument("--image-url", help="URL da imagem")
    p.add_argument("--video-id", help="ID do video")
    p.add_argument("--link-url", help="URL do link")
    p.add_argument("--title", help="Titulo do creative")
    p.add_argument("--body", help="Texto do corpo")

    # --- image ---
    p = sub.add_parser("image", help="Upload de imagem")
    add_account_arg(p)
    grp = p.add_mutually_exclusive_group(required=True)
    grp.add_argument("--url", help="URL da imagem para upload")
    grp.add_argument("--file", help="Caminho local da imagem (ex: C:\\criativos\\img.jpg)")
    p.add_argument("--name", help="Nome da imagem")

    # --- video ---
    p = sub.add_parser("video", help="Upload de video")
    add_account_arg(p)
    grp = p.add_mutually_exclusive_group(required=True)
    grp.add_argument("--url", help="URL do video para upload")
    grp.add_argument("--file", help="Caminho local do video (ex: C:\\criativos\\vid.mp4)")
    p.add_argument("--name", help="Nome do video")
    p.add_argument("--title", help="Titulo do video")
    p.add_argument("--description", help="Descricao do video")

    # --- custom-audience ---
    p = sub.add_parser("custom-audience", help="Criar custom audience")
    add_account_arg(p)
    p.add_argument("--name", required=True, help="Nome da audiencia")
    p.add_argument("--subtype", default="CUSTOM", help="Subtipo (default: CUSTOM)")
    p.add_argument("--description", help="Descricao da audiencia")
    p.add_argument("--customer-file-source",
                   help="Fonte (USER_PROVIDED_ONLY, PARTNER_PROVIDED_ONLY, BOTH_USER_AND_PARTNER_PROVIDED)")

    # --- video-audience ---
    p = sub.add_parser("video-audience", help="Criar público de engajamento com vídeo")
    add_account_arg(p)
    p.add_argument("--name", required=True, help="Nome da audiência")
    p.add_argument("--video-ids",
                   help="IDs de vídeos avulsos separados por vírgula (obter via read.py videos --account act_XXX)")
    p.add_argument("--page-ids",
                   help="IDs de páginas do Facebook separados por vírgula — captura views de todos os vídeos da página")
    p.add_argument("--ig-ids",
                   help="IDs de contas Instagram Business separados por vírgula — captura views de todos os vídeos do IG")
    p.add_argument("--percentage", type=int, default=75, choices=[25, 50, 75, 95],
                   help="Percentual assistido: 25, 50, 75 ou 95 (default: 75)")
    p.add_argument("--retention-days", type=int, default=30,
                   help="Dias de retenção na audiência, máx 365 (default: 30)")
    p.add_argument("--description", help="Descrição opcional")
    p.set_defaults(func=cmd_video_audience)

    # --- lookalike ---
    p = sub.add_parser("lookalike", help="Criar lookalike audience")
    add_account_arg(p)
    p.add_argument("--name", required=True, help="Nome da audiencia")
    p.add_argument("--source", required=True, help="ID da audiencia de origem")
    p.add_argument("--spec", required=True, help='Spec como JSON (ex: \'{"country":"BR","ratio":0.01}\')')

    args = parser.parse_args()

    commands = {
        'campaign': cmd_campaign,
        'adset': cmd_adset,
        'ad': cmd_ad,
        'creative': cmd_creative,
        'image': cmd_image,
        'video': cmd_video,
        'custom-audience': cmd_custom_audience,
        'video-audience': cmd_video_audience,
        'lookalike': cmd_lookalike,
    }

    fn = commands.get(args.command)
    if fn:
        fn(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
