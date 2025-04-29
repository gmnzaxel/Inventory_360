# 📦 Proyecto de Gestión de Stock – Inventory360

## 📄 Descripción del Proyecto

**Tipo:** Aplicación web de gestión de inventario para empresas

**Descripción:**

Inventory360 es una solución integral diseñada para empresas que buscan un control completo y centralizado de su inventario. Permite gestionar múltiples sucursales, productos, movimientos de stock y usuarios desde una misma plataforma, facilitando así la trazabilidad y eficiencia operativa.

---

## 🔍 Características Principales

- Autenticación de usuarios.
- Control de usuarios según roles y empresa.
- Gestión de sucursales.
- Gestión de productos y categorías.
- Registro de movimientos de stock (ingresos y egresos).
- Validación de stock negativo (no permite egresos si no hay stock disponible).
- Reportes filtrables por fechas y sucursales.
- Dashboard con métricas clave.

---

## 👥 Tipos de Usuario

### 1. Administrador de Empresa
- Registra la empresa en el sistema.
- Gestiona sucursales y usuarios.
- Visualiza el inventario completo de la empresa.
- Administra productos y movimientos de todas las sucursales.

### 2. Empleado de Sucursal
- Administra el stock únicamente de su sucursal.
- Registra ingresos y egresos.
- Visualiza reportes limitados a su ubicación.

---

## ✅ Requisitos Funcionales

- Registro e inicio de sesión.
- Alta y modificación de empresas.
- Alta, baja y modificación de sucursales.
- Gestión de productos por empresa.
- Ingreso y egreso de stock por sucursal.
- Visualización del stock actual por sucursal y total de empresa.
- Reportes de movimientos con filtros (fecha, sucursal, producto).
- Gestión de empleados por parte del administrador.
- Acceso restringido según tipo de usuario.

---

## 🚀 Tecnologías Utilizadas

- **Backend:** Django
- **Base de Datos:** MySQL
- **Frontend:** Django Templates + Bootstrap
- **Autenticación:** Django Authentication System
- **API:** Django REST Framework

---

## 🛠️ Requisitos Previos

- Mysql
- Python 3.10+
- pip
- Virtualenv o pipenv (opcional)
- Git

---

## ⚙️ Configuración Inicial

### 🔧 Backend

1. **Clonar el repositorio:**

git clone https://github.com/tu-usuario/inventory360.git
cd inventory360

2. **Crear entorno virtual e instalar dependencias:**

python -m venv env
source env/bin/activate  # En Windows: env\\Scripts\\activate
pip install -r requirements.txt

3. **Aplicar migraciones:**

python manage.py makemigrations
python manage.py migrate

4. **Crear superusuario:**

python manage.py createsuperuser

5.**Ejecutar el servidor:**

python manage.py runserver


---


## 📈 Panel de Administración

Una vez en funcionamiento, accedé al panel admin:

http://127.0.0.1:8000/admin


---

## 📌 Estado del Proyecto

✅ Proyecto funcional  
🔄 En desarrollo continuo  
📢 ¡Pronto con API pública y soporte para React o Vue!

---

## 📄 Licencia

Este proyecto está bajo la licencia **MIT**.
