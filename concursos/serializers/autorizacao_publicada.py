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


class AutorizacoesPublicadasTotalSerializer(serializers.Serializer):
    """Payload do endpoint de extração de dados de autorizações publicadas.

    Regra tudo-ou-nada: ``concurso_uuid`` e ``anos`` são informados **juntos**
    (filtra por concurso + anos) ou **nenhum dos dois** (retorna todos os anos
    existentes). Passar só um deles é inválido. O resultado é sempre quebrado
    por ano de ``data_autorizacao``.
    """

    concurso_uuid = serializers.UUIDField(required=False, allow_null=True)
    anos = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
    )

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Garante que ``concurso_uuid`` e ``anos`` venham juntos ou ausentes.

        Args:
            attrs: dados validados por campo.

        Returns:
            Os mesmos ``attrs`` quando a combinação é válida.

        Raises:
            serializers.ValidationError: apenas um dos dois filtros informado.
        """
        tem_concurso = attrs.get("concurso_uuid") is not None
        tem_anos = bool(attrs.get("anos"))
        if tem_concurso != tem_anos:
            raise serializers.ValidationError(
                "Informe `concurso_uuid` e `anos` juntos, ou nenhum dos dois."
            )
        return attrs
