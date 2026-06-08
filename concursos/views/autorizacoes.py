"""ViewSet de autorizações publicadas."""

from django.db.models import Sum
from django.db.models.functions import ExtractYear
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from concursos.models import AutorizacaoPublicada, Concurso
from concursos.serializers import (
    AutorizacaoPublicadaSerializer,
    AutorizacoesPublicadasTotalSerializer,
)


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

    @action(detail=False, methods=["post"], url_path="total")
    def total(self, request):
        """
        Total de autorizações publicadas (SUM) dos cargos de um concurso,
        agrupado por ano de ``data_autorizacao``.

        POST /autorizacoes-publicadas/total/
        Body: {concurso_uuid, anos?: [int]}
        """
        serializer = AutorizacoesPublicadasTotalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        concurso_uuid = serializer.validated_data["concurso_uuid"]
        anos = serializer.validated_data.get("anos")

        cargos_ids = Concurso.objects.filter(
            uuid=concurso_uuid
        ).values_list("cargos__uuid", flat=True)

        totais = (
            AutorizacaoPublicada.objects.filter(
                cargo__uuid__in=cargos_ids,
                data_autorizacao__isnull=False,
            )
            .annotate(ano=ExtractYear("data_autorizacao"))
            .values("ano")
            .annotate(total=Sum("autorizacoes"))
        )

        if anos:
            totais = totais.filter(ano__in=anos)

        resultado = {
            str(item["ano"]): {"autorizacoes-publicadas": item["total"]}
            for item in totais
        }
        return Response(resultado)
