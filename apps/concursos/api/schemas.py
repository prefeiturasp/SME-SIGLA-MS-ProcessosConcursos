"""Documentação OpenAPI das operações de concursos."""

from __future__ import annotations

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiParameter,
    PolymorphicProxySerializer,
    extend_schema,
)

from cargos.api.schemas import (
    CODIGO_CARGO_EXEMPLO,
    EXEMPLO_CARGO_RESUMIDO,
    EXEMPLO_OPCAO_CARGO,
    NOME_CARGO_EXEMPLO,
    UUID_CARGO_EXEMPLO,
)
from concursos.constants import (
    CONCURSO_SITUACAO_CHOICES,
    CONCURSO_SITUACAO_COMPLETO,
    CONCURSO_SITUACAO_EM_ANDAMENTO,
    CONCURSO_SITUACAO_INCOMPLETO,
    CONCURSO_STATUS_CHOICES,
)
from concursos.models import Concurso
from concursos.serializers import (
    ConcursoAtualizarSituacaoSerializer,
    ConcursoPaginadoSerializer,
    ConcursoSelectSerializer,
    ConcursoSerializer,
)
from core.openapi import (
    RESPOSTA_PAGINA_INEXISTENTE,
    exemplos_requisicao,
    resposta,
    resposta_nao_encontrado,
    respostas,
)
from core.serializers import ErrosValidacaoSerializer
from core.utils import DEFAULT_PAGE_SIZE

TAG_CONCURSOS = "Concursos"

UUID_CONCURSO_EXEMPLO = "7e6d5c4b-3a2f-4e1d-9c8b-7a6f5e4d3c2b"
NOME_CONCURSO_EXEMPLO = "Concurso Professor de Educação Infantil 2025"
NUMERO_PROCESSO_EXEMPLO = "6016.2025/0001234-5"
CODIGO_CONCURSO_EXEMPLO = 215
BANCA_EXEMPLO = "Fundação Exemplo"

STATUS = [codigo for codigo, _ in CONCURSO_STATUS_CHOICES]
SITUACOES = [codigo for codigo, _ in CONCURSO_SITUACAO_CHOICES]

EXEMPLO_DADOS_EDITAL = {
    "codigo": CODIGO_CONCURSO_EXEMPLO,
    "banca_responsavel": BANCA_EXEMPLO,
    "data_autorizacao": "2025-01-20",
    "data_abertura": "2025-03-03",
    "classificacao_final": "2025-09-12",
    "link_edital": "https://exemplo.test/editais/educacao-infantil-2025.pdf",
    "habilitados_geral": 1500,
    "habilitados_nna": 300,
    "habilitados_pcd": 75,
    "retificacoes": "Retificação nº 1, de 10/03/2025: altera o cronograma.",
    "data_homologacao": "2025-10-01",
    "data_prorrogacao": None,
    "vigencia_inicio": "2025-10-01",
    "vigencia_fim": "2027-10-01",
}

EXEMPLO_CONCURSO = {
    "uuid": UUID_CONCURSO_EXEMPLO,
    "nome": NOME_CONCURSO_EXEMPLO,
    "cargos": [EXEMPLO_CARGO_RESUMIDO],
    "criado_em": "2025-01-22T09:30:00-03:00",
    "atualizado_em": "2025-10-01T14:10:00-03:00",
    "numero_processo": NUMERO_PROCESSO_EXEMPLO,
    "status": "ATIVO",
    "situacao": CONCURSO_SITUACAO_COMPLETO,
    **EXEMPLO_DADOS_EDITAL,
}

EXEMPLO_CONCURSO_CRIADO = {
    **EXEMPLO_CONCURSO,
    "atualizado_em": "2025-01-22T09:30:00-03:00",
    "situacao": CONCURSO_SITUACAO_INCOMPLETO,
}

EXEMPLO_CONCURSO_EM_ANDAMENTO = {
    **EXEMPLO_CONCURSO,
    "situacao": CONCURSO_SITUACAO_EM_ANDAMENTO,
}

EXEMPLO_CONCURSO_LISTADO = {
    "uuid": UUID_CONCURSO_EXEMPLO,
    "nome": NOME_CONCURSO_EXEMPLO,
    "cargos": [EXEMPLO_CARGO_RESUMIDO],
    "cargos_descricao": [f"{CODIGO_CARGO_EXEMPLO} - {NOME_CARGO_EXEMPLO}"],
    "numero_processo": NUMERO_PROCESSO_EXEMPLO,
    "codigo": CODIGO_CONCURSO_EXEMPLO,
    "banca_responsavel": BANCA_EXEMPLO,
    "status": "ATIVO",
    "situacao": CONCURSO_SITUACAO_COMPLETO,
}

