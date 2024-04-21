import json
import math
from pprint import pprint

from flask import Flask, render_template, redirect, request, make_response, session, abort, jsonify, url_for
import weapons_resources
from data import db_session
from data.users import User
from data.comment_model import Comment
from forms.comment import AddComment
from data.weapons import Weapons
from forms.weapons import WeaponsForm
from data.armor import Armor
from forms.armor import ArmorForm
from forms.user import RegisterForm
from forms.user import LoginForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)

Previous_page = '/'


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/add_comment", methods=['GET', 'POST'])
def add_comment():
    form = AddComment()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        comment = Comment()
        comment.comment_text = form.text.data
        comment.state_of_comment = Previous_page
        db_sess.add(comment)
        db_sess.commit()
        return redirect(Previous_page)
    if current_user.is_authenticated:

        return render_template('add_comment.html', title='Добавление комментария', form=form, need_comment=False)
    else:
        return render_template("for_noauthorised_users.html", need_comment=False)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/weapons")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form, need_comment=False)
    return render_template('login.html', title='Авторизация', form=form, need_comment=False)


@app.route("/cookie_test")
def cookie_test():
    visits_count = int(request.cookies.get("visits_count", 0))
    if visits_count:
        res = make_response(
            f"Вы пришли на эту страницу {visits_count + 1} раз")
        res.set_cookie("visits_count", str(visits_count + 1),
                       max_age=60 * 60 * 24 * 365 * 2)
    else:
        res = make_response(
            "Вы пришли на эту страницу в первый раз за последние 2 года")
        res.set_cookie("visits_count", '1',
                       max_age=60 * 60 * 24 * 365 * 2)
    return res


@app.route('/weapons/<int:id>', methods=['GET', 'POST'])
@app.route('/weapons/<fav>', methods=['GET', 'POST'])
@app.route('/weapons')
def weapons(id=0, fav=False):
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        if fav == "favourite":
            weapons = db_sess.query(Weapons).filter(
                ((Weapons.user == current_user) | (Weapons.is_private != True)) & (Weapons.favourite == 0))
        else:
            weapons = db_sess.query(Weapons).filter(
                (Weapons.user == current_user) | (Weapons.is_private != True))
    else:
        weapons = db_sess.query(Weapons).filter(Weapons.is_private != True)
    if id != 0:
        weapon1 = db_sess.query(Weapons).filter(Weapons.id == id,
                                                Weapons.user == current_user
                                                ).first()
        if weapon1:
            if weapon1.favourite == 0:
                weapon1.favourite = 1
            else:
                weapon1.favourite = 0
            db_sess.commit()
        else:
            abort(404)
        return redirect("/weapons")
    return render_template("weapons.html", new_weapon=weapons, fav=fav, need_comment=False)


"""
@app.route('/armor/<int:id>', methods=['GET', 'POST'])
@app.route('/armor/<fav>', methods=['GET', 'POST'])
@app.route('/armor')
def armor(id=0, fav=False):
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        if fav == "favourite":
            armor = db_sess.query(Armor).filter(
                ((Armor.user == current_user) | (Armor.is_private != True)) & (Armor.favourite == 0))
        else:
            armor = db_sess.query(Armor).filter(
                (Armor.user == current_user) | (Armor.is_private != True))
    else:
        armor = db_sess.query(Armor).filter(Armor.is_private != True)
    if id != 0:
        armor1 = db_sess.query(Armor).filter(Armor.id == id,
                                             Armor.user == current_user
                                             ).first()
        if armor1:
            if armor1.favourite == 0:
                armor1.favourite = 1
            else:
                armor1.favourite = 0
            db_sess.commit()
        else:
            abort(404)
        return redirect("/armor")
    return render_template("armor.html", new_armor=armor, fav=fav)
"""


@app.route('/')
def index():
    return redirect('/weapons')


@app.route('/weapon/<clas>/<name>')
@app.route('/weapon/<name>')
def weapon(name, clas=None):
    global Previous_page
    img_url = ''
    comments = []
    if not clas:
        Previous_page = f'/weapon/{name}'
        path = None
        with open('maps/map.json', 'r', encoding='UTF-8') as f:
            tmp_dict = json.load(f)
        if name in tmp_dict.keys():
            path = tmp_dict[name]['paths']['json']
        else:
            for elem in tmp_dict.values():
                if elem['additional_key'] == name:
                    path = elem['paths']['json']
                    img_url = elem['paths']['image']
            if path:
                with open(path, 'r', encoding="UTF-8") as f:
                    diction = json.load(f)
        db_sess = db_session.create_session()
        comments = db_sess.query(Comment).filter(Comment.state_of_comment == f'/weapon/{name}').all()

    else:
        Previous_page = f'/weapon/{clas}/{name}'
        with open(f'value/items/weapon/{clas}/{name}.json', 'r', encoding="UTF-8") as f:
            diction = json.load(f)
        img_url = f'/static/value/icons/weapon/{clas}/{name}.png'
        db_sess = db_session.create_session()
        comments = db_sess.query(Comment).filter(Comment.state_of_comment == f'/weapon/{clas}/{name}').all()
    return render_template('weapon_info.html', dict=diction, img_url=img_url, need_comment=True, comments=comments)


