from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Business)
admin.site.register(Branch)
admin.site.register(Product)
admin.site.register(Movement)
admin.site.register(Stock)