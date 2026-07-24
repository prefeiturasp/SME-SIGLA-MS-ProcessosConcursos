"""Rotas de URL do módulo de concursos."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from concursos.api.views import ConcursoViewSet

router = DefaultRouter()
router.register(r"concursos", ConcursoViewSet, basename="concurso")

urlpatterns = [
    path("", include(router.urls)),
]
