
#1 crear entorno
python3 -m venv venv


#2 iniciar entorno
source venv/bin/activate

# 3
pip install django
pip install djangorestframework
pip install psycopg2



#*****Crear nueva app*****
python manage.py startapp <nombre>

#Registrar la app en settings.py:

#INSTALLED_APPS = [
#    ...
#    '<nombre>.apps.ProductsConfig'
#]

#*****Crear y ejecutar migraciones:*****

python manage.py makemigrations

python manage.py migrate



#*****Configurar URLs principales Management/urls.py*****

#from django.contrib import admin
#from django.urls import path, include

#urlpatterns = [
#    path('admin/', admin.site.urls),
#    path('api/', include('products.urls')),
#]


#Para ejecutar el servidor:
python manage.py runserver


#Crear superusuario para el admin:

python manage.py createsuperuser


#*****Ejecutar tests*****

python manage.py test products
