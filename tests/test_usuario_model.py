import unittest
from app import create_app, db
from app.models import Usuario, Cliente


class UsuarioModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        u = Usuario(senha='cat')
        self.assertTrue(u.senha_hash is not None)

    def test_no_password_getter(self):
        u = Usuario(senha='cat')
        with self.assertRaises(AttributeError):
            u.senha

    def test_password_verification(self):
        u = Usuario(senha='cat')
        self.assertTrue(u.verify_senha('cat'))
        self.assertFalse(u.verify_senha('dog'))

    def test_password_salts_are_random(self):
        u = Usuario(senha='cat')
        u2 = Usuario(senha='cat')
        self.assertTrue(u.senha_hash != u2.senha_hash)
