from rest_framework import serializers
from .models import Concurso


class ConcursoSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Concurso
        fields = '__all__'
        read_only_fields = ('criado_em', 'atualizado_em')
