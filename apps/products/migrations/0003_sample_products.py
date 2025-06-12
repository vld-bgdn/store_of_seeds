# products/migrations/0003_sample_products.py
from django.db import migrations


def create_sample_products(apps, schema_editor):
    Category = apps.get_model("products", "Category")
    Product = apps.get_model("products", "Product")
    ProductImage = apps.get_model("products", "ProductImage")

    # Get categories
    seeds = Category.objects.get(slug="microgreens-seeds")
    cabbage = Category.objects.get(slug="cabbage")
    spicy = Category.objects.get(slug="spicy")

    # Create sample products
    product1 = Product.objects.create(
        name="Семена рукколы",
        slug="arugula-seeds",
        article="ARU001",
        category=cabbage,
        price=150,
        stock=50,
        short_description="Семена рукколы для выращивания микрозелени с островатым вкусом.",
        full_description="""Руккола - популярная микрозелень с острым, пряным вкусом, 
        богатая витаминами A, C и K. Идеально подходит для салатов, сэндвичей и украшения блюд.""",
        germination_time="3-5 дней",
        difficulty_level="easy",
        taste_characteristics="Острый, пряный, с легкой горчинкой",
        benefits="Богата витаминами A, C, K и кальцием. Укрепляет иммунитет.",
        recommended_substrate="Кокосовый мат или био-губка",
        growing_instructions="""1. Равномерно распределите семена по поверхности субстрата
        2. Увлажните из пульверизатора
        3. Накройте крышкой на 2 дня для проращивания
        4. После появления ростков откройте и выращивайте при свете
        5. Собирайте урожай на 7-10 день""",
        recommended_temperature="18-22°C",
        harvest_dates="7-10 дней",
    )

    ProductImage.objects.create(
        product=product1, image="products/arugula.jpg", is_main=True
    )

    product2 = Product.objects.create(
        name="Семена базилика",
        slug="basil-seeds",
        article="BAS001",
        category=spicy,
        price=180,
        stock=30,
        short_description="Семена базилика для ароматной микрозелени.",
        full_description="""Микрозелень базилика обладает насыщенным ароматом и вкусом, 
        содержит эфирные масла и антиоксиданты. Прекрасно дополняет итальянские блюда.""",
        germination_time="5-7 дней",
        difficulty_level="medium",
        taste_characteristics="Яркий, пряный, с перечными нотками",
        benefits="Содержит эфирные масла, антиоксиданты, витамины K и A.",
        recommended_substrate="Био-губка",
        growing_instructions="""1. Замочите семена на 4 часа перед посадкой
        2. Равномерно распределите по субстрату
        3. Увлажните и накройте на 3 дня
        4. После прорастания обеспечьте хорошее освещение
        5. Собирайте на 12-14 день""",
        recommended_temperature="20-24°C",
        harvest_dates="12-14 дней",
    )

    ProductImage.objects.create(
        product=product2, image="products/basil.jpg", is_main=True
    )


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0002_initial_categories"),
    ]

    operations = [
        migrations.RunPython(create_sample_products),
    ]
