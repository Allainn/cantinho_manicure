from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask import current_app, request, url_for
from flask_login import UserMixin, AnonymousUserMixin
from app.exceptions import ValidationError
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from marshmallow import fields
from marshmallow_sqlalchemy import ModelSchema
from . import login_manager

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

produto_compra = db.Table ('produto_compra',
   db.Column('produto_id', db.Integer, db.ForeignKey('produto.id'), nullable=False),
   db.Column('compra_id', db.Integer, db.ForeignKey('compra.id'), nullable=False),
   db.Column('valor', db.Numeric(10,2), nullable=False)
)

produto_tipo_servico = db.Table ('produto_tipo_servico',
   db.Column('produto_id', db.Integer, db.ForeignKey('produto.id'), nullable=False),
   db.Column('tipo_servico_id', db.Integer, db.ForeignKey('tipo_servico.id'), nullable=False),
   db.Column('quantidade', db.Integer, nullable=False)
)

equipamento_tipo_servico = db.Table ('equipamento_tipo_servico',
   db.Column('equipamento_id', db.Integer, db.ForeignKey('equipamento.id'), nullable=False),
   db.Column('tipo_servico_id', db.Integer, db.ForeignKey('tipo_servico.id'), nullable=False),
   db.Column('tempo', db.Integer, nullable=False)
)

equipamento_compra = db.Table ('equipamento_compra',
   db.Column('equipamento_id', db.Integer, db.ForeignKey('equipamento.id'), nullable=False),
   db.Column('compra_id', db.Integer, db.ForeignKey('compra.id'), nullable=False),
   db.Column('valor', db.Numeric(10,2), nullable=False)
)

produto_servico = db.Table ('produto_servico',
   db.Column('produto_id', db.Integer, db.ForeignKey('produto.id'), nullable=False),
   db.Column('servico_id', db.Integer, db.ForeignKey('servico.id'), nullable=False),
   db.Column('quantidade', db.Integer, nullable=False)
)

equipamento_servico = db.Table ('equipamento_servico',
   db.Column('equipamento_id', db.Integer, db.ForeignKey('equipamento.id'), nullable=False),
   db.Column('servico_id', db.Integer, db.ForeignKey('servico.id'), nullable=False),
   db.Column('tempo', db.Integer, nullable=False)
)

tipo_servico_servico = db.Table ('tipo_servico_servico',
   db.Column('tipo_servico_id', db.Integer, db.ForeignKey('tipo_servico.id'), nullable=False),
   db.Column('servico_id', db.Integer, db.ForeignKey('servico.id'), nullable=False),
)

class Permissao:
    VER_SERVICOS = 1
    VER_AGENDA = 2
    MARCAR_SERVICO = 4
    SOLICITAR_ORCAMENTO = 8
    CADASTRO_BASICO = 16
    ADMIN = 32

