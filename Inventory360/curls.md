1️⃣ Registrar un nuevo administrador + empresa (sin autenticación)

curl -X POST http://127.0.0.1:8000/user-control/register-admin/ \
-H "Content-Type: application/json" \
-d '{
  "username": "admin1",
  "email": "admin1@test.com",
  "password": "Admin123!",
  "password2": "Admin123!",
  "name": "Admin Uno",
  "business": {
    "name": "Empresa Uno",
    "address": "Calle Principal 123",
    "phone": "123456789"
  }
}'


2️⃣ Login (obtener access y refresh tokens)

curl -X POST http://127.0.0.1:8000/user-control/login/ \
-H "Content-Type: application/json" \
-d '{
  "email": "admin1@test.com",
  "password": "Admin123!"
}'


3️⃣ Crear usuario interno (requiere autenticación ADMIN)

curl -X POST http://127.0.0.1:8000/user-control/admin/create-user/ \
-H "Content-Type: application/json" \
-H "Authorization: Bearer <ACCESS_TOKEN>" \
-d '{
  "email": "empleado1@test.com",
  "name": "Empleado Uno",
  "role": "user",
  "branch_id": 1,
  "password": "Empleado123!",
  "can_purchase": true,
  "can_sale": true,
  "can_adjust": false,
  "can_transfer": false
}'


4️⃣ Crear producto (requiere token)

curl -X POST http://127.0.0.1:8000/api/control/products/ \
-H "Content-Type: application/json" \
-H "Authorization: Bearer <ACCESS_TOKEN>" \
-d '{
  "name": "Producto Test",
  "description": "Producto de prueba",
  "price": "100.00",
  "category_id": 1,
  "business_id": 1
}'


6️⃣ Refrescar token

curl -X POST http://127.0.0.1:8000/user-control/token/refresh/ \
-H "Content-Type: application/json" \
-d '{
  "refresh": "<REFRESH_TOKEN>"
}'


7️⃣ Verificar token

curl -X POST http://127.0.0.1:8000/user-control/token/verify/ \
-H "Content-Type: application/json" \
-d '{
  "token": "<ACCESS_TOKEN>"
}'


8️⃣ Logout (invalidar token)

curl -X POST http://127.0.0.1:8000/user-control/logout/ \
-H "Content-Type: application/json" \
-H "Authorization: Bearer <ACCESS_TOKEN>" \
-d '{
  "refresh": "<REFRESH_TOKEN>"
}'