from flask import jsonify, request, g, url_for, current_app
from .. import db
from ..models import Tipo_Usuario
from . import api

@api.route('/tipos_usuario/')
def get_tipos_usuario():
    tipos_usuario = Tipo_Usuario.query.all()
    return jsonify({'tipos_usuario': [tipo_usuario.to_json() for tipo_usuario in tipos_usuario]})

@api.route('/tipos_usuario/<int:id>')
def get_tipo_usuario(id):
    tipo_usuario = Tipo_Usuario.query.get_or_404(id)
    return jsonify(tipo_usuario.to_json())