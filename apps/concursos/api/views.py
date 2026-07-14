"""Views da API de concursos."""

from __future__ import annotations

from typing import Any

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from concursos.filters import ConcursoFilterSet
from concursos.models import Concurso
from concursos.serializers import ConcursoSerializer
from concursos.services import ConcursosService
from core.utils import CustomPagination


class ConcursoViewSet(viewsets.ModelViewSet):
    """CRUD e listagem de concursos com paginação ou formato select."""

    queryset = Concurso.objects.all()
    serializer_class = ConcursoSerializer
    permission_classes: list[Any] = []
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ConcursoFilterSet
    search_fields = ["nome"]
    ordering_fields = ["nome", "criado_em"]
    ordering = ["-criado_em"]
    pagination_class = CustomPagination

    def get_serializer_class(self) -> type[BaseSerializer]:
        """Retorna serializer conforme action e query ``formato=select``."""
        if self.action == "list":
            return ConcursosService.obter_serializer_listagem(
                self, self.request
            )
        return ConcursoSerializer

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Lista concursos paginados ou em formato select."""
        queryset = self.filter_queryset(self.get_queryset())
        return ConcursosService.listar(self, request, queryset)
