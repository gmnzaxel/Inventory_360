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
- Registra y gestiona la empresa en el sistema.
- Crea y gestiona sucursales y usuarios.
- Acceso completo al inventario de toda la empresa
- Administra productos, categorías y proveedores
- Visualiza reportes globales

### 2. Empleado de Sucursal
- Administra el stock únicamente de su sucursal.
- Registra ingresos y egresos.
- Visualiza reportes limitados a su ubicación.
- Acceso restringido a funciones administrativas

---

## 🏗️ Arquitectura del Sistema
Inventory360 está construido sobre Django con una base de datos MySQL, proporcionando una base robusta para:

- Gestión de inventario
- Administración de usuarios
- Operaciones empresariales
El sistema se estructura en dos aplicaciones Django principales:

- user_control: Gestiona autenticación, perfiles de usuario y permisos
- control: Maneja entidades empresariales, productos y movimientos de inventario

---

## 📊 Modelo de Datos
El sistema utiliza los siguientes modelos principales:

- User: Usuario del sistema con roles y asociación a empresa
- Business: Entidad empresarial con sucursales
- Category: Categorías de productos
- Product: Productos con stock y precios
- Supplier: Proveedores de productos
- Movement: Registro de todos los movimientos de inventario
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

- **Backend:** Django + Django REST Framework
- **Base de Datos:** MySQL
- **Frontend:** React.js
- **Autenticaciones y Sesiones:**  Django Rest Framework Sessions + CSRF Token

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

## 🔌 API REST
Inventory360 expone su funcionalidad a través de una API RESTful construida con Django REST Framework. Los principales endpoints incluyen:

- /api/user/: Gestión de usuarios
- /api/user/login/: Autenticación de usuarios
- /api/user/logout/: Cierre de sesión
- /api/user/admin/create-user/: Creación de usuarios por administradores
- /api/control/model/bussines/: Gestión de empresas
- /api/control/model/products/: Gestión de productos
- /api/control/model/categories/: Gestión de categorías
- /api/control/model/supplier/: Gestión de proveedores
- /api/control/model/movements/: Gestión de movimientos de inventario


---


## 👨‍💻 Desarrollo

### Estructura del Proyecto

Inventory_360/  
├── Inventory360/          # Configuración principal del proyecto  
├── control/               # App para gestión de inventario  
│   ├── models.py          # Modelos de datos para inventario  
│   ├── serializer.py      # Serializadores para la API  
│   ├── views.py           # Vistas y lógica de negocio  
│   └── urls.py            # Rutas de la API  
├── user_control/          # App para gestión de usuarios  
│   ├── models.py          # Modelo de usuario personalizado  
│   ├── serializer.py      # Serializadores para usuarios  
│   ├── views.py           # Vistas de autenticación y gestión  
│   └── urls.py            # Rutas de autenticación  
└── manage.py              # Script de gestión de Django  


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


## 🤝 Contribuciones
Las contribuciones son bienvenidas. Por favor, sigue estos pasos:

- Haz fork del repositorio
- Crea una rama para tu funcionalidad (git checkout -b feature/amazing-feature)
- Haz commit de tus cambios (git commit -m 'Add some amazing feature')
- Push a la rama (git push origin feature/amazing-feature)
- Abre un Pull Request


---


## 📄 Licencia

Este proyecto está bajo la licencia **MIT**.
