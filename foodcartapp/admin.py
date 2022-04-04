from django.contrib import admin
from django.shortcuts import reverse, redirect
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.encoding import iri_to_uri
from django.utils.http import url_has_allowed_host_and_scheme

from geocoder.models import Coordinates
from geocoder.utils import add_coordinates
from .models import Product
from .models import ProductCategory
from .models import Restaurant
from .models import RestaurantMenuItem
from .models import Order
from .models import Position


class RestaurantMenuItemInline(admin.TabularInline):
    model = RestaurantMenuItem
    extra = 0


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    search_fields = [
        'name',
        'address',
        'contact_phone',
    ]
    list_display = [
        'name',
        'address',
        'contact_phone',
    ]
    inlines = [
        RestaurantMenuItemInline
    ]

    def save_model(self, request, obj, form, change):
        if not Coordinates.objects.filter(address=obj.address).exists():
            add_coordinates(obj.address)

        super().save_model(request, obj, form, change)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'get_image_list_preview',
        'name',
        'category',
        'price',
    ]

    list_display_links = [
        'name',
    ]

    list_filter = [
        'category',
    ]

    search_fields = [
        'name',
        'category__name',
    ]

    inlines = [
        RestaurantMenuItemInline
    ]

    fieldsets = (
        ('Общее', {
            'fields': [
                'name',
                'category',
                'image',
                'get_image_preview',
                'price',
            ]
        }),
        ('Подробно', {
            'fields': [
                'special_status',
                'description',
            ],
            'classes': [
                'wide'
            ],
        }),
    )

    readonly_fields = [
        'get_image_preview',
    ]

    class Media:
        css = {
            "all": (
                static("admin/foodcartapp.css")
            )
        }

    def get_image_preview(self, obj):
        if not obj.image:
            return 'выберите картинку'

        return format_html(
            '<img src="{url}" style="max-height: 200px;"/>',
            url=obj.image.url
        )

    get_image_preview.short_description = 'превью'

    def get_image_list_preview(self, obj):
        if not obj.image or not obj.id:
            return 'нет картинки'

        edit_url = reverse('admin:foodcartapp_product_change', args=(obj.id,))

        return format_html(
            '<a href="{edit_url}"><img src="{src}"'
            'style="max-height: 50px;"/></a>',
            edit_url=edit_url,
            src=obj.image.url
        )

    get_image_list_preview.short_description = 'превью'


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    pass


class OrderPositionInline(admin.TabularInline):
    model = Position


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [
        OrderPositionInline
    ]

    def response_post_save_change(self, request, obj):
        if not Coordinates.objects.filter(address=obj.address).exists():
            add_coordinates(obj.address)

        if 'next' not in request.GET:
            return super().response_post_save_change(request, obj)

        elif url_has_allowed_host_and_scheme(request.GET['next'], None):
            url = iri_to_uri(request.GET['next'])
            return redirect(url)

        else:
            raise
