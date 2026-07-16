"""Serializers do domínio de autorizações publicadas."""

from __future__ import annotations

from rest_framework import serializers

from autorizacoes.models import AutorizacaoPublicada
from cargos.models import Cargo


class AutorizacaoPublicadaSerializer(serializers.ModelSerializer):
    """Serializer de autorização publicada com cargo por UUID."""

    cargo = serializers.PrimaryKeyRelatedField(queryset=Cargo.objects.all())

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


class AutorizacoesPublicadasTotalSerializer(serializers.Serializer):
    """Serializer de autorizações publicadas para extração de dados."""

    concurso_uuid = serializers.UUIDField(required=False, allow_null=True)
    anos = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
    )
