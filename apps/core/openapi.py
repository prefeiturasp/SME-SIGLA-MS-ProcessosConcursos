"""Blocos compartilhados da documentação OpenAPI do microsserviço."""

from __future__ import annotations

from typing import Any

from django.db.models import Model
from drf_spectacular.extensions import OpenApiSerializerExtension
from drf_spectacular.openapi import AutoSchema
from drf_spectacular.utils import (
    Direction,
    OpenApiExample,
    OpenApiResponse,
)

from core.serializers import (
    ErroAcessoSerializer,
    ErroDetalheSerializer,
    ErrosValidacaoSerializer,
)

MENSAGENS_DE_ERRO = {"type": "array", "items": {"type": "string"}}

EXEMPLO_TOKEN_INVALIDO = {
    "detail": "Given token not valid for any token type",
    "code": "token_not_valid",
    "messages": [
        {
            "token_class": "AccessToken",
            "token_type": "access",
            "message": "Token is invalid",
        }
    ],
}

EXEMPLO_USUARIO_NAO_ENCONTRADO = {
    "detail": "User not found",
    "code": "user_not_found",
}


class ErrosValidacaoExtension(OpenApiSerializerExtension):
    """Descreve ``ErrosValidacaoSerializer`` como mapa campo → mensagens."""

    target_class = ErrosValidacaoSerializer

    def map_serializer(
        self, auto_schema: AutoSchema, direction: Direction
    ) -> dict[str, Any]:
        """Retorna o schema do mapa de erros de validação."""
        return {
            "type": "object",
            "description": (
                "Erros de validação. Cada chave é o nome de um campo ou "
                "filtro inválido (ou `non_field_errors`) e o valor é a "
                "lista de mensagens. Em campos que são listas, como "
                "`cargos_ids` e `anos`, o valor é um objeto em que cada "
                "chave é a posição do item inválido."
            ),
            "additionalProperties": {
                "oneOf": [
                    MENSAGENS_DE_ERRO,
                    {
                        "type": "object",
                        "additionalProperties": MENSAGENS_DE_ERRO,
                    },
                ]
            },
        }


def resposta(
    modelo: Any, descricao: str, exemplos: dict[str, Any] | None = None
) -> OpenApiResponse:
    """Monta uma resposta documentada com exemplos nomeados.

    Args:
        modelo: Serializer que descreve o corpo, ou ``None`` se não há corpo.
        descricao: Texto exibido para o código de resposta.
        exemplos: Valores de exemplo, indexados pelo nome do exemplo.

    Returns:
        Resposta pronta para o ``responses`` de ``extend_schema``.
    """
    return OpenApiResponse(
        response=modelo,
        description=descricao,
        examples=[
            OpenApiExample(nome, value=valor)
            for nome, valor in (exemplos or {}).items()
        ],
    )


def exemplos_requisicao(exemplos: dict[str, Any]) -> list[OpenApiExample]:
    """Monta exemplos nomeados para o corpo da requisição.

    Args:
        exemplos: Valores de exemplo, indexados pelo nome do exemplo.

    Returns:
        Exemplos prontos para o ``examples`` de ``extend_schema``.
    """
    return [
        OpenApiExample(nome, value=valor, request_only=True)
        for nome, valor in exemplos.items()
    ]


def resposta_nao_encontrado(modelo: type[Model]) -> OpenApiResponse:
    """Monta o 404 de uma rota de detalhe.

    Args:
        modelo: Model consultado pela rota; o nome dele aparece na mensagem.

    Returns:
        Resposta 404 com os textos devolvidos para UUID inexistente e para
        UUID malformado.
    """
    nome = modelo._meta.object_name
    return resposta(
        ErroDetalheSerializer,
        "Registro não encontrado.",
        {
            "UUID inexistente": {
                "detail": f"No {nome} matches the given query."
            },
            "UUID malformado": {"detail": "Não encontrado."},
        },
    )


RESPOSTA_ACESSO_NEGADO = resposta(
    ErroAcessoSerializer,
    (
        "Credencial recusada: token JWT inválido ou expirado, token de "
        "usuário que não existe neste serviço, usuário e senha Basic "
        "incorretos ou falha de CSRF em sessão. O serviço responde 403 "
        "nesses casos, e não 401."
    ),
    {
        "Token JWT inválido": EXEMPLO_TOKEN_INVALIDO,
        "Usuário do token não encontrado": EXEMPLO_USUARIO_NAO_ENCONTRADO,
    },
)

RESPOSTA_PAGINA_INEXISTENTE = resposta(
    ErroDetalheSerializer,
    "Página além da última ou valor de `page` inválido.",
    {"Página inexistente": {"detail": "Página inválida."}},
)

RESPOSTA_ERRO_INTERNO = resposta(
    None,
    "Erro inesperado no servidor. O corpo não segue um modelo JSON.",
)

RESPOSTAS_COMUNS = {
    403: RESPOSTA_ACESSO_NEGADO,
    500: RESPOSTA_ERRO_INTERNO,
}


def respostas(especificas: dict[int, Any]) -> dict[int, Any]:
    """Junta as respostas da operação às comuns a todo o microsserviço.

    Args:
        especificas: Respostas próprias da operação, por código HTTP.

    Returns:
        Respostas ordenadas por código, incluindo 403 e 500.
    """
    return dict(sorted({**RESPOSTAS_COMUNS, **especificas}.items()))
