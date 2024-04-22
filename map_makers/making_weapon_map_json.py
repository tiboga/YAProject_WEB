import json
import os


def maker():
    sp = []
    for root, dirs, files in os.walk('../value'):
        if len(root.split('\\')) > 3:
            if root.split('\\')[2] == 'weapon':
                for file in files:
                    if file.endswith('.json') or file.endswith('.png'):
                        sp.append('/'.join((os.path.join(root, file)).split('\\')))
    sp = list(filter(lambda x: len(x.split('/')) == len(sp[0].split('/')), sp))
    out_diction = dict()

    for elem in sp:
        key = elem.split('/')[-1].split('.')[0]
        if elem.endswith('.json'):
            with open(elem, 'r', encoding="UTF-8") as f:
                dict_info = json.load(f)
        if not (key in out_diction.keys()) and elem.endswith('.json'):
            dict_of_path = dict()
            list_of_paths = list(map(lambda x: {'image': x} if x.endswith('png') else {'json': x},
                                     list(filter(lambda x: x.split('/')[-1].split('.')[0] == key, sp))))
            for e in list_of_paths:
                if list(e.keys())[0] == 'image':
                    dict_of_path['image'] = '/static/' + list(e.values())[0].replace("../", '/')
                else:
                    dict_of_path['json'] = list(e.values())[0].replace("../", '/')[1:]

            out_diction[key] = {'paths': dict_of_path,
                                'additional_key': dict_info['name']}
        with open('../maps/map.json', 'w', encoding='UTF-8') as f:
            json.dump(out_diction, f, ensure_ascii=False)
