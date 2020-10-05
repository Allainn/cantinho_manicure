from flask import jsonify, request, url_for, current_app, abort
from .. import db
from ..models import Tipo_Usuario, Permissao, TipoUsuarioSchema
from . import api
from .errors import forbidden, bad_request2
from sqlalchemy.exc import IntegrityError
from marshmallow.exceptions import ValidationError
#from .decorators import permission_required

@api.route('/tipos_usuario/', methods=['POST'])
#@permission_required(Permissao.ADMIN)
def new_tipo_usuario():
    try:
        tipo_usuario = TipoUsuarioSchema().load(request.json, session=db.session)
    except ValidationError as err:
        print(list(err.messages.values())[0][0])
        campo = list(err.messages.keys())[0].lower().capitalize()
        valor = list(err.messages.values())[0][0].lower()
        mensagem = campo + ' ' + valor
        #abort(400, description=str(err))
        return bad_request2(str(err), mensagem)
    try:
        db.session.add(tipo_usuario)
        db.session.commit()
    except IntegrityError as err:
        abort(400, description=str(err))
    return jsonify(tipo_usuario.to_json()), 201, \
        {'Location':url_for('api.get_tipo_usuario', id=tipo_usuario.id)}

#@auth.login_required
@api.route('/tipos_usuario/')
def get_tipos_usuario():
    tipos_usuario = Tipo_Usuario.query.all()
    return jsonify({'tipos_usuario': [tipo_usuario.to_json() for tipo_usuario in tipos_usuario]})

@api.route('/tipos_usuario/<int:id>')
def get_tipo_usuario(id):
    tipo_usuario = Tipo_Usuario.query.get_or_404(id)
    return jsonify(tipo_usuario.to_json())

@api.route('/tipos_usuario/<int:id>', methods=['PUT'])
def edit_tipo_usuario(id):
    tipo_usuario = Tipo_Usuario.query.get_or_404(id)
    tipo_usuario.descricao = request.json.get('descricao', tipo_usuario.descricao)
    db.session.add(tipo_usuario)
    db.session.commit()
    return jsonify(tipo_usuario.to_json())