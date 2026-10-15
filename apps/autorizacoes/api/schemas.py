"""Documentação OpenAPI de autorizações publicadas e extração de dados."""

from __future__ import annotations

from typing import Any

from drf_spectacular.extensions import OpenApiSerializerExtension
from drf_spectacular.openapi import AutoSchema
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    Direction,
    OpenApiParameter,
    PolymorphicProxySerializer,
    extend_schema,
)
from rest_framework.settings import api_settings

from autorizacoes.models import AutorizacaoPublicada
from autorizacoes.serializers import (
    CHAVE_TOTAL_AUTORIZACOES,
    AutorizacaoPublicadaPaginadaSerializer,
    AutorizacaoPublicadaSerializer,
    AutorizacoesPublicadasTotalSerializer,
    ExtracaoDadosPorAnoSerializer,
    ExtracaoDadosSerializer,
)
from cargos.api.schemas import EXEMPLO_CARGO_RESUMIDO, UUID_CARGO_EXEMPLO
from concursos.api.schemas import UUID_CONCURSO_EXEMPLO
from core.openapi import (
    RESPOSTA_PAGINA_INEXISTENTE,
    exemplos_requisicao,
    resposta,
    resposta_nao_encontrado,
    respostas,
)
from core.serializers import ErrosValidacaoSerializer

TAG_AUTORIZACOES = "Autorizações publicadas"
TAG_EXTRACAO_DADOS = "Extração de dados"

UUID_AUTORIZACAO_EXEMPLO = "d3b07384-d9a0-4c1b-8f5e-6a7b8c9d0e1f"

EXEMPLO_DADOS_AUTORIZACAO = {
    "cargo": UUID_CARGO_EXEMPLO,
    "autorizacoes": 120,
    "data_autorizacao": "2025-03-10",
    "observacao": "Publicada no Diário Oficial de 10/03/2025.",
}

EXEMPLO_AUTORIZACAO = {
    "uuid": UUID_AUTORIZACAO_EXEMPLO,
    **EXEMPLO_DADOS_AUTORIZACAO,
    "criado_em": "2025-03-11T09:00:00-03:00",
    "atualizado_em": "2025-03-11T09:00:00-03:00",
}

EXEMPLO_PAGINA = {
    "count": 1,
    "next": None,
    "previous": None,
    "results": [EXEMPLO_AUTORIZACAO],
}

EXEMPLO_EXTRACAO_2025 = {
    CHAVE_TOTAL_AUTORIZACOES: 120,
    "cargos": [
        {
            **EXEMPLO_CARGO_RESUMIDO,
            "autorizacoes": 120,
            "data_autorizacao": "2025-03-10",
        }
    ],
}

EXEMPLO_EXTRACAO_2026 = {
    CHAVE_TOTAL_AUTORIZACOES: 30,
    "cargos": [
        {
            **EXEMPLO_CARGO_RESUMIDO,
            "autorizacoes": 30,
            "data_autorizacao": "2026-02-01",
        }
    ],
}

EXEMPLO_EXTRACAO = {
    CHAVE_TOTAL_AUTORIZACOES: 150,
    "cargos": [
        {
            **EXEMPLO_CARGO_RESUMIDO,
            "autorizacoes": 150,
            "data_autorizacao": "2026-02-01",
        }
    ],
}

EXEMPLO_EXTRACAO_POR_ANO = {
    "2025": EXEMPLO_EXTRACAO_2025,
    "2026": EXEMPLO_EXTRACAO_2026,
}

ERRO_DATA_INVALIDA = {
    "data_autorizacao": [
        "Formato inválido para data. Use um dos formatos a seguir: "
        "YYYY-MM-DD."
    ]
}


class ExtracaoDadosPorAnoExtension(OpenApiSerializerExtension):
    """Descreve ``ExtracaoDadosPorAnoSerializer`` como mapa ano → totais."""

    target_class = ExtracaoDadosPorAnoSerializer

    def map_serializer(
        self, auto_schema: AutoSchema, direction: Direction
    ) -> dict[str, Any]:
        """Retorna o schema do mapa indexado pelo ano."""
        return {
            "type": "object",
            "description": (
                "Totais de autorizações publicadas separados por ano. Cada "
                "chave é um dos anos pedidos e o valor traz o total e os "
                "cargos daquele ano."
            ),
            "additionalProperties": auto_schema.resolve_serializer(
                ExtracaoDadosSerializer, direction
            ).ref,
        }


