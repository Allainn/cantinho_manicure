from flask import jsonify, request, url_for, current_app, abort
from .. import db
from ..models import Cidade, Estado
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

@api.route('/cidades/<string:uf>')
def get_cidade_estado(uf):
    estado = Estado.query.filter_by(uf=uf).first()
    cidades = Cidade.query.filter_by(estado=estado).all()
    return jsonify({'cidades': [cidade.to_json() for cidade in cidades]})

@api.route('/cidades/uf/<int:id>')
def get_cidade_estado_id(id):
    estado = Estado.query.filter_by(id=id).first()
    cidades = Cidade.query.filter_by(estado=estado).all()
    return jsonify({'cidades': [cidade.to_json() for cidade in cidades]})