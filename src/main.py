import json
from pathlib import Path
from typing import Any


def _format_price(price: float) -> str:
    """Форматирует цену: целые значения без дробной части, иначе как есть."""
    return str(int(price)) if float(price).is_integer() else str(price)


class Product:
    """Класс для представления товара в магазине."""

    name: str
    description: str
    quantity: int
    __price: float

    def __init__(self, name: str, description: str, price: float, quantity: int) -> None:
        """Инициализирует товар. Цена должна быть строго положительной."""
        if price <= 0:
            raise ValueError("Цена не должна быть нулевая или отрицательная")
        self.name = name
        self.description = description
        self.__price = price
        self.quantity = quantity

    @property
    def price(self) -> float:
        """Геттер: возвращает текущую цену товара."""
        return self.__price

    @price.setter
    def price(self, new_price: float) -> None:
        """Сеттер цены: отклоняет неположительные значения, а понижение требует подтверждения."""
        if new_price <= 0:
            print("Цена не должна быть нулевая или отрицательная")
            return

        if new_price < self.__price:
            answer = input(
                f"Цена понижается: {_format_price(self.__price)} -> "
                f"{_format_price(new_price)}. Подтвердить? (y/n): "
            )
            if answer.strip().lower() != "y":
                return

        self.__price = new_price

    @classmethod
    def new_product(
        cls,
        product_data: dict[str, Any],
        products: list["Product"] | None = None,
    ) -> "Product":
        """Создает товар из словаря.

        Если передан список products и в нем уже есть товар с таким же названием,
        то у найденного товара суммируется количество, цена берется максимальная,
        и возвращается именно найденный (обновленный) объект.
        """
        name = product_data["name"]
        price = product_data["price"]
        quantity = product_data["quantity"]

        for existing in products or []:
            if existing.name.strip().lower() == name.strip().lower():
                existing.quantity += quantity
                existing.price = max(existing.price, price)
                return existing

        return cls(name, product_data["description"], price, quantity)


class Category:
    """Класс для представления категории товаров."""

    name: str
    description: str
    __products: list[Product]

    category_count: int = 0
    product_count: int = 0

    def __init__(self, name: str, description: str, products: list[Product]) -> None:
        """Инициализирует категорию и обновляет общие счетчики класса."""
        self.name = name
        self.description = description
        self.__products = list(products)

        Category.category_count += 1
        Category.product_count += len(self.__products)

    def add_product(self, product: Product) -> None:
        """Добавляет товар в категорию. Один и тот же объект дважды не добавляется."""
        if not isinstance(product, Product):
            raise TypeError("В категорию можно добавить только объект класса Product")
        if product in self.__products:
            return
        self.__products.append(product)
        Category.product_count += 1

    @property
    def products(self) -> str:
        """Геттер: товары категории строками «Название, N руб. Остаток: M шт.»."""
        return "".join(
            f"{product.name}, {_format_price(product.price)} руб. "
            f"Остаток: {product.quantity} шт.\n"
            for product in self.__products
        )


def load_categories_from_json(file_path: Path) -> list[Category]:
    """Загружает категории и товары из JSON-файла и создает объекты классов."""
    with open(file_path, encoding="utf-8") as file:
        raw_categories = json.load(file)

    categories = []
    for raw_category in raw_categories:
        products = [Product.new_product(raw_product) for raw_product in raw_category["products"]]
        categories.append(Category(raw_category["name"], raw_category["description"], products))

    return categories


if __name__ == "__main__":  # pragma: no cover
    product1 = Product("Samsung Galaxy S23 Ultra", "256GB, Серый цвет, 200MP камера", 180000.0, 5)
    product2 = Product("Iphone 15", "512GB, Gray space", 210000.0, 8)
    product3 = Product("Xiaomi Redmi Note 11", "1024GB, Синий", 31000.0, 14)

    category1 = Category(
        "Смартфоны",
        "Смартфоны, как средство не только коммуникации, "
        "но и получения дополнительных функций для удобства жизни",
        [product1, product2],
    )
    category1.add_product(product3)
    print(category1.products)

    duplicate = Product.new_product(
        {
            "name": "Iphone 15",
            "description": "512GB, Gray space",
            "price": 230000.0,
            "quantity": 2,
        },
        [product1, product2, product3],
    )
    category1.add_product(duplicate)
    print(category1.products)

    product1.price = 0
    product1.price = 190000.0
    print(product1.price)

    print(Category.category_count, Category.product_count)
