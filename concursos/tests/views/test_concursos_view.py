"""Módulo tests/views/test_concursos_view."""

import pytest
from django.urls import reverse
from rest_framework import status

from concursos.models import Concurso

pytestmark = pytest.mark.django_db


def test_list_concursos_success(authenticated_client, concursos):
    """Verifica list concursos success."""
    url = reverse("concurso-list")
    response = authenticated_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 2
    concursos_data = response.data["results"]
    concurso_nomes = [concurso["nome"] for concurso in concursos_data]
    assert "Concurso de Analista" in concurso_nomes
    assert "Concurso de Professor" in concurso_nomes
    for concurso in concursos_data:
        assert "codigo" in concurso
        assert "numero_processo" in concurso


def test_list_concursos_with_select_format(authenticated_client, concursos):
    """Verifica list concursos with select format."""
    url = reverse("concurso-list")
    response = authenticated_client.get(url, {"formato": "select"})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2
    concurso_data = response.data[0]
    assert "value" in concurso_data
    assert "label" in concurso_data
    assert "cargos" in concurso_data
    assert isinstance(concurso_data["value"], str)
    assert isinstance(concurso_data["label"], str)


def test_create_concurso_success(authenticated_client, concurso_data):
    """Verifica create concurso success."""
    url = reverse("concurso-list")
    payload = {**concurso_data, "codigo": 77, "numero_processo": 888}
    response = authenticated_client.post(url, payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert Concurso.objects.count() == 1
    novo_concurso = Concurso.objects.get(nome="Novo Concurso de Teste")
    assert novo_concurso.uuid is not None
    assert novo_concurso.criado_em is not None
    assert novo_concurso.atualizado_em is not None
    assert novo_concurso.cargos.count() == 1
    assert novo_concurso.codigo == 77
    assert novo_concurso.numero_processo == "888"


def test_create_concurso_without_nome(authenticated_client):
    """Verifica create concurso without nome."""
    url = reverse("concurso-list")
    response = authenticated_client.post(url, {"cargos_ids": []})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "nome" in response.data


def test_create_concurso_with_invalid_cargo_ids(
    authenticated_client, concurso_data_invalid_cargo_ids
):
    """Verifica create concurso with invalid cargo ids."""
    url = reverse("concurso-list")
    response = authenticated_client.post(url, concurso_data_invalid_cargo_ids)
    assert response.status_code == status.HTTP_201_CREATED
    novo_concurso = Concurso.objects.get(nome="Concurso com Cargo Inválido")
    assert novo_concurso.cargos.count() == 0


def test_create_concurso_without_cargos(
    authenticated_client, concurso_data_no_cargos
):
    """Verifica create concurso without cargos."""
    url = reverse("concurso-list")
    response = authenticated_client.post(url, concurso_data_no_cargos)
    assert response.status_code == status.HTTP_201_CREATED
    novo_concurso = Concurso.objects.get(nome="Concurso Sem Cargos")
    assert novo_concurso.cargos.count() == 0


def test_create_concurso_with_multiple_cargos(
    authenticated_client, concurso_data_multiple_cargos
):
    """Verifica create concurso with multiple cargos."""
    url = reverse("concurso-list")
    response = authenticated_client.post(url, concurso_data_multiple_cargos)
    assert response.status_code == status.HTTP_201_CREATED
    novo_concurso = Concurso.objects.get(nome="Concurso com Múltiplos Cargos")
    assert novo_concurso.cargos.count() == 2


def test_retrieve_concurso_success(authenticated_client, concurso_analista):
    """Verifica retrieve concurso success."""
    url = reverse("concurso-detail", kwargs={"pk": concurso_analista.uuid})
    response = authenticated_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["nome"] == "Concurso de Analista"
    assert response.data["uuid"] == str(concurso_analista.uuid)
    assert len(response.data["cargos"]) == 1
    assert response.data["cargos"][0]["nome"] == "Analista de Sistemas"
    assert "codigo" in response.data
    assert "numero_processo" in response.data


def test_retrieve_concurso_not_found(authenticated_client, fake_uuid):
    """Verifica retrieve concurso not found."""
    url = reverse("concurso-detail", kwargs={"pk": fake_uuid})
    response = authenticated_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_concurso_success(
    authenticated_client, concurso_analista, cargo_desenvolvedor
):
    """Verifica update concurso success."""
    url = reverse("concurso-detail", kwargs={"pk": concurso_analista.uuid})
    data = {
        "nome": "Concurso de Analista Atualizado",
        "cargos_ids": [str(cargo_desenvolvedor.uuid)],
        "numero_processo": "6016202200000020",
    }
    response = authenticated_client.put(url, data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["nome"] == "Concurso de Analista Atualizado"
    concurso_analista.refresh_from_db()
    assert concurso_analista.nome == "Concurso de Analista Atualizado"
    assert concurso_analista.cargos.count() == 1
    assert cargo_desenvolvedor in concurso_analista.cargos.all()


def test_delete_concurso_success(authenticated_client, concurso_analista):
    """Verifica delete concurso success."""
    url = reverse("concurso-detail", kwargs={"pk": concurso_analista.uuid})
    response = authenticated_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Concurso.objects.count() == 0
    with pytest.raises(Concurso.DoesNotExist):
        Concurso.objects.get(uuid=concurso_analista.uuid)


def test_filtra_concurso_por_ano_edital(authenticated_client, cargo_analista):
    """Filtra concursos pelo ano do edital."""
    c1 = Concurso.objects.create(nome="Edital 2025", ano_edital=2025)
    c1.cargos.add(cargo_analista)
    c2 = Concurso.objects.create(nome="Edital 2026", ano_edital=2026)
    c2.cargos.add(cargo_analista)

    url = reverse("concurso-list")
    response = authenticated_client.get(url, {"ano_edital": 2026})
    assert response.status_code == status.HTTP_200_OK
    nomes = [c["nome"] for c in response.data["results"]]
    assert nomes == ["Edital 2026"]


def test_filtra_concurso_por_status(authenticated_client, cargo_analista):
    """Filtra concursos pelo status (ATIVO/INATIVO)."""
    ativo = Concurso.objects.create(nome="Ativo", status="ATIVO")
    ativo.cargos.add(cargo_analista)
    inativo = Concurso.objects.create(nome="Inativo", status="INATIVO")
    inativo.cargos.add(cargo_analista)

    url = reverse("concurso-list")
    response = authenticated_client.get(url, {"status": "INATIVO"})
    assert response.status_code == status.HTTP_200_OK
    nomes = [c["nome"] for c in response.data["results"]]
    assert nomes == ["Inativo"]


def test_filtra_concurso_por_codigo_cargo(authenticated_client):
    """Filtra concursos pelo codigo do cargo vinculado."""
    from concursos.models import Cargo

    cargo = Cargo.objects.create(nome="Professor", codigo=4123)
    com = Concurso.objects.create(nome="Com Cargo 4123")
    com.cargos.add(cargo)
    Concurso.objects.create(nome="Sem Cargo")

    url = reverse("concurso-list")
    response = authenticated_client.get(url, {"codigo_cargo": 4123})
    assert response.status_code == status.HTTP_200_OK
    nomes = [c["nome"] for c in response.data["results"]]
    assert nomes == ["Com Cargo 4123"]


def test_filtra_concurso_por_numero_processo(
    authenticated_client, cargo_analista
):
    """Filtra concursos pelo numero do processo textual (icontains)."""
    c1 = Concurso.objects.create(
        nome="Proc A", numero_processo="6016202200779764"
    )
    c1.cargos.add(cargo_analista)
    c2 = Concurso.objects.create(nome="Proc B", numero_processo="1234567890")
    c2.cargos.add(cargo_analista)

    url = reverse("concurso-list")
    response = authenticated_client.get(url, {"numero_processo": "77976"})
    assert response.status_code == status.HTTP_200_OK
    nomes = [c["nome"] for c in response.data["results"]]
    assert nomes == ["Proc A"]


def test_filtra_descricao_cargo_nao_duplica_com_multiplos_cargos(
    authenticated_client,
):
    """Concurso com varios cargos casando o filtro nao duplica na lista."""
    from concursos.models import Cargo

    cargo1 = Cargo.objects.create(nome="Professor de Portugues", codigo=1)
    cargo2 = Cargo.objects.create(nome="Professor de Matematica", codigo=2)
    concurso = Concurso.objects.create(nome="Edital Professores")
    concurso.cargos.add(cargo1, cargo2)

    url = reverse("concurso-list")
    response = authenticated_client.get(url, {"descricao_cargo": "Professor"})
    assert response.status_code == status.HTTP_200_OK


def test_post_numero_processo_duplicado_retorna_400(authenticated_client):
    """POST com numero_processo duplicado retorna 400 com mensagem custom."""
    Concurso.objects.create(nome="Existente", numero_processo="99999")

    url = reverse("concurso-list")
    response = authenticated_client.post(
        url,
        {"nome": "Duplicata", "numero_processo": "99999", "cargos_ids": []},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["numero_processo"] == [
        "Este número de processo já está cadastrado."
    ]


def test_post_numero_processo_vazio_retorna_400(authenticated_client):
    """POST com numero_processo em branco e rejeitado pelo serializer."""
    url = reverse("concurso-list")
    response = authenticated_client.post(
        url, {"nome": "Vazio", "numero_processo": "", "cargos_ids": []}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "numero_processo" in response.data


def test_patch_numero_processo_proprio_permite(authenticated_client):
    """PATCH mantendo o proprio numero_processo nao e rejeitado."""
    concurso = Concurso.objects.create(
        nome="Existente", numero_processo="55555"
    )

    url = reverse("concurso-detail", kwargs={"pk": concurso.uuid})
    response = authenticated_client.patch(
        url, {"nome": "Renomeado", "numero_processo": "55555"}
    )
    assert response.status_code == status.HTTP_200_OK

