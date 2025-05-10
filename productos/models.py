from django.db import models

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.TextField(max_length=100)
    descripcion = models.TextField(null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='productos')
    stock = models.IntegerField(default=0)

    def __str__(self):
        return self.nombre

class Inventario(models.Model):
    tipo = models.CharField(max_length=10, choices=[('entrada', 'Entrada'), ('salida', 'Salida')])
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=0)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad} - {self.tipo} - {self.fecha_actualizacion.strftime('%d-%m-%Y %H:%M')}"

    def save(self, *args, **kwargs):
        if self.pk is None:
            if self.tipo == 'entrada':
                self.producto.stock += self.cantidad
            elif self.tipo == 'salida':
                if self.producto.stock >= self.cantidad:
                    self.producto.stock -= self.cantidad
                else:
                    raise ValueError("Stock insuficiente para realizar la salida.")
            self.producto.save()
        super().save(*args, **kwargs)