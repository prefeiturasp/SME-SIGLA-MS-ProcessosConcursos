from rest_framework import serializers
from concursos.models import Cargo


class CargoSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Cargo.
    """
    class Meta:
        model = Cargo
        fields = ['uuid', 'nome', 'codigo', 'criado_em', 'atualizado_em']
        read_only_fields = ['uuid', 'criado_em', 'atualizado_em']


class CargoListSerializer(serializers.ModelSerializer):
    """
    Serializer para listagem de cargos.
    """
    class Meta:
        model = Cargo
        fields = ['uuid', 'nome', 'codigo']


class CargoSelectSerializer(serializers.ModelSerializer):
    """
    Serializer para selects/dropdowns no frontend.
    """
    value = serializers.UUIDField(source='uuid')
    label = serializers.CharField(source='nome')

    class Meta:
        model = Cargo
        fields = ['value', 'label', 'codigo']

