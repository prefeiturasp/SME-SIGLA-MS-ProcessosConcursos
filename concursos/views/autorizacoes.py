from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny

from concursos.models import AutorizacaoPublicada
from concursos.serializers import AutorizacaoPublicadaSerializer


class AutorizacaoPublicadaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar Autorizações Publicadas.
    """

    queryset = AutorizacaoPublicada.objects.all()
    serializer_class = AutorizacaoPublicadaSerializer
    permission_classes = [AllowAny]  # [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["cargo__codigo", "cargo__uuid"]
    search_fields = ["observacao"]
    ordering_fields = ["data_autorizacao", "criado_em"]
    ordering = ["-data_autorizacao", "-criado_em"]
