"""Documentação OpenAPI das operações de cargos."""

from __future__ import annotations

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema

from cargos.models import Cargo
from cargos.serializers import CargoAutorizacoesSerializer, CargoSerializer
from core.openapi import (
    EXEMPLO_TOKEN_INVALIDO,
    exemplos_requisicao,
    resposta,
    resposta_nao_encontrado,
    respostas,
)
from core.serializers import ErroAcessoSerializer, ErrosValidacaoSerializer

TAG_CARGOS = "Cargos"

UUID_CARGO_EXEMPLO = "9b2f6c1e-3a4d-4e8f-b7a1-6c5d4e3f2a10"
NOME_CARGO_EXEMPLO = "Professor de Educação Infantil"
CODIGO_CARGO_EXEMPLO = 3859

EXEMPLO_CARGO_RESUMIDO = {
    "uuid": UUID_CARGO_EXEMPLO,
    "nome": NOME_CARGO_EXEMPLO,
    "codigo": CODIGO_CARGO_EXEMPLO,
}

EXEMPLO_CARGO = {
    **EXEMPLO_CARGO_RESUMIDO,
    "criado_em": "2026-03-02T10:00:00-03:00",
    "atualizado_em": "2026-03-02T10:00:00-03:00",
}

EXEMPLO_OPCAO_CARGO = {
    "value": UUID_CARGO_EXEMPLO,
    "label": NOME_CARGO_EXEMPLO,
    "codigo": CODIGO_CARGO_EXEMPLO,
}

EXEMPLO_DADOS_CARGO = {
    "nome": NOME_CARGO_EXEMPLO,
    "codigo": CODIGO_CARGO_EXEMPLO,
}

EXEMPLO_CARGO_AUTORIZACOES = {
    **EXEMPLO_CARGO_RESUMIDO,
    "autorizacoes": 150,
    "data_autorizacao_mais_recente": "2026-02-01",
    "total_escolhas": 17,
}

ERRO_CODIGO_NAO_NUMERICO = {"codigo": ["Um número inteiro válido é exigido."]}

PARAMETRO_UUID = OpenApiParameter(
    name="uuid",
    type=OpenApiTypes.UUID,
    location=OpenApiParameter.PATH,
    description="UUID do cargo.",
)

PARAMETROS_LISTAGEM = [
    OpenApiParameter(
        name="codigo",
        type=OpenApiTypes.INT,
        description="Retorna apenas os cargos com o código informado.",
    ),
    OpenApiParameter(
        name="search",
        type=OpenApiTypes.STR,
        description="Busca por trecho do nome ou do código do cargo.",
    ),
    OpenApiParameter(
        name="ordering",
        type=OpenApiTypes.STR,
        description=(
            "Campo de ordenação: `criado_em`. Prefixe com `-` para ordem "
            "decrescente. Padrão: `-criado_em`. Outros campos são "
            "ignorados."
        ),
    ),
]

RESPOSTA_CARGO = resposta(CargoSerializer, "Cargo.", {"Cargo": EXEMPLO_CARGO})

RESPOSTA_NAO_ENCONTRADO = resposta_nao_encontrado(Cargo)

RESPOSTA_DADOS_INVALIDOS = resposta(
    ErrosValidacaoSerializer,
    "Dados inválidos.",
    {
        "Nome ausente": {"nome": ["Este campo é obrigatório."]},
        "Código não numérico": ERRO_CODIGO_NAO_NUMERICO,
    },
)

RESPOSTA_CREDENCIAL_EXIGIDA = resposta(
    ErroAcessoSerializer,
    (
        "Chamada sem credencial ou com credencial recusada. Criar, alterar "
        "e excluir cargos exige usuário autenticado. O serviço responde "
        "403 nesses casos, e não 401."
    ),
    {
        "Sem credencial": {
            "detail": "As credenciais de autenticação não foram fornecidas."
        },
        "Token JWT inválido": EXEMPLO_TOKEN_INVALIDO,
    },
)

