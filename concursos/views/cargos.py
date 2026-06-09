"""ViewSet de cargos e agregados de autorizações."""

from __future__ import annotations

from typing import Any

from django.db.models import Max, Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.request import Request
from rest_framework.response import Response

from concursos.models import Cargo
from concursos.serializers import CargoSerializer
from concursos.services import EscolhasAPIService


class CargoViewSet(viewsets.ModelViewSet):
    """CRUD de cargos e action de autorizações publicadas agregadas."""

    queryset = Cargo.objects.all()
    serializer_class = CargoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["codigo"]
    search_fields = ["nome"]
    ordering_fields = ["criado_em"]
    ordering = ["-criado_em"]

    @action(methods=["get"], detail=False, url_path="autorizacoes-publicadas")
    def autorizacoes_publicadas(
        self,
        request: Request,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        """Lista cargos com totais de autorizações e escolhas.
        
        Args:
            self: Instância do objeto.
            request: Requisição HTTP (sem parâmetros obrigatórios).
            *args: Argumentos posicionais variáveis.
            **kwargs: Argumentos nomeados variáveis.
        
        Returns:
            Resposta HTTP com o resultado da operação.
        
        Raises:
            Nenhuma exceção específica documentada.
        
        Examples:
            GET /api/v1/cargos/autorizacoes-publicadas/::
            [
            {
            "uuid": "...",
            "nome": "Professor",
            "codigo": 1,
            "autorizacoes": 10,
            "data_autorizacao_mais_recente": "2026-01-15",
            "total_escolhas": 5
            }
            ]
        """
        escolhas_por_cargo: dict[str | int, Any] = {}
        resp = EscolhasAPIService().get_escolhas_por_cargo()
        escolhas_por_cargo = resp.json()

        qs = (
            Cargo.objects.all()
            .annotate(
                total_autorizacoes=Sum("autorizacoes__autorizacoes"),
                ultima_autorizacao=Max("autorizacoes__data_autorizacao"),
            )
            .order_by("nome")
        )
        data: list[dict[str, Any]] = []
        for cargo in qs:
            total_escolhas = (
                escolhas_por_cargo.get(str(cargo.codigo))
                or escolhas_por_cargo.get(cargo.codigo)
                or 0
            )
            data_autorizacao = (
                cargo.ultima_autorizacao.isoformat()
                if cargo.ultima_autorizacao
                else None
            )
            data.append(
                {
                    "uuid": str(cargo.uuid),
                    "nome": cargo.nome,
                    "codigo": cargo.codigo,
                    "autorizacoes": int(cargo.total_autorizacoes or 0),
                    "data_autorizacao_mais_recente": data_autorizacao,
                    "total_escolhas": int(total_escolhas or 0),
                }
            )
        return Response(data)
