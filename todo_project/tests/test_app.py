"""
Testes básicos para a aplicação Flask
"""
import pytest
import sys
import os

# Adicionar o diretório pai ao path para importar a app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from todo_project import app, db
from todo_project.observability import record_user_action


@pytest.fixture
def client():
    """Cria um cliente de teste da aplicação"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


def test_app_exists():
    """Testa se a aplicação Flask existe"""
    assert app is not None


def test_app_is_testing(client):
    """Testa se a app está em modo testing"""
    assert app.config['TESTING'] is True


def test_about_route(client):
    """Testa a rota /about"""
    response = client.get('/about')
    assert response.status_code == 200


def test_about_route_redirect(client):
    """Testa se / redireciona para /about"""
    response = client.get('/')
    assert response.status_code in [200, 302]


def test_login_route(client):
    """Testa se a rota de login é acessível"""
    response = client.get('/login')
    assert response.status_code == 200


def test_register_route(client):
    """Testa se a rota de registro é acessível"""
    response = client.get('/register')
    assert response.status_code == 200


def test_404_error(client):
    """Testa se páginas inválidas retornam 404"""
    response = client.get('/pagina-inexistente')
    assert response.status_code == 404


def test_metrics_route(client):
    """Testa se a rota de métricas expõe o formato Prometheus"""
    record_user_action('test', 'success')
    response = client.get('/metrics')
    assert response.status_code == 200
    assert b'todo_app_user_actions_total' in response.data
