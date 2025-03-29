from django.urls import path, include
from rest_framework import routers
from .views import ProductoViewSet, CategoriaViewSet

router = routers.DefaultRouter()
router.register('Productos', ProductoViewSet)
router.register('Categorias', CategoriaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]