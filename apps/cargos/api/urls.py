"""Rotas de URL do módulo de cargos."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from cargos.api.views import CargoViewSet

router = DefaultRouter()
router.register(r"cargos", CargoViewSet, basename="cargo")

urlpatterns = [
    path("", include(router.urls)),
]
