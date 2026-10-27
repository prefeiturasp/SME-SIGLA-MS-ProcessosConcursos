"""Adiciona as colunas provisórias da troca de PK UUID por id inteiro."""

from django.db import migrations, models


class Migration(migrations.Migration):
    """Cria ``novo_id`` nos 3 modelos e as colunas provisórias de vínculo."""

    dependencies = [
        ("concursos", "0007_remove_concurso_ano_edital_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="concurso",
            name="novo_id",
            field=models.BigIntegerField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name="cargo",
            name="novo_id",
            field=models.BigIntegerField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name="autorizacaopublicada",
            name="novo_id",
            field=models.BigIntegerField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name="autorizacaopublicada",
            name="cargo_novo",
            field=models.BigIntegerField(null=True),
        ),
        migrations.AddField(
            model_name="concurso",
            name="cargos_novo",
            field=models.JSONField(null=True),
        ),
    ]
