from flask import jsonify, request, url_for, current_app, abort
from .. import db
from ..models import Bairro, BairroSchema, Permissao, Cidade
from . import api
from .errors import forbidden, bad_request2
from sqlalchemy.exc import IntegrityError, OperationalError
from marshmallow.exceptions import ValidationError
from .decorators import admin_requerido, permissao_requerida

@api.route('/bairros/')
@permissao_requerida(Permissao.VER_SERVICOS)
def get_bairros():
    bairros = Bairro.query.all()
    return jsonify({'bairros': [bairro.to_json() for bairro in bairros]})

@api.route('/bairros/<int:id>')
@permissao_requerida(Permissao.VER_SERVICOS)
def get_bairro(id):
    bairro = Bairro.query.get_or_404(id)
    return jsonify(bairro.to_json())

@api.route('/bairros/', methods=['POST'])
@permissao_requerida(Permissao.CADASTRO_BASICO)
def new_bairro():
    try:
        bairro = BairroSchema().load(request.json, session=db.session)
    except ValidationError as err:
        campo = list(err.messages.keys())[0].lower().capitalize()
        valor = list(err.messages.values())[0][0].lower()
        mensagem = campo + ' ' + valor
        return bad_request2(str(err), mensagem)
    try:
        db.session.add(bairro)
        db.session.commit()
    except IntegrityError as err:
        return bad_request2(str(err), "Erro ao inserir o bairro")
    except OperationalError as err:
        msg = err._message().split('"')[1]
        return bad_request2(str(err), msg)
    return jsonify(bairro.to_json()), 201, \
        {'Location':url_for('api.get_bairro', id=bairro.id)}

@api.route('/bairros/<int:id>', methods=['PUT'])
@permissao_requerida(Permissao.CADASTRO_BASICO)
def edit_bairro(id):
    bairro = Bairro.query.get_or_404(id)
    bairro.descricao = request.json.get('descricao', bairro.descricao)
    cidade = request.json.get('cidade', bairro.cidade)
    if type(cidade) is dict:
        if 'id' in cidade.keys():
            cidade = Cidade.query.get(int(cidade['id']))
        elif 'descricao' in cidade.keys():
            cidade = Cidade.query.filter_by(descricao=cidade['descricao']).first()
        else:
            return bad_request2("Campos id ou descricao da cidade não foram passados") 
        if cidade is None:
            return bad_request2("Cidade não existente", "Cidade não existente")
    bairro.cidade = cidade
    db.session.add(bairro)
    db.session.commit()
    return jsonify(bairro.to_json()), 204

@api.route('/bairros/<int:id>', methods=['DELETE'])
@permissao_requerida(Permissao.CADASTRO_BASICO)
def delete_bairro(id):
    bairro = Bairro.query.get_or_404(id)
    db.session.delete(bairro)
    db.session.commit()
    return jsonify({"mensagem":"Bairro apagado com sucesso"}), 204