"""Fixtures compartilhadas entre os apps."""

import uuid

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from cargos.models import Cargo


@pytest.fixture
def api_client() -> APIClient:
    """Cliente API sem autenticação."""
    return APIClient()


@pytest.fixture
def user() -> User:
    """Usuário de teste para autenticação."""
    return User.objects.create_user(
        username="testuser", password="testpass123", email="test@example.com"
    )


@pytest.fixture
def authenticated_client(api_client: APIClient, user: User) -> APIClient:
    """Cliente API autenticado."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def fake_uuid() -> uuid.UUID:
    """UUID aleatório para cenários de recurso inexistente."""
    return uuid.uuid4()


@pytest.fixture
def cargo_analista() -> Cargo:
    """Cargo de analista usado em vários apps."""
    return Cargo.objects.create(nome="Analista de Sistemas")
