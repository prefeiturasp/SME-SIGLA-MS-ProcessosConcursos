"""
URL configuration for the concursos module.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConcursoViewSet

router = DefaultRouter()
router.register(r'concursos', ConcursoViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 