"""Testes unitários dos models de autorizações publicadas."""

from datetime import date

import pytest

from autorizacoes.models import AutorizacaoPublicada
from cargos.models import Cargo

pytestmark = pytest.mark.django_db


def test_autorizacao_tem_campos_esperados():
    """Model expõe os campos do domínio."""
    fields = [field.name for field in AutorizacaoPublicada._meta.fields]
    for field in [
        "uuid",
        "cargo",
        "autorizacoes",
        "data_autorizacao",
        "observacao",
        "criado_em",
        "atualizado_em",
    ]:
        assert field in fields


def test_autorizacao_str():
    """__str__ começa com Autorização."""
    obj = AutorizacaoPublicada.objects.create()
    assert str(obj).startswith("Autorização ")


def test_autorizacao_com_cargo():
    """Vincula cargo e total de autorizações."""
    cargo = Cargo.objects.create(nome="Teste Cargo")
    obj = AutorizacaoPublicada.objects.create(cargo=cargo, autorizacoes=10)
    assert obj.cargo == cargo
    assert obj.autorizacoes == 10


def test_autorizacao_defaults():
    """Defaults: autorizacoes=0 e observacao vazia."""
    obj = AutorizacaoPublicada.objects.create()
    assert obj.autorizacoes == 0
    assert obj.observacao == ""
    assert obj.cargo is None
    assert obj.data_autorizacao is None


def test_autorizacao_com_data():
    """Persiste data_autorizacao."""
    obj = AutorizacaoPublicada.objects.create(
        autorizacoes=2, data_autorizacao=date(2026, 5, 1)
    )
    obj.refresh_from_db()
    assert obj.data_autorizacao == date(2026, 5, 1)


def test_autorizacao_db_table():
    """Tabela física é autorizacoes_publicadas."""
    assert AutorizacaoPublicada._meta.db_table == "autorizacoes_publicadas"