EXTRACAO_DADOS = PolymorphicProxySerializer(
    component_name="ExtracaoDadosResposta",
    serializers=[ExtracaoDadosSerializer, ExtracaoDadosPorAnoSerializer],
    resource_type_field_name=None,
    many=False,
)

PARAMETRO_UUID = OpenApiParameter(
    name="uuid",
    type=OpenApiTypes.UUID,
    location=OpenApiParameter.PATH,
    description="UUID da autorização publicada.",
)

PARAMETROS_LISTAGEM = [
    OpenApiParameter(
        name="cargo__uuid",
        type=OpenApiTypes.UUID,
        description=(
            "Retorna apenas as autorizações do cargo com o UUID informado."
        ),
    ),
    OpenApiParameter(
        name="cargo__codigo",
        type=OpenApiTypes.INT,
        description=(
            "Retorna apenas as autorizações dos cargos com o código "
            "informado."
        ),
    ),
    OpenApiParameter(
        name="search",
        type=OpenApiTypes.STR,
        description="Busca por trecho da observação.",
    ),
    OpenApiParameter(
        name="ordering",
        type=OpenApiTypes.STR,
        description=(
            "Campo de ordenação: `data_autorizacao` ou `criado_em`. "
            "Prefixe com `-` para ordem decrescente e separe vários campos "
            "por vírgula. Padrão: `-data_autorizacao,-criado_em`. Outros "
            "campos são ignorados."
        ),
    ),
    OpenApiParameter(
        name="page",
        type=OpenApiTypes.INT,
        description=(
            "Número da página, a partir de 1. Cada página traz até "
            f"{api_settings.PAGE_SIZE} autorizações."
        ),
    ),
]

RESPOSTA_AUTORIZACAO = resposta(
    AutorizacaoPublicadaSerializer,
    "Autorização publicada.",
    {"Autorização publicada": EXEMPLO_AUTORIZACAO},
)

RESPOSTA_NAO_ENCONTRADO = resposta_nao_encontrado(AutorizacaoPublicada)

RESPOSTA_DADOS_INVALIDOS = resposta(
    ErrosValidacaoSerializer,
    "Dados inválidos ou cargo inexistente.",
    {
        "Cargo ausente": {"cargo": ["Este campo é obrigatório."]},
        "Cargo inexistente": {
            "cargo": [
                f'Pk inválido "{UUID_CARGO_EXEMPLO}" - objeto não existe.'
            ]
        },
        "Data em formato inválido": ERRO_DATA_INVALIDA,
    },
)

