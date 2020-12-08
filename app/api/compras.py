from flask import jsonify, request, url_for, current_app, abort
from .. import db
from ..models import Compra, CompraSchema, Permissao, Fornecedor, Produto
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
    produtos = request.json.get('produtos', compra.produtos)
    if type(produtos) is list and type(produtos[0]) is dict:
        prods = []
        for p in produtos:
            prod = Produto.query.get(int(p['id']))
            prods.append(prod)
            compra.produtos.append(prod)
        print(prods)
    fornecedor = request.json.get('fornecedor', compra.fornecedor)
    if type(fornecedor) is dict:
        if 'id' in fornecedor.keys():
            fornecedor = Fornecedor.query.get(int(fornecedor['id']))
        else:
            return bad_request2("Campos id do fornecedor não foi passado") 
        if fornecedor is None:
            return bad_request2("Fornecedor não existente", "Fornecedor não existente")
        compra.fornecedor = fornecedor
    db.session.add(compra)
    db.session.commit()
    return jsonify(compra.to_json()), 200

@api.route('/compras/<int:id>', methods=['DELETE'])
@permissao_requerida(Permissao.CADASTRO_BASICO)
def delete_compra(id):
    compra = Compra.query.get_or_404(id)
    comp_json = compra.to_json()
    db.session.delete(compra)
    db.session.commit()
    return jsonify(comp_json), 200