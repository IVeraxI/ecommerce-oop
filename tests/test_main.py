import pytest

from src.main import Category, Product


@pytest.fixture
def product() -> Product:
    """Фикстура: единичный товар для тестов."""
    return Product("Samsung Galaxy S23 Ultra", "256GB, Серый цвет, 200MP камера", 180000.0, 5)


@pytest.fixture
def products(product: Product) -> list[Product]:
    """Фикстура: список из нескольких товаров для тестов."""
    product2 = Product("Iphone 15", "512GB, Gray space", 210000.0, 8)
    return [product, product2]


def test_product_init(product: Product) -> None:
    """Проверяем, что все атрибуты Product заполняются корректно при создании."""
    assert product.name == "Samsung Galaxy S23 Ultra"
    assert product.description == "256GB, Серый цвет, 200MP камера"
    assert product.price == 180000.0
    assert product.quantity == 5


def test_category_init(products: list[Product]) -> None:
    """Проверяем, что атрибуты Category заполняются корректно при создании."""
    category = Category("Смартфоны", "Описание категории смартфонов", products)

    assert category.name == "Смартфоны"
    assert category.description == "Описание категории смартфонов"
    assert category.products == products


def test_category_count_increments(products: list[Product]) -> None:
    """Проверяем, что счетчик категорий увеличивается на 1 при создании новой категории."""
    count_before = Category.category_count
    Category("Смартфоны", "Описание", products)

    assert Category.category_count == count_before + 1


def test_product_count_increments(products: list[Product]) -> None:
    """Проверяем, что счетчик товаров увеличивается на количество товаров в категории."""
    count_before = Category.product_count
    Category("Смартфоны", "Описание", products)

    assert Category.product_count == count_before + len(products)
