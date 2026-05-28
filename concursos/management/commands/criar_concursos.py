"""
Django management command to create sample concursos.
"""

import random

from django.core.management.base import BaseCommand

from concursos.models import Cargo, Concurso


class Command(BaseCommand):
    help = "Cria concursos de exemplo para desenvolvimento"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=5,
            help="Número de concursos a serem criados (padrão: 5)",
        )

    def handle(self, *args, **options):
        count = options["count"]
        self.stdout.write(self.style.SUCCESS(f"Criando {count} concursos..."))

        # Criar cargos de exemplo se solicitado
        cargos_disponiveis = []
        # Lista com (nome, codigo) fixos (não iniciam com 0)
        cargos_definidos = [
            ("Analista de Sistemas", "1001"),
            ("Desenvolvedor Backend", "1002"),
            ("Desenvolvedor Frontend", "1003"),
            ("Analista de Dados", "1004"),
            ("Engenheiro de Software", "1005"),
            ("Arquiteto de Software", "1006"),
            ("DevOps Engineer", "1007"),
            ("QA Engineer", "1008"),
            ("Product Manager", "1009"),
            ("UX/UI Designer", "1010"),
        ]
        self.stdout.write("Criando cargos de exemplo...")
        for nome, codigo in cargos_definidos:
            cargo, created = Cargo.objects.get_or_create(
                nome=nome,
                defaults={
                    "codigo": codigo,
                },
            )
            # Se já existia mas sem código (improvável), define o código fixo
            if not created and not getattr(cargo, "codigo", None):
                cargo.codigo = codigo
                cargo.save(update_fields=["codigo"])

            cargos_disponiveis.append(cargo)
            if created:
                self.stdout.write(
                    f"  ✓ Criado cargo: {nome} (código {cargo.codigo})"
                )
            else:
                self.stdout.write(
                    f"  - Cargo já existe: {nome} (código {cargo.codigo})"
                )

        concursos_criados = []

        for i in range(count):
            # Criar concurso com nome único
            nome_concurso = f"Concurso de Exemplo {i+1}"

            concurso = Concurso.objects.create(nome=nome_concurso)

            # Associar cargos aleatórios se disponíveis
            if cargos_disponiveis:
                num_cargos = random.randint(2, min(3, len(cargos_disponiveis)))
                cargos_escolhidos = random.sample(
                    cargos_disponiveis, num_cargos
                )
                concurso.cargos.set(cargos_escolhidos)

                cargos_info = ", ".join(
                    [cargo.nome for cargo in cargos_escolhidos]
                )
                self.stdout.write(
                    f"  ✓ Criado concurso: {concurso.nome} "
                    f"(Cargos: {cargos_info})"
                )
            else:
                self.stdout.write(
                    f"  ✓ Criado concurso: {concurso.nome} (sem cargos)"
                )

            concursos_criados.append(concurso)

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ {len(concursos_criados)} concursos criados com sucesso!"
            )
        )
