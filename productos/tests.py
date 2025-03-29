from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.test import TransactionTestCase
from .models import Producto, Categoria

class ProductoAPITestCase(APITestCase):

    def setUp(self):
        # Crear una categoría para los productos de prueba
        self.categoria = Categoria.objects.create(nombre="Electrónica")
        
        # Crear un producto de prueba
        self.producto = Producto.objects.create(
            nombre="Laptop",
            descripcion="Laptop de gama alta",
            precio=1500.00,
            categoria=self.categoria
        )
        
        # URLs para las pruebas
        self.lista_url = reverse('producto-list')
        self.detalle_url = reverse('producto-detail', args=[self.producto.id])

    def tearDown(self):
        # Limpiar todos los datos de prueba
        Producto.objects.all().delete()
        Categoria.objects.all().delete()

    def test_lista_productos(self):
        """Verifica que la API devuelve la lista de productos"""
        response = self.client.get(self.lista_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nombre'], "Laptop")

    def test_crear_producto(self):
        """Prueba la creación de un producto nuevo"""
        data = {
            "nombre": "Teléfono",
            "descripcion": "Teléfono de última generación",
            "precio": "800.00",
            "categoria": self.categoria.id
        }
        response = self.client.post(self.lista_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Producto.objects.count(), 2)
        self.assertEqual(Producto.objects.last().nombre, "Teléfono")

    def test_detalle_producto(self):
        """Prueba la recuperación de un producto específico"""
        response = self.client.get(self.detalle_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre'], "Laptop")
        self.assertEqual(float(response.data['precio']), 1500.00)

    def test_actualizar_producto(self):
        """Prueba la actualización de un producto"""
        data = {
            "nombre": "Laptop Pro",
            "descripcion": "Laptop de gama alta mejorada",
            "precio": "1700.00",
            "categoria": self.categoria.id
        }
        response = self.client.put(self.detalle_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.nombre, "Laptop Pro")

    def test_eliminar_producto(self):
        """Prueba la eliminación de un producto"""
        response = self.client.delete(self.detalle_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Producto.objects.count(), 0)