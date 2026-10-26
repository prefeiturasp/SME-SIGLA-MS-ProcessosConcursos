"""Popula ``novo_id``, as colunas provisórias de vínculo e o auditlog.

O vínculo concurso↔cargo é guardado em ``Concurso.cargos_novo`` como lista
de ``novo_id`` dos cargos, pois a tabela M2M é recriada na troca de PK.

Na volta, só o histórico do auditlog precisa ser desfeito; as colunas somem
quando a 0008 é revertida.
"""

import uuid

from django.db import migrations
from django.db.models import OuterRef, Subquery

TAMANHO_LOTE = 1000

MODELOS = ["Concurso", "Cargo", "AutorizacaoPublicada"]


def _gravar_lote(modelo, lote, campos):
    """Grava o lote com ``bulk_update`` e o esvazia.

    Args:
        modelo: Modelo histórico dos objetos do lote.
        lote: Objetos com os campos já preenchidos; é esvaziado.
        campos: Nomes dos campos a gravar.
    """
    modelo.objects.bulk_update(lote, campos, batch_size=TAMANHO_LOTE)
    lote.clear()


def numerar_registros(apps):
    """Grava ``novo_id`` em cada modelo, na ordem de criação.

    A gravação é feita a cada ``TAMANHO_LOTE`` registros, para não manter
    a tabela inteira em memória.

    Args:
        apps: Registro de modelos históricos da migration.
    """
    for nome in MODELOS:
        modelo = apps.get_model("concursos", nome)
        registros = modelo.objects.order_by("criado_em", "uuid").only("uuid")
        lote = []
        for numero, registro in enumerate(
            registros.iterator(chunk_size=TAMANHO_LOTE), start=1
        ):
            registro.novo_id = numero
            lote.append(registro)
            if len(lote) >= TAMANHO_LOTE:
                _gravar_lote(modelo, lote, ["novo_id"])
        _gravar_lote(modelo, lote, ["novo_id"])


def preencher_fk_provisoria(apps):
    """Copia o ``novo_id`` do cargo para ``AutorizacaoPublicada.cargo_novo``.

    FKs nulas continuam nulas, pois a subquery não encontra pai.

    Args:
        apps: Registro de modelos históricos da migration.
    """
    autorizacao = apps.get_model("concursos", "AutorizacaoPublicada")
    cargo = apps.get_model("concursos", "Cargo")
    pai_do_registro = cargo.objects.filter(uuid=OuterRef("cargo_id")).values(
        "novo_id"
    )[:1]
    autorizacao.objects.update(cargo_novo=Subquery(pai_do_registro))


def guardar_vinculos(apps):
    """Grava em ``Concurso.cargos_novo`` os ``novo_id`` dos cargos vinculados.

    A lista é ordenada; concurso sem cargos fica com ``[]``. A gravação é
    feita a cada ``TAMANHO_LOTE`` concursos.

    Args:
        apps: Registro de modelos históricos da migration.
    """
    concurso = apps.get_model("concursos", "Concurso")
    cargo = apps.get_model("concursos", "Cargo")
    vinculo = concurso.cargos.through
    novo_id_por_uuid = dict(cargo.objects.values_list("uuid", "novo_id"))
    cargos_por_concurso = {}
    for concurso_id, cargo_id in vinculo.objects.values_list(
        "concurso_id", "cargo_id"
    ).iterator(chunk_size=TAMANHO_LOTE):
        cargos_por_concurso.setdefault(concurso_id, []).append(
            novo_id_por_uuid[cargo_id]
        )
    lote = []
    for registro in concurso.objects.only("uuid").iterator(
        chunk_size=TAMANHO_LOTE
    ):
        registro.cargos_novo = sorted(cargos_por_concurso.get(registro.pk, []))
        lote.append(registro)
        if len(lote) >= TAMANHO_LOTE:
            _gravar_lote(concurso, lote, ["cargos_novo"])
    _gravar_lote(concurso, lote, ["cargos_novo"])


def _uuid_ou_none(valor):
    """Converte ``object_pk`` em UUID.

    Args:
        valor: Texto gravado em ``LogEntry.object_pk``.

    Returns:
        O UUID, ou ``None`` se o texto não for um UUID válido.
    """
    try:
        return uuid.UUID(valor)
    except ValueError:
        return None


def _tipo_de_conteudo(apps, nome):
    """Busca o ContentType do modelo em ``concursos``.

    Args:
        apps: Registro de modelos históricos da migration.
        nome: Nome do modelo, como em ``MODELOS``.

    Returns:
        O ContentType, ou ``None`` se ele ainda não existir.
    """
    return (
        apps.get_model("contenttypes", "ContentType")
        .objects.filter(app_label="concursos", model=nome.lower())
        .first()
    )


