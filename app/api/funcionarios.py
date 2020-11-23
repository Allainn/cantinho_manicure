from flask import jsonify, request, url_for, current_app, abort
from .. import db
from ..models import Funcionario, FuncionarioSchema, Permissao, Endereco
from . import api
from .errors import forbidden, bad_request2
from sqlalchemy.exc import IntegrityError, OperationalError
from marshmallow.exceptions import ValidationError
from .decorators import permissao_requerida

@api.route('/funcionarios/')
@permissao_requerida(Permissao.ADMIN)
def get_funcionarios():
    funcionarios = Funcionario.query.all()
    return jsonify({'funcionarios': [funcionario.to_json() for funcionario in funcionarios]})

@api.route('/funcionarios/<int:id>')
@permissao_requerida(Permissao.ADMIN)
def get_funcionario(id):
    funcionario = Funcionario.query.get_or_404(id)
    return jsonify(funcionario.to_json())

@api.route('/funcionarios/', methods=['POST'])
@permissao_requerida(Permissao.ADMIN)
def new_funcionario():
    try:
        funcionario = FuncionarioSchema().load(request.json, session=db.session)
    except ValidationError as err:
        campo = list(err.messages.keys())[0].lower().capitalize()
        valor = list(err.messages.values())[0][0].lower()
        mensagem = campo + ' ' + valor
        return bad_request2(str(err), mensagem)
    try:
        db.session.add(funcionario)
        db.session.commit()
    except IntegrityError as err:
       return bad_request2(str(err), "Erro ao inserir o funcionário")
    except OperationalError as err:
        msg = err._message().split('"')[1]
        return bad_request2(str(err), msg)
    return jsonify(funcionario.to_json()), 201, \
        {'Location':url_for('api.get_funcionario', id=funcionario.id)}

@api.route('/funcionarios/<int:id>', methods=['PUT'])
@permissao_requerida(Permissao.ADMIN)
def edit_funcionario(id):
    funcionario = Funcionario.query.get_or_404(id)
    funcionario.nome = request.json.get('nome', funcionario.nome)
    funcionario.telefone1 = request.json.get('telefone1', funcionario.telefone1)
    funcionario.telefone2 = request.json.get('telefone2', funcionario.telefone2)
    funcionario.data_nascimento = request.json.get('data_nascimento', funcionario.data_nascimento)
    funcionario.numero = request.json.get('numero', funcionario.numero)
    endereco = request.json.get('endereco', funcionario.endereco)
    if type(endereco) is dict:
        if 'id' in endereco.keys():
            endereco = Endereco.query.get(int(endereco['id']))
        elif 'rua' in endereco.keys():
            endereco = Endereco.query.filter_by(rua=endereco['rua']).first()
        else:
            return bad_request2("Campos id ou rua do endereço não foram passados") 
        if endereco is None:
            return bad_request2("Endereço não existente", "Endereco não existente")
    funcionario.endereco = endereco
    db.session.add(funcionario)
    db.session.commit()
    return jsonify(funcionario.to_json()), 200

@api.route('/funcionarios/<int:id>', methods=['DELETE'])
@permissao_requerida(Permissao.ADMIN)
def delete_funcionario(id):
    funcionario = Funcionario.query.get_or_404(id)
    db.session.delete(funcionario)
    db.session.commit()
    return jsonify({"mensagem":"Funcionario deletado com sucesso"}), 200