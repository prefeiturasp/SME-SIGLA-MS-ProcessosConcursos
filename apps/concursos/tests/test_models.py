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
        "banca_responsavel",
        "status",
        "situacao",
        "data_autorizacao",
        "data_abertura",
        "classificacao_final",
        "link_edital",
        "habilitados_geral",
        "habilitados_nna",
        "habilitados_pcd",
        "retificacoes",
        "data_homologacao",
        "data_prorrogacao",
        "vigencia_inicio",
        "vigencia_fim",
    ]:
        assert field in fields
    assert "ano_edital" not in fields


def test_concurso_str_retorna_nome():
    """__str__ do concurso é o nome."""
    concurso = Concurso.objects.create(nome="Edital 2026")
    assert str(concurso) == "Edital 2026"


def test_concurso_novos_campos_defaults():
    """Concurso criado sem campos novos usa defaults seguros."""
    concurso = Concurso.objects.create(nome="Concurso Novos Campos")
    assert concurso.status == "ATIVO"
    assert concurso.situacao == "INCOMPLETO"
    assert concurso.banca_responsavel == ""
    assert concurso.numero_processo == ""
    assert concurso.data_autorizacao is None
    assert concurso.data_abertura is None
    assert concurso.classificacao_final is None
    assert concurso.link_edital == ""
    assert concurso.habilitados_geral is None
    assert concurso.habilitados_nna is None
    assert concurso.habilitados_pcd is None
    assert concurso.retificacoes == ""
    assert concurso.data_homologacao is None
    assert concurso.data_prorrogacao is None
    assert concurso.vigencia_inicio is None
    assert concurso.vigencia_fim is None


def test_concurso_novos_campos_atribuidos():
    """Concurso persiste os campos novos."""
    concurso = Concurso.objects.create(
        nome="Concurso 2026",
        banca_responsavel="FGV",
        status="INATIVO",
        numero_processo="6016202200779764",
        data_autorizacao="2026-01-10",
        data_abertura="2026-02-15",
        classificacao_final="2026-06-30",
        link_edital="https://exemplo.gov.br/edital.pdf",
        habilitados_geral=100,
        habilitados_nna=20,
        habilitados_pcd=5,
        retificacoes="Retificação 01/2026.",
        data_homologacao="2026-07-01",
        data_prorrogacao="2028-07-01",
        vigencia_inicio="2026-07-01",
        vigencia_fim="2028-07-01",
    )
    concurso.refresh_from_db()
    assert concurso.banca_responsavel == "FGV"
    assert concurso.status == "INATIVO"
    assert concurso.numero_processo == "6016202200779764"
    assert str(concurso.data_autorizacao) == "2026-01-10"
    assert str(concurso.data_abertura) == "2026-02-15"
    assert str(concurso.classificacao_final) == "2026-06-30"
    assert concurso.link_edital == "https://exemplo.gov.br/edital.pdf"
    assert concurso.habilitados_geral == 100
    assert concurso.habilitados_nna == 20
    assert concurso.habilitados_pcd == 5
    assert concurso.retificacoes == "Retificação 01/2026."
    assert str(concurso.data_homologacao) == "2026-07-01"
    assert str(concurso.data_prorrogacao) == "2028-07-01"
    assert str(concurso.vigencia_inicio) == "2026-07-01"
    assert str(concurso.vigencia_fim) == "2028-07-01"


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
