from flask import jsonify, request, url_for, current_app, abort
from .. import db
from ..models import Endereco, EnderecoSchema
from . import api
from .errors import forbidden, bad_request2
from sqlalchemy.exc import IntegrityError, OperationalError
from marshmallow.exceptions import ValidationError

@api.route('/enderecos/')
def get_enderecos():
    enderecos = Endereco.query.all()
    return jsonify({'enderecos': [endereco.to_json() for endereco in enderecos]})

@api.route('/enderecos/<int:id>')
def get_endereco(id):
    endereco = Endereco.query.get_or_404(id)
    return jsonify(endereco.to_json())

@api.route('/enderecos/', methods=['POST'])
def new_endereco():
    try:
        endereco = EnderecoSchema().load(request.json, session=db.session)
    except ValidationError as err:
        campo = list(err.messages.keys())[0].lower().capitalize()
        valor = list(err.messages.values())[0][0].lower()
        mensagem = campo + ' ' + valor
        return bad_request2(str(err), mensagem)
    try:
        db.session.add(endereco)
        db.session.commit()
    except IntegrityError as err:
       return bad_request2(str(err), "Erro ao inserir o endereço")
    except OperationalError as err:
        msg = err._message().split('"')[1]
        return bad_request2(str(err), msg)
    return jsonify(endereco.to_json()), 201, \
        {'Location':url_for('api.get_endereco', id=endereco.id)}

@api.route('/enderecos/<int:id>', methods=['PUT'])
def edit_endereco(id):
    endereco = Endereco.query.get_or_404(id)
    endereco.descricao = request.json.get('descricao', endereco.descricao)
    db.session.add(endereco)
    db.session.commit()
    return jsonify(endereco.to_json())