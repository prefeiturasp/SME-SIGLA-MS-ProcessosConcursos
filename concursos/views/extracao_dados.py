"""Módulo de extração de dados de autorizações publicadas."""

from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from concursos.serializers import AutorizacoesPublicadasTotalSerializer
from concursos.services import montar_extracao_dados


class ExtracaoDadosViewSet(viewsets.ViewSet):
    """ViewSet de autorizações publicadas para extração de dados."""

    permission_classes = [AllowAny]

    def create(self, request):
        serializer = AutorizacoesPublicadasTotalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dados = serializer.validated_data
        resultado = montar_extracao_dados(
            concurso_uuid=dados.get("concurso_uuid"),
            anos=dados.get("anos"),
        )
        return Response(resultado)
