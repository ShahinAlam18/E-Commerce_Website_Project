from django.core.management.base import BaseCommand
from django.core.files import File
import os
from django.conf import settings
from products.models import Category, Product, Tag


class Command(BaseCommand):
    help = "Seed demo categories, tags, and products"

    def handle(self, *args, **options):
        categories = [
            ("children", "Children"),
            ("men", "Men"),
            ("women", "Women"),
        ]

        created_categories = {}
        for slug, name in categories:
            cat, _ = Category.objects.get_or_create(slug=slug, defaults={"name": name})
            created_categories[slug] = cat

        tag_names = ["new", "sale", "summer", "classic"]
        tags = {}
        for t in tag_names:
            tag, _ = Tag.objects.get_or_create(slug=t, defaults={"name": t.title()})
            tags[t] = tag

        demo_products = [
            # Children (5)
            ("kids-shoe", "Kids Shoe", "children", 19.99, ["new", "sale"], "kids_shoe.png"),
            ("kids-hat", "Kids Hat", "children", 9.99, ["summer"], "kids_hat.png"),
            ("kids-tshirt", "Kids T-Shirt", "children", 12.99, ["summer"], "kids_tshirt.png"),
            ("kids-jacket", "Kids Jacket", "children", 34.99, ["classic"], "kids_jacket.png"),
            ("kids-backpack", "Kids Backpack", "children", 24.99, ["new"], "kids_backpack.png"),
            # Men (5)
            ("mens-shirt", "Men's Shirt", "men", 29.99, ["classic"], "menshirt.png"),
            ("mens-pant", "Men's Pant", "men", 49.99, ["sale"], "menspant.jpg"),
            ("mens-sneaker", "Men's Sneaker", "men", 69.99, ["new"], "mensneaker.jpg"),
            ("mens-watch", "Men's Watch", "men", 89.99, ["classic"], "menwatch.png"),
            ("mens-hoodie", "Men's Hoodie", "men", 39.99, ["summer"], "menshoodie.png"),
            # Women (5)
            ("womens-dress", "Women's Dress", "women", 59.99, ["new"], "womens_dress.png"),
            ("womens-bag", "Women's Bag", "women", 39.99, ["classic", "sale"], "placeholder.png"),
            ("womens-heels", "Women's Heels", "women", 74.99, ["classic"], "placeholder.png"),
            ("womens-top", "Women's Top", "women", 29.99, ["summer"], "placeholder.png"),
            ("womens-jacket", "Women's Jacket", "women", 69.99, ["new"], "placeholder.png"),
        ]

        created = 0
        for slug, name, cat_slug, price, tag_slugs, image_filename in demo_products:
            category = created_categories[cat_slug]
            product, was_created = Product.objects.get_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "category": category,
                    "price": price,
                    "description": f"Demo description for {name}.",
                },
            )
            if was_created:
                created += 1
            # Ensure correct category and price if existing
            if product.category_id != category.id or product.price != price:
                product.category = category
                product.price = price
                product.save()
            
            # Handle image upload
            if not product.image and image_filename != "placeholder.png":
                static_image_path = os.path.join(settings.BASE_DIR, '..', 'static', image_filename)
                if os.path.exists(static_image_path):
                    with open(static_image_path, 'rb') as f:
                        django_file = File(f)
                        product.image.save(image_filename, django_file, save=True)
                        self.stdout.write(f"Added image {image_filename} to {product.name}")
                else:
                    self.stdout.write(self.style.WARNING(f"Image file {image_filename} not found for {product.name}"))
            
            # Tags
            product.tags.set([tags[t] for t in tag_slugs])

        self.stdout.write(self.style.SUCCESS(f"Seed complete. Products created/ensured: {created}"))


