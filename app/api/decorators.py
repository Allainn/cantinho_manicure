from functools import wraps
from flask import abort, g
from .errors import forbidden
#from flask_login import current_user
from ..models import Permissao

def permissao_requerida(permissao):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.current_user.can(permissao):
                return(forbidden("Acesso não autorizado"))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_requerido(f):
    return permissao_requerida(Permissao.ADMIN)(f)