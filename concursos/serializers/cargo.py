"""Serializers do modelo Cargo."""

from rest_framework import serializers

from concursos.models import Cargo


class CargoSerializer(serializers.ModelSerializer):
    """Serializer completo de cargo."""

    class Meta:
        """Configuração do serializer."""

        model = Cargo
        fields = ["uuid", "nome", "codigo", "criado_em", "atualizado_em"]
        read_only_fields = ["uuid", "criado_em", "atualizado_em"]


class CargoListSerializer(serializers.ModelSerializer):
    """Serializer enxuto para listagem de cargos."""

    class Meta:
        """Configuração do serializer."""

        model = Cargo
        fields = ["uuid", "nome", "codigo"]


class CargoSelectSerializer(serializers.ModelSerializer):
    """Serializer ``value``/``label`` para selects no frontend."""

    value = serializers.UUIDField(source="uuid")
    label = serializers.CharField(source="nome")

    class Meta:
        """Configuração do serializer."""

        model = Cargo
        fields = ["value", "label", "codigo"]
