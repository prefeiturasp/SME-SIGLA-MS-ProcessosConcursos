# Generated manually to rename field tipo_processo to tipo_concurso

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('concursos', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='concurso',
            old_name='tipo_processo',
            new_name='tipo_concurso',
        ),
    ] 