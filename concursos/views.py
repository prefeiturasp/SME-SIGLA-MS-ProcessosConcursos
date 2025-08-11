"""
DRF views for the concursos module.
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Concurso
from .serializers import (
    ConcursoSerializer,
)
from .services import ExternalServices


class ConcursoViewSet(viewsets.ModelViewSet):
    
    queryset = Concurso.objects.all()
    # permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'tipo_concurso']
    search_fields = ['concurso_nome', 'descricao']
    ordering_fields = ['concurso_nome', 'data_publicacao', 'criado_em']
    ordering = ['-criado_em']
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'list':
            return ConcursoSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ConcursoSerializer
        return ConcursoSerializer
    
    def perform_create(self, serializer):
        """Override to add custom logic on create."""
        concurso = serializer.save()
        print(concurso)
        ###
    
    def perform_update(self, serializer):
        """Override to add custom logic on update."""
        concurso = serializer.save()
        print(concurso)
        ###
        
    
    def perform_destroy(self, instance):
        """Override to add custom logic on delete."""
        instance.delete()
    
    @action(detail=True, methods=['post'])
    def finalizar(self, request, pk=None):
        """Finalizar um concurso."""
        concurso = self.get_object()
        
        if not concurso.status == 'EM_ANDAMENTO':
            return Response(
                {'error': 'Concurso não pode ser finalizado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        concurso.status = 'FINALIZADO'
        concurso.save()
        
        serializer = self.get_serializer(concurso)
        return Response(serializer.data)

