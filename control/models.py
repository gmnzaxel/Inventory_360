from django.db import models

class Bussines(models.Model):
    nombre = models.CharField(max_length=255)
    direccion = models.TextField()
    telefono = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    text = models.TextField(default="")

    def __str__(self):
        return self.nombre

class User(models.Model):
    nombre = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)
    rol = models.CharField(max_length=50, choices=[('admin', 'Admin'), ('User', 'User')])

    def __str__(self):
        return self.nombre

class Category(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre

class Product(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()

    def __str__(self):
        return self.nombre

class Supplier(models.Model):
    nombre = models.CharField(max_length=255)
    direccion = models.TextField()
    telefono = models.CharField(max_length=20)

    def __str__(self):
        return self.nombre

class Movement(models.Model):
    TIPOS_MOVIMIENTO = [
        ('compra', 'Compra'),
        ('venta', 'Venta'),
        ('ajuste', 'Ajuste'),
        ('salida', 'Salida')
    ]
    tipo = models.CharField(max_length=20, choices=TIPOS_MOVIMIENTO)
    producto_nombre = models.CharField(max_length=255)
    cantidad = models.IntegerField()
    fecha = models.DateTimeField(auto_now_add=True)
    documento_nro = models.CharField(max_length=50, null=True, blank=True)
    
    def __str__(self):
        return f"{self.tipo} - {self.producto_nombre} ({self.cantidad})"