from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask import current_app, request, url_for
from app.exceptions import ValidationError

produto_compra = db.Table ('produto_compra',
   db.Column('produto_id', db.Integer, db.ForeignKey('produto.id')),
   db.Column('compra_id', db.Integer, db.ForeignKey('compra.id')),
   db.Column('valor', db.Numeric(10,2))
)

produto_tipo_servico = db.Table ('produto_tipo_servico',
   db.Column('produto_id', db.Integer, db.ForeignKey('produto.id')),
   db.Column('tipo_servico_id', db.Integer, db.ForeignKey('tipo_servico.id')),
   db.Column('quantidade', db.Integer)
)

equipamento_tipo_servico = db.Table ('equipamento_tipo_servico',
   db.Column('equipamento_id', db.Integer, db.ForeignKey('equipamento.id')),
   db.Column('tipo_servico_id', db.Integer, db.ForeignKey('tipo_servico.id')),
   db.Column('tempo', db.Integer)
)

equipamento_compra = db.Table ('equipamento_compra',
   db.Column('equipamento_id', db.Integer, db.ForeignKey('equipamento.id')),
   db.Column('compra_id', db.Integer, db.ForeignKey('compra.id')),
   db.Column('valor', db.Numeric(10,2))
)

produto_servico = db.Table ('produto_servico',
   db.Column('produto_id', db.Integer, db.ForeignKey('produto.id')),
   db.Column('servico_id', db.Integer, db.ForeignKey('servico.id')),
   db.Column('quantidade', db.Integer)
)

equipamento_servico = db.Table ('equipamento_servico',
   db.Column('equipamento_id', db.Integer, db.ForeignKey('equipamento.id')),
   db.Column('servico_id', db.Integer, db.ForeignKey('servico.id')),
   db.Column('tempo', db.Integer)
)

tipo_servico_servico = db.Table ('tipo_servico_servico',
   db.Column('tipo_servico_id', db.Integer, db.ForeignKey('tipo_servico.id')),
   db.Column('servico_id', db.Integer, db.ForeignKey('servico.id')),
)

class Tipo_Usuario(db.Model):
    __tablename__ = 'tipo_usuario'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(64), unique=True)

    users = db.relationship('Usuario', backref='tipo_usuario', lazy='dynamic')

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

class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    senha_hash = db.Column(db.String(256))
    tipo_usuario_id = db.Column(db.Integer, db.ForeignKey('tipo_usuario.id'))

    funcionarios = db.relationship('Funcionario', backref='usuario', uselist = False)
    clientes = db.relationship('Cliente', backref='usuario', uselist = False)

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

class Estado(db.Model):
    __tablename__ = 'estado'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(2), unique=True)

    cidade = db.relationship('Cidade', backref='estado', lazy='dynamic')

    def __repr__(self):
        return '<Estado %r>' % self.descricao

class Cidade(db.Model):
    __tablename__ = 'cidade'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(64))
    estado_id = db.Column(db.Integer, db.ForeignKey('estado.id'))

    bairro = db.relationship('Bairro', backref='cidade', lazy='dynamic')

    def __repr__(self):
        return '<Cidade %r>' % self.descricao

class Bairro(db.Model):
    __tablename__ = 'bairro'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(64))
    cidade_id = db.Column(db.Integer, db.ForeignKey('cidade.id'))

    endereco = db.relationship('Endereco', backref='bairro', lazy='dynamic')

    def __repr__(self):
        return '<Bairro %r>' % self.descricao

class Endereco(db.Model):
    __tablename__ = 'endereco'
    id = db.Column(db.Integer, primary_key=True)
    rua = db.Column(db.String(64))
    complemento = db.Column(db.String(64), nullable=True)
    bairro_id = db.Column(db.Integer, db.ForeignKey('bairro.id'))

    funcionarios = db.relationship('Funcionario', backref='endereco', lazy='dynamic')
    clientes = db.relationship('Cliente', backref='endereco', lazy='dynamic')
    fornecedores = db.relationship('Fornecedor', backref='endereco', lazy='dynamic')

    def __repr__(self):
        return '<Endereco %r>' % self.rua

