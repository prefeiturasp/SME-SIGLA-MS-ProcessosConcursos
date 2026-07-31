"""Fixtures específicas do app concursos."""

import uuid

import pytest

from cargos.models import Cargo
from concursos.models import Concurso


@pytest.fixture
def cargo_desenvolvedor():
    """Cargo de desenvolvedor para vínculos M2M em concursos."""
    return Cargo.objects.create(nome="Desenvolvedor Backend")


@pytest.fixture
def concurso_analista(cargo_analista):
    """Concurso vinculado ao cargo de analista."""
    concurso = Concurso.objects.create(nome="Concurso de Analista")
    concurso.cargos.add(cargo_analista)
    return concurso


@pytest.fixture
def concursos(cargo_analista):
    """Dois concursos de referência para listagens."""
    concurso_a = Concurso.objects.create(
        nome="Concurso de Analista", situacao="COMPLETO"
    )
    concurso_a.cargos.add(cargo_analista)
    cargo_professor = Cargo.objects.create(nome="Professor de Matemática")
    concurso_p = Concurso.objects.create(
        nome="Concurso de Professor", situacao="EM_ANDAMENTO"
    )
    concurso_p.cargos.add(cargo_professor)
    return {"analista": concurso_a, "professor": concurso_p}


@pytest.fixture
def concurso_data(cargo_analista):
    """Payload válido de concurso com um cargo."""
    return {
        "nome": "Novo Concurso de Teste",
        "cargos_ids": [str(cargo_analista.uuid)],
        "numero_processo": "6016202200000001",
    }


@pytest.fixture
def concurso_data_multiple_cargos(cargo_analista, cargo_desenvolvedor):
    """Payload de concurso com múltiplos cargos."""
    return {
        "nome": "Concurso com Múltiplos Cargos",
        "cargos_ids": [
            str(cargo_analista.uuid),
            str(cargo_desenvolvedor.uuid),
        ],
        "numero_processo": "6016202200000002",
    }


@pytest.fixture
def concurso_data_no_cargos():
    """Payload de concurso sem cargos."""
    return {
        "nome": "Concurso Sem Cargos",
        "numero_processo": "6016202200000003",
    }


@pytest.fixture
def concurso_data_invalid_cargo_ids():
    """Payload de concurso com UUID de cargo inexistente."""
    return {
        "nome": "Concurso com Cargo Inválido",
        "cargos_ids": [str(uuid.uuid4())],
        "numero_processo": "6016202200000004",
    }