@app.route('/class_of_weapon/<clas>')
def ret_class_of_weapon(clas):
    global Previous_page
    Previous_page = f'/class_of_weapon/{clas}'
    with open('maps/map.json', 'r', encoding='UTF-8') as f:
        tmp_dict = json.load(f)
    sp_of_a = []
    for elem in tmp_dict.values():
        if elem['paths']['json'].split("/")[-2] == clas:
            sp_of_a.append(
                {'name': elem['additional_key'], 'href': '/weapon/' + elem['paths']['json'].split('/')[-2:][0] + '/' +
                                                         elem['paths']['json'].split('/')[-2:][1].split('.')[0],
                 "img": elem["paths"]['image']})
    len_line = math.ceil(len(sp_of_a) / 4)
    html_code = '<table>' + ''.join(["<tr>" + ''.join(['' if (j * 4 + i) > len(
        sp_of_a) - 1 else f"<th><ul><li><a href='{sp_of_a[j * 4 + i]['href']}'>{sp_of_a[j * 4 + i]['name']}</a></li><li><a href='{sp_of_a[j * 4 + i]['href']}' ><img src='{sp_of_a[j * 4 + i]['img']}'></a></li></ul></th>"
                                                       for i in range(4)]) + '</tr>' for j in
                                     range(len_line)]) + '</table>'
    db_sess = db_session.create_session()
    comments = db_sess.query(Comment).filter(Comment.state_of_comment == f'/class_of_weapon/{clas}').all()
    return render_template('weapon_group.html', elem=html_code, need_comment=True, comments=comments)


@app.route('/all_weapons')
def all_weapons():
    global Previous_page
    Previous_page = f'/all_weapons'
    translate_dict = {'Отмычка': 1,
                      'Новичок': 2,
                      'Сталкер': 3,
                      'Ветеран': 4,
                      'Мастер': 5,
                      'Легенда': 6,
                      'Just': 7}
    with open('maps/map.json', 'r', encoding='UTF-8') as f:
        tmp_dict = json.load(f)

    with open('maps/color_map.json', 'r', encoding='UTF-8') as f:
        color_map = json.load(f)
    with open('maps/names.json', 'r', encoding='UTF-8') as f:
        name_map = json.load(f)
    dict_with_classes = {'Пистолеты': {1: [],
                                       2: [],
                                       3: [],
                                       4: [],
                                       5: [],
                                       6: [],
                                       7: []},
                         'Пистолеты-пулеметы': {1: [],
                                                2: [],
                                                3: [],
                                                4: [],
                                                5: [],
                                                6: [],
                                                7: []},
                         'Автоматы': {1: [],
                                      2: [],
                                      3: [],
                                      4: [],
                                      5: [],
                                      6: [],
                                      7: []},
                         'Дробовики и ружья': {1: [],
                                               2: [],
                                               3: [],
                                               4: [],
                                               5: [],
                                               6: [],
                                               7: []},
                         'Устройства': {1: [],
                                        2: [],
                                        3: [],
                                        4: [],
                                        5: [],
                                        6: [],
                                        7: []},
                         'Ближний бой': {1: [],
                                         2: [],
                                         3: [],
                                         4: [],
                                         5: [],
                                         6: [],
                                         7: []},
                         'Прочее вооружение': {1: [],
                                               2: [],
                                               3: [],
                                               4: [],
                                               5: [],
                                               6: [],
                                               7: []},
                         'Пулеметы': {1: [],
                                      2: [],
                                      3: [],
                                      4: [],
                                      5: [],
                                      6: [],
                                      7: []},
                         'Снайперские винтовки': {1: [],
                                                  2: [],
                                                  3: [],
                                                  4: [],
                                                  5: [],
                                                  6: [],
                                                  7: []}}
    for elem in tmp_dict.values():
        # if elem['paths']['json'].split("/")[-2] == '':
        with open(elem['paths']['json'], 'r', encoding="UTF-8") as dict_f:
            e = json.load(dict_f)
            rank = list(filter(lambda x: x['key'] == 'Ранг', e['info']))
            clas = list(filter(lambda x: x['key'] == 'Класс', e['info']))
            if not rank:
                rank = {'value': 'Just'}
            else:
                rank = rank[0]
        dict_with_classes[clas[0]['value']][translate_dict[rank['value']]].append(
            {'name': elem['additional_key'],
             'href': '/weapon/' + elem['paths']['json'].split('/')[-2:][0] + '/' +
                     elem['paths']['json'].split('/')[-2:][1].split('.')[0]})
    html_code = ''
    for key in dict_with_classes.keys():
        html_code += f"""<p></p><table>
                            <tr>
                                <th>
                                    <div class="info_box">
                                        <h3><a style="color: #4ad94b" href="/class_of_weapon/{name_map[key]}">{key}</a></h3>
                                    </div>
                                </th>
                            </tr>
                            <tr>"""
        for into_key, into_values in dict_with_classes[key].items():
            html_code += f'''<tr>
                                <th>
                                    <div class="info_box">'''
            for href_and_name in into_values:
                if into_values.index(href_and_name) == len(into_values) - 1:
                    html_code += f'''<a style="color: {color_map[str(into_key)]}" href="{href_and_name['href']}">{href_and_name['name']}</a>'''
                else:
                    html_code += f'''<a style="color: {color_map[str(into_key)]}" href="{href_and_name['href']}">{href_and_name['name']}</a><a style="color: #ffffff"> • </a>'''
            html_code += '''      </div>
                                    </th>
                                </tr>
                                    '''
        html_code += '</table>'
    db_sess = db_session.create_session()
    comments = db_sess.query(Comment).filter(Comment.state_of_comment == '/all_weapons').all()
    return render_template('all_weapons.html', html_code=html_code, need_comment=True, comments=comments)


