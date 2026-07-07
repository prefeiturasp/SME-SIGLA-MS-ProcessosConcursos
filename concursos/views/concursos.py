"""ViewSet de concursos."""

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
from concursos.serializers import (
    ConcursoListSerializer,
    ConcursoSelectSerializer,
    ConcursoSerializer,
)
from concursos.utils import CustomPagination


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
            if self.request.query_params.get("formato") == "select":
                return ConcursoSelectSerializer
            return ConcursoListSerializer
        return ConcursoSerializer

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Lista concursos paginados ou em formato select."""
        queryset = self.filter_queryset(self.get_queryset())

        if request.query_params.get("formato") == "select":
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
