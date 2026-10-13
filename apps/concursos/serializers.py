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
from concursos.repository import ConcursosRepository

logger = logging.getLogger(__name__)

DESCRICOES_CONCURSO = {
    "uuid": {"help_text": "Identificador do concurso."},
    "nome": {"help_text": "Nome do concurso, com até 200 caracteres."},
    "numero_processo": {
        "help_text": "Número do processo administrativo do concurso."
    },
    "codigo": {
        "help_text": (
            "Código do concurso na SME. Vem preenchido nos concursos "
            "importados da SME Integração."
        )
    },
    "banca_responsavel": {"help_text": "Banca responsável pelo concurso."},
    "status": {
        "help_text": (
            "`ATIVO` (padrão ao criar) ou `INATIVO`. Serve para organizar "
            "e filtrar a listagem; não bloqueia cargos nem autorizações."
        )
    },
    "situacao": {
        "help_text": (
            "Situação do concurso. Começa em `INCOMPLETO`. O MS de "
            "convocação leva o concurso a `EM_ANDAMENTO` ao criar um "
            "processo de convocação e de volta a `COMPLETO` ao excluir o "
            "último."
        )
    },
    "data_autorizacao": {"help_text": "Data de autorização do concurso."},
    "data_abertura": {"help_text": "Data de abertura do concurso."},
    "classificacao_final": {"help_text": "Data da classificação final."},
    "link_edital": {
        "help_text": "Endereço (URL) do edital, com até 500 caracteres."
    },
    "habilitados_geral": {
        "help_text": "Quantidade de habilitados na lista geral."
    },
    "habilitados_nna": {
        "help_text": (
            "Quantidade de habilitados na lista de negros, negras ou "
            "afrodescendentes (NNA)."
        )
    },
    "habilitados_pcd": {
        "help_text": (
            "Quantidade de habilitados na lista de pessoas com deficiência "
            "(PcD)."
        )
    },
    "retificacoes": {
        "help_text": "Texto livre com as retificações do edital."
    },
    "data_homologacao": {"help_text": "Data da homologação."},
    "data_prorrogacao": {"help_text": "Data da prorrogação."},
    "vigencia_inicio": {"help_text": "Data de início da vigência."},
    "vigencia_fim": {"help_text": "Data de fim da vigência."},
    "criado_em": {"help_text": "Data e hora de criação do registro."},
    "atualizado_em": {
        "help_text": "Data e hora da última alteração do registro."
    },
}


class ConcursoSerializer(serializers.ModelSerializer):
    """Concurso com os cargos vinculados."""

    cargos = CargoListSerializer(
        many=True, read_only=True, help_text="Cargos vinculados ao concurso."
    )
    cargos_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False,
        help_text=(
            "UUIDs dos cargos a vincular. Substitui os vínculos atuais, e "
            "uma lista vazia remove todos. UUIDs que não existem são "
            "ignorados. Se omitido em uma atualização, os vínculos são "
            "mantidos."
        ),
    )
    numero_processo = serializers.CharField(
        validators=[
            UniqueValidator(
                queryset=Concurso.objects.all(),
                message="Este número de processo já está cadastrado.",
            )
        ],
        help_text=(
            "Número do processo administrativo do concurso. Não pode se "
            "repetir entre concursos."
        ),
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
            **DESCRICOES_CONCURSO,
            "numero_processo": {"validators": []},
        }

    def create(self, validated_data: dict[str, Any]) -> Concurso:
        """Cria concurso e associa cargos por UUID."""
        cargos_ids = validated_data.pop("cargos_ids", [])
        logger.info(f"Criando concurso com dados: {validated_data}")
        try:
            concurso = ConcursosRepository.criar(**validated_data)
        except IntegrityError as e:
            mensagem = f"Erro de integridade ao salvar os dados no banco de dados - {e}."  # noqa: E501
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
        logger.info(f"Atualizando concurso com dados: {validated_data}")
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        try:
            instance.save()
        except IntegrityError as e:
            mensagem = f"Erro de integridade ao salvar os dados no banco de dados - {e}."  # noqa: E501
            logger.error(mensagem)
            raise serializers.ValidationError(mensagem) from e

        if cargos_ids is not None:
            cargos = CargoRepository.buscar_por_uuids(cargos_ids)
            instance.cargos.set(cargos)

        return instance


class ConcursoListSerializer(serializers.ModelSerializer):
    """Concurso resumido, como aparece na listagem."""

    cargos = CargoListSerializer(
        many=True, read_only=True, help_text="Cargos vinculados ao concurso."
    )
    cargos_descricao = serializers.SerializerMethodField(
        help_text='Cargos vinculados, cada um no formato "código - nome".'
    )

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
        extra_kwargs = DESCRICOES_CONCURSO

    def get_cargos_descricao(self, obj: Concurso) -> list[str]:
        """Retorna lista de ``"{codigo} - {nome}"`` por cargo vinculado."""
        return [f"{cargo.codigo} - {cargo.nome}" for cargo in obj.cargos.all()]


class ConcursoSelectSerializer(serializers.ModelSerializer):
    """Concurso como opção de um campo de seleção."""

    value = serializers.UUIDField(
        source="uuid", help_text="UUID do concurso: o valor a enviar."
    )
    label = serializers.CharField(
        source="nome", help_text="Nome do concurso: o texto a exibir."
    )
    cargos = CargoSelectSerializer(
        many=True,
        read_only=True,
        help_text="Cargos do concurso, também como opções de seleção.",
    )

    class Meta:
        """Configuração do serializer."""

        model = Concurso
        fields = ["value", "label", "cargos", "numero_processo", "codigo"]
        extra_kwargs = DESCRICOES_CONCURSO


class ConcursoAtualizarSituacaoSerializer(serializers.Serializer):
    """Situação para a qual o concurso deve passar."""

    situacao = serializers.ChoiceField(
        choices=CONCURSO_SITUACAO_CHOICES,
        help_text=(
            "Situação de destino. Obrigatória. Só `EM_ANDAMENTO` e "
            "`COMPLETO` podem produzir alteração."
        ),
    )


class LinksPaginacaoSerializer(serializers.Serializer):
    """Links de navegação entre as páginas da listagem."""

    next = serializers.URLField(
        allow_null=True,
        help_text="URL da próxima página, ou nulo na última página.",
    )
    previous = serializers.URLField(
        allow_null=True,
        help_text="URL da página anterior, ou nulo na primeira página.",
    )


class ConcursoPaginadoSerializer(serializers.Serializer):
    """Página da listagem de concursos."""

    links = LinksPaginacaoSerializer(
        help_text="Links para as páginas vizinhas."
    )
    count = serializers.IntegerField(
        help_text="Total de concursos que atendem aos filtros."
    )
    page = serializers.IntegerField(help_text="Número da página retornada.")
    page_size = serializers.IntegerField(
        help_text="Quantidade de concursos por página pedida."
    )
    results = ConcursoListSerializer(
        many=True, help_text="Concursos da página."
    )
