from flask import jsonify, request, url_for, current_app, abort
from .. import db
from ..models import Fornecedor, FornecedorSchema, Permissao, Endereco
from . import api
from .errors import forbidden, bad_request2
from sqlalchemy.exc import IntegrityError, OperationalError
from marshmallow.exceptions import ValidationError
from .decorators import permissao_requerida

@api.route('/fornecedores/')
@permissao_requerida(Permissao.CADASTRO_BASICO)
def get_fornecedores():
    fornecedores = Fornecedor.query.all()
    return jsonify({'fornecedores': [fornecedor.to_json() for fornecedor in fornecedores]})

@api.route('/fornecedores/<int:id>')
@permissao_requerida(Permissao.CADASTRO_BASICO)
def get_fornecedor(id):
    fornecedor = Fornecedor.query.get_or_404(id)
    return jsonify(fornecedor.to_json())

@api.route('/fornecedores/', methods=['POST'])
@permissao_requerida(Permissao.CADASTRO_BASICO)
def new_fornecedor():
    try:
        fornecedor = FornecedorSchema().load(request.json, session=db.session)
    except ValidationError as err:
        campo = list(err.messages.keys())[0].lower().capitalize()
        valor = list(err.messages.values())[0][0].lower()
        mensagem = campo + ' ' + valor
        return bad_request2(str(err), mensagem)
    try:
        db.session.add(fornecedor)
        db.session.commit()
    except IntegrityError as err:
       return bad_request2(str(err), "Erro ao inserir o fornecedor")
    except OperationalError as err:
        msg = err._message().split('"')[1]
        return bad_request2(str(err), msg)
    return jsonify(fornecedor.to_json()), 201, \
        {'Location':url_for('api.get_fornecedor', id=fornecedor.id)}

@api.route('/fornecedores/<int:id>', methods=['PUT'])
@permissao_requerida(Permissao.CADASTRO_BASICO)
def edit_fornecedor(id):
    fornecedor = Fornecedor.query.get_or_404(id)
    fornecedor.nome = request.json.get('nome', fornecedor.nome)
    fornecedor.email = request.json.get('email', fornecedor.email)
    fornecedor.telefone1 = request.json.get('telefone1', fornecedor.telefone1)
    fornecedor.telefone2 = request.json.get('telefone2', fornecedor.telefone2)
    fornecedor.data_nascimento = request.json.get('data_nascimento', fornecedor.data_nascimento)
    fornecedor.numero = request.json.get('numero', fornecedor.numero)
    fornecedor.site = request.json.get('site', fornecedor.site)
    fornecedor.instagram = request.json.get('instagram', fornecedor.instagram)
    fornecedor.facebook = request.json.get('facebook', fornecedor.facebook)
    fornecedor.observacao = request.json.get('observacao', fornecedor.observacao)
    endereco = request.json.get('endereco', fornecedor.endereco)
    if type(endereco) is dict:
        if 'id' in endereco.keys():
            endereco = Endereco.query.get(int(endereco['id']))
        elif 'rua' in endereco.keys():
            endereco = Endereco.query.filter_by(rua=endereco['rua']).first()
        else:
            return bad_request2("Campos id ou rua do endereço não foram passados") 
        if endereco is None:
            return bad_request2("Endereço não existente", "Endereco não existente")
    fornecedor.endereco = endereco
    db.session.add(fornecedor)
    db.session.commit()
    return jsonify(fornecedor.to_json()), 200

@api.route('/fornecedores/<int:id>', methods=['DELETE'])
@permissao_requerida(Permissao.CADASTRO_BASICO)
def delete_fornecedor(id):
    fornecedor = Fornecedor.query.get_or_404(id)
    db.session.delete(fornecedor)
    db.session.commit()
    return jsonify({"mensagem":"Fornecedor deletado com sucesso"}), 200