class Tipo_Usuario(db.Model):
    __tablename__ = 'tipo_usuario'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(64), unique=True, nullable=False)
    default = db.Column(db.Boolean, default=False, index=True, nullable=False)
    permissao = db.Column(db.Integer, nullable=False)

    usuarios = db.relationship('Usuario', backref='tipo_usuario', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Tipo_Usuario, self).__init__(**kwargs)
        if self.permissao is None:
            self.permissao = 0

    def __repr__(self):
        return '<Tipo Usuário %r>' % self.descricao

    def to_json(self):
        json_tipo_usuario = {
            'id': self.id,
            'url': url_for('api.get_tipo_usuario', id=self.id),
            'descricao': self.descricao,
        }
        return json_tipo_usuario

    @staticmethod
    def from_json(json_tipo_usuario):
        descricao = json_tipo_usuario.get('descricao')
        if descricao is None or descricao == '':
            raise ValidationError('tipo de usuario nao tem uma descricao')
        return Tipo_Usuario(descricao = descricao)

    def add_permissao(self, perm):
        if not self.tem_permissao(perm):
            self.permissao += perm

    def remove_permissao(self, perm):
        if not self.tem_permissao(perm):
            self.permissao -= perm

    def reset_permissao(self):
        self.permissao = 0

    def tem_permissao(self, perm):
        return self.permissao & perm == perm

    @staticmethod
    def inserir_tipos_usuarios():
        tipos_usuarios = {
            'Usuario': [Permissao.VER_SERVICOS],
            'Cliente': [Permissao.VER_AGENDA, Permissao.MARCAR_SERVICO, 
                        Permissao.SOLICITAR_ORCAMENTO, Permissao.VER_SERVICOS],
            'Funcionario': [Permissao.VER_AGENDA, Permissao.MARCAR_SERVICO, Permissao.SOLICITAR_ORCAMENTO,
                            Permissao.CADASTRO_BASICO, Permissao.VER_SERVICOS],
            'Administrador': [Permissao.VER_AGENDA, Permissao.MARCAR_SERVICO, Permissao.SOLICITAR_ORCAMENTO,
                              Permissao.CADASTRO_BASICO, Permissao.ADMIN, Permissao.VER_SERVICOS]
        }
        default_tipo_usuario = 'Usuario'
        for tp in tipos_usuarios:
            tipo_usuario = Tipo_Usuario.query.filter_by(descricao=tp).first()
            if tipo_usuario is None:
                tipo_usuario = Tipo_Usuario(descricao=tp)
            tipo_usuario.reset_permissao()
            for perm in tipos_usuarios[tp]:
                tipo_usuario.add_permissao(perm)
            tipo_usuario.default = (tipo_usuario.descricao == default_tipo_usuario)
            db.session.add(tipo_usuario)
        db.session.commit()

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(64), unique=True, index=True, nullable=False)
    email = db.Column(db.String(64), unique=True, index=True, nullable=False)
    senha_hash = db.Column(db.String(256), nullable=False)
    confirmado = db.Column(db.Boolean, default=True, nullable=False)
    tipo_usuario_id = db.Column(db.Integer, db.ForeignKey('tipo_usuario.id'), nullable=False)

    funcionarios = db.relationship('Funcionario', backref='usuario', uselist = False)
    clientes = db.relationship('Cliente', backref='usuario', uselist = False)

    def __init__(self, **kwargs):
        super(Usuario, self).__init__(**kwargs)
        if self.tipo_usuario is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.tipo_usuario = Tipo_Usuario.query.filter_by(descricao='Administrador').first()
            if self.tipo_usuario is None:
                self.tipo_usuario = Tipo_Usuario.query.filter_by(default=True).first()

    @property
    def senha(self):
        raise AttributeError('A senha não é um atributo legível')

    @senha.setter
    def senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def verify_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    def __repr__(self):
        return '<Usuario %r>' % self.login

    def to_json(self):
        json_usuario = {
            'id': self.id,
            'url': url_for('api.get_usuario', id=self.id),
            'login': self.login,
            'email': self.email,
            'tipo_usuario': self.tipo_usuario.to_json(),
        }
        return json_usuario

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id}).decode('utf-8')

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'], 
                       expires_in=expiration)
        return s.dumps({'id': self.id}).decode('utf-8')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return Usuario.query.get(data['id'])

    def can(self, perm):
        return self.tipo_usuario is not None and self.tipo_usuario.tem_permissao(perm)

    def is_administrador(self):
        return self.can(Permissao.ADMIN)

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
            print('1111')
        except:
            print('2222')
            return False
        if data.get('confirm') != self.id:
            print('3333')
            return False
        self.confirmado = True
        db.session.add(self)
        return True

class Usuario_Anonimo(AnonymousUserMixin):
    id = None
    def can(self, perm):
        return False

    def is_administrador(self):
        return False

login_manager.anonymous_user = Usuario_Anonimo

class Estado(db.Model):
    __tablename__ = 'estado'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(25), unique=True, nullable=False)
    uf = db.Column(db.String(2), unique=True, nullable=False)

    cidade = db.relationship('Cidade', backref='estado', lazy='dynamic')

    def to_json(self):
        json_estado = {
            'id': self.id,
            'url': url_for('api.get_estado', id=self.id),
            'nome': self.nome,
            'uf': self.uf,
        }
        return json_estado

    def __repr__(self):
        return '<Estado %r>' % self.descricao

class Cidade(db.Model):
    __tablename__ = 'cidade'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(64), nullable=False)
    estado_id = db.Column(db.Integer, db.ForeignKey('estado.id'), nullable=False)

    bairro = db.relationship('Bairro', backref='cidade', lazy='dynamic')

    def to_json(self):
        json_cidade = {
            'id': self.id,
            'url': url_for('api.get_cidade', id=self.id),
            'descricao': self.descricao,
            'estado': self.estado.to_json(),
        }
        return json_cidade

    def __repr__(self):
        return '<Cidade %r>' % self.descricao

