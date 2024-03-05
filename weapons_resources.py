from flask import jsonify
from flask_restful import reqparse, abort, Resource
from data import db_session
from data.weapons import Weapons

parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('content', required=True)
parser.add_argument('is_private', required=True, type=bool)
parser.add_argument('is_published', required=True, type=bool)
parser.add_argument('user_id', required=True, type=int)


def abort_if_weapons_not_found(weapons_id):
    session = db_session.create_session()
    weapons = session.query(Weapons).get(weapons_id)
    if not weapons:
        abort(404, message=f"Weapons {weapons_id} not found")


class WeaponsResource(Resource):
    def get(self, weapons_id):
        abort_if_weapons_not_found(weapons_id)
        session = db_session.create_session()
        weapons = session.query(Weapons).get(weapons_id)
        return jsonify({'weapons': weapons.to_dict(
            only=('title', 'content', 'user_id', 'is_private'))})

    def delete(self, weapons_id):
        abort_if_weapons_not_found(weapons_id)
        session = db_session.create_session()
        weapons = session.query(Weapons).get(weapons_id)
        session.delete(weapons)
        session.commit()
        return jsonify({'success': 'OK'})


class WeaponsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        weapons = session.query(Weapons).all()
        return jsonify({'weapons': [item.to_dict(
            only=('title', 'content', 'user.name')) for item in weapons]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        weapons = Weapons(
            title=args['title'],
            content=args['content'],
            user_id=args['user_id'],
            is_published=args['is_published'],
            is_private=args['is_private']
        )
        session.add(weapons)
        session.commit()
        return jsonify({'id': weapons.id})
