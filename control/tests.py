from django.test import TestCase
from rest_framework.test import APIClient, APIRequestFactory
from rest_framework import status
from control.models import Business, Branch, Category, Product, Document, Movement, Stock
from user_control.models import User
from control.serializer import (
    BusinessSerializer, BranchSerializer, CategorySerializer, ProductSerializer,
    DocumentSerializer, MovementSerializer, StockSerializer
)
from user_control.serializer import AdminRegistrationSerializer, UserCreateByAdminSerializer, UserSerializer
from user_control.permissions import IsAdminUserCustom

class BaseTestCase(TestCase):
    """Clase base para configurar datos comunes."""
    
    def setUp(self):
        self.client = APIClient()
        self.factory = APIRequestFactory()
        # Crear usuario admin
        self.admin_user = User.objects.create(
            email='admin@ejemplo.com',
            name='Admin User',
            role='admin',
            username='adminuser',
            can_purchase=True,
            can_sale=True,
            can_adjust=True,
            can_transfer=True
        )
        self.admin_user.set_password('admin123')
        self.admin_user.save()
        # Crear usuario normal
        self.normal_user = User.objects.create(
            email='user@ejemplo.com',
            name='Normal User',
            role='user',
            username='normaluser',
            can_purchase=False,
            can_sale=False,
            can_adjust=False,
            can_transfer=False
        )
        self.normal_user.set_password('user123')
        self.normal_user.save()
        # Crear empresa
        self.business = Business.objects.create(
            name='Negocio Test',
            address='Calle 123',
            phone='1234567890'
        )
        self.admin_user.business = self.business
        self.normal_user.business = self.business
        self.admin_user.save()
        self.normal_user.save()
        # Crear sucursal
        self.branch = Branch.objects.create(
            name='Sucursal Test',
            address='Calle 456',
            phone='0987654321',
            business=self.business
        )
        self.normal_user.branch = self.branch
        self.normal_user.save()
        # Crear categoría
        self.category = Category.objects.create(
            name='Categoria Test',
            description='Descripción',
            business=self.business
        )
        # Crear producto
        self.product = Product.objects.create(
            name='Producto Test',
            description='Descripción',
            price=10.99,
            business=self.business,
            category=self.category
        )
        # Crear stock
        self.stock = Stock.objects.create(
            product=self.product,
            branch=self.branch,
            quantity=100,
            minimum_stock=10
        )
        # Crear documento
        self.document = Document.objects.create(
            document_type='invoice',
            document_number='INV-001',
            business=self.business,
            created_by=self.admin_user
        )

class BusinessSerializerTest(BaseTestCase):
    """Pruebas para BusinessSerializer."""
    
    def test_create_business(self):
        """Prueba la creación de una empresa."""
        data = {
            'name': 'Negocio Nuevo',
            'address': 'Calle 789',
            'phone': '5555555555',
            'notes': 'Notas'
        }
        serializer = BusinessSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        business = serializer.save()
        self.assertEqual(business.name, 'Negocio Nuevo')

class BranchSerializerTest(BaseTestCase):
    """Pruebas para BranchSerializer."""
    
    def test_create_branch(self):
        """Prueba la creación de una sucursal."""
        data = {
            'name': 'Sucursal Nueva',
            'address': 'Calle 101',
            'phone': '1111111111'
        }
        request = self.factory.post('/api/control/branches/', data)
        request.user = self.admin_user
        serializer = BranchSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        branch = serializer.save(business=self.business)
        self.assertEqual(branch.name, 'Sucursal Nueva')
        self.assertEqual(branch.business, self.business)

class CategorySerializerTest(BaseTestCase):
    """Pruebas para CategorySerializer."""
    
    def test_create_category(self):
        """Prueba la creación de una categoría."""
        data = {
            'name': 'Categoria Nueva',
            'description': 'Descripción Nueva'
        }
        request = self.factory.post('/api/control/categories/', data)
        request.user = self.admin_user
        serializer = CategorySerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        category = serializer.save()
        self.assertEqual(category.name, 'Categoria Nueva')
        self.assertEqual(category.business, self.business)

class ProductSerializerTest(BaseTestCase):
    """Pruebas para ProductSerializer."""
    
    def test_create_product(self):
        """Prueba la creación de un producto válido."""
        data = {
            'name': 'Producto Nuevo',
            'description': 'Descripción Nueva',
            'price': 20.99,
            'business_id': self.business.id,
            'category_id': self.category.id
        }
        request = self.factory.post('/api/control/products/', data)
        request.user = self.admin_user
        serializer = ProductSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        product = serializer.save()
        self.assertEqual(product.name, 'Producto Nuevo')
        self.assertEqual(product.business, self.business)

    def test_invalid_name(self):
        """Prueba un nombre de producto con caracteres inválidos."""
        data = {
            'name': 'Producto123',  # Contiene números
            'description': 'Descripción',
            'price': 20.99,
            'business_id': self.business.id
        }
        request = self.factory.post('/api/control/products/', data)
        request.user = self.admin_user
        serializer = ProductSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('Este campo solo puede contener letras', str(serializer.errors))

