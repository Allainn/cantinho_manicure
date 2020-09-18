from flask import jsonify, request, url_for, current_app, abort
from .. import db
from ..models import Usuario
from . import api
from sqlalchemy.exc import IntegrityError

@api.route('/usuarios/', methods=['POST'])
def new_usuario():
    usuario = Usuario.from_json(request.json)
    try:
        db.session.add(usuario)
        db.session.commit()
    except IntegrityError as err:
        print(err)
        abort(400, description="Bad Resquest")
    return jsonify(usuario.to_json()), 201, \
        {'Location':url_for('api.get_tipo_usuario', id=usuario.id)}

@api.route('/usuarios/')
def get_usuarios():
    usuarios = Usuario.query.all()
    return jsonify({'usuarios': [usuario.to_json() for usuario in usuarios]})

@api.route('/usuarios/<int:id>')
def get_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    return jsonify(usuario.to_json())