class Bairro(db.Model):
    __tablename__ = 'bairro'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(64), nullable=False)
    cidade_id = db.Column(db.Integer, db.ForeignKey('cidade.id'), nullable=False)

    def to_json(self):
        json_bairro = {
            'id': self.id,
            'url': url_for('api.get_bairro', id=self.id),
            'descricao': self.descricao,
            'cidade': self.cidade.to_json(),
        }
        return json_bairro

    endereco = db.relationship('Endereco', backref='bairro', lazy='dynamic')

    def __repr__(self):
        return '<Bairro %r>' % self.descricao

class Endereco(db.Model):
    __tablename__ = 'endereco'
    id = db.Column(db.Integer, primary_key=True)
    rua = db.Column(db.String(64), nullable=False)
    complemento = db.Column(db.String(64), nullable=True)
    bairro_id = db.Column(db.Integer, db.ForeignKey('bairro.id'), nullable=False)

    def to_json(self):
        json_endereco = {
            'id': self.id,
            'url': url_for('api.get_endereco', id=self.id),
            'rua': self.rua,
            'complemento': self.complemento,
            'bairro': self.bairro.to_json(),
        }
        return json_endereco

    funcionarios = db.relationship('Funcionario', backref='endereco', lazy='dynamic')
    clientes = db.relationship('Cliente', backref='endereco', lazy='dynamic')
    fornecedores = db.relationship('Fornecedor', backref='endereco', lazy='dynamic')

    def __repr__(self):
        return '<Endereco %r>' % self.rua

class Funcionario(db.Model):
    __tablename__ = 'funcionario'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(64), nullable=False)
    telefone1 = db.Column(db.String(20), nullable=True)
    telefone2 = db.Column(db.String(20), nullable=True)
    data_nascimento = db.Column(db.Date, nullable=True)
    endereco_id = db.Column(db.Integer, db.ForeignKey('endereco.id'), nullable=False)
    numero = db.Column(db.String(10), nullable=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

    def to_json(self):
        json_funcionario = {
            'id': self.id,
            'url': url_for('api.get_endereco', id=self.id),
            'nome': self.nome,
            'telefone1': self.telefone1,
            'telefone2': self.telefone2,
            'data_nascimento': self.data_nascimento,
            'endereco': self.endereco.to_json(),
            'numero': self.numero,
            'usuario': self.usuario.to_json()
        }
        return json_funcionario

    def __repr__(self):
        return '<Funcionario %r>' % self.nome

class Cliente(db.Model):
    __tablename__ = 'cliente'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(64), nullable=False)
    endereco_id = db.Column(db.Integer, db.ForeignKey('endereco.id'), nullable=False)
    numero = db.Column(db.String(10), nullable=True)
    telefone1 = db.Column(db.String(20), nullable=False)
    telefone2 = db.Column(db.String(20), nullable=True)
    data_nascimento = db.Column(db.Date, nullable=True)
    instagram = db.Column(db.String(64), nullable=True)
    facebook = db.Column(db.String(64), nullable=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

    def to_json(self):
        json_cliente = {
            'id': self.id,
            'url': url_for('api.get_endereco', id=self.id),
            'nome': self.nome,
            'endereco': self.endereco.to_json(),
            'numero': self.numero,
            'telefone1': self.telefone1,
            'telefone2': self.telefone2,
            'data_nascimento': self.data_nascimento,
            'instagram': self.instagram,
            'facebook': self.facebook,
            'usuario': self.usuario.to_json()
        }
        return json_cliente

    def __repr__(self):
        return '<Cliente %r>' % self.nome

class Fornecedor(db.Model):
    __tablename__ = 'fornecedor'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=True)
    endereco_id = db.Column(db.Integer, db.ForeignKey('endereco.id'), nullable=False)
    numero = db.Column(db.String(10), nullable=True)
    telefone1 = db.Column(db.String(20), nullable=False)
    telefone2 = db.Column(db.String(20), nullable=True)
    data_nascimento = db.Column(db.Date, nullable=True)
    site = db.Column(db.String(64), nullable=True)
    instagram = db.Column(db.String(64), nullable=True)
    facebook = db.Column(db.String(64), nullable=True)
    observacao = db.Column(db.String(256), nullable=True)

    def to_json(self):
        json_fornecedor = {
            'id': self.id,
            'url': url_for('api.get_endereco', id=self.id),
            'nome': self.nome,
            'email': self.email,
            'endereco': self.endereco.to_json(),
            'numero': self.numero,
            'telefone1': self.telefone1,
            'telefone2': self.telefone2,
            'data_nascimento': self.data_nascimento,
            'site': self.site,
            'instagram': self.instagram,
            'facebook': self.facebook,
            'observacao': self.observacao
        }
        return json_fornecedor

    def __repr__(self):
        return '<Fornecedor %r>' % self.nome

