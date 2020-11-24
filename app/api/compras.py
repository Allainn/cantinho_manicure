from flask import jsonify, request, url_for, current_app, abort
from .. import db
from ..models import Compra, CompraSchema, Permissao
from . import api
from .errors import forbidden, bad_request2
from sqlalchemy.exc import IntegrityError, OperationalError
from marshmallow.exceptions import ValidationError
from .decorators import permissao_requerida

@api.route('/compras/')
@permissao_requerida(Permissao.CADASTRO_BASICO)
def get_compras():
    compras = Compra.query.all()
    return jsonify({'compras': [compra.to_json() for compra in compras]})

@api.route('/compras/<int:id>')
@permissao_requerida(Permissao.CADASTRO_BASICO)
def get_compra(id):
    compra = Compra.query.get_or_404(id)
    return jsonify(compra.to_json())

@api.route('/compras/', methods=['POST'])
@permissao_requerida(Permissao.CADASTRO_BASICO)
def new_compra():
    try:
        compra = CompraSchema().load(request.json, session=db.session)
    except ValidationError as err:
        campo = list(err.messages.keys())[0].lower().capitalize()
        valor = list(err.messages.values())[0][0].lower()
        mensagem = campo + ' ' + valor
        return bad_request2(str(err), mensagem)
    try:
        db.session.add(compra)
        db.session.commit()
    except IntegrityError as err:
       return bad_request2(str(err), "Erro ao inserir o compra")
    except OperationalError as err:
        msg = err._message().split('"')[1]
        return bad_request2(str(err), msg)
    return jsonify(compra.to_json()), 201, \
        {'Location':url_for('api.get_compra', id=compra.id)}

@api.route('/compras/<int:id>', methods=['PUT'])
@permissao_requerida(Permissao.CADASTRO_BASICO)
def edit_compra(id):
    compra = Compra.query.get_or_404(id)
    compra.valor = request.json.get('valor', compra.valor)
    compra.data = request.json.get('data', compra.data)
    compra.observacao = request.json.get('observacao', compra.observacao)
    db.session.add(compra)
    db.session.commit()
    return jsonify(compra.to_json()), 200

@api.route('/compras/<int:id>', methods=['DELETE'])
@permissao_requerida(Permissao.CADASTRO_BASICO)
def delete_compra(id):
    compra = Compra.query.get_or_404(id)
    db.session.delete(compra)
    db.session.commit()
    return jsonify({"mensagem":"Compra deletado com sucesso"}), 200