class DocumentSerializerTest(BaseTestCase):
    """Pruebas para DocumentSerializer."""
    
    def test_create_document(self):
        """Prueba la creación de un documento con created_by automático."""
        data = {
            'document_type': 'invoice',
            'document_number': 'INV-002'
        }
        request = self.factory.post('/api/control/documents/', data)
        request.user = self.admin_user
        serializer = DocumentSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        document = serializer.save()
        self.assertEqual(document.created_by, self.admin_user)
        self.assertEqual(document.business, self.business)

class MovementSerializerTest(BaseTestCase):
    """Pruebas para MovementSerializer."""
    
    def test_valid_sale_movement(self):
        """Prueba la creación de un movimiento de venta válido."""
        data = {
            'movement_type': 'sale',
            'quantity': 5,
            'unit_price': 10.99,
            'product_id': self.product.id,
            'branch_id': self.branch.id,
            'document_id': self.document.id
        }
        request = self.factory.post('/api/control/movements/', data)
        request.user = self.admin_user
        serializer = MovementSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        movement = serializer.save()
        self.assertEqual(movement.movement_type, 'sale')
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.quantity, 95)

    def test_invalid_document_type(self):
        """Prueba un movimiento con document_type incorrecto."""
        invalid_document = Document.objects.create(
            document_type='purchase_order',
            document_number='PO-001',
            business=self.business,
            created_by=self.admin_user
        )
        data = {
            'movement_type': 'sale',
            'quantity': 5,
            'unit_price': 10.99,
            'product_id': self.product.id,
            'branch_id': self.branch.id,
            'document_id': invalid_document.id
        }
        request = self.factory.post('/api/control/movements/', data)
        request.user = self.admin_user
        serializer = MovementSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('El documento debe ser de tipo', str(serializer.errors))

    def test_missing_unit_price(self):
        """Prueba un movimiento de compra sin unit_price."""
        data = {
            'movement_type': 'purchase',
            'quantity': 10,
            'product_id': self.product.id,
            'branch_id': self.branch.id
        }
        request = self.factory.post('/api/control/movements/', data)
        request.user = self.admin_user
        serializer = MovementSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('El precio unitario es requerido', str(serializer.errors))

    def test_no_permission(self):
        """Prueba un movimiento por un usuario sin permisos."""
        data = {
            'movement_type': 'sale',
            'quantity': 5,
            'unit_price': 10.99,
            'product_id': self.product.id,
            'branch_id': self.branch.id,
            'document_id': self.document.id
        }
        request = self.factory.post('/api/control/movements/', data)
        request.user = self.normal_user  # Sin can_sale
        serializer = MovementSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('No tienes permiso para registrar ventas', str(serializer.errors))

class StockSerializerTest(BaseTestCase):
    """Pruebas para StockSerializer."""
    
    def test_is_low_stock(self):
        """Prueba el campo is_low_stock."""
        self.stock.quantity = 5  # Menor que minimum_stock (10)
        self.stock.save()
        serializer = StockSerializer(self.stock)
        self.assertTrue(serializer.data['is_low_stock'])

    def test_invalid_minimum_stock(self):
        """Prueba un minimum_stock negativo."""
        data = {
            'product_id': self.product.id,
            'branch_id': self.branch.id,
            'minimum_stock': -1
        }
        request = self.factory.post('/api/control/stocks/', data)
        request.user = self.admin_user
        serializer = StockSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('El stock mínimo no puede ser negativo', str(serializer.errors))

class AdminRegistrationSerializerTest(BaseTestCase):
    """Pruebas para AdminRegistrationSerializer."""
    
    def test_register_admin(self):
        """Prueba el registro de un administrador con empresa."""
        data = {
            'name': 'Nuevo Admin',
            'email': 'nuevo@ejemplo.com',
            'username': 'nuevoadmin',
            'password': 'admin123',
            'password2': 'admin123',
            'business': {
                'name': 'Negocio Nuevo',
                'address': 'Calle 789',
                'phone': '5555555555'
            }
        }
        serializer = AdminRegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertEqual(user.role, 'admin')
        self.assertIsNotNone(user.business)

    def test_password_mismatch(self):
        """Prueba contraseñas que no coinciden."""
        data = {
            'name': 'Nuevo Admin',
            'email': 'nuevo@ejemplo.com',
            'username': 'nuevoadmin',
            'password': 'admin123',
            'password2': 'admin456',
            'business': {
                'name': 'Negocio Nuevo',
                'address': 'Calle 789',
                'phone': '5555555555'
            }
        }
        serializer = AdminRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('Las contraseñas no coinciden', str(serializer.errors))

