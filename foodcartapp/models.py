from phonenumber_field.modelfields import PhoneNumberField

from django.db import models
from django.db.models import F, OuterRef, Subquery, Sum
from django.core.validators import MinValueValidator, MaxValueValidator


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
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
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
    def all_cost(self):
        positions = Position.objects.filter (
            order=OuterRef('pk')
        ).all_cost().order_by().values('order')

        order_cost = positions.annotate(total=Sum('cost')).values('total')
        
        return self.annotate(cost=Subquery(order_cost))


class Order(models.Model):
    address = models.CharField (
        max_length=150,
        verbose_name='адрес'
    )

    first_name = models.CharField (
        max_length=50,
        verbose_name='имя'
    )

    last_name = models.CharField (
        max_length=50,
        verbose_name='фамилия'
    )

    phonenumber = PhoneNumberField (
        db_index=True,
        verbose_name='контактный телефон'
    )

    products = models.ManyToManyField (
        Product,
        related_name='orders',
        verbose_name='товары',
        through='Position'
    )

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f'{self.first_name} {self.last_name} {self.address}'


class PositionQuerySet(models.QuerySet):
    def all_cost(self):
        return self.annotate(cost=F('product__price') * F('quantity'))


class Position(models.Model):
    order = models.ForeignKey (
        Order,
        on_delete=models.CASCADE,
        related_name='positions',
        verbose_name='заказ'
    )

    product = models.ForeignKey (
        Product,
        on_delete=models.CASCADE,
        related_name='positions',
        verbose_name='товар'
    )

    quantity = models.IntegerField (
        validators=[
            MinValueValidator(1),
            MaxValueValidator(25)
        ],
        verbose_name='количество'
    )

    objects = PositionQuerySet.as_manager()
