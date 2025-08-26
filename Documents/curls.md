Registrar un nuevo usuario + empresa (solo si NO estás autenticado)

curl -X POST http://127.0.0.1:8000/api/user/register/register/ \
-H "Content-Type: application/json" \
-d '{
  "username": "admin1",
  "email": "admin1@test.com",
  "password": "Admin123!",
  "password2": "Admin123!",
  "name": "Admin Uno",
  "company": {
    "name": "Empresa Uno",
    "cuit": "12345678901",
    "email": "empresa1@test.com",
    "phone": "123456789",
    "address": "Calle Principal 123"
  }
}'

Login (obtener access y refresh tokens)
curl -X POST http://127.0.0.1:8000/api/user/login/ \
-H "Content-Type: application/json" \
-d '{
  "username": "joaco",
  "password": "joaco"
}'


{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOi...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOi..."
}

Obtener productos (o cualquier recurso protegido)
curl -X GET http://127.0.0.1:8000/api/control/model/product/ \
-H "Authorization: Bearer <ACCESS_TOKEN>"


Crear un producto (admin o empleado autenticado)
curl -X POST http://127.0.0.1:8000/api/control/model/product/ \
-H "Content-Type: application/json" \
-H "Authorization: Bearer <ACCESS_TOKEN>" \
-d '{
  "name": "Producto Test",
  "description": "Descripción",
  "category": "General",
  "price": "100.00"
}'


Crear un movimiento de stock
curl -X POST http://127.0.0.1:8000/api/control/model/stock_movement/ \
-H "Content-Type: application/json" \
-H "Authorization: Bearer <ACCESS_TOKEN>" \
-d '{
  "movement_type": "incoming",
  "quantity": 10,
  "description": "Ingreso inicial",
  "product": 1,
  "branch": 1
}'


Refrescar token (si se vence el access)
curl -X POST http://127.0.0.1:8000/api/user/token/refresh/ \
-H "Content-Type: application/json" \
-d '{
  "refresh": "<REFRESH_TOKEN>"
}'


Verificar token (si se vence el access)
curl -X POST http://127.0.0.1:8000/api/user/token/verify/ \
-H "Content-Type: application/json" \
-d '{
  "token": "<ACCESS_TOKEN>"
}'

Logout (invalidar refresh token)
curl -X POST http://127.0.0.1:8000/api/user/logout/ \
-H "Content-Type: application/json" \
-H "Authorization: Bearer <ACCESS_TOKEN>" \
-d '{
  "refresh": "<REFRESH_TOKEN>"
}'