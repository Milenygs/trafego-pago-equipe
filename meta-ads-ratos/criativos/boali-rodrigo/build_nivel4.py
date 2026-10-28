import os, sys, json, time
sys.path.insert(0, os.path.join(os.path.expanduser('~'), 'OneDrive', '.claude', 'skills', 'meta-ads-ratos', 'scripts'))
from lib import init_api
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.exceptions import FacebookRequestError
init_api()
acc = AdAccount('act_295475086762368')
estado = json.load(open('publico_nivel4_2026-10-14.json', encoding='utf-8'))
targeting = {
  'age_min': 30, 'age_max': 55,
  'geo_locations': {'countries': ['BR'], 'location_types': ['home', 'recent']},
  'excluded_geo_locations': {'regions': [{'key': '438'}, {'key': '441'}, {'key': '457'}, {'key': '458'}], 'cities': [{'key': '267027'}]},
  'custom_audiences': [{'id': estado['nivel4']}, {'id': estado['form_abriu']}],
  'excluded_custom_audiences': [{'id': estado['form_enviou']}, {'id': '120251445531230156'}, {'id': estado['crm_todos']}, {'id': '120251445501230156'}],
  'publisher_platforms': ['instagram'], 'instagram_positions': ['stream', 'story', 'reels', 'profile_feed', 'ig_search'],
  'device_platforms': ['mobile', 'desktop'],
  'targeting_automation': {'advantage_audience': 0},
  'targeting_relaxation_types': {'lookalike': 0, 'custom_audience': 0},
}
params = {'name': '[NIVEL 4] [VIU A OFERTA 75% + ABRIU FORM] [FORMS] 30-55', 'campaign_id': '120251445536860156',
          'daily_budget': 4000, 'billing_event': 'IMPRESSIONS', 'optimization_goal': 'LEAD_GENERATION',
          'bid_strategy': 'LOWEST_COST_WITHOUT_CAP', 'destination_type': 'ON_AD',
          'promoted_object': {'page_id': '110751468238380'}, 'targeting': targeting, 'status': 'PAUSED'}
modo = sys.argv[1] if len(sys.argv) > 1 else 'validar'
try:
    if modo == 'validar':
        r = acc.create_ad_set(params=dict(params, execution_options=['validate_only'])); print('VALIDATE OK', r.export_all_data() if hasattr(r,'export_all_data') else r)
    else:
        r = acc.create_ad_set(params=params); estado['adset'] = r['id']; print('CONJUNTO CRIADO:', r['id'])
        json.dump(estado, open('publico_nivel4_2026-10-14.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
except FacebookRequestError as e:
    print('ERRO', e.api_error_code(), e.api_error_subcode(), (e.body().get('error', {}).get('error_user_msg') or e.api_error_message())[:300])
