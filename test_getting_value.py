import json
import os
import traceback
from pprint import pprint

sp = []
for root, dirs, files in os.walk(
        'E:\\TIBOPF\\PycharmProjects\\YAProject_WEB\\stalcraft-database-main\\ru\\items\\weapon\\pistol'):
    for file in files:
        if file.endswith('.json'):
            sp.append('/'.join((os.path.join(root, file)).split('\\')))
sp = list(filter(lambda x: len(x.split('/')) == len(sp[0].split('/')), sp))
language = 'ru'
for e in sp:
    print(e)
    with open(e, 'r', encoding="UTF-8") as f:
        diction = json.load(f)
    try:
        name = diction['name']['lines']['ru']
        # main_info = [{'key':elem['key']['lines'][language], 'value': elem['value']['lines'][language]} for elem in list(filter(lambda x: x != [], [elem['elements'] for elem in diction['infoBlocks'] if 'elements' in elem.keys()]))[0]]
        try:
            main_info = diction['infoBlocks'][0]['elements']
        except:
            main_info = []
        try:
            additional_info = diction['infoBlocks'][2]['elements']
        except:
            additional_info = []
        try:
            additional_characteristic_info = diction['infoBlocks'][3]['elements']
        except:
            additional_characteristic_info = []
        try:
            damage_info = diction['infoBlocks'][4]['elements']
        except:
            damage_info = []
        try:
            description = {'key': 'Краткое описание', 'value': diction['infoBlocks'][-1]['text']['lines'][language]}
        except:
            description = {}
        out_main_info = []
        out_additional_info = []
        out_additional_characteristic_info = []
        out_damage_info = []
        for elem in main_info:
            if elem['type'] == 'key-value':
                out_main_info.append({'key': elem['key']['lines'][language], 'value': elem['value']['lines'][language]})
            elif elem['type'] == 'numeric':
                out_main_info.append(
                    {'key': elem['name']['lines'][language], 'value': elem['formatted']['value'][language]})
        for elem in additional_info:
            if elem['type'] == 'key-value':
                out_additional_info.append(
                    {'key': elem['key']['lines'][language], 'value': elem['value']['lines'][language]})
            elif elem['type'] == 'numeric':
                out_additional_info.append(
                    {'key': elem['name']['lines'][language], 'value': elem['formatted']['value'][language]})
        for elem in additional_characteristic_info:
            if elem['type'] == 'key-value':
                out_additional_characteristic_info.append(
                    {'key': elem['key']['lines'][language], 'value': elem['value']['lines'][language]})
            elif elem['type'] == 'numeric':
                out_additional_characteristic_info.append(
                    {'key': elem['name']['lines'][language], 'value': elem['formatted']['value'][language]})
        for elem in damage_info:
            if elem['type'] == 'key-value':
                out_damage_info.append(
                    {'key': elem['key']['lines'][language], 'value': elem['value']['lines'][language]})
            elif elem['type'] == 'numeric':
                out_damage_info.append(
                    {'key': elem['name']['lines'][language], 'value': elem['formatted']['value'][language]})
            elif elem['type'] == 'text':
                out_damage_info.append(
                    {'key': elem['text']['lines'][language].split(':')[0], 'value': elem['text']['lines'][language]})
        out_diction = {'Основная информация': out_main_info, 'Дополнительная информация': out_additional_info,
                       'Характеристики': out_additional_characteristic_info, 'Информация об уроне': out_damage_info,
                       'Описание': description}
        path = '/'.join(e.split('/')[-4:])
        for i in range(1, 4):
            tmp_path = '/'.join(path.split('/')[:i])
            if not(os.path.isdir(tmp_path)):
                os.mkdir(tmp_path)
        with open(f"{path}", 'w') as f:
            json.dump(out_diction, f, ensure_ascii=False)
    except:
        print(e, traceback.format_exc())
        n = input()
