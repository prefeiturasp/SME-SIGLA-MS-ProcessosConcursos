"""Módulo tests/views/test_concursos_view."""
import pytest
from django.urls import reverse
from rest_framework import status

from concursos.models import Concurso

pytestmark = pytest.mark.django_db


def test_list_concursos_success(authenticated_client, concursos):
    """Verifica list concursos success.
    
    Args:
        authenticated_client: Cliente autenticado para requisições de teste.
        concursos: Parâmetro concursos da operação.
    
    Returns:
        Nenhum valor; valida comportamento via asserções.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
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
    """Verifica list concursos with select format.
    
    Args:
        authenticated_client: Cliente autenticado para requisições de teste.
        concursos: Parâmetro concursos da operação.
    
    Returns:
        Nenhum valor; valida comportamento via asserções.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
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
    """Verifica create concurso success.
    
    Args:
        authenticated_client: Cliente autenticado para requisições de teste.
        concurso_data: Parâmetro concurso data da operação.
    
    Returns:
        Nenhum valor; valida comportamento via asserções.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
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
    assert novo_concurso.numero_processo == 888


def test_create_concurso_without_nome(authenticated_client):
    """Verifica create concurso without nome.
    
    Args:
        authenticated_client: Cliente autenticado para requisições de teste.
    
    Returns:
        Nenhum valor; valida comportamento via asserções.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    url = reverse("concurso-list")
    response = authenticated_client.post(url, {"cargos_ids": []})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "nome" in response.data


def test_create_concurso_with_invalid_cargo_ids(
    authenticated_client, concurso_data_invalid_cargo_ids
):
    """Verifica create concurso with invalid cargo ids.
    
    Args:
        authenticated_client: Cliente autenticado para requisições de teste.
        concurso_data_invalid_cargo_ids: Parâmetro concurso data invalid cargo ids da operação.
    
    Returns:
        Nenhum valor; valida comportamento via asserções.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    url = reverse("concurso-list")
    response = authenticated_client.post(url, concurso_data_invalid_cargo_ids)
    assert response.status_code == status.HTTP_201_CREATED
    novo_concurso = Concurso.objects.get(nome="Concurso com Cargo Inválido")
    assert novo_concurso.cargos.count() == 0


def test_create_concurso_without_cargos(
    authenticated_client, concurso_data_no_cargos
):
    """Verifica create concurso without cargos.
    
    Args:
        authenticated_client: Cliente autenticado para requisições de teste.
        concurso_data_no_cargos: Parâmetro concurso data no cargos da operação.
    
    Returns:
        Nenhum valor; valida comportamento via asserções.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    url = reverse("concurso-list")
    response = authenticated_client.post(url, concurso_data_no_cargos)
    assert response.status_code == status.HTTP_201_CREATED
    novo_concurso = Concurso.objects.get(nome="Concurso Sem Cargos")
    assert novo_concurso.cargos.count() == 0


def test_create_concurso_with_multiple_cargos(
    authenticated_client, concurso_data_multiple_cargos
):
    """Verifica create concurso with multiple cargos.
    
    Args:
        authenticated_client: Cliente autenticado para requisições de teste.
        concurso_data_multiple_cargos: Parâmetro concurso data multiple cargos da operação.
    
    Returns:
        Nenhum valor; valida comportamento via asserções.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    url = reverse("concurso-list")
    response = authenticated_client.post(url, concurso_data_multiple_cargos)
    assert response.status_code == status.HTTP_201_CREATED
    novo_concurso = Concurso.objects.get(nome="Concurso com Múltiplos Cargos")
    assert novo_concurso.cargos.count() == 2


def test_retrieve_concurso_success(authenticated_client, concurso_analista):
    """Verifica retrieve concurso success.
    
    Args:
        authenticated_client: Cliente autenticado para requisições de teste.
        concurso_analista: Parâmetro concurso analista da operação.
    
    Returns:
        Nenhum valor; valida comportamento via asserções.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
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
    """Verifica retrieve concurso not found.
    
    Args:
        authenticated_client: Cliente autenticado para requisições de teste.
        fake_uuid: Parâmetro fake uuid da operação.
    
    Returns:
        Nenhum valor; valida comportamento via asserções.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    url = reverse("concurso-detail", kwargs={"pk": fake_uuid})
    response = authenticated_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_concurso_success(
    authenticated_client, concurso_analista, cargo_desenvolvedor
):
    """Verifica update concurso success.
    
    Args:
        authenticated_client: Cliente autenticado para requisições de teste.
        concurso_analista: Parâmetro concurso analista da operação.
        cargo_desenvolvedor: Parâmetro cargo desenvolvedor da operação.
    
    Returns:
        Nenhum valor; valida comportamento via asserções.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    url = reverse("concurso-detail", kwargs={"pk": concurso_analista.uuid})
    data = {
        "nome": "Concurso de Analista Atualizado",
        "cargos_ids": [str(cargo_desenvolvedor.uuid)],
    }
    response = authenticated_client.put(url, data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["nome"] == "Concurso de Analista Atualizado"
    concurso_analista.refresh_from_db()
    assert concurso_analista.nome == "Concurso de Analista Atualizado"
    assert concurso_analista.cargos.count() == 1
    assert cargo_desenvolvedor in concurso_analista.cargos.all()


def test_delete_concurso_success(authenticated_client, concurso_analista):
    """Verifica delete concurso success.
    
    Args:
        authenticated_client: Cliente autenticado para requisições de teste.
        concurso_analista: Parâmetro concurso analista da operação.
    
    Returns:
        Nenhum valor; valida comportamento via asserções.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    url = reverse("concurso-detail", kwargs={"pk": concurso_analista.uuid})
    response = authenticated_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Concurso.objects.count() == 0
    with pytest.raises(Concurso.DoesNotExist):
        Concurso.objects.get(uuid=concurso_analista.uuid)
