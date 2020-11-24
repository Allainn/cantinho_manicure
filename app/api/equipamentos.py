from flask import jsonify, request, url_for, current_app, abort
from .. import db
from ..models import Equipamento, EquipamentoSchema, Permissao
from . import api
from .errors import forbidden, bad_request2
from sqlalchemy.exc import IntegrityError, OperationalError
from marshmallow.exceptions import ValidationError
from .decorators import permissao_requerida

@api.route('/equipamentos/')
@permissao_requerida(Permissao.CADASTRO_BASICO)
def get_equipamentos():
    equipamentos = Equipamento.query.all()
    return jsonify({'equipamentos': [equipamento.to_json() for equipamento in equipamentos]})

@api.route('/equipamentos/<int:id>')
@permissao_requerida(Permissao.CADASTRO_BASICO)
def get_equipamento(id):
    equipamento = Equipamento.query.get_or_404(id)
    return jsonify(equipamento.to_json())

@api.route('/equipamentos/', methods=['POST'])
@permissao_requerida(Permissao.CADASTRO_BASICO)
def new_equipamento():
    try:
        equipamento = EquipamentoSchema().load(request.json, session=db.session)
    except ValidationError as err:
        campo = list(err.messages.keys())[0].lower().capitalize()
        valor = list(err.messages.values())[0][0].lower()
        mensagem = campo + ' ' + valor
        return bad_request2(str(err), mensagem)
    try:
        db.session.add(equipamento)
        db.session.commit()
    except IntegrityError as err:
       return bad_request2(str(err), "Erro ao inserir o equipamento")
    except OperationalError as err:
        msg = err._message().split('"')[1]
        return bad_request2(str(err), msg)
    return jsonify(equipamento.to_json()), 201, \
        {'Location':url_for('api.get_equipamento', id=equipamento.id)}

@api.route('/equipamentos/<int:id>', methods=['PUT'])
@permissao_requerida(Permissao.CADASTRO_BASICO)
def edit_equipamento(id):
    equipamento = Equipamento.query.get_or_404(id)
    equipamento.descricao = request.json.get('descricao', equipamento.descricao)
    equipamento.tempo = request.json.get('tempo', equipamento.tempo)
    equipamento.preco_tempo = request.json.get('preco_tempo', equipamento.preco_tempo)
    equipamento.observacao = request.json.get('observacao', equipamento.observacao)
    db.session.add(equipamento)
    db.session.commit()
    return jsonify(equipamento.to_json()), 200

@api.route('/equipamentos/<int:id>', methods=['DELETE'])
@permissao_requerida(Permissao.CADASTRO_BASICO)
def delete_equipamento(id):
    equipamento = Equipamento.query.get_or_404(id)
    db.session.delete(equipamento)
    db.session.commit()
    return jsonify({"mensagem":"Equipamento deletado com sucesso"}), 200