"""Módulo views/__init__."""

from .autorizacoes import AutorizacaoPublicadaViewSet
from .cargos import CargoViewSet
from .concursos import ConcursoViewSet

__all__ = ["CargoViewSet", "ConcursoViewSet", "AutorizacaoPublicadaViewSet"]
