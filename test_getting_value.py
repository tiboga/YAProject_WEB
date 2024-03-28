import json
import os
import traceback
from pprint import pprint

sp = []
for root, dirs, files in os.walk('D:\\PythonProjects\\YAProject_WEB\\stalcraft-database-main\\ru\\items\\weapon'):
    for file in files:
        if file.endswith('.json'):
            sp.append('/'.join((os.path.join(root, file)).split('\\')))
language = 'ru'
for e in sp:
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
        additional_characteristic_info = diction['infoBlocks'][3]['elements']
        damage_info = diction['infoBlocks'][4]['elements']
        description = {'key': 'Краткое описание', 'value': diction['infoBlocks'][-1]['text']['lines'][language]}
        out_main_info = []
        out_additional_info = []
        out_additional_characteristic_info = []
        out_damage_info = []
        for elem in main_info:
            if elem['type'] == 'key-value':
                out_main_info.append({'key': elem['key']['lines'][language], 'value': elem['value']['lines'][language]})
            else:
                out_main_info.append({'key': elem['name']['lines'][language], 'value': elem['formatted']['value'][language]})
        for elem in additional_info:
            if elem['type'] == 'key-value':
                out_additional_info.append({'key': elem['key']['lines'][language], 'value': elem['value']['lines'][language]})
            else:
                out_additional_info.append(
                    {'key': elem['name']['lines'][language], 'value': elem['formatted']['value'][language]})
        for elem in additional_characteristic_info:
            if elem['type'] == 'key-value':
                out_additional_characteristic_info.append(
                    {'key': elem['key']['lines'][language], 'value': elem['value']['lines'][language]})
            else:
                out_additional_characteristic_info.append(
                    {'key': elem['name']['lines'][language], 'value': elem['formatted']['value'][language]})
        for elem in damage_info:
            if elem['type'] == 'key-value':
                out_damage_info.append({'key': elem['key']['lines'][language], 'value': elem['value']['lines'][language]})
            elif elem['type'] == 'numeric':
                out_damage_info.append({'key': elem['name']['lines'][language], 'value': elem['formatted']['value'][language]})
            elif elem['type'] == 'text':
                out_damage_info.append(
                    {'key': elem['text']['lines'][language].split(':')[0], 'value': elem['text']['lines'][language]})
        out_diction = {'Основная информация': out_main_info, 'Дополнительная информация': out_additional_info,
                       'Характеристики': out_additional_characteristic_info, 'Информация об уроне': out_damage_info,
                       'Описание': description}
        with open(f"{''.join(e.split('/')[4:-1])}", 'w') as f:
            json.dump(out_diction, f, ensure_ascii=False)
    except:
        print(e, traceback.format_exc())
        n = input()