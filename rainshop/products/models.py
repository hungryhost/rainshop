from django.db import models
from djmoney.models.fields import MoneyField


class Product(models.Model):
	class Meta:
		db_table = 'products'
		verbose_name_plural = 'Products'

	name = models.CharField(null=False, blank=False, max_length=255)
	cost = MoneyField(null=False, blank=False, default_currency='USD',
							   max_digits=10, decimal_places=2)
	price = MoneyField(null=False, blank=False, default_currency='USD',
								max_digits=10, decimal_places=2)
	quantity = models.IntegerField(null=False, blank=False)

	created_at = models.DateTimeField(auto_now_add=True, editable=False)
	updated_at = models.DateTimeField(auto_now=True, editable=False)

	def __str__(self):
		return self.name
