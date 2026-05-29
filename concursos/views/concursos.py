from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from concursos.models import Concurso
from concursos.serializers import (
    ConcursoListSerializer,
    ConcursoSelectSerializer,
    ConcursoSerializer,
)
from concursos.utils import CustomPagination


class ConcursoViewSet(viewsets.ModelViewSet):
    queryset = Concurso.objects.all()
    serializer_class = ConcursoSerializer
    permission_classes = []
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["nome"]
    search_fields = ["nome"]
    ordering_fields = ["nome", "criado_em"]
    ordering = ["-criado_em"]
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == "list":
            if self.request.query_params.get("formato") == "select":
                return ConcursoSelectSerializer
            return ConcursoListSerializer
        return ConcursoSerializer

    def list(self, request, *args, **kwargs):
        """
        Lista todos os concursos.
        Se formato=select, retorna sem paginação.
        """
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
