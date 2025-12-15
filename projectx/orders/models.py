from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product

User = get_user_model()


class Order(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("cancelled", "Cancelled"),
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    stripe_session_id = models.CharField(max_length=255, blank=True, default="")
    shipping_address = models.TextField(blank=True, default="")
    billing_address = models.TextField(blank=True, default="")
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"Order #{self.id} - {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self) -> str:
        return f"{self.product.name} x{self.quantity}"

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="carts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user"], name="uniq_active_cart_per_user")
        ]

    def __str__(self) -> str:
        return f"Cart #{self.id} for {self.user.username}"

    @classmethod
    def get_for_user(cls, user: User) -> "Cart":
        cart, _ = cls.objects.get_or_create(user=user)
        return cart

    def add_product(self, product: Product, quantity: int = 1) -> None:
        if quantity <= 0:
            return
        item, created = CartItem.objects.get_or_create(
            cart=self, product=product, defaults={"quantity": quantity, "unit_price": product.price}
        )
        if not created:
            item.quantity += quantity
            # Keep the last known product price as unit_price
            item.unit_price = product.price
            item.save()

    def set_quantity(self, product: Product, quantity: int) -> None:
        if quantity <= 0:
            self.remove_product(product)
            return
        item, _ = CartItem.objects.get_or_create(
            cart=self, product=product, defaults={"quantity": quantity, "unit_price": product.price}
        )
        item.quantity = quantity
        item.unit_price = product.price
        item.save()

    def remove_product(self, product: Product) -> None:
        CartItem.objects.filter(cart=self, product=product).delete()

    def clear(self) -> None:
        self.items.all().delete()

    def items_count(self) -> int:
        return sum(i.quantity for i in self.items.all())

    def subtotal(self):
        from decimal import Decimal
        total = Decimal("0.00")
        for i in self.items.all():
            total += i.unit_price * i.quantity
        return total

    def to_order(self, user: User | None = None) -> Order:
        """Create an Order snapshot from this cart and return it. Does not clear the cart."""
        order = Order.objects.create(
            user=user or self.user,
            status="pending",
            total_amount=self.subtotal(),
        )
        for item in self.items.select_related("product"):
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.unit_price,
            )
        return order


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["cart", "product"], name="uniq_product_per_cart")
        ]

    def line_total(self):
        return self.unit_price * self.quantity

    def __str__(self) -> str:
        return f"{self.product.name} x{self.quantity}"