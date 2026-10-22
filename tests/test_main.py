from pathlib import Path
from typing import Any

import pytest

from src.main import Category, Product, load_categories_from_json


@pytest.fixture(autouse=True)
def reset_counters() -> None:
    """Обнуляет счетчики класса Category, чтобы тесты не влияли друг на друга."""
    Category.category_count = 0
    Category.product_count = 0


@pytest.fixture
def product() -> Product:
    """Фикстура: единичный товар для тестов."""
    return Product("Samsung Galaxy S23 Ultra", "256GB, Серый цвет, 200MP камера", 180000.0, 5)


@pytest.fixture
def products(product: Product) -> list[Product]:
    """Фикстура: список из нескольких товаров для тестов."""
    return [product, Product("Iphone 15", "512GB, Gray space", 210000.0, 8)]


@pytest.fixture
def category(products: list[Product]) -> Category:
    """Фикстура: категория с двумя товарами."""
    return Category("Смартфоны", "Описание категории смартфонов", products)


@pytest.fixture
def product_data() -> dict[str, Any]:
    """Фикстура: словарь с параметрами нового товара."""
    return {
        "name": "Xiaomi Redmi Note 11",
        "description": "1024GB",
        "price": 31000.5,
        "quantity": 14,
    }


# ---------- Задание из урока 1 ----------


def test_product_init(product: Product) -> None:
    """Атрибуты Product корректно заполняются при создании."""
    assert product.name == "Samsung Galaxy S23 Ultra"
    assert product.description == "256GB, Серый цвет, 200MP камера"
    assert product.price == 180000.0
    assert product.quantity == 5


def test_product_init_invalid_price() -> None:
    """Создать товар с неположительной ценой нельзя."""
    with pytest.raises(ValueError, match="Цена не должна быть нулевая или отрицательная"):
        Product("Бракованный", "Описание", 0, 1)


def test_category_init(category: Category) -> None:
    """Атрибуты Category корректно заполняются при создании."""
    assert category.name == "Смартфоны"
    assert category.description == "Описание категории смартфонов"


def test_counters(category: Category, products: list[Product]) -> None:
    """Счетчики категорий и товаров считаются при инициализации."""
    assert Category.category_count == 1
    assert Category.product_count == 2

    Category("Телевизоры", "Описание", [products[0]])

    assert Category.category_count == 2
    assert Category.product_count == 3


def test_load_categories_from_json(tmp_path: Path) -> None:
    """Категории и товары корректно загружаются из JSON-файла."""
    json_file = tmp_path / "test_products.json"
    json_file.write_text(
        '[{"name": "Ноутбуки", "description": "Описание", "products": ['
        '{"name": "MacBook Air", "description": "M2", "price": 120000.0, "quantity": 3}]}]',
        encoding="utf-8",
    )

    categories = load_categories_from_json(json_file)

    assert len(categories) == 1
    assert categories[0].name == "Ноутбуки"
    assert categories[0].products == "MacBook Air, 120000 руб. Остаток: 3 шт.\n"


# ---------- Задания урока 2 ----------


def test_category_products_are_private(category: Category) -> None:
    """Прямого доступа к списку товаров извне нет."""
    with pytest.raises(AttributeError):
        category.__products  # noqa: B018


def test_products_getter_format(category: Category) -> None:
    """Геттер выводит товары в формате «Название, N руб. Остаток: M шт.»."""
    assert category.products == (
        "Samsung Galaxy S23 Ultra, 180000 руб. Остаток: 5 шт.\n"
        "Iphone 15, 210000 руб. Остаток: 8 шт.\n"
    )


def test_products_getter_fractional_price() -> None:
    """Копейки в цене не теряются при выводе."""
    category = Category("Мелочь", "Описание", [Product("Спички", "Коробок", 80.5, 15)])

    assert category.products == "Спички, 80.5 руб. Остаток: 15 шт.\n"


def test_add_product(category: Category, product_data: dict[str, Any]) -> None:
    """add_product добавляет товар и увеличивает счетчик товаров."""
    new = Product.new_product(product_data)

    category.add_product(new)

    assert "Xiaomi Redmi Note 11, 31000.5 руб. Остаток: 14 шт." in category.products
    assert Category.product_count == 3


def test_add_product_same_object_twice(category: Category, product: Product) -> None:
    """Один и тот же объект повторно не добавляется."""
    category.add_product(product)

    assert Category.product_count == 2


def test_add_product_wrong_type(category: Category) -> None:
    """В категорию нельзя добавить не Product."""
    with pytest.raises(TypeError):
        category.add_product("не товар")  # type: ignore[arg-type]


def test_new_product(product_data: dict[str, Any]) -> None:
    """Класс-метод создает объект Product из словаря."""
    new = Product.new_product(product_data)

    assert isinstance(new, Product)
    assert new.name == "Xiaomi Redmi Note 11"
    assert new.description == "1024GB"
    assert new.price == 31000.5
    assert new.quantity == 14


def test_new_product_duplicate_sums_quantity_and_takes_max_price(
    products: list[Product],
) -> None:
    """Дубликат по имени: количество суммируется, цена — максимальная."""
    data = {"name": " iphone 15 ", "description": "x", "price": 230000.0, "quantity": 2}

    result = Product.new_product(data, products)

    assert result is products[1]
    assert result.quantity == 10
    assert result.price == 230000.0


def test_new_product_duplicate_keeps_higher_old_price(products: list[Product]) -> None:
    """Если старая цена выше, она сохраняется."""
    data = {"name": "Iphone 15", "description": "x", "price": 100.0, "quantity": 1}

    result = Product.new_product(data, products)

    assert result.price == 210000.0
    assert result.quantity == 9


def test_new_product_no_duplicate(products: list[Product], product_data: dict[str, Any]) -> None:
    """Если совпадений по имени нет, создается новый объект."""
    result = Product.new_product(product_data, products)

    assert result not in products


def test_price_setter_valid_raise(product: Product) -> None:
    """Повышение цены применяется без подтверждения."""
    product.price = 200000.0

    assert product.price == 200000.0


@pytest.mark.parametrize("bad_price", [0, -1, -100.5])
def test_price_setter_rejects_non_positive(
    product: Product, bad_price: float, capsys: pytest.CaptureFixture[str]
) -> None:
    """Нулевая и отрицательная цена: сообщение в консоль, цена не меняется."""
    product.price = bad_price

    assert product.price == 180000.0
    assert capsys.readouterr().out.strip() == "Цена не должна быть нулевая или отрицательная"


@pytest.mark.parametrize(
    ("answer", "expected"),
    [("y", 100000.0), ("Y", 100000.0), (" y ", 100000.0), ("n", 180000.0), ("", 180000.0)],
)
def test_price_setter_lowering_requires_confirmation(
    product: Product, monkeypatch: pytest.MonkeyPatch, answer: str, expected: float
) -> None:
    """Понижение цены применяется только после подтверждения «y»."""
    monkeypatch.setattr("builtins.input", lambda _: answer)

    product.price = 100000.0

    assert product.price == expected
