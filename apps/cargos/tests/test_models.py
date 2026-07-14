"""Testes unitários dos models de cargos (e BaseModel via Cargo)."""

import uuid

import pytest
from django.utils import timezone

from cargos.models import Cargo

pytestmark = pytest.mark.django_db


def test_base_model_preenche_uuid_e_timestamps():
    """BaseModel gera UUID e datas ao criar."""
    cargo = Cargo.objects.create(nome="Teste")
    assert cargo.uuid is not None
    assert cargo.criado_em is not None
    assert cargo.atualizado_em is not None
    assert isinstance(cargo.uuid, uuid.UUID)
    assert isinstance(cargo.criado_em, timezone.datetime)
    assert isinstance(cargo.atualizado_em, timezone.datetime)


def test_cargo_tem_campos_esperados():
    """Cargo expõe os campos do domínio."""
    fields = [field.name for field in Cargo._meta.fields]
    for field in ["uuid", "nome", "codigo", "criado_em", "atualizado_em"]:
        assert field in fields


def test_cargo_str_retorna_nome():
    """__str__ do cargo é o nome."""
    cargo = Cargo.objects.create(nome="Analista", codigo=10)
    assert str(cargo) == "Analista"


def test_cargo_codigo_default_zero():
    """Codigo default é 0 quando não informado."""
    cargo = Cargo.objects.create(nome="Sem código explícito")
    assert cargo.codigo == 0


def test_cargo_persiste_codigo():
    """Cargo grava codigo informado."""
    cargo = Cargo.objects.create(nome="Professor", codigo=4123)
    cargo.refresh_from_db()
    assert cargo.codigo == 4123


def test_cargo_db_table():
    """Tabela física do Cargo é cargos."""
    assert Cargo._meta.db_table == "cargos"


def test_cargo_ordering_por_nome():
    """Ordering padrão do Cargo é por nome."""
    Cargo.objects.create(nome="Zeta")
    Cargo.objects.create(nome="Alfa")
    nomes = list(Cargo.objects.values_list("nome", flat=True))
    assert nomes == ["Alfa", "Zeta"]
