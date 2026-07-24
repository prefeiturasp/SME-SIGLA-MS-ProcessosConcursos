"""FilterSets do app concursos."""

from __future__ import annotations

from django_filters import rest_framework as filters

from concursos.models import Concurso


class ConcursoFilterSet(filters.FilterSet):
    """Filtros da listagem de concursos (busca do Figma)."""

    nome = filters.CharFilter(field_name="nome", lookup_expr="icontains")
    numero_processo = filters.CharFilter(
        field_name="numero_processo", lookup_expr="icontains"
    )
    banca_responsavel = filters.CharFilter(
        field_name="banca_responsavel", lookup_expr="icontains"
    )
    codigo_cargo = filters.NumberFilter(field_name="cargos__codigo")
    descricao_cargo = filters.CharFilter(
        field_name="cargos__nome", lookup_expr="icontains"
    )

    class Meta:
        """Configuracao do filterset."""

        model = Concurso
        fields = [
            "nome",
            "numero_processo",
            "banca_responsavel",
            "status",
            "situacao",
            "codigo_cargo",
            "descricao_cargo",
        ]
