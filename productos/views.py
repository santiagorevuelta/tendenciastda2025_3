import json
import logging
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponse, JsonResponse
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import logout
from .models import Producto, Categoria, Inventario
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.conf import settings
from .serializers import ProductoSerializer, CategoriaSerializer, InventarioSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from io import BytesIO  # Añade esta línea al inicio del archivo
from django.utils import timezone  # También necesaria para la fecha
from django.contrib import messages


# Configuración de logging
logger = logging.getLogger(__name__)

def initial_view(request):
    logger.info(f"Acceso a vista inicial - Usuario: {'autenticado' if request.user.is_authenticated else 'no autenticado'}")
    if request.user.is_authenticated:
        logger.info(f"Redirección por rol - Usuario: {request.user.username}, Rol: {request.user.profile.role}")
        if request.user.profile.role == 'admin':
            logger.debug("Redirigiendo a dashboard de administrador")
            return redirect('admin_dashboard')
        else:
            logger.debug("Redirigiendo a dashboard de empleado")
            return redirect('empleado_dashboard')
    
    logger.debug("Redirigiendo a login")
    return redirect('login')

def logout_view(request):
    if request.method == 'POST':
        username = request.user.username if request.user.is_authenticated else 'usuario desconocido'
        logger.info(f"Intento de logout - Usuario: {username}")
        logout(request)
        logger.info(f"Logout exitoso - Usuario: {username}")
        return redirect('login')
    logger.warning("Intento de logout con método GET")
    return redirect('login')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        logger.info(f"Intento de login - Usuario: {username}")
        
        user = authenticate(request, username=username, password=request.POST['password'])
        if user is not None:
            login(request, user)
            logger.info(f"Login exitoso - Usuario: {username}, Rol: {user.profile.role}")
            
            if user.profile.role == 'admin':
                logger.debug("Redirigiendo a dashboard de administrador")
                return redirect('admin_dashboard')
            else:
                logger.debug("Redirigiendo a dashboard de empleado")
                return redirect('empleado_dashboard')
        else:
            logger.warning(f"Credenciales inválidas - Usuario: {username}")
            return render(request, 'login.html', {'error': 'Credenciales inválidas'})
    
    logger.debug("Acceso a página de login")
    return render(request, 'login.html')

@login_required(login_url='/login/')
def admin_dashboard(request):
    if request.user.profile.role != 'admin':
        logger.warning(f"Intento de acceso no autorizado a admin_dashboard - Usuario: {request.user.username}")
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

    logger.info(f"Acceso a admin_dashboard - Usuario: {request.user.username}")
    try:
        productos = Producto.objects.select_related('categoria').all()
        categorias = Categoria.objects.all()
        productos_bajo_stock = Producto.objects.filter(stock__lte=5)
        inventarios = Inventario.objects.select_related('producto').order_by('-fecha_actualizacion')
        
        logger.debug(f"Datos cargados - Productos: {productos.count()}, Categorías: {categorias.count()}, Productos bajo stock: {productos_bajo_stock.count()}")
        
        return render(request, 'admin_dashboard.html', {
            'productos': productos,
            'inventarios': inventarios,
            'categorias': categorias,
            'productos_bajo_stock': productos_bajo_stock
        })
    except Exception as e:
        logger.error(f"Error en admin_dashboard - Usuario: {request.user.username}, Error: {str(e)}")
        raise

