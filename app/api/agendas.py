from flask import jsonify, request, url_for, current_app, abort
from .. import db
from ..models import Agenda, AgendaSchema, Permissao
from . import api
from .errors import forbidden, bad_request2
from sqlalchemy.exc import IntegrityError, OperationalError
from marshmallow.exceptions import ValidationError
from .decorators import permissao_requerida

@api.route('/agendas/')
@permissao_requerida(Permissao.VER_AGENDA)
def get_agendas():
    agendas = Agenda.query.all()
    return jsonify({'agendas': [agenda.to_json() for agenda in agendas]})

@api.route('/agendas/<int:id>')
@permissao_requerida(Permissao.VER_AGENDA)
def get_agenda(id):
    agenda = Agenda.query.get_or_404(id)
    return jsonify(agenda.to_json())

@api.route('/agendas/', methods=['POST'])
@permissao_requerida(Permissao.MARCAR_SERVICO)
def new_agenda():
    try:
        agenda = AgendaSchema().load(request.json, session=db.session)
    except ValidationError as err:
        campo = list(err.messages.keys())[0].lower().capitalize()
        valor = list(err.messages.values())[0][0].lower()
        mensagem = campo + ' ' + valor
        return bad_request2(str(err), mensagem)
    try:
        db.session.add(agenda)
        db.session.commit()
    except IntegrityError as err:
       return bad_request2(str(err), "Erro ao inserir o agenda")
    except OperationalError as err:
        msg = err._message().split('"')[1]
        return bad_request2(str(err), msg)
    return jsonify(agenda.to_json()), 201, \
        {'Location':url_for('api.get_agenda', id=agenda.id)}

@api.route('/agendas/<int:id>', methods=['PUT'])
@permissao_requerida(Permissao.MARCAR_SERVICO)
def edit_agenda(id):
    agenda = Agenda.query.get_or_404(id)
    agenda.data = request.json.get('data', agenda.data)
    agenda.observacao = request.json.get('observacao', agenda.observacao)
    db.session.add(agenda)
    db.session.commit()
    return jsonify(agenda.to_json()), 200

@api.route('/agendas/<int:id>', methods=['DELETE'])
@permissao_requerida(Permissao.MARCAR_SERVICO)
def delete_agenda(id):
    agenda = Agenda.query.get_or_404(id)
    age_json = agenda.to_json
    db.session.delete(agenda)
    db.session.commit()
    return jsonify(age_json), 200