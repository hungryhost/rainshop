from django.conf import settings
from django.db import models
from products.models import Product
from djmoney.models.fields import MoneyField


class Cart(models.Model):
	class Meta:
		db_table = 'carts'
		verbose_name_plural = 'Carts'
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		related_name='carts',
		on_delete=models.CASCADE,
	)
	product = models.ForeignKey(
		Product,
		on_delete=models.CASCADE
	)
	quantity = models.IntegerField(default=1, blank=False, null=False)
	created_at = models.DateTimeField(auto_now_add=True, editable=False)
	updated_at = models.DateTimeField(auto_now=True, editable=False)

