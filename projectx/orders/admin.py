from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "get_user", "get_products", "get_quantities", "status", "total_amount", "created_at")
    list_select_related = ['user']
    inlines = [OrderItemInline]

    def get_user(self, obj):
        return obj.user.username if obj.user else "Guest"
    get_user.short_description = "Customer"
    
    def get_products(self, obj):
        return ", ".join([item.product.name for item in obj.items.all()])
    get_products.short_description = "Products"
    
    def get_quantities(self, obj):
        return ", ".join([f"{item.quantity}" for item in obj.items.all()])
    get_quantities.short_description = "Quantities"


