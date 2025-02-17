from phonenumber_field.modelfields import PhoneNumberField

from django.db import models
from django.db.models import Sum
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Prefetch
from django.utils import timezone


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    image = models.ImageField('картинка')

    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True
    )

    description = models.TextField(
        'описание',
        max_length=200,
        blank=True
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )

    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):
    def get_total_cost(self):
        return self.annotate(cost=Sum(('positions__cost')))

    def get_restaurants_executors(self):
        orders = self.get_total_cost()
        restaurants = Restaurant.objects.prefetch_related(
            Prefetch(
                'menu_items',
                queryset=RestaurantMenuItem.objects.filter(availability=True),
                to_attr="availible_products"
            )
        )

        restaurants_with_actual_positions = []

        for restaurant in restaurants:
            actual_products_ids = [
                product.product.id for product in restaurant.availible_products
            ]
            restaurants_with_actual_positions.append(
                {
                    'restaurant_id': restaurant.id,
                    'address': restaurant.address,
                    'actual_positions_ids': actual_products_ids
                }
            )

        for order in orders:
            order.restaurants_executors = []
            order_positions = order.positions.all()
            order_products_ids = [
                position.product.id for position in order_positions
            ]

            for restaurant in restaurants_with_actual_positions:
                if set(order_products_ids).issubset(
                    restaurant['actual_positions_ids']
                ):
                    order.restaurants_executors.append(restaurant)

        return orders


class Order(models.Model):
    NEW = 'NW'
    PROCESSED = 'PD'
    BROUGHT = 'BT'
    CASH = 'CH'
    CREDIT_CARD = 'CD'
    UNSPECIFIED = 'UD'

    STATUS_CHOICE = [
        (NEW, 'новый'),
        (PROCESSED, 'обработан'),
        (BROUGHT, 'доставлен')
    ]

    PAYMENT_METHOD_CHOICE = [
        (CASH, 'наличные'),
        (CREDIT_CARD, 'карточкой'),
        (UNSPECIFIED, 'не указано')
    ]

    address = models.CharField(
        max_length=150,
        verbose_name='адрес'
    )

    first_name = models.CharField(
        max_length=50,
        verbose_name='имя'
    )

    last_name = models.CharField(
        max_length=50,
        verbose_name='фамилия'
    )

    phonenumber = PhoneNumberField(
        db_index=True,
        verbose_name='контактный телефон'
    )

    products = models.ManyToManyField(
        Product,
        related_name='orders',
        verbose_name='товары',
        through='Position'
    )

    status = models.CharField(
        max_length=12,
        choices=STATUS_CHOICE,
        default=NEW,
        verbose_name='статус заказа',
        db_index=True
    )

    comment = models.TextField(
        blank=True,
        verbose_name='комментарий'
    )

    registered_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name='дата оформления'
    )

    called_at = models.DateTimeField(
        blank=True,
        null=True,
        db_index=True,
        verbose_name='дата звонка'
    )

    delivered_at = models.DateTimeField(
        blank=True,
        null=True,
        db_index=True,
        verbose_name='дата доставки'
    )

    payment_method = models.CharField(
        max_length=12,
        choices=PAYMENT_METHOD_CHOICE,
        default=UNSPECIFIED,
        db_index=True,
        verbose_name='способ оплаты'
    )

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f'{self.first_name} {self.last_name} {self.address}'


class Position(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='positions',
        verbose_name='заказ'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='positions',
        verbose_name='товар'
    )

    quantity = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(25)
        ],
        verbose_name='количество'
    )

    cost = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[
            MinValueValidator(0)
        ],
        verbose_name='стоимость позиции'
    )
