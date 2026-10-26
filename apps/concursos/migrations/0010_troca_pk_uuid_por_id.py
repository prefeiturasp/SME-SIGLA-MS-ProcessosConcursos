"""Troca a PK UUID pelo ``id`` inteiro carregado na 0009."""

import uuid

import django.db.models.deletion
from django.core.management.color import no_style
from django.db import migrations, models

MODELOS = ["Concurso", "Cargo", "AutorizacaoPublicada"]

MENSAGEM_VOLTA = (
    "Reverter a troca de PK com dados não é suportado: restaure o backup."
)


def impedir_volta_com_dados(apps, schema_editor):
    """Bloqueia a volta se alguma das 3 tabelas tiver linhas.

    Cobre o banco parado na 0010 (por exemplo, quando a 0011 falha): a
    volta perderia a FK de autorização e os vínculos concurso↔cargo.

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


def reiniciar_sequencias(apps, schema_editor):
    """Faz a sequência de cada ``id`` continuar depois do maior valor.

    No PostgreSQL a coluna vira identity começando em 1, e sem este passo
    o primeiro INSERT colidiria com os ids da carga. No SQLite a lista de
    comandos vem vazia.

    Args:
        apps: Registro de modelos históricos da migration.
        schema_editor: Editor de esquema da conexão em uso.
    """
    conexao = schema_editor.connection
    modelos = [apps.get_model("concursos", nome) for nome in MODELOS]
    with conexao.cursor() as cursor:
        for sql in conexao.ops.sequence_reset_sql(no_style(), modelos):
            cursor.execute(sql)


class Migration(migrations.Migration):
    """Promove ``novo_id`` a PK ``id`` e refaz as relações apontando para ele.

    A FK de autorização e o M2M ``Concurso.cargos`` saem primeiro, para o
    banco deixar remover a PK do ``uuid``; os vínculos do M2M estão
    guardados em ``Concurso.cargos_novo`` e voltam na 0011. O nome
    provisório ``novo_id`` evita colidir com o ``id`` que o Django cria no
    estado intermediário, quando o modelo fica sem PK. ``novo_id`` vira
    NOT NULL antes de virar PK: na volta, o PostgreSQL só aceita o DROP NOT
    NULL depois que a PK sai. A última operação só age na volta, que ela
    bloqueia se houver dados.
    """

    dependencies = [
        ("concursos", "0009_popula_novo_id"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="autorizacaopublicada",
            name="cargo",
        ),
        migrations.RemoveField(
            model_name="concurso",
            name="cargos",
        ),
        *[
            migrations.AlterField(
                model_name=nome.lower(),
                name="uuid",
                field=models.UUIDField(
                    default=uuid.uuid4, editable=False, unique=True
                ),
            )
            for nome in MODELOS
        ],
        *[
            migrations.AlterField(
                model_name=nome.lower(),
                name="novo_id",
                field=models.BigIntegerField(editable=False),
            )
            for nome in MODELOS
        ],
        *[
            migrations.AlterField(
                model_name=nome.lower(),
                name="novo_id",
                field=models.BigAutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name="ID",
                ),
            )
            for nome in MODELOS
        ],
        *[
            migrations.RenameField(
                model_name=nome.lower(), old_name="novo_id", new_name="id"
            )
            for nome in MODELOS
        ],
        migrations.RenameField(
            model_name="autorizacaopublicada",
            old_name="cargo_novo",
            new_name="cargo",
        ),
        migrations.AlterField(
            model_name="autorizacaopublicada",
            name="cargo",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="autorizacoes",
                to="concursos.cargo",
                verbose_name="Cargo",
            ),
        ),
        migrations.AddField(
            model_name="concurso",
            name="cargos",
            field=models.ManyToManyField(
                related_name="concursos",
                to="concursos.cargo",
                verbose_name="Cargos",
            ),
        ),
        migrations.RunPython(reiniciar_sequencias, migrations.RunPython.noop),
        migrations.RunPython(
            migrations.RunPython.noop, impedir_volta_com_dados
        ),
    ]
