from flask import jsonify, request, url_for, current_app, abort
from .. import db
from ..models import Cliente, ClienteSchema, Permissao, Endereco
from . import api
from .errors import forbidden, bad_request2
from sqlalchemy.exc import IntegrityError, OperationalError
from marshmallow.exceptions import ValidationError
from .decorators import permissao_requerida

@api.route('/clientes/')
@permissao_requerida(Permissao.CADASTRO_BASICO)
def get_clientes():
    clientes = Cliente.query.all()
    return jsonify({'clientes': [cliente.to_json() for cliente in clientes]})

@api.route('/clientes/<int:id>')
@permissao_requerida(Permissao.CADASTRO_BASICO)
def get_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    return jsonify(cliente.to_json())

@api.route('/clientes/', methods=['POST'])
@permissao_requerida(Permissao.CADASTRO_BASICO)
def new_cliente():
    try:
        cliente = ClienteSchema().load(request.json, session=db.session)
    except ValidationError as err:
        campo = list(err.messages.keys())[0].lower().capitalize()
        valor = list(err.messages.values())[0][0].lower()
        mensagem = campo + ' ' + valor
        return bad_request2(str(err), mensagem)
    try:
        db.session.add(cliente)
        db.session.commit()
    except IntegrityError as err:
       return bad_request2(str(err), "Erro ao inserir o cliente")
    except OperationalError as err:
        msg = err._message().split('"')[1]
        return bad_request2(str(err), msg)
    return jsonify(cliente.to_json()), 201, \
        {'Location':url_for('api.get_cliente', id=cliente.id)}

@api.route('/clientes/<int:id>', methods=['PUT'])
@permissao_requerida(Permissao.CADASTRO_BASICO)
def edit_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    cliente.nome = request.json.get('nome', cliente.nome)
    cliente.telefone1 = request.json.get('telefone1', cliente.telefone1)
    cliente.telefone2 = request.json.get('telefone2', cliente.telefone2)
    cliente.data_nascimento = request.json.get('data_nascimento', cliente.data_nascimento)
    cliente.numero = request.json.get('numero', cliente.numero)
    cliente.instagram = request.json.get('instagram', cliente.instagram)
    cliente.facebook = request.json.get('facebook', cliente.facebook)
    endereco = request.json.get('endereco', cliente.endereco)
    if type(endereco) is dict:
        if 'id' in endereco.keys():
            endereco = Endereco.query.get(int(endereco['id']))
        elif 'rua' in endereco.keys():
            endereco = Endereco.query.filter_by(rua=endereco['rua']).first()
        else:
            return bad_request2("Campos id ou rua do endereço não foram passados") 
        if endereco is None:
            return bad_request2("Endereço não existente", "Endereco não existente")
    cliente.endereco = endereco
    db.session.add(cliente)
    db.session.commit()
    return jsonify(cliente.to_json()), 200

@api.route('/clientes/<int:id>', methods=['DELETE'])
@permissao_requerida(Permissao.CADASTRO_BASICO)
def delete_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    cli_json = cliente.to_json()
    db.session.delete(cliente)
    db.session.commit()
    return jsonify(cli_json), 200