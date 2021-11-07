from django.conf import settings
from django.db import models
from products.models import Product
from djmoney.models.fields import MoneyField


class Order(models.Model):
	class Meta:
		db_table = 'orders'
		verbose_name_plural = 'Orders'

	STATUS_OPTIONS = [
		('PAID', 'Paid'),
		('CREATED', 'Created'),
		('CANCELLED', 'Cancelled'),
		('RETURNED', 'Returned'),

	]
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
	)
	status = models.CharField(
		choices=STATUS_OPTIONS,
		default='CREATED',
		max_length=10,
		null=False,
		blank=False
	)
	order_price = MoneyField(default=0, null=False, blank=False, default_currency='USD',
							 max_digits=10, decimal_places=2)
	created_at = models.DateTimeField(auto_now_add=True, editable=False)
	updated_at = models.DateTimeField(auto_now=True, editable=False)


class OrderItem(models.Model):
	class Meta:
		db_table = 'order_items'
		verbose_name_plural = 'Order Items'

	order = models.ForeignKey(
		Order,
		related_name='items',
		on_delete=models.CASCADE
	)
	product = models.ForeignKey(
		Product,
		related_name='order_items',
		null=True,
		on_delete=models.SET_NULL
	)
	product_name = models.CharField(null=False, blank=False, max_length=255)
	product_price = MoneyField(null=False, blank=False, default_currency='USD',
					  max_digits=10, decimal_places=2)
	product_final_price = MoneyField(default=0, null=False, blank=False, default_currency='USD',
							 max_digits=10, decimal_places=2)
	quantity = models.IntegerField(default=1, blank=False, null=False)
	created_at = models.DateTimeField(auto_now_add=True, editable=False)
	updated_at = models.DateTimeField(auto_now=True, editable=False)