@app.route('/all_armor')
def all_armor():
    translate_dict = {'Отмычка': 1,
                      'Новичок': 2,
                      'Сталкер': 3,
                      'Ветеран': 4,
                      'Мастер': 5,
                      'Легенда': 6,
                      'Just': 7,
                      "Устройства": 8}
    with open('maps/map_armor.json', 'r', encoding='UTF-8') as f:
        tmp_dict = json.load(f)

    with open('maps/color_map.json', 'r', encoding='UTF-8') as f:
        color_map = json.load(f)
    with open('maps/names_armor.json', 'r', encoding='UTF-8') as f:
        name_map = json.load(f)
    dict_with_classes = {'Одежда': {1: [],
                                    2: [],
                                    3: [],
                                    4: [],
                                    5: [],
                                    6: [],
                                    7: [],
                                    8: []
                                    },
                         'Боевые': {1: [],
                                    2: [],
                                    3: [],
                                    4: [],
                                    5: [],
                                    6: [],
                                    7: [],
                                    8: []
                                    },
                         'Комбинированные': {1: [],
                                             2: [],
                                             3: [],
                                             4: [],
                                             5: [],
                                             6: [],
                                             7: [],
                                             8: []
                                             },
                         'Устройства': {1: [],
                                        2: [],
                                        3: [],
                                        4: [],
                                        5: [],
                                        6: [],
                                        7: [],
                                        8: []
                                        },
                         'Научные': {1: [],
                                     2: [],
                                     3: [],
                                     4: [],
                                     5: [],
                                     6: [],
                                     7: [],
                                     8: []
                                     }}
    for elem in tmp_dict.values():
        # if elem['paths']['json'].split("/")[-2] == '':
        with open(elem['paths']['json'], 'r', encoding="UTF-8") as dict_f:
            e = json.load(dict_f)
            rank = list(filter(lambda x: x['key'] == 'Ранг', e['info']))
            clas = list(filter(lambda x: x['key'] == 'Класс', e['info']))
            if not rank:
                rank = {'value': 'Just'}
            else:
                rank = rank[0]
        dict_with_classes[clas[0]['value']][translate_dict[rank['value']]].append(
            {'name': elem['additional_key'],
             'href': '/armor/' + elem['paths']['json'].split('/')[-2:][0] + '/' +
                     elem['paths']['json'].split('/')[-2:][1].split('.')[0]})
    pprint(dict_with_classes)
    html_code = ''
    for key in dict_with_classes.keys():
        print(name_map[key])
        html_code += f"""<table>
                            <tr>
                                <th>
                                    <div class="info_box">
                                        <h2 style="color: #4ad94b" href="/class_of_armor/{name_map[key]}">{key}</h2>
                                    </div>
                                </th>
                            </tr>
                            <tr>"""
        for into_key, into_values in dict_with_classes[key].items():
            html_code += f'''<tr>
                                <th>
                                    <div class="info_box">'''
            for href_and_name in into_values:
                html_code += f'''<a style="color: {color_map[str(into_key)]}" href="{href_and_name['href']}">{href_and_name['name']} </a>'''
            html_code += '''      </div>
                                    </th>
                                </tr>
                                    '''
        html_code += '</table>'

    return render_template('all_armor.html', html_code=html_code)


