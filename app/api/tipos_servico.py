from flask import jsonify, request, url_for, current_app, abort
from .. import db
from ..models import Tipo_Servico, Tipo_ServicoSchema, Permissao
from . import api
from .errors import forbidden, bad_request2
from sqlalchemy.exc import IntegrityError, OperationalError
from marshmallow.exceptions import ValidationError
from .decorators import permissao_requerida

@api.route('/tipos_servico/')
@permissao_requerida(Permissao.VER_SERVICOS)
def get_tipos_servico():
    tipos_servico = Tipo_Servico.query.all()
    return jsonify({'tipos_servico': [tipo_servico.to_json() for tipo_servico in tipos_servico]})

@api.route('/tipos_servico/<int:id>')
@permissao_requerida(Permissao.VER_SERVICOS)
def get_tipo_servico(id):
    tipo_servico = Tipo_Servico.query.get_or_404(id)
    return jsonify(tipo_servico.to_json())

@api.route('/tipos_servico/', methods=['POST'])
@permissao_requerida(Permissao.CADASTRO_BASICO)
def new_tipo_servico():
    try:
        tipo_servico = Tipo_ServicoSchema().load(request.json, session=db.session)
    except ValidationError as err:
        campo = list(err.messages.keys())[0].lower().capitalize()
        valor = list(err.messages.values())[0][0].lower()
        mensagem = campo + ' ' + valor
        return bad_request2(str(err), mensagem)
    try:
        db.session.add(tipo_servico)
        db.session.commit()
    except IntegrityError as err:
       return bad_request2(str(err), "Erro ao inserir o tipo_servico")
    except OperationalError as err:
        msg = err._message().split('"')[1]
        return bad_request2(str(err), msg)
    return jsonify(tipo_servico.to_json()), 201, \
        {'Location':url_for('api.get_tipo_servico', id=tipo_servico.id)}

@api.route('/tipos_servico/<int:id>', methods=['PUT'])
@permissao_requerida(Permissao.CADASTRO_BASICO)
def edit_tipo_servico(id):
    tipo_servico = Tipo_Servico.query.get_or_404(id)
    tipo_servico.descricao = request.json.get('descricao', tipo_servico.descricao)
    tipo_servico.tempo = request.json.get('tempo', tipo_servico.tempo)
    tipo_servico.valor = request.json.get('valor', tipo_servico.valor)
    tipo_servico.observacao = request.json.get('observacao', tipo_servico.observacao)
    db.session.add(tipo_servico)
    db.session.commit()
    return jsonify(tipo_servico.to_json()), 200

@api.route('/tipos_servico/<int:id>', methods=['DELETE'])
@permissao_requerida(Permissao.CADASTRO_BASICO)
def delete_tipo_servico(id):
    tipo_servico = Tipo_Servico.query.get_or_404(id)
    db.session.delete(tipo_servico)
    db.session.commit()
    return jsonify({"mensagem":"Tipo_Servico deletado com sucesso"}), 200