OPERACOES_CARGOS = {
    "list": extend_schema(
        operation_id="listar_cargos",
        summary="Listar cargos",
        description=(
            "Retorna todos os cargos, do mais recente para o mais antigo. "
            "A lista não é paginada."
        ),
        parameters=PARAMETROS_LISTAGEM,
        responses=respostas(
            {
                200: resposta(
                    CargoSerializer(many=True),
                    "Cargos cadastrados.",
                    {"Cargo": EXEMPLO_CARGO},
                ),
                400: resposta(
                    ErrosValidacaoSerializer,
                    "Filtro `codigo` com valor não numérico.",
                    {
                        "Código não numérico": {
                            "codigo": ["Informe um número."]
                        }
                    },
                ),
            }
        ),
    ),
    "create": extend_schema(
        operation_id="criar_cargo",
        summary="Criar cargo",
        description=(
            "Cria um cargo. Exige usuário autenticado. Apenas `nome` é "
            "obrigatório. O serviço não impede dois cargos com o mesmo "
            "nome ou o mesmo código."
        ),
        request=CargoSerializer,
        examples=exemplos_requisicao({"Novo cargo": EXEMPLO_DADOS_CARGO}),
        responses=respostas(
            {
                201: resposta(
                    CargoSerializer, "Cargo criado.", {"Cargo": EXEMPLO_CARGO}
                ),
                400: RESPOSTA_DADOS_INVALIDOS,
                403: RESPOSTA_CREDENCIAL_EXIGIDA,
            }
        ),
    ),
    "retrieve": extend_schema(
        operation_id="detalhar_cargo",
        summary="Detalhar cargo",
        description="Retorna um cargo pelo UUID.",
        parameters=[PARAMETRO_UUID],
        responses=respostas(
            {200: RESPOSTA_CARGO, 404: RESPOSTA_NAO_ENCONTRADO}
        ),
    ),
    "update": extend_schema(
        operation_id="atualizar_cargo",
        summary="Atualizar cargo",
        description=(
            "Substitui os dados do cargo. Exige usuário autenticado. "
            "`nome` é obrigatório; se `codigo` não for enviado, o valor "
            "atual é mantido."
        ),
        parameters=[PARAMETRO_UUID],
        request=CargoSerializer,
        examples=exemplos_requisicao({"Dados do cargo": EXEMPLO_DADOS_CARGO}),
        responses=respostas(
            {
                200: RESPOSTA_CARGO,
                400: RESPOSTA_DADOS_INVALIDOS,
                403: RESPOSTA_CREDENCIAL_EXIGIDA,
                404: RESPOSTA_NAO_ENCONTRADO,
            }
        ),
    ),
    "partial_update": extend_schema(
        operation_id="atualizar_parcial_cargo",
        summary="Atualizar cargo parcialmente",
        description=(
            "Altera apenas os campos enviados. Exige usuário autenticado."
        ),
        parameters=[PARAMETRO_UUID],
        request=CargoSerializer,
        examples=exemplos_requisicao(
            {"Corrigir o código": {"codigo": CODIGO_CARGO_EXEMPLO}}
        ),
        responses=respostas(
            {
                200: RESPOSTA_CARGO,
                400: resposta(
                    ErrosValidacaoSerializer,
                    "Dados inválidos.",
                    {"Código não numérico": ERRO_CODIGO_NAO_NUMERICO},
                ),
                403: RESPOSTA_CREDENCIAL_EXIGIDA,
                404: RESPOSTA_NAO_ENCONTRADO,
            }
        ),
    ),
    "destroy": extend_schema(
        operation_id="excluir_cargo",
        summary="Excluir cargo",
        description=(
            "Exclui o cargo definitivamente e desfaz os vínculos dele com "
            "concursos. Exige usuário autenticado.\n\n"
            "Um cargo com autorizações publicadas não pode ser excluído: "
            "hoje a tentativa termina em erro 500, sem corpo JSON."
        ),
        parameters=[PARAMETRO_UUID],
        responses=respostas(
            {
                204: resposta(None, "Cargo excluído."),
                403: RESPOSTA_CREDENCIAL_EXIGIDA,
                404: RESPOSTA_NAO_ENCONTRADO,
                500: resposta(
                    None,
                    (
                        "Erro inesperado no servidor. Acontece também "
                        "quando o cargo tem autorizações publicadas "
                        "vinculadas. O corpo não segue um modelo JSON."
                    ),
                ),
            }
        ),
    ),
    "autorizacoes_publicadas": extend_schema(
        operation_id="listar_cargos_com_autorizacoes",
        summary="Listar cargos com autorizações e escolhas",
        description=(
            "Retorna todos os cargos, em ordem alfabética, com a soma das "
            "autorizações publicadas, a data da autorização mais recente e "
            "o total de escolhas registradas no MS-Escolhas para o código "
            "do cargo. A lista não é paginada e os filtros da listagem de "
            "cargos não se aplicam.\n\n"
            "A resposta depende do MS-Escolhas: se ele não responder, a "
            "chamada termina em erro 500."
        ),
        filters=False,
        responses=respostas(
            {
                200: resposta(
                    CargoAutorizacoesSerializer(many=True),
                    "Cargos com os totais de autorizações e de escolhas.",
                    {"Cargo com autorizações": EXEMPLO_CARGO_AUTORIZACOES},
                ),
                500: resposta(
                    None,
                    (
                        "Erro inesperado no servidor. Acontece também "
                        "quando o MS-Escolhas não responde ou responde com "
                        "erro. O corpo não segue um modelo JSON."
                    ),
                ),
            }
        ),
    ),
}
