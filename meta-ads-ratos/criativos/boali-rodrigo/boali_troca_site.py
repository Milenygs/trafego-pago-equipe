"""Boali 14/10: troca os publicos WEBSITE do pixel morto 623640363239234 pelos do pixel 4253291668254806.
Uso: python boali_troca_site.py validar|aplicar"""
import os, sys, json, copy, time
sys.path.insert(0, os.path.join(os.path.expanduser('~'), 'OneDrive', '.claude', 'skills', 'meta-ads-ratos', 'scripts'))
from lib import init_api
from facebook_business.adobjects.adset import AdSet
from facebook_business.exceptions import FacebookRequestError
init_api()
TROCA = {'120207589325560156': '120251732878670156',   # PageView 90DD -> SITE FRANQUIA 180D
         '120236761297380156': '120251732878670156',   # Vistou Site Franquia -> SITE FRANQUIA 180D
         '120237818661500156': '120251732879750156'}   # CADASTRO REALIZADO -> CRM TODOS OS LEADS 180D
SETS = ['120251313225380156','120250112177130156','120250111279470156','120249976014280156','120249949945780156','120249949929600156']
modo = sys.argv[1]
antes = {}
for sid in SETS:
    d = AdSet(sid).api_get(fields=['name','targeting']).export_all_data(); antes[sid] = d
    t = copy.deepcopy(d['targeting']); t.pop('targeting_optimization', None)
    for campo in ('custom_audiences', 'excluded_custom_audiences'):
        if campo not in t: continue
        novo, vistos = [], set()
        for x in t[campo]:
            i = TROCA.get(x['id'], x['id'])
            if i not in vistos: novo.append({'id': i}); vistos.add(i)
        t[campo] = novo
    p = {'targeting': t}
    if modo == 'validar': p['execution_options'] = ['validate_only']
    try:
        AdSet(sid).api_update(params=p); print(modo, 'OK', sid, d['name'][:50])
    except FacebookRequestError as e:
        print(modo, 'ERRO', sid, e.api_error_code(), e.api_error_subcode(), (e.body().get('error', {}).get('error_user_msg') or e.api_error_message())[:250])
    time.sleep(1.5 if modo == 'aplicar' else 0.7)
if modo == 'aplicar':
    json.dump(antes, open('boali_troca_site_antes_2026-10-14.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
