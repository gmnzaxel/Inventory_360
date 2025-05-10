from django.test import TestCase
from rest_framework.test import APIClient, APITestCase
from django.urls import reverse
from rest_framework import status
from .models import Business, Branch, Category, Product, Document, Movement, Stock
from .serializer import (
    BusinessSerializer, BranchSerializer, CategorySerializer, ProductSerializer,
    DocumentSerializer, MovementSerializer, StockSerializer
)
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory
import uuid

User = get_user_model()

class BusinessSerializerTest(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@ejemplo.com',
            password='testpass123',
            role='admin'
        )
        self.business = Business.objects.create(
            name='Negocio Test',
            address='Calle Test',
            phone='1234567890'
        )
        self.user.business = self.business
        self.user.save()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_valid_business(self):
        data = {
            'name': 'Negocio Nuevo',
            'address': 'Calle Nueva',
            'phone': '0987654321',
            'notes': 'Notas'
        }
        serializer = BusinessSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        business = serializer.save()
        self.assertEqual(business.name, 'Negocio Nuevo')

    def test_invalid_phone(self):
        data = {
            'name': 'Negocio Nuevo',
            'address': 'Calle Nueva',
            'phone': '12345',
            'notes': 'Notas'
        }
        serializer = BusinessSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('phone', serializer.errors)

class BranchSerializerTest(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@ejemplo.com',
            password='testpass123',
            role='admin'
        )
        self.business = Business.objects.create(
            name='Negocio Test',
            address='Calle Test',
            phone='1234567890'
        )
        self.user.business = self.business
        self.user.save()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_valid_branch(self):
        data = {
            'name': 'Sucursal Nueva',
            'address': 'Calle 101',
            'phone': '1111111111'
        }
        request = self.factory.post('/api/control/branches/', data)
        request.user = self.user
        serializer = BranchSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        branch = serializer.save()
        self.assertEqual(branch.name, 'Sucursal Nueva')
        self.assertEqual(branch.business, self.business)

    def test_invalid_phone(self):
        data = {
            'name': 'Sucursal Nueva',
            'address': 'Calle 101',
            'phone': '123'
        }
        request = self.factory.post('/api/control/branches/', data)
        request.user = self.user
        serializer = BranchSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('phone', serializer.errors)

class CategorySerializerTest(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@ejemplo.com',
            password='testpass123',
            role='admin'
        )
        self.business = Business.objects.create(
            name='Negocio Test',
            address='Calle Test',
            phone='1234567890'
        )
        self.user.business = self.business
        self.user.save()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_valid_category(self):
        data = {
            'name': 'Categoria Nueva',
            'description': 'Descripción'
        }
        request = self.factory.post('/api/control/categories/', data)
        request.user = self.user
        serializer = CategorySerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        category = serializer.save()
        self.assertEqual(category.name, 'Categoria Nueva')
        self.assertEqual(category.business, self.business)

    def test_duplicate_category(self):
        Category.objects.create(
            name='Categoria Existente',
            description='Descripción',
            business=self.business
        )
        data = {
            'name': 'Categoria Existente',
            'description': 'Descripción'
        }
        request = self.factory.post('/api/control/categories/', data)
        request.user = self.user
        serializer = CategorySerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)

class ProductSerializerTest(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@ejemplo.com',
            password='testpass123',
            role='admin'
        )
        self.business = Business.objects.create(
            name='Negocio Test',
            address='Calle Test',
            phone='1234567890'
        )
        self.user.business = self.business
        self.user.save()
        self.category = Category.objects.create(
            name='Categoria Test',
            description='Descripción',
            business=self.business
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_valid_product(self):
        data = {
            'name': 'Producto Nuevo',
            'description': 'Descripción',
            'price': 20.99,
            'category_id': self.category.id
        }
        request = self.factory.post('/api/control/products/', data)
        request.user = self.user
        serializer = ProductSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        product = serializer.save()
        self.assertEqual(product.name, 'Producto Nuevo')
        self.assertEqual(product.business, self.business)

    def test_invalid_name(self):
        data = {
            'name': 'Producto123',
            'description': 'Descripción',
            'price': 20.99,
            'category_id': self.category.id
        }
        request = self.factory.post('/api/control/products/', data)
        request.user = self.user
        serializer = ProductSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)

    def test_invalid_price(self):
        data = {
            'name': 'Producto Nuevo',
            'description': 'Descripción',
            'price': -10,
            'category_id': self.category.id
        }
        request = self.factory.post('/api/control/products/', data)
        request.user = self.user
        serializer = ProductSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('price', serializer.errors)

