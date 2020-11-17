from flask import jsonify, request, url_for, current_app, abort
from .. import db
from ..models import Cidade
from . import api
from sqlalchemy.exc import IntegrityError

@api.route('/cidades/')
def get_cidades():
    cidades = Cidade.query.all()
    return jsonify({'cidades': [cidade.to_json() for cidade in cidades]})

@api.route('/cidades/<int:id>')
def get_cidade(id):
    cidade = Cidade.query.get_or_404(id)
    return jsonify(cidade.to_json())