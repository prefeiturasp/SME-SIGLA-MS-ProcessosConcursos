"""Django management command to create/update Cargos e Concursos.

usando a API de Integração da SME.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from cargos.models import Cargo
from concursos.models import Concurso
from concursos.services.sme_integration import (
    buscar_cargos_de_smeintegracao,
    buscar_concursos_de_smeintegracao,
)


class Command(BaseCommand):
    """Define Command."""

    help = "Cria/atualiza Cargos e Concursos a partir da API SME Integração"

    def add_arguments(self, parser):
        """Registra argumentos da linha de comando."""
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Executa sem gravar alterações no banco",
        )

    def handle(self, *args, **options):
        """Executa a lógica principal do comando.

        Cria/atualiza Cargos e Concursos a partir da API SME Integração.
        """
        dry_run: bool = options.get("dry_run", False)

        try:
            self.stdout.write("Buscando cargos na API...")
            cargos_api = buscar_cargos_de_smeintegracao()
            self.stdout.write(f" - Recebidos {len(cargos_api)} cargos")

            self.stdout.write("Buscando concursos na API...")
            concursos_api = buscar_concursos_de_smeintegracao()
            self.stdout.write(f" - Recebidos {len(concursos_api)} concursos")
        except Exception as exc:
            self.stderr.write(
                self.style.ERROR(f"Erro ao consultar API: {exc}")
            )
            return

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "Execução em modo dry-run; nada será gravado."
                )
            )

        try:
            with transaction.atomic():
                # Upsert de Cargos
                codigo_to_cargo: dict[int, Cargo] = {}
                created_cargos = updated_cargos = 0
                for item in cargos_api:
                    try:
                        codigo_raw = item.get("codigo")
                        nome = item.get("nome")
                        if codigo_raw is None or nome is None:
                            continue
                        codigo = int(codigo_raw)
                    except Exception:
                        continue

                    cargo, created = Cargo.objects.get_or_create(
                        codigo=codigo,
                        defaults={"nome": nome},
                    )
                    if created:
                        created_cargos += 1
                    else:
                        if cargo.nome != nome:
                            cargo.nome = nome
                            cargo.save(update_fields=["nome"])
                            updated_cargos += 1
                    codigo_to_cargo[codigo] = cargo

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Cargos -> criados: {created_cargos}, "
                        f"atualizados: {updated_cargos}"
                    )
                )

                # Upsert de Concursos
                created_conc = updated_conc = linked_m2m = 0
                for item in concursos_api:
                    try:
                        codigo_concurso = item["codigo"]
                        nome_concurso = item["nome"]
                        numero_processo = str(item["numero_processo"])
                        cargos_codes: list[int] = item["cargos"]
                    except Exception:
                        continue

                    concurso, created = Concurso.objects.get_or_create(
                        codigo=codigo_concurso,
                        defaults={
                            "nome": nome_concurso,
                            "numero_processo": numero_processo,
                        },
                    )
                    if created:
                        created_conc += 1
                    else:
                        fields_to_update = []
                        if concurso.nome != nome_concurso:
                            concurso.nome = nome_concurso
                            fields_to_update.append("nome")
                        if concurso.numero_processo != numero_processo:
                            concurso.numero_processo = numero_processo
                            fields_to_update.append("numero_processo")
                        if fields_to_update:
                            concurso.save(update_fields=fields_to_update)
                            updated_conc += 1

                    # Vincular cargos (M2M)
                    cargos_objs = [
                        codigo_to_cargo[c]
                        for c in cargos_codes
                        if c in codigo_to_cargo
                    ]
                    if cargos_objs:
                        concurso.cargos.set(cargos_objs)
                        linked_m2m += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Concursos -> criados: {created_conc}, "
                        f"atualizados: {updated_conc}, "
                        f"m2m vinculados: {linked_m2m}"
                    )
                )

                if dry_run:
                    self.stdout.write(
                        self.style.WARNING("Dry-run: revertendo transação.")
                    )
                    raise transaction.TransactionManagementError(
                        "Dry-run: rollback intencional"
                    )

        except transaction.TransactionManagementError as te:
            # Dry-run rollback esperado
            self.stdout.write(self.style.WARNING(str(te)))
        except Exception as exc:
            self.stderr.write(
                self.style.ERROR(f"Erro ao persistir no banco: {exc}")
            )
            return

        self.stdout.write(
            self.style.SUCCESS("✅ Importação concluída com sucesso.")
        )