class Tipo_Quantidade(db.Model):
    __tablename__ = 'tipo_quantidade'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(64), nullable=True)
    sigla = db.Column(db.String(2), nullable=False)

    def __repr__(self):
        return '<Tipo Quantidade %r>' % self.sigla

class Produto(db.Model):
    __tablename__ = 'produto'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(64), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    tipo_quantidade_id = db.Column(db.Integer, db.ForeignKey('tipo_quantidade.id'), nullable=False)
    preco_un = db.Column(db.Numeric(10,2), nullable=False)
    observacao = db.Column(db.String(256), nullable=True)

    compras = db.relationship('Compra', 
                               secondary = produto_compra,  
                               backref=db.backref('produto', lazy='dynamic'),
                               lazy='dynamic')

class Equipamento(db.Model):
    __tablename__ = 'equipamento'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(64), nullable=False)
    tempo = db.Column(db.Integer, nullable=False)
    preco_tempo = db.Column(db.Numeric(10,2), nullable=False)
    observacao = db.Column(db.String(256), nullable=True)

    compras = db.relationship('Compra', 
                               secondary = equipamento_compra,  
                               backref=db.backref('equipamento', lazy='dynamic'),
                               lazy='dynamic')

class Compra(db.Model):
    __tablename__ = 'compra'
    id = db.Column(db.Integer, primary_key=True)
    fornecedor_id = db.Column(db.Integer, db.ForeignKey('fornecedor.id'), nullable=False)
    valor = db.Column(db.Numeric(10,2), nullable=False)
    data = db.Column(db.Date, nullable=False)
    observacao = db.Column(db.String(256), nullable=True)

    produtos = db.relationship('Produto', 
                               secondary = produto_compra, 
                               backref=db.backref('compra', lazy='dynamic'), 
                               lazy='dynamic')
    equipamentos = db.relationship('Equipamento', 
                                   secondary = equipamento_compra,
                                   backref=db.backref('compra', lazy='dynamic'), 
                                   lazy='dynamic')

class Tipo_Servico(db.Model):
    __tablename__ = 'tipo_servico'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(64), nullable=False)
    tempo = db.Column(db.Integer, nullable=False)
    valor = db.Column(db.Numeric(10,2), nullable=False)
    observacao = db.Column(db.String(256), nullable=True)

    produtos = db.relationship('Produto', 
                               secondary = produto_tipo_servico, 
                               backref=db.backref('tipo_servico', lazy='dynamic'), 
                               lazy='dynamic')
    equipamentos = db.relationship('Equipamento', 
                                   secondary = equipamento_tipo_servico,
                                   backref=db.backref('tipo_servico', lazy='dynamic'), 
                                   lazy='dynamic')

class Servico(db.Model):
    __tablename__ = 'servico'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    valor = db.Column(db.Numeric(10,2), nullable=False)
    tempo = db.Column(db.Integer, nullable=False)
    observacao = db.Column(db.String(256), nullable=True)

    tipos_servico = db.relationship('Tipo_Servico', 
                                    secondary = tipo_servico_servico, 
                                    backref=db.backref('servico', lazy='dynamic'), 
                                    lazy='dynamic')
    produtos = db.relationship('Produto', 
                               secondary = produto_servico, 
                               backref=db.backref('servico', lazy='dynamic'), 
                               lazy='dynamic')
    equipamentos = db.relationship('Equipamento', 
                                   secondary = equipamento_servico,
                                   backref=db.backref('servico', lazy='dynamic'), 
                                   lazy='dynamic')
    agenda = db.relationship('Agenda', backref='servico', uselist = False)

class Agenda(db.Model):
    __tablename__ = 'agenda'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    servico_id = db.Column(db.Integer, db.ForeignKey('servico.id'), nullable=False)
    data = db.Column(db.DateTime, nullable=False)
    observacao = db.Column(db.String(256), nullable=True)

class TipoUsuarioSchema(ModelSchema):
    class Meta:
        model = Tipo_Usuario

class UsuarioSchema(ModelSchema):
    class Meta:
        model = Usuario

class BairroSchema(ModelSchema):
    class Meta:
        model = Bairro

class EnderecoSchema(ModelSchema):
    class Meta:
        model = Endereco

class FuncionarioSchema(ModelSchema):
    class Meta:
        model = Funcionario

class ClienteSchema(ModelSchema):
    class Meta:
        model = Cliente

class FornecedorSchema(ModelSchema):
    class Meta:
        model = Fornecedor