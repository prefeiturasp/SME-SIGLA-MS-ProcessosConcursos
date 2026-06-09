"""Django management command to clear all concursos."""

from django.core.management.base import BaseCommand

from concursos.models import Cargo, Concurso


class Command(BaseCommand):
    """Define Command."""

    help = "Remove todos os registros da tabela de concursos"

    def handle(self, *args, **options):
        """Executa a lógica principal do comando.

        Remove todos os registros da tabela de concursos.
        """
        total_concursos = Concurso.objects.count()
        total_cargos = Cargo.objects.count()
        # Executar a exclusão
        self.stdout.write(
            self.style.SUCCESS(
                f"Removendo {total_concursos} concursos "
                f"e {total_cargos} cargos..."
            )
        )

        try:
            # Método 1: Usando delete() em queryset (mais seguro)
            Concurso.objects.all().delete()
            Cargo.objects.all().delete()

            # Método 2: Usando SQL direto (mais rápido, mas menos seguro)
            # with connection.cursor() as cursor:
            #     cursor.execute("DELETE FROM concursos")

            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ {total_concursos} concursos e "
                    f"{total_cargos} cargos removidos com sucesso!"
                )
            )

            # Verificar se realmente foi limpo
            concursos_restantes = Concurso.objects.count()
            cargos_restantes = Cargo.objects.count()
            if concursos_restantes == 0 and cargos_restantes == 0:
                self.stdout.write(
                    self.style.SUCCESS("✅ Tabelas completamente limpas!")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"⚠️  Ainda restam {concursos_restantes} "
                        f"concursos e {cargos_restantes} cargos."
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Erro ao remover registros: {e}")
            )
