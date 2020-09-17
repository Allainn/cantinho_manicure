from flask import jsonify
from app.exceptions import ValidationError
from . import api


# def bad_request(message):
#     response = jsonify({'error': 'bad request', 'message': message})
#     response.status_code = 400
#     return response


def unauthorized(message):
    response = jsonify({'error': 'unauthorized', 'message': message})
    response.status_code = 401
    return response


def forbidden(message):
    response = jsonify({'error': 'forbidden', 'message': message})
    response.status_code = 403
    return response

@api.errorhandler(500)
def not_found(message):
    return jsonify(error=str(message)), 500

@api.errorhandler(400)
def bad_request(message):
    return jsonify(error=str(message)), 400

@api.errorhandler(404)
def not_found(message):
    return jsonify(error=str(message)), 404

@api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])