EXEMPLO_PAGINA = {
    "links": {"next": None, "previous": None},
    "count": 1,
    "page": 1,
    "page_size": DEFAULT_PAGE_SIZE,
    "results": [EXEMPLO_CONCURSO_LISTADO],
}

EXEMPLO_OPCAO_CONCURSO = {
    "value": UUID_CONCURSO_EXEMPLO,
    "label": NOME_CONCURSO_EXEMPLO,
    "cargos": [EXEMPLO_OPCAO_CARGO],
    "numero_processo": NUMERO_PROCESSO_EXEMPLO,
    "codigo": CODIGO_CONCURSO_EXEMPLO,
}

EXEMPLO_CADASTRO_MINIMO = {
    "nome": NOME_CONCURSO_EXEMPLO,
    "numero_processo": NUMERO_PROCESSO_EXEMPLO,
}

EXEMPLO_CADASTRO_COMPLETO = {
    **EXEMPLO_CADASTRO_MINIMO,
    "cargos_ids": [UUID_CARGO_EXEMPLO],
    **EXEMPLO_DADOS_EDITAL,
}

ERRO_NUMERO_REPETIDO = {
    "numero_processo": ["Este número de processo já está cadastrado."]
}

LISTAGEM_CONCURSOS = PolymorphicProxySerializer(
    component_name="ConcursoListagem",
    serializers=[
        ConcursoPaginadoSerializer,
        ConcursoSelectSerializer(many=True),
    ],
    resource_type_field_name=None,
    many=False,
)

PARAMETRO_UUID = OpenApiParameter(
    name="uuid",
    type=OpenApiTypes.UUID,
    location=OpenApiParameter.PATH,
    description="UUID do concurso.",
)

PARAMETROS_LISTAGEM = [
    OpenApiParameter(
        name="nome",
        type=OpenApiTypes.STR,
        description=(
            "Retorna os concursos cujo nome contém o trecho informado, sem "
            "diferenciar maiúsculas de minúsculas."
        ),
    ),
    OpenApiParameter(
        name="numero_processo",
        type=OpenApiTypes.STR,
        description=(
            "Retorna os concursos cujo número de processo contém o trecho "
            "informado."
        ),
    ),
    OpenApiParameter(
        name="banca_responsavel",
        type=OpenApiTypes.STR,
        description=(
            "Retorna os concursos cuja banca responsável contém o trecho "
            "informado, sem diferenciar maiúsculas de minúsculas."
        ),
    ),
    OpenApiParameter(
        name="codigo_cargo",
        type=OpenApiTypes.INT,
        description=(
            "Retorna os concursos que têm um cargo com o código informado."
        ),
    ),
    OpenApiParameter(
        name="descricao_cargo",
        type=OpenApiTypes.STR,
        description=(
            "Retorna os concursos que têm um cargo cujo nome contém o "
            "trecho informado, sem diferenciar maiúsculas de minúsculas."
        ),
    ),
    OpenApiParameter(
        name="status",
        type=OpenApiTypes.STR,
        enum=STATUS,
        description="Retorna apenas os concursos com o status informado.",
    ),
    OpenApiParameter(
        name="situacao",
        type=OpenApiTypes.STR,
        enum=SITUACOES,
        description="Retorna apenas os concursos na situação informada.",
    ),
    OpenApiParameter(
        name="status__in",
        type=OpenApiTypes.STR,
        many=True,
        enum=STATUS,
        explode=False,
        style="form",
        description=(
            "Retorna os concursos com qualquer um dos status informados, "
            "separados por vírgula. Valores desconhecidos são ignorados."
        ),
    ),
    OpenApiParameter(
        name="situacao__in",
        type=OpenApiTypes.STR,
        many=True,
        enum=SITUACOES,
        explode=False,
        style="form",
        description=(
            "Retorna os concursos em qualquer uma das situações "
            "informadas, separadas por vírgula. Valores desconhecidos são "
            "ignorados."
        ),
    ),
    OpenApiParameter(
        name="search",
        type=OpenApiTypes.STR,
        description="Busca por trecho do nome do concurso.",
    ),
    OpenApiParameter(
        name="ordering",
        type=OpenApiTypes.STR,
        description=(
            "Campo de ordenação: `nome` ou `criado_em`. Prefixe com `-` "
            "para ordem decrescente e separe vários campos por vírgula. "
            "Padrão: `-criado_em`. Outros campos são ignorados."
        ),
    ),
    OpenApiParameter(
        name="page",
        type=OpenApiTypes.INT,
        description=(
            "Número da página, a partir de 1. Sem efeito com "
            "`formato=select`."
        ),
    ),
    OpenApiParameter(
        name="page_size",
        type=OpenApiTypes.INT,
        description=(
            "Quantidade de concursos por página. Padrão: "
            f"{DEFAULT_PAGE_SIZE}. Sem efeito com `formato=select`."
        ),
    ),
    OpenApiParameter(
        name="formato",
        type=OpenApiTypes.STR,
        enum=["select"],
        description=(
            "Com `select`, a resposta deixa de ser paginada e traz a lista "
            "simples de `value` e `label`, para preencher campos de seleção."
        ),
    ),
]