class UserCreateByAdminSerializerTest(BaseTestCase):
    """Pruebas para UserCreateByAdminSerializer."""
    
    def test_create_user_by_admin(self):
        """Prueba la creación de un usuario por un admin."""
        data = {
            'email': 'nuevo_usuario@ejemplo.com',
            'name': 'Nuevo Usuario',
            'role': 'user',
            'password': 'user123',
            'branch_id': self.branch.id,
            'can_sale': True
        }
        request = self.factory.post('/user-control/admin/create-user/', data)
        request.user = self.admin_user
        serializer = UserCreateByAdminSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertEqual(user.role, 'user')
        self.assertEqual(user.branch, self.branch)
        self.assertTrue(user.can_sale)

    def test_user_without_branch(self):
        """Prueba crear un usuario sin sucursal (debería fallar)."""
        data = {
            'email': 'nuevo_usuario@ejemplo.com',
            'name': 'Nuevo Usuario',
            'role': 'user',
            'password': 'user123',
            'can_sale': True
        }
        request = self.factory.post('/user-control/admin/create-user/', data)
        request.user = self.admin_user
        serializer = UserCreateByAdminSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('Los usuarios deben estar asignados a una sucursal', str(serializer.errors))

class UserSerializerTest(BaseTestCase):
    """Pruebas para UserSerializer."""
    
    def test_user_data(self):
        """Prueba la serialización de datos de usuario."""
        serializer = UserSerializer(self.admin_user)
        self.assertEqual(serializer.data['email'], 'admin@ejemplo.com')
        self.assertEqual(serializer.data['role'], 'admin')

