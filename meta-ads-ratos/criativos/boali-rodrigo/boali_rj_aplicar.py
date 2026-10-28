"""Boali 08/10: excluir a cidade do Rio de Janeiro (267027) dos conjuntos CP 01-CP 10.
Uso: python boali_rj_aplicar.py validar|aplicar|conferir"""
import os, sys, json, copy, re, time
sys.path.insert(0, os.path.join(os.path.expanduser('~'), 'OneDrive', '.claude', 'skills', 'meta-ads-ratos', 'scripts'))
from lib import init_api
from facebook_business.adobjects.adset import AdSet
from facebook_business.exceptions import FacebookRequestError

HERE = os.path.dirname(os.path.abspath(__file__))
RJ = '267027'
modo = sys.argv[1]

rows = json.load(open(os.path.join(HERE, 'boali_rj_antes.json'), encoding='utf-8'))


def no_escopo(r):
    camp = r['campaign']['name'] if 'campaign' in r else ''
    if not re.match(r'^CP (0[1-9]|10) ', camp):
        return False
    geo = r['targeting'].get('geo_locations', {})
    so_pinos = geo.get('custom_locations') and not (geo.get('countries') or geo.get('regions') or geo.get('cities'))
    return not so_pinos


alvo = [r for r in rows if no_escopo(r)]
init_api()
res = []
for r in alvo:
    exc_atual = r['targeting'].get('excluded_geo_locations', {})
    if any(c['key'] == RJ for c in exc_atual.get('cities', [])):
        res.append((r['id'], r['name'][:55], 'JA_TINHA'))
        continue
    if modo == 'conferir':
        t = AdSet(r['id']).api_get(fields=['targeting'])['targeting']
        exc = t.get('excluded_geo_locations', {}) if isinstance(t, dict) else t.export_all_data().get('excluded_geo_locations', {})
        ok = any(c['key'] == RJ for c in exc.get('cities', []))
        regs = [x['key'] for x in exc.get('regions', [])]
        res.append((r['id'], r['name'][:55], 'RJ_OK' if ok else 'RJ_FALTANDO', 'regioes=' + ','.join(regs)))
        time.sleep(0.5)
        continue
    # targeting AO VIVO (o JSON de 08/10 so define o escopo; nao sobrescrever mudancas feitas depois)
    t = AdSet(r['id']).api_get(fields=['targeting'])['targeting']
    t = copy.deepcopy(t if isinstance(t, dict) else t.export_all_data())
    if any(c['key'] == RJ for c in t.get('excluded_geo_locations', {}).get('cities', [])):
        res.append((r['id'], r['name'][:55], 'JA_TINHA'))
        continue
    t.pop('targeting_optimization', None)
    exc = t.setdefault('excluded_geo_locations', {})
    exc.setdefault('cities', []).append({'key': RJ})
    params = {'targeting': t}
    if modo == 'validar':
        params['execution_options'] = ['validate_only']
    try:
        AdSet(r['id']).api_update(params=params)
        res.append((r['id'], r['name'][:55], 'OK'))
    except FacebookRequestError as e:
        res.append((r['id'], r['name'][:55], 'ERRO %s/%s %s' % (e.api_error_code(), e.api_error_subcode(),
                                                               (e.body().get('error', {}).get('error_user_msg') or e.api_error_message())[:160])))
    time.sleep(1.5 if modo == 'aplicar' else 0.5)

for x in res:
    print(' | '.join(x))
print('conjuntos no escopo:', len(alvo))
json.dump(res, open(os.path.join(HERE, 'boali_rj_%s.json' % modo), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
