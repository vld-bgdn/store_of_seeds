# products/migrations/0002_initial_categories.py
from django.db import migrations


def create_initial_categories(apps, schema_editor):
    Category = apps.get_model("products", "Category")

    # Main categories
    seeds = Category.objects.create(name="Семена микрозелени", slug="microgreens-seeds")
    equipment = Category.objects.create(
        name="Оборудование для выращивания", slug="growing-equipment"
    )
    preparations = Category.objects.create(
        name="Препараты и добавки", slug="preparations-additives"
    )
    accessories = Category.objects.create(name="Аксессуары", slug="accessories")

    # Subcategories for seeds
    Category.objects.create(name="Капустные", slug="cabbage", parent=seeds)
    Category.objects.create(name="Пряные", slug="spicy", parent=seeds)
    Category.objects.create(
        name="Проростки для сока", slug="sprouts-for-juice", parent=seeds
    )
    Category.objects.create(name="Разное", slug="miscellaneous-seeds", parent=seeds)

    # Subcategories for equipment
    Category.objects.create(
        name="Поддоны и лотки", slug="pallets-trays", parent=equipment
    )
    Category.objects.create(
        name="Субстраты и маты", slug="substrates-mats", parent=equipment
    )
    Category.objects.create(name="Фитолампы", slug="phytolights", parent=equipment)
    Category.objects.create(name="Проращиватели", slug="sprouters", parent=equipment)

    # Subcategories for preparations
    Category.objects.create(
        name="Биопрепараты", slug="biopreparations", parent=preparations
    )
    Category.objects.create(name="Удобрения", slug="fertilizers", parent=preparations)

    # Subcategories for accessories
    Category.objects.create(name="Инструменты", slug="tools", parent=accessories)
    Category.objects.create(name="Контейнеры", slug="containers", parent=accessories)


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_initial_categories),
    ]