class BusinessViewTest(BaseTestCase):
    """Pruebas para BusinessView."""
    
    def test_get_business(self):
        """Prueba consultar la empresa del usuario."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/control/businesses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Negocio Test')

class BranchViewTest(BaseTestCase):
    """Pruebas para BranchView."""
    
    def test_create_branch_admin(self):
        """Prueba crear una sucursal como admin."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'name': 'Sucursal Nueva',
            'address': 'Calle 101',
            'phone': '1111111111'
        }
        response = self.client.post('/api/control/branches/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Sucursal Nueva')

    def test_create_branch_user(self):
        """Prueba crear una sucursal como usuario (debería fallar)."""
        self.client.force_authenticate(user=self.normal_user)
        data = {
            'name': 'Sucursal Nueva',
            'address': 'Calle 101',
            'phone': '1111111111'
        }
        response = self.client.post('/api/control/branches/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class CategoryViewTest(BaseTestCase):
    """Pruebas para CategoryView."""
    
    def test_create_category_admin(self):
        """Prueba crear una categoría como admin."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'name': 'Categoria Nueva',
            'description': 'Descripción Nueva'
        }
        response = self.client.post('/api/control/categories/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Categoria Nueva')

class ProductViewTest(BaseTestCase):
    """Pruebas para ProductView."""
    
    def test_create_product_admin(self):
        """Prueba crear un producto como admin."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'name': 'Producto Nuevo',
            'description': 'Descripción Nueva',
            'price': 20.99,
            'business_id': self.business.id,
            'category_id': self.category.id
        }
        response = self.client.post('/api/control/products/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Producto Nuevo')

    def test_list_products_user(self):
        """Prueba listar productos como usuario (solo los de su sucursal)."""
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.get('/api/control/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Solo el producto con stock en la sucursal

class DocumentViewTest(BaseTestCase):
    """Pruebas para DocumentView."""
    
    def test_create_document(self):
        """Prueba crear un documento como admin."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'document_type': 'purchase_order',
            'document_number': 'PO-002'
        }
        response = self.client.post('/api/control/documents/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['document_number'], 'PO-002')

    def test_delete_document_user(self):
        """Prueba eliminar un documento como usuario (debería fallar)."""
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.delete(f'/api/control/documents/{self.document.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class MovementViewTest(BaseTestCase):
    """Pruebas para MovementView."""
    
    def test_create_movement(self):
        """Prueba crear un movimiento como admin."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'movement_type': 'sale',
            'quantity': 5,
            'unit_price': 10.99,
            'product_id': self.product.id,
            'branch_id': self.branch.id,
            'document_id': self.document.id
        }
        response = self.client.post('/api/control/movements/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.quantity, 95)

    def test_create_movement_no_permission(self):
        """Prueba crear un movimiento sin permisos."""
        self.client.force_authenticate(user=self.normal_user)
        data = {
            'movement_type': 'sale',
            'quantity': 5,
            'unit_price': 10.99,
            'product_id': self.product.id,
            'branch_id': self.branch.id,
            'document_id': self.document.id
        }
        response = self.client.post('/api/control/movements/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class StockViewTest(BaseTestCase):
    """Pruebas para StockView."""
    
    def test_filter_by_product(self):
        """Prueba filtrar stock por product_id."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f'/api/control/stocks/?product_id={self.product.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['quantity'], 100)

    def test_by_product_name(self):
        """Prueba la acción by_product_name."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/control/stocks/by-product-name/Producto Test/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['quantity'], 100)

class RegisterAdminViewTest(BaseTestCase):
    """Pruebas para RegisterAdminView."""
    
    def test_register_admin(self):
        """Prueba registrar un administrador."""
        data = {
            'name': 'Nuevo Admin',
            'email': 'nuevo@ejemplo.com',
            'username': 'nuevoadmin',
            'password': 'admin123',
            'password2': 'admin123',
            'business': {
                'name': 'Negocio Nuevo',
                'address': 'Calle 789',
                'phone': '5555555555'
            }
        }
        response = self.client.post('/user-control/register-admin/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.filter(email='nuevo@ejemplo.com').count(), 1)

class CreateUserByAdminViewTest(BaseTestCase):
    """Pruebas para CreateUserByAdminView."""
    
    def test_create_user_by_admin(self):
        """Prueba crear un usuario por un admin."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'email': 'nuevo_usuario@ejemplo.com',
            'name': 'Nuevo Usuario',
            'role': 'user',
            'password': 'user123',
            'branch_id': self.branch.id,
            'can_sale': True
        }
        response = self.client.post('/user-control/admin/create-user/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.filter(email='nuevo_usuario@ejemplo.com').count(), 1)

class UserViewTest(BaseTestCase):
    """Pruebas para UserView."""
    
    def test_list_users_admin(self):
        """Prueba listar usuarios como admin."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/user-control/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # admin_user y normal_user

    def test_list_users_user(self):
        """Prueba listar usuarios como usuario (solo ve su propio perfil)."""
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.get('/user-control/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['email'], 'user@ejemplo.com')

class LoginViewTest(BaseTestCase):
    """Pruebas para LoginView."""
    
    def test_login_success(self):
        """Prueba iniciar sesión con credenciales correctas."""
        data = {
            'identifier': 'admin@ejemplo.com',
            'password': 'admin123'
        }
        response = self.client.post('/user-control/login/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'admin@ejemplo.com')

    def test_login_invalid(self):
        """Prueba iniciar sesión con credenciales incorrectas."""
        data = {
            'identifier': 'admin@ejemplo.com',
            'password': 'wrong'
        }
        response = self.client.post('/user-control/login/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Credenciales incorrectas', response.data['error'])

class LogoutViewTest(BaseTestCase):
    """Pruebas para LogoutView."""
    
    def test_logout(self):
        """Prueba cerrar sesión."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post('/user-control/logout/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Logout exitoso')

class ModelTests(BaseTestCase):
    """Pruebas para métodos de modelos."""
    
    def test_business_str(self):
        """Prueba el método __str__ de Business."""
        self.assertEqual(str(self.business), 'Negocio Test')

    def test_branch_str(self):
        """Prueba el método __str__ de Branch."""
        self.assertEqual(str(self.branch), 'Sucursal Test - Negocio Test')

    def test_category_str(self):
        """Prueba el método __str__ de Category."""
        self.assertEqual(str(self.category), 'Categoria Test')

    def test_product_str(self):
        """Prueba el método __str__ de Product."""
        self.assertEqual(str(self.product), 'Producto Test (Negocio Test)')

    def test_document_str(self):
        """Prueba el método __str__ de Document."""
        self.assertEqual(str(self.document), 'invoice #INV-001')

    def test_movement_str(self):
        """Prueba el método __str__ de Movement."""
        movement = Movement.objects.create(
            movement_type='sale',
            product=self.product,
            branch=self.branch,
            quantity=5,
            unit_price=10.99,
            document=self.document,
            user=self.admin_user
        )
        self.assertEqual(str(movement), f"sale - {self.product.name} (5) from None to {self.branch}")

    def test_stock_str(self):
        """Prueba el método __str__ de Stock."""
        self.assertEqual(str(self.stock), f"{self.product.name} in {self.branch.name}: 100")

    def test_stock_unique_together(self):
        """Prueba la restricción unique_together de Stock."""
        with self.assertRaises(Exception):
            Stock.objects.create(
                product=self.product,
                branch=self.branch,
                quantity=50,
                minimum_stock=5
            )

class PermissionTests(BaseTestCase):
    """Pruebas para permisos."""
    
    def test_is_admin_user_custom(self):
        """Prueba el permiso IsAdminUserCustom."""
        permission = IsAdminUserCustom()
        request = self.factory.post('/')
        request.user = self.admin_user
        self.assertTrue(permission.has_permission(request, None))
        request.user = self.normal_user
        self.assertFalse(permission.has_permission(request, None))