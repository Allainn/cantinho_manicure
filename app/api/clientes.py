from flask import jsonify, request, url_for, current_app, abort
from .. import db
from ..models import Cliente
from . import api
from sqlalchemy.exc import IntegrityError

@api.route('/clientes/', methods=['POST'])
def new_cliente():
    cliente = Cliente.from_json(request.json)
    try:
        db.session.add(cliente)
        db.session.commit()
    except IntegrityError as err:
        print(err)
        abort(400, description="Bad Resquest")
    return jsonify(cliente.to_json()), 201, \
        {'Location':url_for('api.get_tipo_cliente', id=cliente.id)}

@api.route('/clientes/')
def get_clientes():
    clientes = Cliente.query.all()
    return jsonify({'clientes': [cliente.to_json() for cliente in clientes]})

@api.route('/clientes/<int:id>')
def get_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    return jsonify(cliente.to_json())

@api.route('/clientes/<int:id>', methods=['PUT'])
def edit_cliente(id):
    cliente = Tipo_Usuario.query.get_or_404(id)
    cliente.descricao = request.json.get('descricao', cliente.descricao)
    db.session.add(cliente)
    db.session.commit()
    return jsonify(cliente.to_json())