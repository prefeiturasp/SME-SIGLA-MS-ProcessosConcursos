"""
Django management command to create sample concursos.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from concursos.models import Concurso
import uuid
import random


class Command(BaseCommand):
    help = 'Cria concursos de exemplo para desenvolvimento'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help='Número de concursos a serem criados (padrão: 5)'
        )

    def handle(self, *args, **options):
        count = options['count']
        
        self.stdout.write(
            self.style.SUCCESS(f'Criando {count} concursos com valores aleatórios...')
        )
        
        concursos_criados = []
        
        for i in range(count):
            # Gerar valores aleatórios para os campos com choices
            # Status aleatório
            status_choices = [choice[0] for choice in Concurso.CONCURSO_STATUS_CHOICES]
            random_status = random.choice(status_choices)
            
            # Tipo de concurso aleatório
            tipo_choices = [choice[0] for choice in Concurso.CONCURSO_TIPOS_CHOICES]
            random_tipo = random.choice(tipo_choices)
            
            # Descrição aleatória
            descricao_choices = [choice[0] for choice in Concurso.DESCRICAO_TIPOS_CHOICES]
            random_descricao = random.choice(descricao_choices)
            
            concurso = Concurso.objects.create(
                concurso_uuid=uuid.uuid4(),
                concurso_nome=f'Concurso de Exemplo {i+1}',
                descricao=random_descricao,
                tipo_concurso=random_tipo,
                status=random_status,
                data_publicacao=timezone.now(),
                data_convocacao=timezone.now(),
                numero_convocados=i+1
            )
            concursos_criados.append(concurso)
            
            # Mostrar informações do concurso criado
            status_display = dict(Concurso.CONCURSO_STATUS_CHOICES)[random_status]
            tipo_display = dict(Concurso.CONCURSO_TIPOS_CHOICES)[random_tipo]
            descricao_display = dict(Concurso.DESCRICAO_TIPOS_CHOICES)[random_descricao]
            
            self.stdout.write(
                f'  ✓ Criado concurso: {concurso.concurso_nome} '
                f'(Status: {status_display}, Tipo: {tipo_display}, Descrição: {descricao_display})'
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ {len(concursos_criados)} concursos criados com sucesso!'
            )
        ) 