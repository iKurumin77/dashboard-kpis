import json
p='locales/es.json'
try:
    s=open(p,'r',encoding='utf-8').read()
    json.loads(s)
    print('OK')
except Exception as e:
    print('ERR', e)
