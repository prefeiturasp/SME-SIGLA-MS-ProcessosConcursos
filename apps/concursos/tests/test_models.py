"""Testes unitários dos models de concursos."""

import pytest

from concursos.models import Concurso

pytestmark = pytest.mark.django_db


def test_concurso_tem_campos_esperados():
    """Concurso expõe campos base e de domínio."""
    fields = [field.name for field in Concurso._meta.fields]
    for field in [
        "uuid",
        "nome",
        "criado_em",
        "atualizado_em",
        "numero_processo",
        "codigo",
        "ano_edital",
        "banca_responsavel",
        "status",
    ]:
        assert field in fields


def test_concurso_str_retorna_nome():
    """__str__ do concurso é o nome."""
    concurso = Concurso.objects.create(nome="Edital 2026")
    assert str(concurso) == "Edital 2026"


def test_concurso_novos_campos_defaults():
    """Concurso criado sem campos novos usa defaults seguros."""
    concurso = Concurso.objects.create(nome="Concurso Novos Campos")
    assert concurso.status == "ATIVO"
    assert concurso.banca_responsavel == ""
    assert concurso.ano_edital is None
    assert concurso.numero_processo == ""


def test_concurso_novos_campos_atribuidos():
    """Concurso persiste os campos novos."""
    concurso = Concurso.objects.create(
        nome="Concurso 2026",
        ano_edital=2026,
        banca_responsavel="FGV",
        status="INATIVO",
        numero_processo="6016202200779764",
    )
    concurso.refresh_from_db()
    assert concurso.ano_edital == 2026
    assert concurso.banca_responsavel == "FGV"
    assert concurso.status == "INATIVO"
    assert concurso.numero_processo == "6016202200779764"


def test_concurso_criado_sem_codigo_fica_null():
    """Concurso criado sem codigo fica com codigo NULL."""
    concurso = Concurso.objects.create(nome="Concurso Sem Codigo")
    assert concurso.codigo is None


def test_get_or_create_codigo_real_nao_colide_com_manuais():
    """get_or_create por codigo real não casa concursos manuais."""
    Concurso.objects.create(nome="Manual 1")
    Concurso.objects.create(nome="Manual 2")
    concurso, created = Concurso.objects.get_or_create(
        codigo=100, defaults={"nome": "Importado"}
    )
    assert created is True
    assert concurso.nome == "Importado"
    assert Concurso.objects.count() == 3


def test_concurso_db_table():
    """Tabela física é concursos."""
    assert Concurso._meta.db_table == "concursos"


def test_concurso_m2m_cargos(cargo_analista):
    """Concurso vincula cargos via M2M."""
    concurso = Concurso.objects.create(nome="Com Cargo")
    concurso.cargos.add(cargo_analista)
    assert list(concurso.cargos.all()) == [cargo_analista]
