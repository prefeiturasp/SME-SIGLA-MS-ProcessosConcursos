"""Views da API de autorizações publicadas."""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from autorizacoes.models import AutorizacaoPublicada
from autorizacoes.serializers import (
    AutorizacaoPublicadaSerializer,
    AutorizacoesPublicadasTotalSerializer,
)
from autorizacoes.services import montar_extracao_dados


class AutorizacaoPublicadaViewSet(viewsets.ModelViewSet):
    """CRUD de autorizações publicadas por cargo."""

    queryset = AutorizacaoPublicada.objects.all()
    serializer_class = AutorizacaoPublicadaSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["cargo__codigo", "cargo__uuid"]
    search_fields = ["observacao"]
    ordering_fields = ["data_autorizacao", "criado_em"]
    ordering = ["-data_autorizacao", "-criado_em"]


class ExtracaoDadosViewSet(viewsets.ViewSet):
    """ViewSet de autorizações publicadas para extração de dados."""

    permission_classes = [AllowAny]

    def create(self, request: Request) -> Response:
        """Recebe filtros e retorna a Extração de Dados agregada."""
        serializer = AutorizacoesPublicadasTotalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dados = serializer.validated_data
        resultado = montar_extracao_dados(
            concurso_uuid=dados.get("concurso_uuid"),
            anos=dados.get("anos"),
        )
        return Response(resultado)
