import os
import click
from flask_migrate import Migrate
from app import create_app, db
from app.models import *

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)
    
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Usuario=Usuario, Tipo_Usuario=Tipo_Usuario, Estado=Estado, 
                Cidade=Cidade, Bairro=Bairro, Endereco=Endereco, Funcionario=Funcionario,
                Cliente=Cliente, Fonecedor=Fornecedor, Tipo_Quantidade=Tipo_Quantidade, 
                Produto=Produto, Compra=Compra, Equipamento=Equipamento,
                produto_compra=produto_compra,equipamento_compra=equipamento_compra, 
                Tipo_Servico=Tipo_Servico, produto_tipo_servico=produto_tipo_servico, 
                equipamento_tipo_servico=equipamento_tipo_servico, Servico=Servico,
                produto_servico=produto_servico, equipamento_servico=equipamento_servico,
                tipo_servico_servico=tipo_servico_servico, Agenda=Agenda, 
                TipoUsuarioSchema=TipoUsuarioSchema, Permissao=Permissao)

@app.cli.command()
@click.argument('test_names', nargs=-1)
def test(test_names):
    """Run the unit tests."""
    import unittest
    if test_names:
        tests = unittest.TestLoader().loadTestsFromNames(test_names)
    else:
        tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)