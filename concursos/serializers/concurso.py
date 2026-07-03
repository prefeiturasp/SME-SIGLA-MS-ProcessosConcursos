"""Serializers do modelo Concurso."""

from __future__ import annotations

from typing import Any

from rest_framework import serializers

from concursos.models import Cargo, Concurso

from .cargo import CargoListSerializer, CargoSelectSerializer


class ConcursoSerializer(serializers.ModelSerializer):
    """Serializer completo de concurso com vínculo de cargos."""

    cargos = CargoListSerializer(many=True, read_only=True)
    cargos_ids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True, required=False
    )

    class Meta:
        """Configuração do serializer."""

        model = Concurso
        fields = [
            "uuid",
            "nome",
            "cargos",
            "cargos_ids",
            "criado_em",
            "atualizado_em",
            "numero_processo",
            "codigo",
            "ano_edital",
            "banca_responsavel",
            "status",
        ]
        read_only_fields = ["uuid", "criado_em", "atualizado_em"]

    def create(self, validated_data: dict[str, Any]) -> Concurso:
        """Cria concurso e associa cargos por UUID.

        Args:
            self: Instância do objeto.
            validated_data: dados validados; ``cargos_ids`` opcional.

        Returns:
            Instância do concurso persistida.

        Raises:
            Nenhuma exceção específica documentada.
        """
        cargos_ids = validated_data.pop("cargos_ids", [])
        concurso = Concurso.objects.create(**validated_data)

        if cargos_ids:
            cargos = Cargo.objects.filter(uuid__in=cargos_ids)
            concurso.cargos.set(cargos)

        return concurso

    def update(
        self,
        instance: Concurso,
        validated_data: dict[str, Any],
    ) -> Concurso:

        """Atualiza concurso e, se informado, substitui cargos vinculados."""
        cargos_ids = validated_data.pop("cargos_ids", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if cargos_ids is not None:
            cargos = Cargo.objects.filter(uuid__in=cargos_ids)
            instance.cargos.set(cargos)

        return instance


class ConcursoListSerializer(serializers.ModelSerializer):
    """Serializer enxuto para listagem de concursos."""

    cargos = CargoListSerializer(many=True, read_only=True)
    cargos_descricao = serializers.SerializerMethodField()

    class Meta:
        """Configuração do serializer."""

        model = Concurso
        fields = [
            "uuid",
            "nome",
            "cargos",
            "cargos_descricao",
            "numero_processo",
            "codigo",
            "ano_edital",
            "banca_responsavel",
            "status",
        ]

    def get_cargos_descricao(self, obj: Concurso) -> list[str]:
        """Retorna lista de ``"{codigo} - {nome}"`` por cargo vinculado.

        Args:
            obj: Instância de concurso serializada.

        Returns:
            Lista de strings ``"codigo - nome"`` dos cargos vinculados.
        """
        return [f"{cargo.codigo} - {cargo.nome}" for cargo in obj.cargos.all()]


class ConcursoSelectSerializer(serializers.ModelSerializer):
    """Serializer ``value``/``label`` para selects no frontend."""

    value = serializers.UUIDField(source="uuid")
    label = serializers.CharField(source="nome")
    cargos = CargoSelectSerializer(many=True, read_only=True)

    class Meta:
        """Configuração do serializer."""

        model = Concurso
        fields = ["value", "label", "cargos", "numero_processo", "codigo"]
