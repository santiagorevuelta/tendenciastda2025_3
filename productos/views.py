from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponse
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import logout
from .models import Producto, Categoria, Inventario
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.conf import settings
from .serializers import ProductoSerializer, CategoriaSerializer, InventarioSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from rest_framework.exceptions import ValidationError

def initial_view(request):
    if request.user.is_authenticated:
        productos_bajo_stock = Producto.objects.filter(stock__lte=5)
        return render(request, 'dashboard.html', {'productos_bajo_stock': productos_bajo_stock})

    return redirect('login')

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            return render(request, 'login.html', {'error': 'Credenciales inválidas'})
    return render(request, 'login.html')

@login_required
def admin_dashboard(request):
    if request.user.profile.role != 'admin':
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

    productos = Producto.objects.all()
    inventarios = Inventario.objects.select_related('producto').order_by('-fecha_actualizacion')
    return render(request, 'admin_dashboard.html', {'productos': productos,'inventarios':inventarios})


@login_required
def empleado_dashboard(request):
    if request.user.profile.role == 'secretary':
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

    productos = Producto.objects.all()
    return render(request, 'empleado_dashboard.html', {'productos': productos})


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

    def get_permissions(self):
        if getattr(settings, 'TESTING', False):
            return[AllowAny()]
        return [IsAuthenticated()]
    
    @swagger_auto_schema(
        operation_description="Listar todas las categorías disponibles.",
        responses={
            200: openapi.Response(
                description="Lista de categorías obtenida correctamente.",
                schema=CategoriaSerializer(many=True)
            )
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Crear una nueva categoría.",
        responses={
            201: openapi.Response(
                description="Categoría creada correctamente.",
                schema=CategoriaSerializer
            ),
            400: "Solicitud incorrecta. Verifique los datos enviados.",
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Obtener una categoría específica por su ID.",
        responses={
            200: openapi.Response(
                description="Categoría obtenida correctamente.",
                schema=CategoriaSerializer
            ),
            404: "No encontrado. La categoría con el ID especificado no existe.",
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Actualizar una categoría específica por su ID.",
        responses={
            200: openapi.Response(
                description="Categoría actualizada correctamente.",
                schema=CategoriaSerializer
            ),
            400: "Solicitud incorrecta. Verifique los datos enviados.",
            404: "No encontrado. La categoría con el ID especificado no existe.",
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Actualizar parcialmente una categoría específica por su ID.",
        responses={
            200: openapi.Response(
                description="Categoría actualizada correctamente.",
                schema=CategoriaSerializer
            ),
            400: "Solicitud incorrecta. Verifique los datos enviados.",
            404: "No encontrado. La categoría con el ID especificado no existe.",
        }   
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Eliminar una categoría específica por su ID.",
        responses={
            204: "Categoría eliminada correctamente.",
            404: "No encontrado. La categoría con el ID especificado no existe.",
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

    def get_permissions(self):
        if getattr(settings, 'TESTING', False):
            return[AllowAny()]
        return [IsAuthenticated()]
        # return [AllowAny()]

    @swagger_auto_schema(
        operation_description="Listar todos los productos disponibles (requiere autenticación JWT).",
        responses={
            200: openapi.Response(
                description="Lista de productos obtenida correctamente.",
                schema=ProductoSerializer(many=True)
            ),
            401: "No autorizado. El token JWT no está presente o es inválido.",
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Crear un nuevo producto (requiere autenticación JWT).",
        
        responses={
            201: openapi.Response(
                description="Producto creado correctamente.",
                schema=ProductoSerializer
            ),
            400: "Solicitud incorrecta. Verifique los datos enviados.",
            401: "No autorizado. El token JWT no está presente o es inválido.",
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Obtener un producto específico por su ID (requiere autenticación JWT).",
        responses={
            200: openapi.Response(
                description="Producto obtenido correctamente.",
                schema=ProductoSerializer
            ),
            404: "No encontrado. El producto con el ID especificado no existe.",
            401: "No autorizado. El token JWT no está presente o es inválido.",
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Actualizar un producto específico por su ID (requiere autenticación JWT).",
        responses={
            200: openapi.Response(
                description="Producto actualizado correctamente.",
                schema=ProductoSerializer
            ),
            400: "Solicitud incorrecta. Verifique los datos enviados.",
            404: "No encontrado. El producto con el ID especificado no existe.",
            401: "No autorizado. El token JWT no está presente o es inválido.",
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Actualizar parcialmente un producto específico por su ID (requiere autenticación JWT).",
        responses={
            200: openapi.Response(
                description="Producto actualizado correctamente.",
                schema=ProductoSerializer
            ),
            400: "Solicitud incorrecta. Verifique los datos enviados.",
            404: "No encontrado. El producto con el ID especificado no existe.",
            401: "No autorizado. El token JWT no está presente o es inválido.",
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Eliminar un producto específico por su ID (requiere autenticación JWT).",
        responses={
            204: "Producto eliminado correctamente.",
            404: "No encontrado. El producto con el ID especificado no existe.",
            401: "No autorizado. El token JWT no está presente o es inválido.",
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)



class InventarioViewSet(viewsets.ModelViewSet):
    queryset = Inventario.objects.all()
    serializer_class = InventarioSerializer


@login_required
def exportar_inventarios_pdf(request):
    # Crear la respuesta como un archivo PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="reporte_inventarios.pdf"'

    # Crear el objeto canvas de reportlab
    p = canvas.Canvas(response, pagesize=letter)

    # Configuración de fuente
    p.setFont("Helvetica", 10)

    # Título
    p.drawString(200, 750, "Reporte de Inventarios")

    # Definir columnas para el reporte
    p.drawString(30, 730, "Tipo")
    p.drawString(120, 730, "Producto")
    p.drawString(300, 730, "Cantidad")
    p.drawString(420, 730, "Fecha Actualización")

    # Obtener los inventarios
    inventarios = Inventario.objects.select_related('producto').all()
    y = 710

    for inv in inventarios:
        p.drawString(30, y, inv.get_tipo_display())  # Tipo (Entrada/Salida)
        p.drawString(120, y, inv.producto.nombre)  # Producto
        p.drawString(300, y, str(inv.cantidad))  # Cantidad
        p.drawString(420, y, inv.fecha_actualizacion.strftime("%Y-%m-%d %H:%M:%S"))  # Fecha
        y -= 20  # Mover hacia abajo para la siguiente fila

        if y < 100:  # Si llegamos al final de la página, crear una nueva
            p.showPage()  # Crea una nueva página
            p.setFont("Helvetica", 10)
            y = 750  # Reiniciar la posición vertical

    p.showPage()
    p.save()
    return response

@login_required
def exportar_productos_pdf(request):
    # Crear la respuesta como un archivo PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="reporte_productos.pdf"'

    # Crear el objeto canvas de reportlab
    p = canvas.Canvas(response, pagesize=letter)

    # Configuración de fuente
    p.setFont("Helvetica", 10)

    # Título
    p.drawString(200, 750, "Reporte de Productos")

    # Definir columnas para el reporte
    p.drawString(30, 730, "Nombre")
    p.drawString(200, 730, "Descripción")
    p.drawString(420, 730, "Precio")
    p.drawString(500, 730, "Stock")

    # Obtener los productos
    productos = Producto.objects.all()
    y = 710

    for producto in productos:
        p.drawString(30, y, producto.nombre)  # Nombre del producto
        p.drawString(200, y, producto.descripcion)  # Descripción
        p.drawString(420, y, str(producto.precio))  # Precio
        p.drawString(500, y, str(producto.stock))  # Stock
        y -= 20  # Mover hacia abajo para la siguiente fila

        if y < 100:  # Si llegamos al final de la página, crear una nueva
            p.showPage()  # Crea una nueva página
            p.setFont("Helvetica", 10)
            y = 750  # Reiniciar la posición vertical

    p.showPage()
    p.save()
    return response