def _regravar_entradas(apps, entradas, novos_valores):
    """Regrava ``object_pk`` e ``object_id`` das entradas escolhidas.

    A gravação é feita a cada ``TAMANHO_LOTE`` entradas, e só os campos
    alterados são carregados, sem as colunas JSON do auditlog.

    Args:
        apps: Registro de modelos históricos da migration.
        entradas: ``QuerySet`` de ``LogEntry`` a examinar.
        novos_valores: Função que recebe ``(object_pk, object_id)`` da
            entrada e devolve os novos ``(object_pk, object_id)``, ou
            ``None`` para deixá-la como está.
    """
    log_entry = apps.get_model("auditlog", "LogEntry")
    campos = ["object_pk", "object_id"]
    lote = []
    for pk, object_pk, object_id in entradas.values_list(
        "pk", "object_pk", "object_id"
    ).iterator(chunk_size=TAMANHO_LOTE):
        valores = novos_valores(object_pk, object_id)
        if valores is None:
            continue
        lote.append(
            log_entry(pk=pk, object_pk=valores[0], object_id=valores[1])
        )
        if len(lote) >= TAMANHO_LOTE:
            _gravar_lote(log_entry, lote, campos)
    _gravar_lote(log_entry, lote, campos)


def _para_novo_id(novo_id_por_uuid):
    """Monta a regra que troca o UUID de ``object_pk`` pelo ``novo_id``.

    Args:
        novo_id_por_uuid: Mapa ``{UUID: novo_id}`` do modelo.

    Returns:
        Função ``(object_pk, object_id) -> (object_pk, object_id) | None``.
    """

    def regra(object_pk, object_id):
        novo_id = novo_id_por_uuid.get(_uuid_ou_none(object_pk))
        if novo_id is None:
            return None
        return str(novo_id), novo_id

    return regra


def _para_uuid(uuid_por_novo_id):
    """Monta a regra que troca o ``novo_id`` de ``object_id`` pelo UUID.

    Args:
        uuid_por_novo_id: Mapa ``{novo_id: UUID}`` do modelo.

    Returns:
        Função ``(object_pk, object_id) -> (object_pk, object_id) | None``.
    """

    def regra(object_pk, object_id):
        uuid_do_registro = uuid_por_novo_id.get(object_id)
        if uuid_do_registro is None:
            return None
        return str(uuid_do_registro), None

    return regra


def remapear_auditlog(apps):
    """Aponta os ``LogEntry`` antigos para o ``novo_id`` do registro.

    Só toca entradas com ``object_id`` nulo cujo ``object_pk`` seja o UUID
    de um registro existente; as demais ficam como estavam.

    Args:
        apps: Registro de modelos históricos da migration.
    """
    log_entry = apps.get_model("auditlog", "LogEntry")
    for nome in MODELOS:
        tipo = _tipo_de_conteudo(apps, nome)
        if tipo is None:
            continue
        modelo = apps.get_model("concursos", nome)
        entradas = log_entry.objects.filter(
            content_type=tipo, object_id__isnull=True
        )
        _regravar_entradas(
            apps,
            entradas,
            _para_novo_id(dict(modelo.objects.values_list("uuid", "novo_id"))),
        )


def restaurar_auditlog(apps, schema_editor):
    """Devolve os ``LogEntry`` ao formato antigo, com ``object_pk`` em UUID.

    Desfaz ``remapear_auditlog``: cada entrada cujo ``object_id`` é o
    ``novo_id`` de um registro volta a ter ``object_pk = str(uuid)`` e
    ``object_id`` nulo, que é como o código anterior à troca de PK a busca.
    As demais entradas ficam como estavam.

    Args:
        apps: Registro de modelos históricos da migration.
        schema_editor: Editor de esquema (não usado).
    """
    log_entry = apps.get_model("auditlog", "LogEntry")
    for nome in MODELOS:
        tipo = _tipo_de_conteudo(apps, nome)
        if tipo is None:
            continue
        modelo = apps.get_model("concursos", nome)
        entradas = log_entry.objects.filter(
            content_type=tipo, object_id__isnull=False
        )
        uuid_por_novo_id = dict(
            modelo.objects.filter(novo_id__isnull=False).values_list(
                "novo_id", "uuid"
            )
        )
        _regravar_entradas(apps, entradas, _para_uuid(uuid_por_novo_id))


def popular_novo_id(apps, schema_editor):
    """Numera os registros, preenche as colunas provisórias e o log.

    Args:
        apps: Registro de modelos históricos da migration.
        schema_editor: Editor de esquema (não usado).
    """
    numerar_registros(apps)
    preencher_fk_provisoria(apps)
    guardar_vinculos(apps)
    remapear_auditlog(apps)


class Migration(migrations.Migration):
    """Carga de dados das colunas criadas na 0008."""

    dependencies = [
        ("concursos", "0008_adiciona_novo_id"),
        ("auditlog", "0017_add_actor_email"),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.RunPython(popular_novo_id, restaurar_auditlog),
    ]
