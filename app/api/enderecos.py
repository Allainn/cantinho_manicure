from flask import jsonify, request, url_for, current_app, abort
from .. import db
from ..models import Endereco, EnderecoSchema, Permissao, Bairro
from . import api
from .errors import forbidden, bad_request2
from sqlalchemy.exc import IntegrityError, OperationalError
from marshmallow.exceptions import ValidationError
from .decorators import permissao_requerida

@api.route('/enderecos/')
@permissao_requerida(Permissao.VER_SERVICOS)
def get_enderecos():
    enderecos = Endereco.query.all()
    return jsonify({'enderecos': [endereco.to_json() for endereco in enderecos]})

@api.route('/enderecos/<int:id>')
@permissao_requerida(Permissao.VER_SERVICOS)
def get_endereco(id):
    endereco = Endereco.query.get_or_404(id)
    return jsonify(endereco.to_json())

@api.route('/enderecos/', methods=['POST'])
@permissao_requerida(Permissao.CADASTRO_BASICO)
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
@permissao_requerida(Permissao.CADASTRO_BASICO)
def edit_endereco(id):
    endereco = Endereco.query.get_or_404(id)
    endereco.rua = request.json.get('rua', endereco.rua)
    endereco.complemento = request.json.get('rua', endereco.complemento)
    bairro = request.json.get('bairro', endereco.bairro)
    if type(bairro) is dict:
        if 'id' in bairro.keys():
            bairro = Bairro.query.get(int(bairro['id']))
        elif 'descricao' in bairro.keys():
            bairro = Bairro.query.filter_by(descricao=bairro['descricao']).first()
        else:
            return bad_request2("Campos id ou descricao do bairro não foram passados") 
        if bairro is None:
            return bad_request2("Bairro não existente", "Bairro não existente")
    endereco.bairro = bairro
    db.session.add(endereco)
    db.session.commit()
    return jsonify(endereco.to_json()), 200

@api.route('/enderecos/<int:id>', methods=['DELETE'])
@permissao_requerida(Permissao.CADASTRO_BASICO)
def delete_endereco(id):
    endereco = Endereco.query.get_or_404(id)
    db.session.delete(endereco)
    db.session.commit()
    return jsonify({"mensagem":"Endereço apagado com sucesso"}), 200