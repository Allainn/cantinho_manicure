from flask import jsonify, request, url_for, current_app, abort
from .. import db
from ..models import Bairro, BairroSchema
from . import api
from .errors import forbidden, bad_request2
from sqlalchemy.exc import IntegrityError, OperationalError
from marshmallow.exceptions import ValidationError

@api.route('/bairros/')
def get_bairros():
    bairros = Bairro.query.all()
    return jsonify({'bairros': [bairro.to_json() for bairro in bairros]})

@api.route('/bairros/<int:id>')
def get_bairro(id):
    bairro = Bairro.query.get_or_404(id)
    return jsonify(bairro.to_json())

@api.route('/bairros/', methods=['POST'])
def new_bairro():
    try:
        bairro = BairroSchema().load(request.json, session=db.session)
    except ValidationError as err:
        print(list(err.messages.values())[0][0])
        campo = list(err.messages.keys())[0].lower().capitalize()
        valor = list(err.messages.values())[0][0].lower()
        mensagem = campo + ' ' + valor
        #abort(400, description=str(err))
        return bad_request2(str(err), mensagem)
    try:
        db.session.add(bairro)
        db.session.commit()
    except IntegrityError as err:
        print(err)
        abort(400, description="Bad Resquest")
    except OperationalError as err:
        #print(err._message().split('"'))
        msg = err._message().split('"')[1]
        return bad_request2(str(err), msg)
    return jsonify(bairro.to_json()), 201, \
        {'Location':url_for('api.get_bairro', id=bairro.id)}

@api.route('/bairros/<int:id>', methods=['PUT'])
def edit_bairro(id):
    bairro = Bairro.query.get_or_404(id)
    bairro.descricao = request.json.get('descricao', bairro.descricao)
    db.session.add(bairro)
    db.session.commit()
    return jsonify(bairro.to_json())