class Funcionario(db.Model):
    __tablename__ = 'funcionario'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(64))
    telefone1 = db.Column(db.String(20), nullable=True)
    telefone2 = db.Column(db.String(20), nullable=True)
    data_nascimento = db.Column(db.Date, nullable=True)
    endereco_id = db.Column(db.Integer, db.ForeignKey('endereco.id'))
    numero = db.Column(db.String(10), nullable=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))

    def __repr__(self):
        return '<Funcionario %r>' % self.nome

class Cliente(db.Model):
    __tablename__ = 'cliente'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(64))
    endereco_id = db.Column(db.Integer, db.ForeignKey('endereco.id'))
    numero = db.Column(db.String(10), nullable=True)
    telefone1 = db.Column(db.String(20))
    telefone2 = db.Column(db.String(20), nullable=True)
    data_nascimento = db.Column(db.Date, nullable=True)
    instagram = db.Column(db.String(64))
    facebook = db.Column(db.String(64))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))

    def __repr__(self):
        return '<Cliente %r>' % self.nome

class Fornecedor(db.Model):
    __tablename__ = 'fornecedor'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(64))
    email = db.Column(db.String(64), nullable=True)
    endereco_id = db.Column(db.Integer, db.ForeignKey('endereco.id'))
    numero = db.Column(db.String(10), nullable=True)
    telefone1 = db.Column(db.String(20))
    telefone2 = db.Column(db.String(20), nullable=True)
    data_nascimento = db.Column(db.Date, nullable=True)
    site = db.Column(db.String(64))
    instagram = db.Column(db.String(64))
    facebook = db.Column(db.String(64))
    observacao = db.Column(db.String(256))

    def __repr__(self):
        return '<Fornecedor %r>' % self.nome

class Tipo_Quantidade(db.Model):
    __tablename__ = 'tipo_quantidade'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(64), nullable=True)
    sigla = db.Column(db.String(2))

    def __repr__(self):
        return '<Tipo Quantidade %r>' % self.sigla

class Produto(db.Model):
    __tablename__ = 'produto'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(64))
    quantidade = db.Column(db.Integer)
    tipo_quantidade_id = db.Column(db.Integer, db.ForeignKey('tipo_quantidade.id'))
    preco_un = db.Column(db.Numeric(10,2))
    observacao = db.Column(db.String(256))

    compras = db.relationship('Compra', 
                               secondary = produto_compra,  
                               backref=db.backref('produto', lazy='dynamic'),
                               lazy='dynamic')

class Equipamento(db.Model):
    __tablename__ = 'equipamento'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(64))
    tempo = db.Column(db.Integer)
    preco_tempo = db.Column(db.Numeric(10,2))
    observacao = db.Column(db.String(256))

    compras = db.relationship('Compra', 
                               secondary = equipamento_compra,  
                               backref=db.backref('equipamento', lazy='dynamic'),
                               lazy='dynamic')

class Compra(db.Model):
    __tablename__ = 'compra'
    id = db.Column(db.Integer, primary_key=True)
    fornecedor_id = db.Column(db.Integer, db.ForeignKey('fornecedor.id'))
    valor = db.Column(db.Numeric(10,2))
    data = db.Column(db.Date)
    observacao = db.Column(db.String(256))

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
    descricao = db.Column(db.String(64))
    tempo = db.Column(db.Integer)
    valor = db.Column(db.Numeric(10,2))
    observacao = db.Column(db.String(256))

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
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'))
    valor = db.Column(db.Numeric(10,2))
    tempo = db.Column(db.Integer)
    observacao = db.Column(db.String(256))

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
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'))
    servico_id = db.Column(db.Integer, db.ForeignKey('servico.id'))
    data = db.Column(db.DateTime)
    observacao = db.Column(db.String(256))