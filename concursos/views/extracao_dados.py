"""ViewSet de extração de dados de autorizações publicadas."""

from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from concursos.serializers import AutorizacoesPublicadasTotalSerializer
from concursos.services import montar_extracao_dados


class ExtracaoDadosViewSet(viewsets.ViewSet):
    """
    Indicadores de autorizações publicadas para extração de dados.

    POST /extracao-dados/
    Body: {concurso_uuid?, anos?: [int]}
    Com `anos`: agrupado por ano de ``data_autorizacao``.
    Sem `anos`: retorna a chave "total" com a soma de todas as autorizações.
    Em ambos os casos inclui totais por cargo em ``cargos``.
    Sem `concurso_uuid`: agrega autorizações de todos os concursos.
    """

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
