from flask import jsonify, request, url_for, current_app, abort
from .. import db
from ..models import Produto, ProdutoSchema, Permissao, Tipo_Quantidade
from . import api
from .errors import forbidden, bad_request2
from sqlalchemy.exc import IntegrityError, OperationalError
from marshmallow.exceptions import ValidationError
from .decorators import permissao_requerida

@api.route('/produtos/')
@permissao_requerida(Permissao.CADASTRO_BASICO)
def get_produtos():
    produtos = Produto.query.all()
    return jsonify({'produtos': [produto.to_json() for produto in produtos]})

@api.route('/produtos/<int:id>')
@permissao_requerida(Permissao.CADASTRO_BASICO)
def get_produto(id):
    produto = Produto.query.get_or_404(id)
    return jsonify(produto.to_json())

@api.route('/produtos/', methods=['POST'])
@permissao_requerida(Permissao.CADASTRO_BASICO)
def new_produto():
    try:
        produto = ProdutoSchema().load(request.json, session=db.session)
    except ValidationError as err:
        campo = list(err.messages.keys())[0].lower().capitalize()
        valor = list(err.messages.values())[0][0].lower()
        mensagem = campo + ' ' + valor
        return bad_request2(str(err), mensagem)
    try:
        db.session.add(produto)
        db.session.commit()
    except IntegrityError as err:
       return bad_request2(str(err), "Erro ao inserir o produto")
    except OperationalError as err:
        msg = err._message().split('"')[1]
        return bad_request2(str(err), msg)
    return jsonify(produto.to_json()), 201, \
        {'Location':url_for('api.get_produto', id=produto.id)}

@api.route('/produtos/<int:id>', methods=['PUT'])
@permissao_requerida(Permissao.CADASTRO_BASICO)
def edit_produto(id):
    produto = Produto.query.get_or_404(id)
    produto.descricao = request.json.get('descricao', produto.descricao)
    produto.quantidade = request.json.get('quantidade', produto.quantidade)
    produto.preco_un = request.json.get('preco_un', produto.preco_un)
    produto.observacao = request.json.get('observacao', produto.observacao)
    tipo_quantidade = request.json.get('tipo_quantidade', produto.tipo_quantidade)
    if type(tipo_quantidade) is dict:
        if 'id' in tipo_quantidade.keys():
            tipo_quantidade = Tipo_Quantidade.query.get(int(tipo_quantidade['id']))
        elif 'sigla' in tipo_quantidade.keys():
            tipo_quantidade = Tipo_Quantidade.query.filter_by(sigla=tipo_quantidade['sigla']).first()
        elif 'descricao' in tipo_quantidade.keys():
            tipo_quantidade = Tipo_Quantidade.query.filter_by(descricao=tipo_quantidade['descricao']).first()
        else:
            return bad_request2("Campos id, sigla ou descrição do tipo de quantidade não foram passados") 
        if tipo_quantidade is None:
            return bad_request2("Tipo_Quantidade não existente", "Tipo de quantidade não existente")
    produto.tipo_quantidade = tipo_quantidade
    db.session.add(produto)
    db.session.commit()
    return jsonify(produto.to_json()), 200

@api.route('/produtos/<int:id>', methods=['DELETE'])
@permissao_requerida(Permissao.CADASTRO_BASICO)
def delete_produto(id):
    produto = Produto.query.get_or_404(id)
    db.session.delete(produto)
    db.session.commit()
    return jsonify({"mensagem":"Produto deletado com sucesso"}), 200