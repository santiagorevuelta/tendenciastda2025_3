from django.urls import path, include
from rest_framework import routers
from .views import ProductoViewSet, CategoriaViewSet, InventarioViewSet
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import view_logs, export_logs_pdf, clear_logs

router = routers.DefaultRouter()
router.register('productos', ProductoViewSet)
router.register('categorias', CategoriaViewSet)
router.register('inventarios', InventarioViewSet)

urlpatterns = [
    path('', views.initial_view, name='initial'),
    path('api/', include(router.urls)),
    # vistas html
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('empleado-dashboard/', views.empleado_dashboard, name='empleado_dashboard'),
    # aciones de descarga
    path('exportar-inventarios-pdf/', views.exportar_inventarios_pdf, name='exportar_inventarios_pdf'),
    path('exportar-productos-pdf/', views.exportar_productos_pdf, name='exportar_productos_pdf'),
    path('exportar_productos_json/', views.exportar_productos_json, name='exportar_productos_json'),
    path('exportar_inventarios_json/', views.exportar_inventarios_json, name='exportar_inventarios_json'),
    #logs
    path('logs/', view_logs, name='view_logs'),
    path('logs/export-pdf/', export_logs_pdf, name='export_logs_pdf'),
    path('logs/clear/', clear_logs, name='clear_logs'),
    # urls.py
    path('productos/eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
]