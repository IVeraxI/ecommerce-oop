import json
from pathlib import Path
from typing import Any
from abc import ABC, abstractmethod


class BaseProduct(ABC):
    """Абстрактный базовый класс для всех продуктов."""

    @classmethod
    @abstractmethod
    def new_product(cls, *args, **kwargs) -> "BaseProduct":
        """Создает новый товар. Обязателен для переопределения."""
        pass


class MixinLog:
    """Миксин для логирования создания объектов."""

    def __init__(self, *args, **kwargs) -> None:
        """Печатает лог при создании объекта и передает вызов дальше по MRO."""
        print(repr(self))
        super().__init__(*args, **kwargs)

    def __repr__(self) -> str:
        """Определяет формат вывода лога."""
        return f"{self.__class__.__name__}('{self.name}', '{self.description}', {self.price}, {self.quantity})"


def _format_price(price: float) -> str:
    """Форматирует цену: целые значения без дробной части, иначе как есть."""
    return str(int(price)) if float(price).is_integer() else str(price)


class Product(BaseProduct, MixinLog):
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

        # Вызываем __init__ у MixinLog через MRO
        super().__init__()

    def __str__(self) -> str:
        """Строковое отображение товара."""
        return f"{self.name}, {_format_price(self.price)} руб. Остаток: {self.quantity} шт."

    def __add__(self, other: "Product") -> float:
        """Сложение товаров: сумма произведений цены на количество.
        Складывать можно только объекты одного и того же класса."""
        if type(self) is not type(other):
            raise TypeError("Складывать можно только товары одного и того же класса")
        return (self.price * self.quantity) + (other.price * other.quantity)

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
        """Создает товар из словаря. Дубликаты суммируют остаток и обновляют цену."""
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

    def __str__(self) -> str:
        """Строковое отображение категории с общим количеством товаров."""
        total_quantity = sum(product.quantity for product in self.__products)
        return f"{self.name}, количество продуктов: {total_quantity} шт."

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
        """Геттер: товары категории строками."""
        return "".join(f"{str(product)}\n" for product in self.__products)


class CategoryIterator:
    """Вспомогательный класс для итерации по товарам одной категории."""

    def __init__(self, category: Category) -> None:
        self._category = category
        self._index = -1

    def __iter__(self) -> "CategoryIterator":
        self._index = -1
        return self

    def __next__(self) -> Product:
        # Получаем доступ к приватному списку продуктов через name mangling
        products = self._category._Category__products
        if self._index + 1 < len(products):
            self._index += 1
            return products[self._index]
        raise StopIteration


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

    category1 = Category("Смартфоны", "Современные гаджеты", [product1, product2])
    print(str(product1))
    print(str(category1))
    print(product1 + product2)

    # Итератор
    for item in CategoryIterator(category1):
        print(item.name)


class Smartphone(Product):
    """Класс для смартфона, наследуется от Product."""

    def __init__(
        self,
        name:str,
        description:str,
        price:float,
        quantity:int,
        efficiency:float,
        model: str,
        memory: int,
        color: str,
    ) -> None:
        """Инициализирует смартфон, расширяя базовый товар."""
        super().__init__(name, description, price, quantity)
        self.efficiency = efficiency
        self.model = model
        self.memory = memory
        self.color = color


class LawnGrass(Product):
    """Класс для газонной травы, наследуется от Product."""

    def __init__(
        self,
        name:str,
        description:str,
        price:float,
        quantity:int,
        country: str,
        germination_period: int,
        color: str,
    ) -> None:
        """Инициализирует газонную траву, расширяя базовый товар."""
        super().__init__(name, description, price, quantity)
        self.country = country
        self.germination_period = germination_period
        self.color = color
