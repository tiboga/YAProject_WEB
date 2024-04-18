import json
import os
import pprint
import traceback

sp = []
for root, dirs, files in os.walk(
        'stalcraft-database-main\\ru\\items\\weapon'):
    for file in files:
        if file.endswith('.json'):
            sp.append('/'.join((os.path.join(root, file)).split('\\')))
sp = list(filter(lambda x: len(x.split('/')) == len(sp[0].split('/')), sp))
language = 'ru'
for e in sp:
    print(e)
    with open(e, 'r', encoding="UTF-8") as f:
        original_diction = json.load(f)
    try:
        name = original_diction['name']['lines']['ru']
        info = []
        if not os.path.isdir('./value'):
            os.mkdir('./value')
            print(True)
        for elem in original_diction['infoBlocks']:
            if elem['type'] == 'list':
                tmp_diction = elem['elements']
            elif elem['type'] == 'text':
                tmp_diction = [elem['text']]
            else:
                tmp_diction = []
            if tmp_diction:
                out_sp = []
                for tmp in tmp_diction:
                    if tmp['type'] == 'key-value':
                        out_sp.append(
                            {'key': tmp['key']['lines'][language], 'value': tmp['value']['lines'][language]})
                    elif tmp['type'] == 'numeric':
                        out_sp.append(
                            {'key': tmp['name']['lines'][language], 'value': tmp['formatted']['value'][language]})
                    elif tmp['type'] == 'translation':
                        out_sp.append(
                            {'key': 'description',
                             'value': tmp['lines'][language]})
                info.extend(out_sp)
        out_diction = {'name': name, 'info': info}
        path = '/'.join(e.split('/')[-4:])
        for i in range(1, 4):
            tmp_path = './value/' + '/'.join(path.split('/')[:i])
            if not (os.path.isdir(tmp_path)):
                os.mkdir(tmp_path)
        with open(f"./value/{path}", 'w', encoding='UTF-8') as f:
            json.dump(out_diction, f, ensure_ascii=False)
    except:
        print(e, traceback.format_exc())
        n = input()
