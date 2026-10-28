"""Serializers do domínio de autorizações publicadas."""

from __future__ import annotations

from typing import Any

from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers

from autorizacoes.models import AutorizacaoPublicada
from cargos.models import Cargo

CHAVE_TOTAL_AUTORIZACOES = "autorizacoes-publicadas"

DESCRICOES_AUTORIZACAO = {
    "uuid": {"help_text": "Identificador da autorização publicada."},
    "autorizacoes": {
        "help_text": (
            "Quantidade de autorizações (vagas) publicadas. Assume 0 "
            "quando não é enviada."
        )
    },
    "data_autorizacao": {
        "help_text": (
            "Data em que a autorização foi publicada. Registros sem data "
            "ficam fora da extração de dados."
        )
    },
    "observacao": {"help_text": "Texto livre, com até 500 caracteres."},
    "criado_em": {"help_text": "Data e hora de criação do registro."},
    "atualizado_em": {
        "help_text": "Data e hora da última alteração do registro."
    },
}


class AutorizacaoPublicadaSerializer(serializers.ModelSerializer):
    """Autorizações publicadas para um cargo em uma data."""

    cargo = serializers.SlugRelatedField(
        slug_field="uuid",
        queryset=Cargo.objects.all(),
        error_messages={
            "does_not_exist": 'Pk inválido "{value}" - objeto não existe.'
        },
        help_text=(
            "UUID do cargo autorizado. Obrigatório na API. Registros "
            "criados pelo Django Admin podem vir com nulo."
        ),
    )

    class Meta:
        """Configuração do serializer."""

        model = AutorizacaoPublicada
        fields = [
            "uuid",
            "cargo",
            "autorizacoes",
            "data_autorizacao",
            "observacao",
            "criado_em",
            "atualizado_em",
        ]
        read_only_fields = ["uuid", "criado_em", "atualizado_em"]
        extra_kwargs = DESCRICOES_AUTORIZACAO


class AutorizacoesPublicadasTotalSerializer(serializers.Serializer):
    """Filtros da extração de dados de autorizações publicadas."""

    concurso_uuid = serializers.UUIDField(
        required=False,
        allow_null=True,
        help_text=(
            "Restringe a extração aos cargos vinculados ao concurso. Um "
            "concurso inexistente resulta em totais zerados."
        ),
    )
    anos = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
        help_text=(
            "Anos de autorização a extrair. Quando informado e não vazio, "
            "a resposta vem separada por ano."
        ),
    )


@extend_schema_serializer(many=False)
class AutorizacaoPublicadaPaginadaSerializer(serializers.Serializer):
    """Página da listagem de autorizações publicadas."""

    count = serializers.IntegerField(
        help_text="Total de autorizações que atendem aos filtros."
    )
    next = serializers.URLField(
        allow_null=True,
        help_text="URL da próxima página, ou nulo na última página.",
    )
    previous = serializers.URLField(
        allow_null=True,
        help_text="URL da página anterior, ou nulo na primeira página.",
    )
    results = AutorizacaoPublicadaSerializer(
        many=True, help_text="Autorizações publicadas da página."
    )


class CargoExtracaoSerializer(serializers.Serializer):
    """Total de autorizações publicadas de um cargo no recorte pedido."""

    uuid = serializers.UUIDField(help_text="Identificador do cargo.")
    nome = serializers.CharField(help_text="Nome do cargo.")
    codigo = serializers.IntegerField(
        allow_null=True, help_text="Código numérico do cargo na SME."
    )
    autorizacoes = serializers.IntegerField(
        help_text="Soma das autorizações publicadas para o cargo no recorte."
    )
    data_autorizacao = serializers.DateField(
        help_text="Data da autorização mais recente do cargo no recorte."
    )


class ExtracaoDadosSerializer(serializers.Serializer):
    """Total de autorizações publicadas, geral e por cargo."""

    autorizacoes_publicadas = serializers.IntegerField(
        help_text=(
            "Soma das autorizações publicadas no recorte. Inclui as "
            "autorizações sem cargo, que não aparecem em `cargos`."
        )
    )
    cargos = CargoExtracaoSerializer(
        many=True,
        help_text="Totais por cargo, em ordem alfabética do nome.",
    )

    def get_fields(self) -> dict[str, Any]:
        """Publica ``autorizacoes_publicadas`` com a chave real da resposta."""
        return {
            (
                CHAVE_TOTAL_AUTORIZACOES
                if nome == "autorizacoes_publicadas"
                else nome
            ): campo
            for nome, campo in super().get_fields().items()
        }


class ExtracaoDadosPorAnoSerializer(serializers.Serializer):
    """Totais de autorizações publicadas separados por ano."""
