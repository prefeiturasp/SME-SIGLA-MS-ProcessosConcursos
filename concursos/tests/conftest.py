"""Módulo tests/conftest."""
import uuid

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from concursos.models import Cargo, Concurso


@pytest.fixture
def api_client():
    """Fixture para criar um cliente API de teste.
    
    Returns:
        Resultado da operação.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    return APIClient()


@pytest.fixture
def user():
    """Fixture para criar um usuário de teste.
    
    Returns:
        Resultado da operação.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    return User.objects.create_user(
        username="testuser", password="testpass123", email="test@example.com"
    )


@pytest.fixture
def authenticated_client(api_client, user):
    """Fixture para criar um cliente API autenticado.
    
    Args:
        api_client: Cliente de API para requisições de teste.
        user: Parâmetro user da operação.
    
    Returns:
        Resultado da operação.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def cargo_analista():
    """Fixture para criar um cargo de analista.
    
    Returns:
        Resultado da operação.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    return Cargo.objects.create(nome="Analista de Sistemas")


@pytest.fixture
def cargo_desenvolvedor():
    """Fixture para criar um cargo de desenvolvedor.
    
    Returns:
        Resultado da operação.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    return Cargo.objects.create(nome="Desenvolvedor Backend")


@pytest.fixture
def cargo_professor():
    """Fixture para criar um cargo de professor.
    
    Returns:
        Resultado da operação.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    return Cargo.objects.create(nome="Professor de Matemática")


@pytest.fixture
def cargos(cargo_analista, cargo_desenvolvedor, cargo_professor):
    """Fixture para criar múltiplos cargos de teste.
    
    Args:
        cargo_analista: Parâmetro cargo analista da operação.
        cargo_desenvolvedor: Parâmetro cargo desenvolvedor da operação.
        cargo_professor: Parâmetro cargo professor da operação.
    
    Returns:
        Resultado da operação.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    return {
        "analista": cargo_analista,
        "desenvolvedor": cargo_desenvolvedor,
        "professor": cargo_professor,
    }


@pytest.fixture
def concurso_analista(cargo_analista):
    """Fixture para criar um concurso de analista.
    
    Args:
        cargo_analista: Parâmetro cargo analista da operação.
    
    Returns:
        Resultado da operação.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    concurso = Concurso.objects.create(nome="Concurso de Analista")
    concurso.cargos.add(cargo_analista)
    return concurso


@pytest.fixture
def concurso_professor(cargo_professor):
    """Fixture para criar um concurso de professor.
    
    Args:
        cargo_professor: Parâmetro cargo professor da operação.
    
    Returns:
        Resultado da operação.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    concurso = Concurso.objects.create(nome="Concurso de Professor")
    concurso.cargos.add(cargo_professor)
    return concurso


@pytest.fixture
def concursos(concurso_analista, concurso_professor):
    """Fixture para criar múltiplos concursos de teste.
    
    Args:
        concurso_analista: Parâmetro concurso analista da operação.
        concurso_professor: Parâmetro concurso professor da operação.
    
    Returns:
        Resultado da operação.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    return {"analista": concurso_analista, "professor": concurso_professor}


@pytest.fixture
def cargo_data():
    """Fixture para dados de cargo válidos.
    
    Returns:
        Resultado da operação.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    return {"nome": "Novo Cargo de Teste"}


@pytest.fixture
def cargo_data_invalid():
    """Fixture para dados de cargo inválidos.
    
    Returns:
        Resultado da operação.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    return {
        "nome": ""  # Nome vazio é inválido
    }


@pytest.fixture
def cargo_data_long_name():
    """Fixture para dados de cargo com nome muito longo.
    
    Returns:
        Resultado da operação.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    return {
        "nome": "A" * 201  # Mais que max_length=200
    }


@pytest.fixture
def concurso_data(cargo_analista):
    """Fixture para dados de concurso válidos.
    
    Args:
        cargo_analista: Parâmetro cargo analista da operação.
    
    Returns:
        Resultado da operação.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    return {
        "nome": "Novo Concurso de Teste",
        "cargos_ids": [str(cargo_analista.uuid)],
    }


@pytest.fixture
def concurso_data_multiple_cargos(cargo_analista, cargo_desenvolvedor):
    """Fixture para dados de concurso com múltiplos cargos.
    
    Args:
        cargo_analista: Parâmetro cargo analista da operação.
        cargo_desenvolvedor: Parâmetro cargo desenvolvedor da operação.
    
    Returns:
        Resultado da operação.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    return {
        "nome": "Concurso com Múltiplos Cargos",
        "cargos_ids": [
            str(cargo_analista.uuid),
            str(cargo_desenvolvedor.uuid),
        ],
    }


@pytest.fixture
def concurso_data_no_cargos():
    """Fixture para dados de concurso sem cargos.
    
    Returns:
        Resultado da operação.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    return {"nome": "Concurso Sem Cargos"}


@pytest.fixture
def concurso_data_invalid():
    """Fixture para dados de concurso inválidos.
    
    Returns:
        Resultado da operação.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    return {
        "nome": "",  # Nome vazio é inválido
        "cargos_ids": ["invalid-uuid"],
    }


@pytest.fixture
def concurso_data_invalid_cargo_ids():
    """Fixture para dados de concurso com IDs de cargo inválidos.
    
    Returns:
        Resultado da operação.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    fake_uuid = uuid.uuid4()
    return {
        "nome": "Concurso com Cargo Inválido",
        "cargos_ids": [str(fake_uuid)],
    }


@pytest.fixture
def fake_uuid():
    """Fixture para gerar UUIDs falsos para testes.
    
    Returns:
        Resultado da operação.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    return uuid.uuid4()


@pytest.fixture
def multiple_cargos():
    """Fixture para criar múltiplos cargos para testes de paginação.
    
    Returns:
        Resultado da operação.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    cargos = []
    for i in range(25):
        cargo = Cargo.objects.create(nome=f"Cargo Teste {i}")
        cargos.append(cargo)
    return cargos


@pytest.fixture
def multiple_concursos():
    """Fixture para criar múltiplos concursos para testes de paginação.
    
    Returns:
        Resultado da operação.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    concursos = []
    for i in range(25):
        concurso = Concurso.objects.create(nome=f"Concurso Teste {i}")
        concursos.append(concurso)
    return concursos
