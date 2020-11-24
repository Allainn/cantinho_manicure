from flask import jsonify, request, url_for, current_app, abort
from .. import db
from ..models import Servico, ServicoSchema, Permissao
from . import api
from .errors import forbidden, bad_request2
from sqlalchemy.exc import IntegrityError, OperationalError
from marshmallow.exceptions import ValidationError
from .decorators import permissao_requerida

@api.route('/servicos/')
@permissao_requerida(Permissao.VER_SERVICOS)
def get_servicos():
    servicos = Servico.query.all()
    return jsonify({'servicos': [servico.to_json() for servico in servicos]})

@api.route('/servicos/<int:id>')
@permissao_requerida(Permissao.VER_SERVICOS)
def get_servico(id):
    servico = Servico.query.get_or_404(id)
    return jsonify(servico.to_json())

@api.route('/servicos/', methods=['POST'])
@permissao_requerida(Permissao.CADASTRO_BASICO)
def new_servico():
    try:
        servico = ServicoSchema().load(request.json, session=db.session)
    except ValidationError as err:
        campo = list(err.messages.keys())[0].lower().capitalize()
        valor = list(err.messages.values())[0][0].lower()
        mensagem = campo + ' ' + valor
        return bad_request2(str(err), mensagem)
    try:
        db.session.add(servico)
        db.session.commit()
    except IntegrityError as err:
       return bad_request2(str(err), "Erro ao inserir o servico")
    except OperationalError as err:
        msg = err._message().split('"')[1]
        return bad_request2(str(err), msg)
    return jsonify(servico.to_json()), 201, \
        {'Location':url_for('api.get_servico', id=servico.id)}

@api.route('/servicos/<int:id>', methods=['PUT'])
@permissao_requerida(Permissao.CADASTRO_BASICO)
def edit_servico(id):
    servico = Servico.query.get_or_404(id)
    servico.data = request.json.get('data', servico.data)
    servico.valor = request.json.get('valor', servico.valor)
    servico.tempo = request.json.get('tempo', servico.tempo)
    servico.observacao = request.json.get('observacao', servico.observacao)
    db.session.add(servico)
    db.session.commit()
    return jsonify(servico.to_json()), 200

@api.route('/servicos/<int:id>', methods=['DELETE'])
@permissao_requerida(Permissao.CADASTRO_BASICO)
def delete_servico(id):
    servico = Servico.query.get_or_404(id)
    db.session.delete(servico)
    db.session.commit()
    return jsonify({"mensagem":"Servico deletado com sucesso"}), 200