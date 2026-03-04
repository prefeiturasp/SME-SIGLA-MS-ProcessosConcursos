from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from django.db.models import Sum, Max
from concursos.services import EscolhasAPIService
import logging

from concursos.models import Cargo
from concursos.serializers import (
    CargoSerializer,
    CargoListSerializer,
    CargoSelectSerializer,
)
from concursos.utils import CustomPagination


class CargoViewSet(viewsets.ModelViewSet):
    queryset = Cargo.objects.all()
    serializer_class = CargoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['nome']
    ordering_fields = ['criado_em']
    ordering = ['-criado_em']

    @action(methods=['get'], detail=False, url_path='autorizacoes-publicadas')
    def autorizacoes_publicadas(self, request, *args, **kwargs):
        """
        Lista todos os cargos com agregados de autorizações publicadas:
        - total de autorizacoes
        - data_autorizacao_mais_recente
        """
        # Busca totais de escolhas por cargo no ms-escolhas
        escolhas_por_cargo = {}
        resp = EscolhasAPIService().get_escolhas_por_cargo()
        escolhas_por_cargo = resp.json()

        qs = (
            Cargo.objects
            .all()
            .annotate(
                total_autorizacoes=Sum('autorizacoes__autorizacoes'),
                ultima_autorizacao=Max('autorizacoes__data_autorizacao'),
            )
            .order_by('nome')
        )
        data = []
        for cargo in qs:
            total_escolhas = escolhas_por_cargo.get(str(cargo.codigo)) or escolhas_por_cargo.get(cargo.codigo) or 0
            data.append({
                'uuid': str(cargo.uuid),
                'nome': cargo.nome,
                'codigo': cargo.codigo,
                'autorizacoes': int(cargo.total_autorizacoes or 0),
                'data_autorizacao_mais_recente': cargo.ultima_autorizacao.isoformat() if cargo.ultima_autorizacao else None,
                'total_escolhas': int(total_escolhas or 0),
            })
        return Response(data)
