"""Módulo tests/test_commands_criar_concursos_api."""

from unittest.mock import patch

import pytest
from django.core.management import call_command

from cargos.models import Cargo
from concursos.models import Concurso

pytestmark = pytest.mark.django_db


def _mock_cargos():
    # serviço retorna 'codigo' como str; comando faz int(...)
    """Executa  mock cargos."""
    return [
        {"codigo": "101", "nome": "Professor A"},
        {"codigo": "102", "nome": "Professor B"},
    ]


def _mock_concursos():
    # serviço retorna ints
    """Executa  mock concursos."""
    return [
        {
            "codigo": 1,
            "nome": "Concurso 2026",
            "numero_processo": 999,
            "cargos": [101, 102],
        }
    ]


@patch(
    "concursos.management.commands.criar_concursos_api.buscar_cargos_de_smeintegracao",
    autospec=True,
)
@patch(
    "concursos.management.commands.criar_concursos_api.buscar_concursos_de_smeintegracao",
    autospec=True,
)
def test_criar_concursos_api_cria_registros(
    mock_buscar_concursos, mock_buscar_cargos
):
    """Verifica criar concursos api cria registros."""
    mock_buscar_cargos.return_value = _mock_cargos()
    mock_buscar_concursos.return_value = _mock_concursos()

    call_command("criar_concursos_api")

    assert Cargo.objects.count() == 2
    assert Concurso.objects.count() == 1

    cargo_101 = Cargo.objects.get(codigo=101)
    Cargo.objects.get(codigo=102)
    concurso = Concurso.objects.get(codigo=1)

    # M2M vinculado
    cargos_ids = set(concurso.cargos.values_list("codigo", flat=True))
    assert cargos_ids == {101, 102}

    # Campos atualizados corretamente
    assert concurso.nome == "Concurso 2026"
    assert concurso.numero_processo == "999"
    assert cargo_101.nome == "Professor A"


@patch(
    "concursos.management.commands.criar_concursos_api.buscar_cargos_de_smeintegracao",
    autospec=True,
)
@patch(
    "concursos.management.commands.criar_concursos_api.buscar_concursos_de_smeintegracao",
    autospec=True,
)
def test_criar_concursos_api_atualiza_existentes(
    mock_buscar_concursos, mock_buscar_cargos
):
    # Pre-existentes com nomes antigos
    """Verifica criar concursos api atualiza existentes."""
    c101 = Cargo.objects.create(nome="Antigo 101", codigo=101)
    c102 = Cargo.objects.create(nome="Antigo 102", codigo=102)
    concurso = Concurso.objects.create(
        nome="Antigo Concurso", numero_processo="1", codigo=1
    )
    concurso.cargos.set([c101])

    mock_buscar_cargos.return_value = _mock_cargos()
    mock_buscar_concursos.return_value = _mock_concursos()

    call_command("criar_concursos_api")

    # Deve atualizar nomes e M2M
    c101.refresh_from_db()
    c102.refresh_from_db()
    concurso.refresh_from_db()

    assert c101.nome == "Professor A"
    assert c102.nome == "Professor B"
    assert concurso.nome == "Concurso 2026"
    assert concurso.numero_processo == "999"
    assert set(concurso.cargos.values_list("codigo", flat=True)) == {101, 102}


@patch(
    "concursos.management.commands.criar_concursos_api.buscar_cargos_de_smeintegracao",
    autospec=True,
)
@patch(
    "concursos.management.commands.criar_concursos_api.buscar_concursos_de_smeintegracao",
    autospec=True,
)
def test_criar_concursos_api_dry_run_nao_persiste(
    mock_buscar_concursos, mock_buscar_cargos
):
    """Verifica criar concursos api dry run nao persiste."""
    mock_buscar_cargos.return_value = _mock_cargos()
    mock_buscar_concursos.return_value = _mock_concursos()

    call_command("criar_concursos_api", "--dry-run")

    assert Cargo.objects.count() == 0
    assert Concurso.objects.count() == 0


@patch(
    "concursos.management.commands.criar_concursos_api.buscar_cargos_de_smeintegracao",
    autospec=True,
)
@patch(
    "concursos.management.commands.criar_concursos_api.buscar_concursos_de_smeintegracao",
    autospec=True,
)
def test_criar_concursos_api_quebra_api_nao_cria(
    mock_buscar_concursos, mock_buscar_cargos
):
    """Verifica criar concursos api quebra api nao cria."""
    mock_buscar_cargos.side_effect = Exception("API indisponível")
    mock_buscar_concursos.return_value = []

    # Não deve lançar, apenas abortar e não criar nada
    call_command("criar_concursos_api")

    assert Cargo.objects.count() == 0
    assert Concurso.objects.count() == 0


@patch(
    "concursos.management.commands.criar_concursos_api.buscar_cargos_de_smeintegracao",
    autospec=True,
)
@patch(
    "concursos.management.commands.criar_concursos_api.buscar_concursos_de_smeintegracao",
    autospec=True,
)
def test_criar_concursos_api_nao_colide_com_concursos_manuais(
    mock_buscar_concursos, mock_buscar_cargos
):
    """Importação com concursos manuais (codigo NULL) nao colide.

    Concursos criados manualmente pela tela de Cadastro nao
    enviam ``codigo`` e ficam com ``codigo=NULL``. A importação
    da API SME deve criar o concurso com o codigo real sem
    levantar ``MultipleObjectsReturned`` e sem afetar os
    concursos manuais.
    """
    manual_1 = Concurso.objects.create(nome="Manual 1")
    manual_2 = Concurso.objects.create(nome="Manual 2")

    mock_buscar_cargos.return_value = _mock_cargos()
    mock_buscar_concursos.return_value = _mock_concursos()

    call_command("criar_concursos_api")

    manual_1.refresh_from_db()
    manual_2.refresh_from_db()

    assert manual_1.codigo is None
    assert manual_1.nome == "Manual 1"
    assert manual_2.codigo is None
    assert manual_2.nome == "Manual 2"

    importado = Concurso.objects.get(codigo=1)
    assert importado.nome == "Concurso 2026"
    assert Concurso.objects.count() == 3