OPERACOES_AUTORIZACOES = {
    "list": extend_schema(
        operation_id="listar_autorizacoes_publicadas",
        summary="Listar autorizações publicadas",
        description=(
            "Lista as autorizações publicadas, da data de autorização mais "
            "recente para a mais antiga, com paginação. Use `cargo__uuid` "
            "para ver as autorizações de um cargo."
        ),
        parameters=PARAMETROS_LISTAGEM,
        responses=respostas(
            {
                200: resposta(
                    AutorizacaoPublicadaPaginadaSerializer,
                    "Página de autorizações publicadas.",
                    {"Lista paginada": EXEMPLO_PAGINA},
                ),
                400: resposta(
                    ErrosValidacaoSerializer,
                    (
                        "Filtro `cargo__uuid` ou `cargo__codigo` com valor "
                        "inválido."
                    ),
                    {
                        "UUID de cargo malformado": {
                            "cargo__uuid": ["Insira um UUID válido."]
                        },
                        "Código de cargo não numérico": {
                            "cargo__codigo": ["Informe um número."]
                        },
                    },
                ),
                404: RESPOSTA_PAGINA_INEXISTENTE,
            }
        ),
    ),
    "create": extend_schema(
        operation_id="criar_autorizacao_publicada",
        summary="Criar autorização publicada",
        description=(
            "Registra a quantidade de autorizações publicadas para um "
            "cargo. Apenas `cargo` é obrigatório, e o cargo precisa "
            "existir. Sem `autorizacoes`, o valor é 0; sem "
            "`data_autorizacao`, o registro fica sem data e não entra na "
            "extração de dados.\n\n"
            "`autorizacoes` aceita qualquer inteiro, inclusive negativo."
        ),
        request=AutorizacaoPublicadaSerializer,
        examples=exemplos_requisicao(
            {"Nova autorização": EXEMPLO_DADOS_AUTORIZACAO}
        ),
        responses=respostas(
            {
                201: resposta(
                    AutorizacaoPublicadaSerializer,
                    "Autorização publicada criada.",
                    {"Autorização publicada": EXEMPLO_AUTORIZACAO},
                ),
                400: RESPOSTA_DADOS_INVALIDOS,
            }
        ),
    ),
    "retrieve": extend_schema(
        operation_id="detalhar_autorizacao_publicada",
        summary="Detalhar autorização publicada",
        description="Retorna uma autorização publicada pelo UUID.",
        parameters=[PARAMETRO_UUID],
        responses=respostas(
            {200: RESPOSTA_AUTORIZACAO, 404: RESPOSTA_NAO_ENCONTRADO}
        ),
    ),
    "update": extend_schema(
        operation_id="atualizar_autorizacao_publicada",
        summary="Atualizar autorização publicada",
        description=(
            "Substitui os dados da autorização. `cargo` é obrigatório; os "
            "demais campos, quando não enviados, mantêm o valor atual."
        ),
        parameters=[PARAMETRO_UUID],
        request=AutorizacaoPublicadaSerializer,
        examples=exemplos_requisicao(
            {"Dados da autorização": EXEMPLO_DADOS_AUTORIZACAO}
        ),
        responses=respostas(
            {
                200: RESPOSTA_AUTORIZACAO,
                400: RESPOSTA_DADOS_INVALIDOS,
                404: RESPOSTA_NAO_ENCONTRADO,
            }
        ),
    ),
    "partial_update": extend_schema(
        operation_id="atualizar_parcial_autorizacao_publicada",
        summary="Atualizar autorização publicada parcialmente",
        description="Altera apenas os campos enviados.",
        parameters=[PARAMETRO_UUID],
        request=AutorizacaoPublicadaSerializer,
        examples=exemplos_requisicao(
            {
                "Retificar a quantidade": {
                    "autorizacoes": 130,
                    "observacao": (
                        "Quantidade retificada no Diário Oficial de "
                        "02/04/2025."
                    ),
                }
            }
        ),
        responses=respostas(
            {
                200: RESPOSTA_AUTORIZACAO,
                400: resposta(
                    ErrosValidacaoSerializer,
                    "Dados inválidos ou cargo inexistente.",
                    {
                        "Quantidade não numérica": {
                            "autorizacoes": [
                                "Um número inteiro válido é exigido."
                            ]
                        },
                        "Data em formato inválido": ERRO_DATA_INVALIDA,
                    },
                ),
                404: RESPOSTA_NAO_ENCONTRADO,
            }
        ),
    ),
    "destroy": extend_schema(
        operation_id="excluir_autorizacao_publicada",
        summary="Excluir autorização publicada",
        description="Exclui a autorização publicada definitivamente.",
        parameters=[PARAMETRO_UUID],
        responses=respostas(
            {
                204: resposta(None, "Autorização publicada excluída."),
                404: RESPOSTA_NAO_ENCONTRADO,
            }
        ),
    ),
}

OPERACOES_EXTRACAO_DADOS = {
    "create": extend_schema(
        operation_id="extrair_dados_autorizacoes",
        summary="Extrair totais de autorizações publicadas",
        description=(
            "Soma as autorizações publicadas e devolve o total geral e o "
            "total por cargo. Só entram autorizações com data. É uma "
            "consulta: nada é gravado, e o sucesso responde 200.\n\n"
            "`concurso_uuid` restringe a soma aos cargos vinculados ao "
            "concurso; um concurso inexistente ou sem cargos resulta em "
            "totais zerados, não em 404. Com `anos`, a resposta passa a "
            "ser um objeto com uma chave por ano pedido, inclusive os anos "
            "sem autorizações. Sem filtros, envie `{}`."
        ),
        request=AutorizacoesPublicadasTotalSerializer,
        examples=exemplos_requisicao(
            {
                "Sem filtros": {},
                "Por concurso e ano": {
                    "concurso_uuid": UUID_CONCURSO_EXEMPLO,
                    "anos": [2025, 2026],
                },
            }
        ),
        responses=respostas(
            {
                200: resposta(
                    EXTRACAO_DADOS,
                    "Totais gerais ou, com `anos`, totais por ano.",
                    {
                        "Total geral": EXEMPLO_EXTRACAO,
                        "Por ano": EXEMPLO_EXTRACAO_POR_ANO,
                    },
                ),
                400: resposta(
                    ErrosValidacaoSerializer,
                    "Filtros inválidos.",
                    {
                        "UUID de concurso malformado": {
                            "concurso_uuid": ["Must be a valid UUID."]
                        },
                        "Ano não numérico": {
                            "anos": {
                                "0": ["Um número inteiro válido é exigido."]
                            }
                        },
                    },
                ),
            }
        ),
    ),
}
