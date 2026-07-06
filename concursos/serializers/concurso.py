"""Serializers do modelo Concurso."""

from __future__ import annotations

from typing import Any

from django.db import IntegrityError
from rest_framework import serializers

from concursos.models import Cargo, Concurso
from concursos.services import numero_processo_esta_disponivel

from .cargo import CargoListSerializer, CargoSelectSerializer

NUMERO_PROCESSO_DUPLICADO_MSG = (
    "Já existe um concurso com este número de processo."
)


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
        # Desabilita o UniqueValidator automatico do DRF (gerado pela
        # UniqueConstraint do model), que dispararia antes do
        # validate_numero_processo com uma mensagem generica e ignoraria a
        # condicao de "apenas nao-vazios". A unicidade e garantida pelo
        # validate_numero_processo (mensagem custom) e pela constraint do
        # banco.
        extra_kwargs = {"numero_processo": {"validators": []}}

    def validate_numero_processo(self, value: str) -> str:
        """Garante que o numero do processo seja unico quando preenchido.

        Args:
            value: Numero do processo informado (pode ser vazio).

        Returns:
            O proprio valor, se disponivel.

        Raises:
            serializers.ValidationError: Se o numero ja estiver em uso
                por outro concurso.
        """
        excluir_uuid = str(self.instance.uuid) if self.instance else None
        if not numero_processo_esta_disponivel(
            value, excluir_uuid=excluir_uuid
        ):
            raise serializers.ValidationError(NUMERO_PROCESSO_DUPLICADO_MSG)
        return value

    def create(self, validated_data: dict[str, Any]) -> Concurso:
        """Cria concurso e associa cargos por UUID.

        Args:
            self: Instância do objeto.
            validated_data: dados validados; ``cargos_ids`` opcional.

        Returns:
            Instância do concurso persistida.

        Raises:
            serializers.ValidationError: Se o ``numero_processo`` violar a
                constraint de unicidade do banco (ex.: em requisicoes
                concorrentes que passam pela validacao de leitura).
        """
        cargos_ids = validated_data.pop("cargos_ids", [])
        try:
            concurso = Concurso.objects.create(**validated_data)
        except IntegrityError as erro:
            raise self._traduzir_erro_numero_processo_duplicado(erro)

        if cargos_ids:
            cargos = Cargo.objects.filter(uuid__in=cargos_ids)
            concurso.cargos.set(cargos)

        return concurso

    def update(
        self,
        instance: Concurso,
        validated_data: dict[str, Any],
    ) -> Concurso:

        """Atualiza concurso e, se informado, substitui cargos vinculados.

        Raises:
            serializers.ValidationError: Se o ``numero_processo`` violar a
                constraint de unicidade do banco em requisicoes
                concorrentes.
        """
        cargos_ids = validated_data.pop("cargos_ids", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        try:
            instance.save()
        except IntegrityError as erro:
            raise self._traduzir_erro_numero_processo_duplicado(erro)

        if cargos_ids is not None:
            cargos = Cargo.objects.filter(uuid__in=cargos_ids)
            instance.cargos.set(cargos)

        return instance

    @staticmethod
    def _traduzir_erro_numero_processo_duplicado(
        erro: IntegrityError,
    ) -> serializers.ValidationError:
        """Traduz IntegrityError de numero de processo duplicado em erro 400.

        Garante que uma violacao da constraint de unicidade do
        ``numero_processo`` (possivel sob concorrencia, apos passar pela
        validacao de leitura) seja devolvida como HTTP 400 no mesmo
        formato do ``validate_numero_processo``, em vez de propagar como
        HTTP 500. Outras violacoes de integridade sao repropagadas sem
        alteracao.

        Args:
            erro: A excecao IntegrityError capturada.

        Returns:
            Uma ``ValidationError`` no campo ``numero_processo`` se o erro
            for de unicidade do numero do processo.

        Raises:
            IntegrityError: Se o erro nao for relacionado ao
                ``numero_processo``.
        """
        if "numero_processo" in str(erro).lower():
            return serializers.ValidationError(
                {"numero_processo": [NUMERO_PROCESSO_DUPLICADO_MSG]}
            )
        raise erro


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
