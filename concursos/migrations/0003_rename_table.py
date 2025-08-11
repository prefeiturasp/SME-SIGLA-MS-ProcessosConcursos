# Generated manually to rename table from processos_convocacao to concursos

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('concursos', '0002_rename_tipo_processo_to_tipo_concurso'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='concurso',
            table='concursos',
        ),
    ] 