import json
from pprint import pprint

from flask import Flask, render_template, redirect, request, make_response, session, abort, jsonify, url_for
import weapons_resources
from data import db_session
from data.users import User
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


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


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
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


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
    return render_template("weapons.html", new_weapon=weapons, fav=fav)


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


@app.route('/')
def index():
    return redirect('/weapons')


@app.route('/new_weapon', methods=['GET', 'POST'])
@login_required
def add_weapons():
    form = WeaponsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        weapons = Weapons()
        weapons.title = form.title.data
        weapons.content = form.content.data
        weapons.is_private = form.is_private.data
        current_user.weapons.append(weapons)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/weapons')
    return render_template('new_weapon.html', title='Добавление оружия',
                           form=form)


@app.route('/weapon/<clas>/<name>')
@app.route('/weapon/<name>')
def weapon(name, clas=None):
    img_url = ''
    if not clas:
        path = None
        with open('map.json', 'r', encoding='UTF-8') as f:
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

    else:
        with open(f'value/items/weapon/{clas}/{name}.json', 'r', encoding="UTF-8") as f:
            diction = json.load(f)
    return render_template('weapon_info.html', dict=diction, img_url=img_url)


@app.route('/class_of_weapon/<clas>')
def ret_class_of_weapon(clas):
    with open('map.json', 'r', encoding='UTF-8') as f:
        tmp_dict = json.load(f)
    sp_of_a = []
    for elem in tmp_dict.values():
        if elem['paths']['json'].split("/")[-2] == clas:
            sp_of_a.append(
                {'name': elem['additional_key'], 'href': '/weapon/' + elem['paths']['json'].split('/')[-2:][0] + '/' + elem['paths']['json'].split('/')[-2:][1].split('.')[0]})
    return render_template('weapon_group.html', sp=sp_of_a)


@app.route('/new_weapon/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_weapons(id):
    form = WeaponsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        weapons = db_sess.query(Weapons).filter(Weapons.id == id,
                                                Weapons.user == current_user
                                                ).first()
        if weapons:
            form.title.data = weapons.title
            form.content.data = weapons.content
            form.is_private.data = weapons.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        weapons = db_sess.query(Weapons).filter(Weapons.id == id,
                                                Weapons.user == current_user
                                                ).first()
        if weapons:
            weapons.title = form.title.data
            weapons.content = form.content.data
            weapons.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/weapons')
        else:
            abort(404)
    return render_template('new_weapon.html',
                           title='Редактирование новости',
                           form=form
                           )


@app.route('/weapons_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def weapons_delete(id):
    db_sess = db_session.create_session()
    weapons = db_sess.query(Weapons).filter(Weapons.id == id,
                                            Weapons.user == current_user
                                            ).first()
    if weapons:
        db_sess.delete(weapons)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/weapons')


@app.route('/new_armor', methods=['GET', 'POST'])
@login_required
def add_armor():
    form = ArmorForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        armor = Armor()
        armor.title = form.title.data
        armor.content = form.content.data
        armor.is_private = form.is_private.data
        current_user.armor.append(armor)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/armor')
    return render_template('new_armor.html', title='Добавление брони',
                           form=form)


@app.route('/new_armor/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_armor(id):
    form = ArmorForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        armor = db_sess.query(Armor).filter(Armor.id == id,
                                            Armor.user == current_user
                                            ).first()
        if armor:
            form.title.data = armor.title
            form.content.data = armor.content
            form.is_private.data = armor.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        armor = db_sess.query(Armor).filter(Armor.id == id,
                                            Armor.user == current_user
                                            ).first()
        if armor:
            armor.title = form.title.data
            armor.content = form.content.data
            armor.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/armor')
        else:
            abort(404)
    return render_template('new_armor.html',
                           title='Редактирование новости',
                           form=form
                           )


@app.route('/armor_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def armor_delete(id):
    db_sess = db_session.create_session()
    armor = db_sess.query(Armor).filter(Armor.id == id,
                                        Armor.user == current_user
                                        ).first()
    if armor:
        db_sess.delete(armor)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/armor')


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
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


def main():
    db_session.global_init("db/blogs.db")
    # api.add_resource(weapons_resources.WeaponsListResource, '/api/v2/weapons')
    # api.add_resource(weapons_resources.WeaponsResource, '/api/v2/weapons/<int:weapons_id>')
    app.run()


if __name__ == '__main__':
    main()
