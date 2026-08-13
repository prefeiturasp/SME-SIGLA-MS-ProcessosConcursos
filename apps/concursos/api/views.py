"""Views da API de concursos."""

from __future__ import annotations

from typing import Any

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from concursos.constants import (
    CONCURSO_SITUACAO_COMPLETO,
    CONCURSO_SITUACAO_EM_ANDAMENTO,
)
from concursos.filters import ConcursoFilterSet
from concursos.models import Concurso
from concursos.repository import ConcursosRepository
from concursos.serializers import (
    ConcursoAtualizarSituacaoSerializer,
    ConcursoListSerializer,
    ConcursoSelectSerializer,
    ConcursoSerializer,
)
from core.utils import CustomPagination

# Transições permitidas: situação alvo -> situação de origem exigida
_TRANSICOES_PERMITIDAS = {
    CONCURSO_SITUACAO_EM_ANDAMENTO: CONCURSO_SITUACAO_COMPLETO,
    CONCURSO_SITUACAO_COMPLETO: CONCURSO_SITUACAO_EM_ANDAMENTO,
}


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

    @action(detail=True, methods=["patch"], url_path="atualizar-situacao")
    def atualizar_situacao(
        self, request: Request, pk: str | None = None
    ) -> Response:
        """Aplica transição de situação se o estado atual permitir."""
        concurso = self.get_object()
        serializer = ConcursoAtualizarSituacaoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        situacao_alvo = serializer.validated_data["situacao"]

        origem_exigida = _TRANSICOES_PERMITIDAS.get(situacao_alvo)
        if origem_exigida is not None and concurso.situacao == origem_exigida:
            ConcursosRepository.atualizar_situacao(concurso, situacao_alvo)
            concurso.refresh_from_db()

        return Response(
            ConcursoSerializer(concurso).data, status=status.HTTP_200_OK
        )
