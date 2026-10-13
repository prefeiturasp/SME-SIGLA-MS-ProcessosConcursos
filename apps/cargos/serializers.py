"""Serializers do domínio de cargos."""

from rest_framework import serializers

from cargos.models import Cargo

DESCRICOES_CARGO = {
    "uuid": {"help_text": "Identificador do cargo."},
    "nome": {"help_text": "Nome do cargo."},
    "codigo": {
        "help_text": (
            "Código numérico do cargo na SME, usado para cruzar o cargo "
            "com os demais microsserviços. Pode se repetir entre cargos e "
            "assume 0 quando não é enviado."
        )
    },
    "criado_em": {"help_text": "Data e hora de criação do registro."},
    "atualizado_em": {
        "help_text": "Data e hora da última alteração do registro."
    },
}


class CargoSerializer(serializers.ModelSerializer):
    """Cargo ofertado nos concursos."""

    class Meta:
        """Configuração do serializer."""

        model = Cargo
        fields = ["uuid", "nome", "codigo", "criado_em", "atualizado_em"]
        read_only_fields = ["uuid", "criado_em", "atualizado_em"]
        extra_kwargs = DESCRICOES_CARGO


class CargoListSerializer(serializers.ModelSerializer):
    """Cargo resumido, como aparece dentro de um concurso."""

    class Meta:
        """Configuração do serializer."""

        model = Cargo
        fields = ["uuid", "nome", "codigo"]
        extra_kwargs = DESCRICOES_CARGO


class CargoSelectSerializer(serializers.ModelSerializer):
    """Cargo como opção de um campo de seleção."""

    value = serializers.UUIDField(
        source="uuid", help_text="UUID do cargo: o valor a enviar."
    )
    label = serializers.CharField(
        source="nome", help_text="Nome do cargo: o texto a exibir."
    )

    class Meta:
        """Configuração do serializer."""

        model = Cargo
        fields = ["value", "label", "codigo"]
        extra_kwargs = DESCRICOES_CARGO


class CargoAutorizacoesSerializer(serializers.Serializer):
    """Cargo com o total de autorizações publicadas e de escolhas."""

    uuid = serializers.UUIDField(help_text="Identificador do cargo.")
    nome = serializers.CharField(help_text="Nome do cargo.")
    codigo = serializers.IntegerField(
        allow_null=True, help_text="Código numérico do cargo na SME."
    )
    autorizacoes = serializers.IntegerField(
        help_text=(
            "Soma das autorizações publicadas para o cargo, inclusive as "
            "que não têm data."
        )
    )
    data_autorizacao_mais_recente = serializers.DateField(
        allow_null=True,
        help_text=(
            "Data da autorização publicada mais recente do cargo, ou nulo "
            "se nenhuma tem data."
        ),
    )
    total_escolhas = serializers.IntegerField(
        help_text=(
            "Quantidade de escolhas registradas no MS-Escolhas para o "
            "código do cargo."
        )
    )
