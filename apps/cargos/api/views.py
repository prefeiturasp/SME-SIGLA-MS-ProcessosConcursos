"""Views da API de cargos."""

from __future__ import annotations

from typing import Any

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.request import Request
from rest_framework.response import Response

from cargos.models import Cargo
from cargos.serializers import CargoSerializer
from cargos.services import CargosService


class CargoViewSet(viewsets.ModelViewSet):
    """CRUD de cargos e action de autorizações publicadas agregadas."""

    queryset = Cargo.objects.all()
    serializer_class = CargoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["codigo"]
    search_fields = ["nome", "codigo"]
    ordering_fields = ["criado_em"]
    ordering = ["-criado_em"]
    pagination_class = None

    @action(methods=["get"], detail=False, url_path="autorizacoes-publicadas")
    def autorizacoes_publicadas(
        self,
        request: Request,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        """Lista cargos com totais de autorizações e escolhas."""
        return Response(
            CargosService.listar_autorizacoes_publicadas_agregadas()
        )
