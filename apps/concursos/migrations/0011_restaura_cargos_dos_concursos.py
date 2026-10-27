"""Restaura os vínculos concurso↔cargo na tabela M2M recriada na 0010.

Os vínculos estão em ``Concurso.cargos_novo``, gravados pela 0009 como
lista de ``id`` dos cargos. Na volta, a lista é regravada a partir da
tabela intermediária, que fica vazia como a 0010 a deixou.
"""

from django.db import migrations

TAMANHO_LOTE = 1000


def _gravar_lote(modelo, lote, campos):
    """Grava o lote com ``bulk_update`` e o esvazia.

    Args:
        modelo: Modelo histórico dos objetos do lote.
        lote: Objetos com os campos já preenchidos; é esvaziado.
        campos: Nomes dos campos a gravar.
    """
    modelo.objects.bulk_update(lote, campos, batch_size=TAMANHO_LOTE)
    lote.clear()


def _criar_lote(modelo, lote):
    """Insere o lote com ``bulk_create`` e o esvazia.

    Args:
        modelo: Modelo histórico dos objetos do lote.
        lote: Objetos a inserir; é esvaziado.
    """
    modelo.objects.bulk_create(lote, batch_size=TAMANHO_LOTE)
    lote.clear()


def restaurar_vinculos(apps, schema_editor):
    """Cria as linhas da tabela M2M a partir de ``Concurso.cargos_novo``.

    Concurso com ``cargos_novo`` vazio ou nulo fica sem vínculos. A
    inserção é feita a cada ``TAMANHO_LOTE`` vínculos.

    Args:
        apps: Registro de modelos históricos da migration.
        schema_editor: Editor de esquema (não usado).
    """
    concurso = apps.get_model("concursos", "Concurso")
    vinculo = concurso.cargos.through
    lote = []
    for concurso_id, cargos_ids in concurso.objects.values_list(
        "id", "cargos_novo"
    ).iterator(chunk_size=TAMANHO_LOTE):
        for cargo_id in cargos_ids or []:
            lote.append(vinculo(concurso_id=concurso_id, cargo_id=cargo_id))
            if len(lote) >= TAMANHO_LOTE:
                _criar_lote(vinculo, lote)
    _criar_lote(vinculo, lote)


def salvar_vinculos(apps, schema_editor):
    """Regrava ``Concurso.cargos_novo`` a partir da tabela intermediária.

    A lista é ordenada; concurso sem cargos fica com ``[]``. Depois as
    linhas da tabela intermediária são apagadas, deixando-a como a 0010 a
    criou. A gravação é feita a cada ``TAMANHO_LOTE`` concursos.

    Args:
        apps: Registro de modelos históricos da migration.
        schema_editor: Editor de esquema (não usado).
    """
    concurso = apps.get_model("concursos", "Concurso")
    vinculo = concurso.cargos.through
    cargos_por_concurso = {}
    for concurso_id, cargo_id in vinculo.objects.values_list(
        "concurso_id", "cargo_id"
    ).iterator(chunk_size=TAMANHO_LOTE):
        cargos_por_concurso.setdefault(concurso_id, []).append(cargo_id)
    lote = []
    for registro in concurso.objects.only("id").iterator(
        chunk_size=TAMANHO_LOTE
    ):
        registro.cargos_novo = sorted(cargos_por_concurso.get(registro.pk, []))
        lote.append(registro)
        if len(lote) >= TAMANHO_LOTE:
            _gravar_lote(concurso, lote, ["cargos_novo"])
    _gravar_lote(concurso, lote, ["cargos_novo"])
    vinculo.objects.all().delete()


class Migration(migrations.Migration):
    """Carga dos vínculos M2M guardados na 0009; só dados."""

    dependencies = [
        ("concursos", "0010_troca_pk_uuid_por_id"),
    ]

    operations = [
        migrations.RunPython(restaurar_vinculos, salvar_vinculos),
    ]
