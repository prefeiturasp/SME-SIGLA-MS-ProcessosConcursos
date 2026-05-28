from rest_framework import serializers

from concursos.models import AutorizacaoPublicada, Cargo


class AutorizacaoPublicadaSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo AutorizacaoPublicada.
    """

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

    def create(self, validated_data):
        cargo_uuid = validated_data.pop("cargo", None)
        if cargo_uuid:
            try:
                validated_data["cargo"] = Cargo.objects.get(uuid=cargo_uuid)
            except Cargo.DoesNotExist as err:
                raise serializers.ValidationError(
                    {"cargo": "Cargo não encontrado"}
                ) from err
        return super().create(validated_data)
