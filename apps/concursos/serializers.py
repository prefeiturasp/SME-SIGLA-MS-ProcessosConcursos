"""Serializers do domínio de concursos."""

from __future__ import annotations

import logging
from typing import Any

from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from cargos.repository import CargoRepository
from cargos.serializers import CargoListSerializer, CargoSelectSerializer
from concursos.constants import CONCURSO_SITUACAO_CHOICES
from concursos.models import Concurso

logger = logging.getLogger(__name__)


class ConcursoSerializer(serializers.ModelSerializer):
    """Serializer completo de concurso com vínculo de cargos."""

    cargos = CargoListSerializer(many=True, read_only=True)
    cargos_ids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True, required=False
    )
    numero_processo = serializers.CharField(
        validators=[
            UniqueValidator(
                queryset=Concurso.objects.all(),
                message="Este número de processo já está cadastrado.",
            )
        ]
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
            "banca_responsavel",
            "status",
            "situacao",
            "data_autorizacao",
            "data_abertura",
            "classificacao_final",
            "link_edital",
            "habilitados_geral",
            "habilitados_nna",
            "habilitados_pcd",
            "retificacoes",
            "data_homologacao",
            "data_prorrogacao",
            "vigencia_inicio",
            "vigencia_fim",
        ]
        read_only_fields = ["uuid", "criado_em", "atualizado_em"]
        extra_kwargs: dict[str, Any] = {
            "numero_processo": {"validators": []},
        }

    def create(self, validated_data: dict[str, Any]) -> Concurso:
        """Cria concurso e associa cargos por UUID."""
        cargos_ids = validated_data.pop("cargos_ids", [])
        try:
            concurso = Concurso.objects.create(**validated_data)
        except IntegrityError as e:
            mensagem = (
                f"Erro de integridade ao salvar os dados no banco "
                f"de dados - {str(e)}."
            )
            logger.error(mensagem)
            raise serializers.ValidationError(mensagem) from e

        if cargos_ids:
            cargos = CargoRepository.buscar_por_uuids(cargos_ids)
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
        try:
            instance.save()
        except IntegrityError as e:
            mensagem = (
                f"Erro de integridade ao salvar os dados no banco "
                f"de dados - {str(e)}."
            )
            logger.error(mensagem)
            raise serializers.ValidationError(mensagem) from e

        if cargos_ids is not None:
            cargos = CargoRepository.buscar_por_uuids(cargos_ids)
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
            "banca_responsavel",
            "status",
            "situacao",
        ]

    def get_cargos_descricao(self, obj: Concurso) -> list[str]:
        """Retorna lista de ``"{codigo} - {nome}"`` por cargo vinculado."""
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


class ConcursoAtualizarSituacaoSerializer(serializers.Serializer):
    """Valida o campo situacao para a transição de estado do concurso."""

    situacao = serializers.ChoiceField(choices=CONCURSO_SITUACAO_CHOICES)
