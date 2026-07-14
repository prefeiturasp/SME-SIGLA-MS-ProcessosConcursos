"""Serviços de listagem e orquestração de concursos."""

from __future__ import annotations

from typing import Any

from django.db.models import QuerySet
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework.viewsets import GenericViewSet


class ConcursosService:
    """Regras de listagem de concursos (select vs paginado)."""

    @staticmethod
    def obter_serializer_listagem(
        view: GenericViewSet,
        request: Request,
    ) -> type[BaseSerializer]:
        """Escolhe o serializer de listagem conforme ``formato``."""
        if request.query_params.get("formato") == "select":
            from concursos.serializers import ConcursoSelectSerializer

            return ConcursoSelectSerializer
        from concursos.serializers import ConcursoListSerializer

        return ConcursoListSerializer

    @staticmethod
    def listar(
        view: GenericViewSet,
        request: Request,
        queryset: QuerySet,
    ) -> Response:
        """Lista concursos em formato select (sem página) ou paginado."""
        serializer_class = ConcursosService.obter_serializer_listagem(
            view, request
        )
        serializer_ctx: dict[str, Any] = view.get_serializer_context()

        if request.query_params.get("formato") == "select":
            serializer = serializer_class(
                queryset, many=True, context=serializer_ctx
            )
            return Response(serializer.data)

        page = view.paginate_queryset(queryset)
        if page is not None:
            serializer = serializer_class(
                page, many=True, context=serializer_ctx
            )
            return view.get_paginated_response(serializer.data)

        serializer = serializer_class(
            queryset, many=True, context=serializer_ctx
        )
        return Response(serializer.data)
