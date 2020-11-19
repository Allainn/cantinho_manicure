from flask import jsonify, request, url_for, current_app, abort, g
from .. import db
from ..models import Usuario, Permissao, UsuarioSchema, Tipo_Usuario
from .decorators import admin_requerido, permissao_requerida
from . import api
from sqlalchemy.exc import IntegrityError
from .errors import forbidden, bad_request2
from sqlalchemy.exc import IntegrityError, OperationalError
from marshmallow.exceptions import ValidationError

@api.route('/usuarios/', methods=['POST'])
def new_usuario():
    try:
        usuario = UsuarioSchema().load(request.json, session=db.session)
        usuario.senha = usuario.senha_hash
    except ValidationError as err:
        print(list(err.messages.values())[0][0])
        campo = list(err.messages.keys())[0].lower().capitalize()
        valor = list(err.messages.values())[0][0].lower()
        mensagem = campo + ' ' + valor
        return bad_request2(str(err), mensagem)
    try:
        db.session.add(usuario)
        db.session.commit()
    except IntegrityError as err:
        return bad_request2(str(err), "Email ou login existente")
    except OperationalError as err:
        msg = err._message().split('"')[1]
        return bad_request2(str(err), msg)
    return jsonify(usuario.to_json()), 201, \
        {'Location':url_for('api.get_usuario', id=usuario.id)}

@api.route('/usuarios/')
@admin_requerido
def get_usuarios():
    usuarios = Usuario.query.all()
    return jsonify({'usuarios': [usuario.to_json() for usuario in usuarios]})

@api.route('/usuarios/<int:id>')
@admin_requerido
def get_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    return jsonify(usuario.to_json())

@api.route('/usuarios/<int:id>', methods=['PUT'])
@admin_requerido
def edit_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    usuario.login = request.json.get('login', usuario.login)
    usuario.email = request.json.get('email', usuario.email)
    tipo_usuario = request.json.get('tipo_usuario', usuario.tipo_usuario)
    if type(tipo_usuario) is dict:
        if 'id' in tipo_usuario.keys():
            tipo_usuario = Tipo_Usuario.query.get(int(tipo_usuario['id']))
        elif 'descricao' in tipo_usuario.keys():
            tipo_usuario = Tipo_Usuario.query.filter_by(descricao=tipo_usuario['descricao']).first()
        else:
            return bad_request2("Campos id ou descricao do tipo de usuario não foram passados") 
        if tipo_usuario is None:
            return bad_request2("Tipo de usuario não existente", "Tipo de usuario não existente")
    usuario.tipo_usuario = tipo_usuario
    db.session.add(usuario)
    db.session.commit()
    return jsonify(usuario.to_json())