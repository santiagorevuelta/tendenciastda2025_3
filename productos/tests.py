import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from .models import Producto, Categoria

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def crear_producto(db, crear_categoria):
    return Producto.objects.create(
        nombre="Laptop",
        descripcion="Laptop de gama alta",
        precio="1500.00",
        categoria=crear_categoria
    )

@pytest.mark.django_db
def test_crear_producto(api_client, crear_categoria):
    """Prueba la creación de un producto"""
    url = reverse('producto-list')
    data = {
        "nombre": "Tablet",
        "descripcion": "Tablet de gama media",
        "precio": "800.00",
        "categoria": crear_categoria.id
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == 201
    assert response.data['nombre'] == data['nombre']
    assert response.data['descripcion'] == data['descripcion']
    assert response.data['precio'] == str(data['precio'])
    assert response.data['categoria'] == data['categoria']

@pytest.mark.django_db
def test_listar_productos(api_client, crear_producto):
    """Prueba la obtención de la lista de productos"""
    url = reverse('producto-list')
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data[0]['nombre'] == crear_producto.nombre

@pytest.mark.django_db
def test_obtener_producto(api_client, crear_producto, crear_categoria):
    """Prueba la obtención de un producto por ID"""
    url = reverse('producto-detail', args=[crear_producto.id])
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data['nombre'] == crear_producto.nombre
    assert response.data['descripcion'] == crear_producto.descripcion
    assert response.data['precio'] == str(crear_producto.precio)
    assert response.data['categoria'] == crear_categoria.id

@pytest.mark.django_db
def test_actualizar_producto(api_client, crear_producto, crear_categoria):
    url = reverse('producto-detail', args=[crear_producto.id])
    data = {
        "nombre": "Laptop Actualizada",
        "descripcion": "Laptop de gama alta actualizada",
        "precio": "1600.00",
        "categoria": crear_categoria.id
    }
    response = api_client.put(url, data, format='json')
    assert response.status_code == 200
    assert response.data['nombre'] == data['nombre']
    assert response.data['descripcion'] == data['descripcion']
    assert response.data['precio'] == str(data['precio'])
    assert response.data['categoria'] == data['categoria']

@pytest.mark.django_db
def test_eliminar_producto(api_client, crear_producto):
    url = reverse('producto-detail', args=[crear_producto.id])
    response = api_client.delete(url)
    assert response.status_code == 204
    assert not Producto.objects.filter(id=crear_producto.id).exists()

    
###############################################################################

@pytest.fixture
def crear_categoria(db):
    return Categoria.objects.create(nombre="Electrónica")

@pytest.mark.django_db
def test_crear_categoria(api_client):
    url = reverse('categoria-list')
    data = {
        "nombre": "Electrodomésticos"
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == 201
    assert response.data['nombre'] == data['nombre']

@pytest.mark.django_db
def test_listar_categorias(api_client, crear_categoria):
    url = reverse('categoria-list')
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data[0]['nombre'] == crear_categoria.nombre

@pytest.mark.django_db
def test_obtener_categoria(api_client, crear_categoria):
    """Prueba la obtención de una categoría por ID"""
    url = reverse('categoria-detail', args=[crear_categoria.id])
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data['nombre'] == crear_categoria.nombre
    assert response.data['id'] == crear_categoria.id

@pytest.mark.django_db
def test_actualizar_categoria(api_client, crear_categoria):
    url = reverse('categoria-detail', args=[crear_categoria.id])
    data = {
        "nombre": "Electrodomésticos Actualizada"
    }
    response = api_client.put(url, data, format='json')
    assert response.status_code == 200
    assert response.data['nombre'] == data['nombre']
    assert response.data['id'] == crear_categoria.id

@pytest.mark.django_db
def test_eliminar_categoria(api_client, crear_categoria):
    """Prueba la eliminación de una categoría"""
    url = reverse('categoria-detail', args=[crear_categoria.id])
    response = api_client.delete(url)
    assert response.status_code == 204
    assert not Categoria.objects.filter(id=crear_categoria.id).exists()