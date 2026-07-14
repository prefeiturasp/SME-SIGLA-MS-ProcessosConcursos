"""Serializers do domínio de autorizações publicadas."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from rest_framework import serializers

from autorizacoes.models import AutorizacaoPublicada
from cargos.repository import CargoRepository


class AutorizacaoPublicadaSerializer(serializers.ModelSerializer):
    """Serializer de autorização publicada com cargo por UUID."""

    cargo = serializers.UUIDField(required=False, allow_null=True)

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

    def create(self, validated_data: dict[str, Any]) -> AutorizacaoPublicada:
        """Cria autorização resolvendo cargo a partir do UUID."""
        cargo_uuid: UUID | None = validated_data.pop("cargo", None)
        if cargo_uuid:
            cargo = CargoRepository.obter_modelo_por_uuid(cargo_uuid)
            if cargo is None:
                raise serializers.ValidationError(
                    {"cargo": "Cargo não encontrado"}
                )
            validated_data["cargo"] = cargo
        return super().create(validated_data)


class AutorizacoesPublicadasTotalSerializer(serializers.Serializer):
    """Serializer de autorizações publicadas para extração de dados."""

    concurso_uuid = serializers.UUIDField(required=False, allow_null=True)
    anos = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
    )
