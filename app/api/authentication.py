from flask import g, jsonify
from flask_httpauth import HTTPBasicAuth
from ..models import Usuario
from .errors import unauthorized, forbidden
from . import api

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(email_or_token, password):
    if email_or_token == '':
        return False
    if password == '':
        print("Entrou")
        g.current_user = Usuario.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    usuario = Usuario.query.filter_by(email=email_or_token).first()
    if not usuario:
        return False
    g.current_user = usuario
    g.token_used = False
    return usuario.verify_senha(password)

@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')

@api.before_request
@auth.login_required
def before_request():
    if not g.current_user.confirmado:
    #if not True:
        return forbidden('Unconfirmed account')

@api.route('/tokens/', methods=['POST'])
def get_token():
    if g.token_used:
        return unauthorized('Invalid credentials')
    return jsonify({
        'token': g.current_user.generate_auth_token(expiration=3600), 
        'expiration': 3600})