class DocumentSerializerTest(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@ejemplo.com',
            password='testpass123',
            role='admin'
        )
        self.business = Business.objects.create(
            name='Negocio Test',
            address='Calle Test',
            phone='1234567890'
        )
        self.user.business = self.business
        self.user.save()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_valid_document(self):
        data = {
            'document_type': 'invoice',
            'document_number': 'INV-001'
        }
        request = self.factory.post('/api/control/documents/', data)
        request.user = self.user
        serializer = DocumentSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        document = serializer.save()
        self.assertEqual(document.document_type, 'invoice')
        self.assertEqual(document.business, self.business)

    def test_duplicate_document(self):
        Document.objects.create(
            document_type='invoice',
            document_number='INV-001',
            business=self.business,
            created_by=self.user
        )
        data = {
            'document_type': 'invoice',
            'document_number': 'INV-001'
        }
        request = self.factory.post('/api/control/documents/', data)
        request.user = self.user
        serializer = DocumentSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('document_number', serializer.errors)

class StockSerializerTest(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@ejemplo.com',
            password='testpass123',
            role='admin'
        )
        self.business = Business.objects.create(
            name='Negocio Test',
            address='Calle Test',
            phone='1234567890'
        )
        self.user.business = self.business
        self.user.save()
        self.branch = Branch.objects.create(
            name='Sucursal Test',
            address='Calle Test',
            phone='1234567890',
            business=self.business
        )
        self.category = Category.objects.create(
            name='Categoria Test',
            description='Descripción',
            business=self.business
        )
        self.product = Product.objects.create(
            name='Producto Test',
            description='Descripción',
            price=10.99,
            business=self.business,
            category=self.category
        )
        self.stock = Stock.objects.create(
            product=self.product,
            branch=self.branch,
            quantity=5,
            minimum_stock=10
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_is_low_stock(self):
        request = self.factory.get('/api/control/stocks/')
        request.user = self.user
        serializer = StockSerializer(self.stock, context={'request': request})
        self.assertTrue(serializer.data['is_low_stock'])

    def test_invalid_minimum_stock(self):
        data = {
            'product_id': self.product.id,
            'branch_id': self.branch.id,
            'quantity': 100,
            'minimum_stock': -10
        }
        request = self.factory.post('/api/control/stocks/', data)
        request.user = self.user
        serializer = StockSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('minimum_stock', serializer.errors)

class MovementSerializerTest(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@ejemplo.com',
            password='testpass123',
            role='admin',
            can_sale=True,
            can_purchase=True,
            can_adjust=True,
            can_transfer=True
        )
        self.business = Business.objects.create(
            name='Negocio Test',
            address='Calle Test',
            phone='1234567890'
        )
        self.user.business = self.business
        self.user.save()
        self.branch = Branch.objects.create(
            name='Sucursal Test',
            address='Calle Test',
            phone='1234567890',
            business=self.business
        )
        self.category = Category.objects.create(
            name='Categoria Test',
            description='Descripción',
            business=self.business
        )
        self.product = Product.objects.create(
            name='Producto Test',
            description='Descripción',
            price=10.99,
            business=self.business,
            category=self.category
        )
        self.document = Document.objects.create(
            document_type='invoice',
            document_number='INV-001',
            business=self.business,
            created_by=self.user
        )
        self.stock = Stock.objects.create(
            product=self.product,
            branch=self.branch,
            quantity=100,
            minimum_stock=10
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_valid_sale_movement(self):
        data = {
            'movement_type': 'sale',
            'quantity': 5,
            'unit_price': 10.0,
            'product_id': self.product.id,
            'branch_id': self.branch.id,
            'document_id': self.document.id
        }
        request = self.factory.post('/api/control/movements/', data)
        request.user = self.user
        serializer = MovementSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        movement = serializer.save()
        self.assertEqual(movement.movement_type, 'sale')
        self.assertEqual(movement.quantity, 5)
        self.assertEqual(movement.product, self.product)

    def test_insufficient_stock(self):
        data = {
            'movement_type': 'sale',
            'quantity': 150,
            'unit_price': 10.0,
            'product_id': self.product.id,
            'branch_id': self.branch.id,
            'document_id': self.document.id
        }
        request = self.factory.post('/api/control/movements/', data)
        request.user = self.user
        serializer = MovementSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('Stock insuficiente', str(serializer.errors))

    def test_invalid_document_type(self):
        invalid_document = Document.objects.create(
            document_type='adjustment',
            document_number='ADJ-001',
            business=self.business,
            created_by=self.user
        )
        data = {
            'movement_type': 'sale',
            'quantity': 5,
            'unit_price': 10.0,
            'product_id': self.product.id,
            'branch_id': self.branch.id,
            'document_id': invalid_document.id
        }
        request = self.factory.post('/api/control/movements/', data)
        request.user = self.user
        serializer = MovementSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('El documento debe ser de tipo', str(serializer.errors))

    def test_missing_unit_price(self):
        data = {
            'movement_type': 'purchase',
            'quantity': 5,
            'product_id': self.product.id,
            'branch_id': self.branch.id,
            'document_id': self.document.id
        }
        request = self.factory.post('/api/control/movements/', data)
        request.user = self.user
        serializer = MovementSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('El precio unitario es requerido', str(serializer.errors))

    def test_no_permission(self):
        user_no_perm = User.objects.create_user(
            username='noperm',
            email='noperm@ejemplo.com',
            password='testpass123',
            role='user',
            can_sale=False,
            business=self.business
        )
        data = {
            'movement_type': 'sale',
            'quantity': 5,
            'unit_price': 10.0,
            'product_id': self.product.id,
            'branch_id': self.branch.id,
            'document_id': self.document.id
        }
        request = self.factory.post('/api/control/movements/', data)
        request.user = user_no_perm
        serializer = MovementSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('No tienes permiso para registrar ventas', str(serializer.errors))

class BusinessViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@ejemplo.com',
            password='testpass123',
            role='admin'
        )
        self.business = Business.objects.create(
            name='Negocio Test',
            address='Calle Test',
            phone='1234567890'
        )
        self.user.business = self.business
        self.user.save()
        self.client.force_authenticate(user=self.user)

    def test_create_business_admin(self):
        data = {
            'name': 'Negocio Nuevo',
            'address': 'Calle Nueva',
            'phone': '0987654321',
            'notes': 'Notas'
        }
        response = self.client.post('/api/control/businesses/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Negocio Nuevo')

    def test_list_businesses(self):
        response = self.client.get('/api/control/businesses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

class BranchViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@ejemplo.com',
            password='testpass123',
            role='admin'
        )
        self.business = Business.objects.create(
            name='Negocio Test',
            address='Calle Test',
            phone='1234567890'
        )
        self.user.business = self.business
        self.user.save()
        self.client.force_authenticate(user=self.user)

    def test_create_branch_admin(self):
        data = {
            'name': 'Sucursal Nueva',
            'address': 'Calle 101',
            'phone': '1111111111'
        }
        print(f"test_create_branch_admin data: {data}")
        response = self.client.post('/api/control/branches/', data)
        print(f"test_create_branch_admin response: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Sucursal Nueva')

    def test_list_branches(self):
        Branch.objects.create(
            name='Sucursal Test',
            address='Calle Test',
            phone='1234567890',
            business=self.business
        )
        response = self.client.get('/api/control/branches/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

class CategoryViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@ejemplo.com',
            password='testpass123',
            role='admin'
        )
        self.business = Business.objects.create(
            name='Negocio Test',
            address='Calle Test',
            phone='1234567890'
        )
        self.user.business = self.business
        self.user.save()
        self.client.force_authenticate(user=self.user)

    def test_create_category_admin(self):
        data = {
            'name': 'Categoria Nueva',
            'description': 'Descripción'
        }
        response = self.client.post('/api/control/categories/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Categoria Nueva')

    def test_list_categories(self):
        Category.objects.create(
            name='Categoria Test',
            description='Descripción',
            business=self.business
        )
        response = self.client.get('/api/control/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

class ProductViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@ejemplo.com',
            password='testpass123',
            role='admin'
        )
        self.user_non_admin = User.objects.create_user(
            username='testuser2',
            email='test2@ejemplo.com',
            password='testpass123',
            role='user'
        )
        self.business = Business.objects.create(
            name='Negocio Test',
            address='Calle Test',
            phone='1234567890'
        )
        self.user.business = self.business
        self.user_non_admin.business = self.business
        self.user.save()
        self.user_non_admin.save()
        self.branch = Branch.objects.create(
            name='Sucursal Test',
            address='Calle Test',
            phone='1234567890',
            business=self.business
        )
        self.user_non_admin.branch = self.branch
        self.user_non_admin.save()
        self.category = Category.objects.create(
            name='Categoria Test',
            description='Descripción',
            business=self.business
        )
        self.product = Product.objects.create(
            name='Producto Test',
            description='Descripción',
            price=10.99,
            business=self.business,
            category=self.category
        )
        self.stock = Stock.objects.create(
            product=self.product,
            branch=self.branch,
            quantity=100,
            minimum_stock=10
        )

    def test_create_product_admin(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'name': 'Producto Nuevo',
            'description': 'Descripción Nueva',
            'price': 20.99,
            'category_id': self.category.id
        }
        print(f"test_create_product_admin: user_business={self.user.business}, category_business={self.category.business}, data={data}")
        response = self.client.post('/api/control/products/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Producto Nuevo')

    def test_list_products_user(self):
        self.client.force_authenticate(user=self.user_non_admin)
        response = self.client.get('/api/control/products/')
        print(f"test_list_products_user response: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Producto Test')

    def test_update_product(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'price': 15.99
        }
        response = self.client.patch(f'/api/control/products/{self.product.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['price'], 15.99)

class DocumentViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@ejemplo.com',
            password='testpass123',
            role='admin'
        )
        self.business = Business.objects.create(
            name='Negocio Test',
            address='Calle Test',
            phone='1234567890'
        )
        self.user.business = self.business
        self.user.save()
        self.client.force_authenticate(user=self.user)

    def test_create_document(self):
        data = {
            'document_type': 'invoice',
            'document_number': 'INV-001'
        }
        response = self.client.post('/api/control/documents/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['document_type'], 'invoice')

    def test_list_documents(self):
        Document.objects.create(
            document_type='invoice',
            document_number='INV-001',
            business=self.business,
            created_by=self.user
        )
        response = self.client.get('/api/control/documents/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

class StockViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@ejemplo.com',
            password='testpass123',
            role='admin'
        )
        self.business = Business.objects.create(
            name='Negocio Test',
            address='Calle Test',
            phone='1234567890'
        )
        self.user.business = self.business
        self.user.save()
        self.branch = Branch.objects.create(
            name='Sucursal Test',
            address='Calle Test',
            phone='1234567890',
            business=self.business
        )
        self.category = Category.objects.create(
            name='Categoria Test',
            description='Descripción',
            business=self.business
        )
        self.product = Product.objects.create(
            name='Producto Test',
            description='Descripción',
            price=10.99,
            business=self.business,
            category=self.category
        )
        self.stock = Stock.objects.create(
            product=self.product,
            branch=self.branch,
            quantity=100,
            minimum_stock=10
        )
        self.client.force_authenticate(user=self.user)

    def test_filter_by_product(self):
        response = self.client.get(f'/api/control/stocks/?product_id={self.product.id}')
        print(f"test_filter_by_product response: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['product'], self.product.id)
        self.assertEqual(response.data[0]['is_low_stock'], False)

    def test_by_product_name(self):
        response = self.client.get('/api/control/stocks/by-product-name/Producto Test/')
        print(f"test_by_product_name response: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['product'], self.product.id)
        self.assertEqual(response.data[0]['is_low_stock'], False)

class MovementViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@ejemplo.com',
            password='testpass123',
            role='admin',
            can_sale=True,
            can_purchase=True,
            can_adjust=True,
            can_transfer=True
        )
        self.business = Business.objects.create(
            name='Negocio Test',
            address='Calle Test',
            phone='1234567890'
        )
        self.user.business = self.business
        self.user.save()
        self.branch = Branch.objects.create(
            name='Sucursal Test',
            address='Calle Test',
            phone='1234567890',
            business=self.business
        )
        self.category = Category.objects.create(
            name='Categoria Test',
            description='Descripción',
            business=self.business
        )
        self.product = Product.objects.create(
            name='Producto Test',
            description='Descripción',
            price=10.99,
            business=self.business,
            category=self.category
        )
        self.document = Document.objects.create(
            document_type='invoice',
            document_number='INV-001',
            business=self.business,
            created_by=self.user
        )
        self.stock = Stock.objects.create(
            product=self.product,
            branch=self.branch,
            quantity=100,
            minimum_stock=10
        )
        self.client.force_authenticate(user=self.user)

    def test_create_movement(self):
        data = {
            'movement_type': 'sale',
            'quantity': 5,
            'unit_price': 10.0,
            'product_id': self.product.id,
            'branch_id': self.branch.id,
            'document_id': self.document.id
        }
        print(f"test_create_movement: data={data}")
        response = self.client.post('/api/control/movements/', data)
        print(f"test_create_movement response: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['movement_type'], 'sale')
        self.assertEqual(response.data['quantity'], 5)

class IntegrationTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_full_flow(self):
        # Registro
        new_user = User.objects.create_user(
            username='nuevoadmin',
            email='nuevo@ejemplo.com',
            password='testpass123',
            name='Nuevo Admin',
            role='admin'
        )
        print(f"test_full_flow: created user={new_user}")
        new_user.can_sale = True
        new_user.can_purchase = True
        new_user.can_adjust = True
        new_user.can_transfer = True
        new_user.save()

        # Crear negocio
        business_data = {
            'name': 'Negocio Nuevo',
            'address': 'Calle Nueva',
            'phone': '0987654321'
        }
        new_user.business = Business.objects.create(**business_data)
        new_user.save()
        print(f"test_full_flow: new_admin_business={new_user.business}")

        # Login
        self.client.force_authenticate(user=new_user)

        # Crear sucursal
        branch_data = {
            'name': 'Sucursal Nueva',
            'address': 'Calle 101',
            'phone': '1111111111'
        }
        response = self.client.post('/api/control/branches/', branch_data)
        print(f"test_full_flow branch response: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        branch = Branch.objects.get(name='Sucursal Nueva')

        # Crear categoría
        category_data = {
            'name': 'Categoria Nueva',
            'description': 'Descripción'
        }
        response = self.client.post('/api/control/categories/', category_data)
        print(f"test_full_flow category response: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        category = Category.objects.get(name='Categoria Nueva')
        print(f"test_full_flow: category_business={category.business}")

        # Crear producto
        product_data = {
            'name': 'Producto Nuevo',
            'description': 'Descripción',
            'price': 20.99,
            'category_id': category.id
        }
        print(f"test_full_flow: product_data={product_data}")
        response = self.client.post('/api/control/products/', product_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        product = Product.objects.get(name='Producto Nuevo')

        # Crear stock
        stock_data = {
            'product_id': product.id,
            'branch_id': branch.id,
            'quantity': 100,
            'minimum_stock': 10
        }
        response = self.client.post('/api/control/stocks/', stock_data)
        print(f"test_full_flow stock response: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Crear documento
        document_data = {
            'document_type': 'invoice',
            'document_number': 'INV-002'
        }
        response = self.client.post('/api/control/documents/', document_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        document = Document.objects.get(document_number='INV-002')

        # Crear movimiento
        movement_data = {
            'movement_type': 'sale',
            'quantity': 5,
            'unit_price': 10.0,
            'product_id': product.id,
            'branch_id': branch.id,
            'document_id': document.id
        }
        response = self.client.post('/api/control/movements/', movement_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['movement_type'], 'sale')