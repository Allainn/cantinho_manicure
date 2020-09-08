from flask import jsonify, request, g, url_for, current_app
from .. import db
from ..models import Usuario
from . import api

@api.route('/usuarios/')
def get_usuarios():
    usuarios = Usuario.query.all()
    return jsonify({'usuarios': [usuario.to_json() for usuario in usuarios]})

@api.route('/usuarios/<int:id>')
def get_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    return jsonify(usuario.to_json())