@app.route('/armor/<clas>/<name>')
@app.route('/armor/<name>')
def armor(name, clas=None):
    global Previous_page
    img_url = ''
    if not clas:

        Previous_page = f'/armor/{name}'
        path = None
        with open('maps/map_armor.json', 'r', encoding='UTF-8') as f:
            tmp_dict = json.load(f)
        if name in tmp_dict.keys():
            path = tmp_dict[name]['paths']['json']
        else:
            for elem in tmp_dict.values():
                if elem['additional_key'] == name:
                    path = elem['paths']['json']
                    img_url = elem['paths']['image']
            if path:
                with open(path, 'r', encoding="UTF-8") as f:
                    diction = json.load(f)
        db_sess = db_session.create_session()
        comments = db_sess.query(Comment).filter(Comment.state_of_comment == f'/armor/{name}').all()
    else:
        Previous_page = f'/armor/{clas}/{name}'
        with open(f'value/items/armor/{clas}/{name}.json', 'r', encoding="UTF-8") as f:
            diction = json.load(f)
        img_url = f'/static/value/icons/armor/{clas}/{name}.png'
        db_sess = db_session.create_session()
        comments = db_sess.query(Comment).filter(Comment.state_of_comment == f'/armor/{clas}/{name}').all()
    return render_template('armor_info.html', dict=diction, img_url=img_url, need_comment=True, comments=comments)


@app.route('/class_of_armor/<clas>/<fav>')
@app.route('/class_of_armor/<clas>')
def ret_class_of_armor(clas, fav=None):
    global Previous_page
    Previous_page = f'/class_of_armor/{clas}'
    db_sess = db_session.create_session()
    with open('maps/map_armor.json', 'r', encoding='UTF-8') as f:
        tmp_dict = json.load(f)
    sp_of_a = []
    armor = db_sess.query(Armor).filter(Armor.user == current_user
                                            ).first()
    items_in_armor = ""
    if armor:
        items_in_armor = f"{armor.clothes}, {armor.combat}, {armor.combined}, {armor.device}, {armor.scientist}"
    if not fav:
        for elem in tmp_dict.values():
            if elem['paths']['json'].split("/")[-2] == clas:
                sp_of_a.append(
                    {'name': elem['additional_key'],
                     'href': '/armor/' + elem['paths']['json'].split('/')[-2:][0] + '/' +
                             elem['paths']['json'].split('/')[-2:][1].split('.')[0],
                     "img": elem["paths"]['image']})
    else:
        if armor:
            if clas == 'clothes':
                if fav not in str(armor.clothes):
                    armor.clothes = f'{armor.clothes}, {fav}'
                else:
                    armor.clothes = armor.clothes.replace(f", {fav}", "")
            elif clas == 'combat':
                if fav not in str(armor.combat):
                    armor.combat = f'{armor.combat}, {fav}'
                else:
                    armor.combat = armor.combat.replace(f", {fav}", "")
            elif clas == 'combined':
                if fav not in str(armor.combined):
                    armor.combined = f'{armor.combined}, {fav}'
                else:
                    armor.combined = armor.combined.replace(f", {fav}", "")
            elif clas == 'device':
                if fav not in str(armor.device):
                    armor.device = f'{armor.device}, {fav}'
                else:
                    armor.device = armor.device.replace(f", {fav}", "")
            elif clas == 'scientist':
                if fav not in str(armor.scientist):
                    armor.scientist = f'{armor.scientist}, {fav}'
                else:
                    armor.scientist = armor.scientist.replace(f", {fav}", "")
            db_sess.commit()

            return redirect(f"/class_of_armor/{clas}")
        else:
            armor1 = Armor()
            current_user.armor.append(armor1)
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect(f"/class_of_armor/{clas}/{fav}")
    db_sess = db_session.create_session()
    comments = db_sess.query(Comment).filter(Comment.state_of_comment == f'/class_of_armor/{clas}').all()
    return render_template('armor_group.html', sp=sp_of_a, clas=clas, items_in_armor=items_in_armor, need_comment=True, comments=comments)

@app.route("/session_test")
def session_test():
    visits_count = session.get('visits_count', 0)
    session['visits_count'] = visits_count + 1
    return make_response(
        f"Вы пришли на эту страницу {visits_count + 1} раз")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/weapons")


@app.route('/register', methods=['GET', 'POST'])
def register():
    global Previous_page
    Previous_page = f'/register'
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают", need_comment=False)
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть", need_comment=False)
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form, need_comment=False)


def main():
    global Previous_page
    db_session.global_init("db/blogs.db")
    Previous_page = '/'
    # api.add_resource(weapons_resources.WeaponsListResource, '/api/v2/weapons')
    # api.add_resource(weapons_resources.WeaponsResource, '/api/v2/weapons/<int:weapons_id>')
    app.run()


if __name__ == '__main__':
    Previous_page = '/'
    main()
