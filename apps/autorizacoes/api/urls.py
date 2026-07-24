"""Rotas de URL do módulo de autorizações."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from autorizacoes.api.views import (
    AutorizacaoPublicadaViewSet,
    ExtracaoDadosViewSet,
)

router = DefaultRouter()
router.register(
    r"autorizacoes-publicadas",
    AutorizacaoPublicadaViewSet,
    basename="autorizacao-publicada",
)
router.register(
    r"extracao-dados", ExtracaoDadosViewSet, basename="extracao-dados"
)

urlpatterns = [
    path("", include(router.urls)),
]
