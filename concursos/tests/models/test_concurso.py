"""Módulo tests/models/test_concurso."""

import pytest

from concursos.models import Concurso

pytestmark = pytest.mark.django_db


def test_concurso_model_fields():
    """Verifica concurso model fields."""
    fields = [field.name for field in Concurso._meta.fields]
    expected_fields = ["uuid", "nome", "criado_em", "atualizado_em"]
    for field in expected_fields:
        assert field in fields


def test_concurso_novos_campos_defaults():
    """Concurso criado sem os campos novos usa defaults seguros."""
    concurso = Concurso.objects.create(nome="Concurso Novos Campos")
    assert concurso.ativo is True
    assert concurso.banca_responsavel == ""
    assert concurso.ano_edital is None
    assert concurso.numero_processo == ""


def test_concurso_novos_campos_atribuidos():
    """Concurso persiste os campos novos e numero_processo textual."""
    concurso = Concurso.objects.create(
        nome="Concurso 2026",
        ano_edital=2026,
        banca_responsavel="FGV",
        ativo=False,
        numero_processo="6016202200779764",
    )
    concurso.refresh_from_db()
    assert concurso.ano_edital == 2026
    assert concurso.banca_responsavel == "FGV"
    assert concurso.ativo is False
    assert concurso.numero_processo == "6016202200779764"


def test_concurso_criado_sem_codigo_fica_null():
    """Concurso criado sem codigo fica com codigo NULL (nao 0)."""
    concurso = Concurso.objects.create(nome="Concurso Sem Codigo")
    assert concurso.codigo is None


def test_get_or_create_codigo_real_nao_colide_com_manuais():
    """get_or_create por codigo real nao casa concursos manuais.

    Concursos manuais ficam com codigo NULL, entao um
    get_or_create com codigo real da API cria um novo registro
    em vez de colidir/atualizar um dos manuais.
    """
    Concurso.objects.create(nome="Manual 1")
    Concurso.objects.create(nome="Manual 2")
    concurso, created = Concurso.objects.get_or_create(
        codigo=100, defaults={"nome": "Importado"}
    )
    assert created is True
    assert concurso.nome == "Importado"
    assert Concurso.objects.count() == 3
