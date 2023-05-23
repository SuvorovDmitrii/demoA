from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _
from .validator import LoginValidator, NameValidator

class User(AbstractUser):
    username = models.CharField('Логин', max_length=150, unique=True,
                                help_text='Обязательное поле. Только латиница, цифры и тире.',
                                validators=[LoginValidator()],
                                error_messages={'unique': _('Пользователь с таким именем уже существует')})
    first_name = models.CharField(_('first name'), max_length=150, validators=[NameValidator()])
    last_name = models.CharField(_('last name'), max_length=150, validators=[NameValidator()])
    patronymic = models.CharField('Отчество', max_length=150, validators=[NameValidator()])

    def __str__(self):
        return '%s %s' % (self.first_name, self.last_name)

class AbstaractModel(models.Model):
    name = models.CharField(max_length=30, verbose_name='Название')
    objects = models.Manager()

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

class Category(AbstaractModel):
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

class Status(AbstaractModel):
    class Meta:
        verbose_name = 'Статус'
        verbose_name_plural = 'Статусы'

class Product(AbstaractModel):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')
    image = models.ImageField('Изображение')
    price = models.IntegerField('Цена')
    country = models.CharField(max_length=50, verbose_name='Страна производитель')
    type = models.CharField(max_length=50, verbose_name='Тип', default='Струйный')
    amount = models.IntegerField('Количество на складе')

    class Meta:
        verbose_name = 'Торвар'
        verbose_name_plural = 'Торвары'

class Cart(AbstaractModel):
    name = None
    user = models.ForeignKey('User', on_delete=models.CASCADE, verbose_name='Пользователь')
    product = models.ForeignKey('Product', on_delete=models.CASCADE, verbose_name='Товар')
    amount = models.IntegerField('Количество товаров')

    class Meta:
        verbose_name = 'Корзина'

class OrderProduct(AbstaractModel):
    name = None
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, verbose_name='Товар')
    amount = models.IntegerField(verbose_name='Количество товаров')

class Order(AbstaractModel):
    name = None
    user = models.ForeignKey('User', on_delete=models.CASCADE, verbose_name='Пользователь')
    date_create = models.DateTimeField(verbose_name='Дата заказа', auto_now_add=True)
    status = models.ForeignKey('Status', on_delete=models.CASCADE, verbose_name='Статус', default=1)
    result = models.CharField(max_length=50, verbose_name='Причина отказа')

    @property
    def amount(self):
        return OrderProduct.objects.filter(order=self.pk).aggregate(Sum('amount'))['amount__sum']

    amount.fget.short_description = 'Количество'

    @property
    def products(self):
        return OrderProduct.objects.filter(order=self.pk)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'покупатель: {self.user}, дата: {str(self.date_create).split(".")[0]}'