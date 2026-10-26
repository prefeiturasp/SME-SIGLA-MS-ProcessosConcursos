"""Remove a coluna provisória ``cargos_novo`` e protege a volta da troca.

Reverter a troca de PK com dados perderia a FK de autorização e os
vínculos concurso↔cargo, pois as colunas UUID voltariam vazias. A volta
desta migration só é permitida com as 3 tabelas vazias.
"""

from django.db import migrations

MODELOS = ["Concurso", "Cargo", "AutorizacaoPublicada"]

MENSAGEM_VOLTA = (
    "Reverter a troca de PK com dados não é suportado: restaure o backup."
)


def impedir_volta_com_dados(apps, schema_editor):
    """Bloqueia a volta se alguma das 3 tabelas tiver linhas.

    Args:
        apps: Registro de modelos históricos da migration.
        schema_editor: Editor de esquema (não usado).

    Raises:
        RuntimeError: Se ``concurso``, ``cargo`` ou ``autorizacaopublicada``
            tiverem algum registro.
    """
    for nome in MODELOS:
        if apps.get_model("concursos", nome).objects.exists():
            raise RuntimeError(MENSAGEM_VOLTA)


class Migration(migrations.Migration):
    """Apaga ``cargos_novo``, já restaurado na tabela M2M pela 0011."""

    dependencies = [
        ("concursos", "0011_restaura_cargos_dos_concursos"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="concurso",
            name="cargos_novo",
        ),
        migrations.RunPython(
            migrations.RunPython.noop, impedir_volta_com_dados
        ),
    ]
