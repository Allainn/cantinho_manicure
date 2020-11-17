from flask import jsonify, request, url_for, current_app, abort
from .. import db
from ..models import Estado
from . import api
from sqlalchemy.exc import IntegrityError

@api.route('/estados/')
def get_estados():
    estados = Estado.query.all()
    return jsonify({'estados': [estado.to_json() for estado in estados]})

@api.route('/estados/<int:id>')
def get_estado(id):
    estado = Estado.query.get_or_404(id)
    return jsonify(estado.to_json())