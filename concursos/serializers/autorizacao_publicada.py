"""Serializer de autorização publicada."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from rest_framework import serializers

from concursos.models import AutorizacaoPublicada, Cargo


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
        """Cria autorização resolvendo cargo a partir do UUID.

        Args:
            self: Instância do objeto.
            validated_data: dados validados; ``cargo`` é UUID opcional.

        Returns:
            Resposta HTTP com os dados serializados.

        Raises:
            ValidationError: Se os dados informados forem inválidos.
        """
        cargo_uuid: UUID | None = validated_data.pop("cargo", None)
        if cargo_uuid:
            try:
                validated_data["cargo"] = Cargo.objects.get(uuid=cargo_uuid)
            except Cargo.DoesNotExist as err:
                raise serializers.ValidationError(
                    {"cargo": "Cargo não encontrado"}
                ) from err
        return super().create(validated_data)