@login_required(login_url='/login/')
def empleado_dashboard(request):
    if request.user.profile.role == 'secretary':
        logger.warning(f"Intento de acceso no autorizado a empleado_dashboard - Usuario: {request.user.username}, Rol: secretary")
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

    logger.info(f"Acceso a empleado_dashboard - Usuario: {request.user.username}")
    try:
        productos = Producto.objects.select_related('categoria').all()
        productos_bajo_stock = Producto.objects.filter(stock__lte=5)
        categorias = Categoria.objects.all()
        
        logger.debug(f"Datos cargados - Productos: {productos.count()}, Productos bajo stock: {productos_bajo_stock.count()}")
        
        return render(request, 'empleado_dashboard.html', {
            'productos': productos,
            'categorias': categorias,
            'productos_bajo_stock': productos_bajo_stock
        })
    except Exception as e:
        logger.error(f"Error en empleado_dashboard - Usuario: {request.user.username}, Error: {str(e)}")
        raise

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

    def get_permissions(self):
        if getattr(settings, 'TESTING', False):
            logger.debug("Modo TESTING - Permisos AllowAny")
            return [AllowAny()]
        return [IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        logger.info(f"Listando categorías - Usuario: {request.user.username}")
        try:
            response = super().list(request, *args, **kwargs)
            logger.debug(f"Categorías listadas exitosamente - Total: {len(response.data)}")
            return response
        except Exception as e:
            logger.error(f"Error al listar categorías - Usuario: {request.user.username}, Error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        logger.info(f"Creando categoría - Usuario: {request.user.username}, Datos: {request.data}")
        try:
            response = super().create(request, *args, **kwargs)
            logger.info(f"Categoría creada exitosamente - ID: {response.data.get('id')}")
            return response
        except Exception as e:
            logger.error(f"Error al crear categoría - Usuario: {request.user.username}, Error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        logger.info(f"Obteniendo categoría - Usuario: {request.user.username}, ID: {kwargs.get('pk')}")
        try:
            response = super().retrieve(request, *args, **kwargs)
            logger.debug(f"Categoría obtenida exitosamente - ID: {kwargs.get('pk')}")
            return response
        except Exception as e:
            logger.error(f"Error al obtener categoría - Usuario: {request.user.username}, ID: {kwargs.get('pk')}, Error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        logger.info(f"Actualizando categoría - Usuario: {request.user.username}, ID: {kwargs.get('pk')}, Datos: {request.data}")
        try:
            response = super().update(request, *args, **kwargs)
            logger.info(f"Categoría actualizada exitosamente - ID: {kwargs.get('pk')}")
            return response
        except Exception as e:
            logger.error(f"Error al actualizar categoría - Usuario: {request.user.username}, ID: {kwargs.get('pk')}, Error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        logger.info(f"Actualización parcial de categoría - Usuario: {request.user.username}, ID: {kwargs.get('pk')}, Datos: {request.data}")
        try:
            response = super().partial_update(request, *args, **kwargs)
            logger.info(f"Categoría actualizada parcialmente exitosamente - ID: {kwargs.get('pk')}")
            return response
        except Exception as e:
            logger.error(f"Error en actualización parcial de categoría - Usuario: {request.user.username}, ID: {kwargs.get('pk')}, Error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        logger.warning(f"Eliminando categoría - Usuario: {request.user.username}, ID: {kwargs.get('pk')}")
        try:
            instance = self.get_object()
            response = super().destroy(request, *args, **kwargs)
            logger.warning(f"Categoría eliminada exitosamente - ID: {instance.id}, Nombre: {instance.nombre}")
            return response
        except Exception as e:
            logger.error(f"Error al eliminar categoría - Usuario: {request.user.username}, ID: {kwargs.get('pk')}, Error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

    def get_permissions(self):
        if getattr(settings, 'TESTING', False):
            logger.debug("Modo TESTING - Permisos AllowAny")
            return [AllowAny()]
        return [IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        logger.info(f"Listando productos - Usuario: {request.user.username}, Filtros: {request.query_params}")
        try:
            response = super().list(request, *args, **kwargs)
            logger.debug(f"Productos listados exitosamente - Total: {len(response.data)}")
            return response
        except Exception as e:
            logger.error(f"Error al listar productos - Usuario: {request.user.username}, Error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        logger.info(f"Creando producto - Usuario: {request.user.username}, Datos: {request.data}")
        try:
            response = super().create(request, *args, **kwargs)
            logger.info(f"Producto creado exitosamente - ID: {response.data.get('id')}")
            return response
        except Exception as e:
            logger.error(f"Error al crear producto - Usuario: {request.user.username}, Error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        logger.info(f"Obteniendo producto - Usuario: {request.user.username}, ID: {kwargs.get('pk')}")
        try:
            response = super().retrieve(request, *args, **kwargs)
            logger.debug(f"Producto obtenido exitosamente - ID: {kwargs.get('pk')}")
            return response
        except Exception as e:
            logger.error(f"Error al obtener producto - Usuario: {request.user.username}, ID: {kwargs.get('pk')}, Error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        logger.info(f"Actualizando producto - Usuario: {request.user.username}, ID: {kwargs.get('pk')}, Datos: {request.data}")
        try:
            response = super().update(request, *args, **kwargs)
            logger.info(f"Producto actualizado exitosamente - ID: {kwargs.get('pk')}")
            return response
        except Exception as e:
            logger.error(f"Error al actualizar producto - Usuario: {request.user.username}, ID: {kwargs.get('pk')}, Error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        logger.info(f"Actualización parcial de producto - Usuario: {request.user.username}, ID: {kwargs.get('pk')}, Datos: {request.data}")
        try:
            response = super().partial_update(request, *args, **kwargs)
            logger.info(f"Producto actualizado parcialmente exitosamente - ID: {kwargs.get('pk')}")
            return response
        except Exception as e:
            logger.error(f"Error en actualización parcial de producto - Usuario: {request.user.username}, ID: {kwargs.get('pk')}, Error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        logger.warning(f"Eliminando producto - Usuario: {request.user.username}, ID: {kwargs.get('pk')}")
        try:
            instance = self.get_object()
            response = super().destroy(request, *args, **kwargs)
            logger.warning(f"Producto eliminado exitosamente - ID: {instance.id}, Nombre: {instance.nombre}")
            return response
        except Exception as e:
            logger.error(f"Error al eliminar producto - Usuario: {request.user.username}, ID: {kwargs.get('pk')}, Error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class InventarioViewSet(viewsets.ModelViewSet):
    queryset = Inventario.objects.all()
    serializer_class = InventarioSerializer

    def get_permissions(self):
        if getattr(settings, 'TESTING', False):
            logger.debug("Modo TESTING - Permisos AllowAny")
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        try:
            instance = serializer.save()
            producto = instance.producto
            logger.info(f"Registro de inventario creado - ID: {instance.id}, Tipo: {instance.tipo}, "
                      f"Producto: {producto.nombre}, Cantidad: {instance.cantidad}, "
                      f"Usuario: {self.request.user.username}")
        except Exception as e:
            logger.error(f"Error al crear registro de inventario - Usuario: {self.request.user.username}, Error: {str(e)}")
            raise

@login_required
def eliminar_producto(request, producto_id):
    logger.warning(f"Intento de eliminar producto - Usuario: {request.user.username}, Producto ID: {producto_id}")
    try:
        producto = get_object_or_404(Producto, id=producto_id)
        if request.method == 'POST':
            producto.delete()
            logger.warning(f"Producto eliminado exitosamente - ID: {producto_id}, Nombre: {producto.nombre}, "
                          f"Usuario: {request.user.username}")
            return JsonResponse({'status': 'success'}, status=200)
        logger.warning(f"Método no permitido para eliminar producto - Usuario: {request.user.username}")
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    except Exception as e:
        logger.error(f"Error al eliminar producto - Usuario: {request.user.username}, Producto ID: {producto_id}, "
                    f"Error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def exportar_inventarios_pdf(request):
    logger.info(f"Generando PDF de inventarios - Usuario: {request.user.username}")
    try:
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="reporte_inventarios.pdf"'

        p = canvas.Canvas(response, pagesize=letter)
        p.setFont("Helvetica", 10)
        p.drawString(200, 750, "Reporte de Inventarios")
        
        p.drawString(30, 730, "Tipo")
        p.drawString(120, 730, "Producto")
        p.drawString(300, 730, "Cantidad")
        p.drawString(420, 730, "Fecha Actualización")

        inventarios = Inventario.objects.select_related('producto').all()
        y = 710

        for inv in inventarios:
            p.drawString(30, y, inv.get_tipo_display())
            p.drawString(120, y, inv.producto.nombre)
            p.drawString(300, y, str(inv.cantidad))
            p.drawString(420, y, inv.fecha_actualizacion.strftime("%Y-%m-%d %H:%M:%S"))
            y -= 20

            if y < 100:
                p.showPage()
                p.setFont("Helvetica", 10)
                y = 750

        p.showPage()
        p.save()
        
        logger.info(f"PDF de inventarios generado exitosamente - Usuario: {request.user.username}, "
                  f"Registros: {inventarios.count()}")
        return response
    except Exception as e:
        logger.error(f"Error al generar PDF de inventarios - Usuario: {request.user.username}, Error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def exportar_productos_pdf(request):
    logger.info(f"Generando PDF de productos - Usuario: {request.user.username}")
    try:
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="reporte_productos.pdf"'

        p = canvas.Canvas(response, pagesize=letter)
        p.setFont("Helvetica", 10)
        p.drawString(200, 750, "Reporte de Productos")
        
        p.drawString(30, 730, "Nombre")
        p.drawString(200, 730, "Descripción")
        p.drawString(420, 730, "Precio")
        p.drawString(500, 730, "Stock")

        productos = Producto.objects.all()
        y = 710

        for producto in productos:
            p.drawString(30, y, producto.nombre)
            p.drawString(200, y, producto.descripcion)
            p.drawString(420, y, str(producto.precio))
            p.drawString(500, y, str(producto.stock))
            y -= 20

            if y < 100:
                p.showPage()
                p.setFont("Helvetica", 10)
                y = 750

        p.showPage()
        p.save()
        
        logger.info(f"PDF de productos generado exitosamente - Usuario: {request.user.username}, "
                  f"Productos: {productos.count()}")
        return response
    except Exception as e:
        logger.error(f"Error al generar PDF de productos - Usuario: {request.user.username}, Error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def exportar_productos_json(request):
    logger.info(f"Generando JSON de productos - Usuario: {request.user.username if request.user.is_authenticated else 'Anónimo'}")
    try:
        productos = Producto.objects.select_related('categoria').all()
        data = []

        for p in productos:
            data.append({
                'id': p.id,
                'nombre': p.nombre,
                'descripcion': p.descripcion,
                'precio': float(p.precio),
                'stock': p.stock,
                'categoria': p.categoria.nombre
            })

        response = HttpResponse(
            json.dumps(data, indent=4, ensure_ascii=False),
            content_type='application/json'
        )
        response['Content-Disposition'] = 'attachment; filename="productos.json"'
        
        logger.info(f"JSON de productos generado exitosamente - Productos: {len(data)}")
        return response
    except Exception as e:
        logger.error(f"Error al generar JSON de productos - Error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def exportar_inventarios_json(request):
    logger.info(f"Generando JSON de inventarios - Usuario: {request.user.username if request.user.is_authenticated else 'Anónimo'}")
    try:
        inventarios = Inventario.objects.select_related('producto').all()
        data = []

        for i in inventarios:
            data.append({
                'id': i.id,
                'tipo': i.tipo,
                'producto': i.producto.nombre,
                'cantidad': i.cantidad,
                'fecha_actualizacion': i.fecha_actualizacion.isoformat()
            })

        response = HttpResponse(
            json.dumps(data, indent=4, ensure_ascii=False),
            content_type='application/json'
        )
        response['Content-Disposition'] = 'attachment; filename="inventarios.json"'
        
        logger.info(f"JSON de inventarios generado exitosamente - Registros: {len(data)}")
        return response
    except Exception as e:
        logger.error(f"Error al generar JSON de inventarios - Error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
    
@login_required
@user_passes_test(lambda u: u.profile.role == 'admin')
def view_logs(request):
    if not request.user.profile.role == 'admin':
        logger.warning(f"Intento de acceso no autorizado a logs - Usuario: {request.user.username}")
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")
    
    log_file_path = os.path.join(settings.BASE_DIR, 'logs/django.log')
    error_log_path = os.path.join(settings.BASE_DIR, 'logs/errors.log')
    
    logs = []
    errors = []
    
    try:
        with open(log_file_path, 'r', encoding='latin-1') as f:  # Cambiado a latin-1
            logs = f.readlines()[-500:]  # Últimas 500 líneas
    except FileNotFoundError:
        logger.error("Archivo de logs no encontrado")
        logs = ["No se encontró el archivo de logs\n"]
    
    try:
        with open(error_log_path, 'r', encoding='latin-1') as f:  # Cambiado a latin-1
            errors = f.readlines()[-500:]  # Últimas 500 líneas
    except FileNotFoundError:
        logger.error("Archivo de errores no encontrado")
        errors = ["No se encontró el archivo de errores\n"]
    
    context = {
        'logs': logs,
        'errors': errors,
    }
    
    return render(request, 'logs.html', context)



@login_required
@user_passes_test(lambda u: u.profile.role == 'admin')
def export_logs_pdf(request):
    """Exportar logs a PDF"""
    if not request.user.profile.role == 'admin':
        return HttpResponseForbidden("No tienes permiso para realizar esta acción.")
    
    log_file_path = os.path.join(settings.BASE_DIR, 'logs/django.log')
    error_log_path = os.path.join(settings.BASE_DIR, 'logs/errors.log')
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="logs_exportados.pdf"'
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Configuración inicial
    p.setFont("Helvetica", 10)
    p.drawString(100, 750, "Reporte de Logs del Sistema")
    p.drawString(100, 735, f"Generado el: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
    p.drawString(100, 720, f"Por usuario: {request.user.username}")
    
    y_position = 700  # Posición inicial para los logs
    
    # Función para agregar texto con manejo de paginación
    def add_text(text, y):
        if y < 50:  # Si queda poco espacio, crea nueva página
            p.showPage()
            p.setFont("Helvetica", 10)
            return 750  # Retorna nueva posición Y
        p.drawString(50, y, text)
        return y - 15
    
    # Leer y agregar logs normales
    try:
        with open(log_file_path, 'r', encoding='latin-1') as f:
            p.setFont("Helvetica-Bold", 12)
            y_position = add_text("LOGS DE ACTIVIDAD:", y_position)
            p.setFont("Helvetica", 10)
            
            for line in f.readlines()[-500:]:
                y_position = add_text(line.strip(), y_position)
    except FileNotFoundError:
        y_position = add_text("No se encontró el archivo de logs", y_position)
    
    # Leer y agregar errores
    try:
        with open(error_log_path, 'r', encoding='latin-1') as f:
            p.setFont("Helvetica-Bold", 12)
            y_position = add_text("\nLOGS DE ERROR:", y_position)
            p.setFont("Helvetica", 10)
            
            for line in f.readlines()[-500:]:
                y_position = add_text(line.strip(), y_position)
    except FileNotFoundError:
        y_position = add_text("No se encontró el archivo de errores", y_position)
    
    p.showPage()
    p.save()
    
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response

@login_required
@user_passes_test(lambda u: u.profile.role == 'admin')
def clear_logs(request):
    """Borrar todos los logs"""
    if not request.user.profile.role == 'admin':
        return HttpResponseForbidden("No tienes permiso para realizar esta acción.")
    
    log_file_path = os.path.join(settings.BASE_DIR, 'logs/django.log')
    error_log_path = os.path.join(settings.BASE_DIR, 'logs/errors.log')
    
    try:
        # Vaciar archivo de logs
        open(log_file_path, 'w').close()
        open(error_log_path, 'w').close()
        messages.success(request, "Los logs han sido borrados exitosamente.")
    except Exception as e:
        messages.error(request, f"Error al borrar logs: {str(e)}")
    
    return redirect('view_logs')

