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
            validated_data: dados validados; ``cargo`` é UUID opcional.

        Returns:
            Instância ``AutorizacaoPublicada`` criada.

        Raises:
            serializers.ValidationError: cargo UUID inexistente.
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


class AutorizacoesPublicadasTotalSerializer(serializers.Serializer):
    """Payload do endpoint de total de autorizações publicadas por concurso.

    ``anos`` é opcional: se informado, restringe o resultado a esses anos;
    se omitido, retorna todos os anos com autorizações.
    """

    concurso_uuid = serializers.UUIDField()
    anos = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
    )