RESPOSTA_CONCURSO = resposta(
    ConcursoSerializer,
    "Concurso com os cargos vinculados.",
    {"Concurso": EXEMPLO_CONCURSO},
)

RESPOSTA_NAO_ENCONTRADO = resposta_nao_encontrado(Concurso)

RESPOSTA_DADOS_INVALIDOS = resposta(
    ErrosValidacaoSerializer,
    "Dados inválidos ou número de processo já cadastrado.",
    {
        "Campos obrigatórios ausentes": {
            "nome": ["Este campo é obrigatório."],
            "numero_processo": ["Este campo é obrigatório."],
        },
        "Número de processo repetido": ERRO_NUMERO_REPETIDO,
        "UUID de cargo malformado": {
            "cargos_ids": {"0": ["Must be a valid UUID."]}
        },
    },
)

OPERACOES_CONCURSOS = {
    "list": extend_schema(
        operation_id="listar_concursos",
        summary="Listar concursos",
        description=(
            "Lista os concursos, do mais recente para o mais antigo. Os "
            "filtros podem ser combinados.\n\n"
            "Com `formato=select` a resposta não é paginada: vem a lista "
            "simples usada para preencher campos de seleção, com os mesmos "
            "filtros aplicados.\n\n"
            "Com `codigo_cargo` ou `descricao_cargo`, um concurso aparece "
            "repetido quando mais de um cargo dele atende ao filtro, e "
            "`count` conta as repetições."
        ),
        parameters=PARAMETROS_LISTAGEM,
        responses=respostas(
            {
                200: resposta(
                    LISTAGEM_CONCURSOS,
                    (
                        "Página de concursos ou, com `formato=select`, "
                        "lista simples de opções."
                    ),
                    {
                        "Lista paginada": EXEMPLO_PAGINA,
                        "Formato select": [EXEMPLO_OPCAO_CONCURSO],
                    },
                ),
                400: resposta(
                    ErrosValidacaoSerializer,
                    (
                        "Filtro `status`, `situacao` ou `codigo_cargo` com "
                        "valor inválido."
                    ),
                    {
                        "Status inexistente": {
                            "status": [
                                "Faça uma escolha válida. XYZ não é uma "
                                "das escolhas disponíveis."
                            ]
                        },
                        "Código de cargo não numérico": {
                            "codigo_cargo": ["Informe um número."]
                        },
                    },
                ),
                404: RESPOSTA_PAGINA_INEXISTENTE,
            }
        ),
    ),
    "create": extend_schema(
        operation_id="criar_concurso",
        summary="Criar concurso",
        description=(
            "Cria um concurso. Apenas `nome` e `numero_processo` são "
            "obrigatórios, e o número de processo não pode se repetir "
            "entre concursos. Sem `status` e `situacao`, o concurso nasce "
            "`ATIVO` e `INCOMPLETO`.\n\n"
            "`cargos_ids` vincula cargos já cadastrados. UUIDs que não "
            "existem são ignorados, sem erro."
        ),
        request=ConcursoSerializer,
        examples=exemplos_requisicao(
            {
                "Cadastro mínimo": EXEMPLO_CADASTRO_MINIMO,
                "Com cargos e dados do edital": EXEMPLO_CADASTRO_COMPLETO,
            }
        ),
        responses=respostas(
            {
                201: resposta(
                    ConcursoSerializer,
                    "Concurso criado.",
                    {"Concurso criado": EXEMPLO_CONCURSO_CRIADO},
                ),
                400: RESPOSTA_DADOS_INVALIDOS,
            }
        ),
    ),
    "retrieve": extend_schema(
        operation_id="detalhar_concurso",
        summary="Detalhar concurso",
        description="Retorna um concurso com os cargos vinculados.",
        parameters=[PARAMETRO_UUID],
        responses=respostas(
            {200: RESPOSTA_CONCURSO, 404: RESPOSTA_NAO_ENCONTRADO}
        ),
    ),
    "update": extend_schema(
        operation_id="atualizar_concurso",
        summary="Atualizar concurso",
        description=(
            "Substitui os dados do concurso. `nome` e `numero_processo` "
            "são obrigatórios; os demais campos, quando não enviados, "
            "mantêm o valor atual. Sem `cargos_ids`, os cargos vinculados "
            "são mantidos; com lista vazia, todos os vínculos são "
            "removidos.\n\n"
            "`situacao` pode ser enviada diretamente, sem as regras de "
            "transição da rota `atualizar-situacao`."
        ),
        parameters=[PARAMETRO_UUID],
        request=ConcursoSerializer,
        examples=exemplos_requisicao(
            {"Dados do concurso": EXEMPLO_CADASTRO_COMPLETO}
        ),
        responses=respostas(
            {
                200: RESPOSTA_CONCURSO,
                400: RESPOSTA_DADOS_INVALIDOS,
                404: RESPOSTA_NAO_ENCONTRADO,
            }
        ),
    ),
    "partial_update": extend_schema(
        operation_id="atualizar_parcial_concurso",
        summary="Atualizar concurso parcialmente",
        description=(
            "Altera apenas os campos enviados. Para `cargos_ids` e "
            "`situacao` vale o mesmo que na atualização completa."
        ),
        parameters=[PARAMETRO_UUID],
        request=ConcursoSerializer,
        examples=exemplos_requisicao(
            {
                "Registrar a homologação": {
                    "data_homologacao": "2025-10-01",
                    "vigencia_inicio": "2025-10-01",
                    "vigencia_fim": "2027-10-01",
                },
                "Remover todos os cargos": {"cargos_ids": []},
            }
        ),
        responses=respostas(
            {
                200: RESPOSTA_CONCURSO,
                400: resposta(
                    ErrosValidacaoSerializer,
                    "Dados inválidos ou número de processo já cadastrado.",
                    {
                        "Data em formato inválido": {
                            "data_homologacao": [
                                "Formato inválido para data. Use um dos "
                                "formatos a seguir: YYYY-MM-DD."
                            ]
                        },
                        "Número de processo repetido": ERRO_NUMERO_REPETIDO,
                    },
                ),
                404: RESPOSTA_NAO_ENCONTRADO,
            }
        ),
    ),
    "destroy": extend_schema(
        operation_id="excluir_concurso",
        summary="Excluir concurso",
        description=(
            "Exclui o concurso definitivamente, junto com os vínculos dele "
            "com cargos. Os cargos e as autorizações publicadas "
            "permanecem. A exclusão não verifica se há processos de "
            "convocação do concurso em outro microsserviço."
        ),
        parameters=[PARAMETRO_UUID],
        responses=respostas(
            {
                204: resposta(None, "Concurso excluído."),
                404: RESPOSTA_NAO_ENCONTRADO,
            }
        ),
    ),
    "atualizar_situacao": extend_schema(
        operation_id="atualizar_situacao_concurso",
        summary="Atualizar a situação do concurso",
        description=(
            "Aplica uma das duas transições de situação: de `COMPLETO` "
            "para `EM_ANDAMENTO` e de `EM_ANDAMENTO` para `COMPLETO`. Em "
            "qualquer outro caso, inclusive quando a situação atual não é "
            "a de origem exigida, a resposta é 200 com o concurso "
            "inalterado.\n\n"
            "É a rota usada pelo MS de convocação: ao criar um processo de "
            "convocação o concurso passa a `EM_ANDAMENTO`, e ao excluir o "
            "último processo volta a `COMPLETO`."
        ),
        parameters=[PARAMETRO_UUID],
        request=ConcursoAtualizarSituacaoSerializer,
        examples=exemplos_requisicao(
            {
                "Passar a em andamento": {
                    "situacao": CONCURSO_SITUACAO_EM_ANDAMENTO
                },
                "Voltar a completo": {"situacao": CONCURSO_SITUACAO_COMPLETO},
            }
        ),
        responses=respostas(
            {
                200: resposta(
                    ConcursoSerializer,
                    "Concurso após a chamada, alterado ou não.",
                    {"Concurso em andamento": EXEMPLO_CONCURSO_EM_ANDAMENTO},
                ),
                400: resposta(
                    ErrosValidacaoSerializer,
                    "Situação ausente ou fora das opções.",
                    {
                        "Situação ausente": {
                            "situacao": ["Este campo é obrigatório."]
                        },
                        "Situação inexistente": {
                            "situacao": ['"XYZ" não é um escolha válido.']
                        },
                    },
                ),
                404: RESPOSTA_NAO_ENCONTRADO,
            }
        ),
    ),
}
