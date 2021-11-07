from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers
from rest_framework.reverse import reverse
from .models import Product
from djmoney.contrib.django_rest_framework import MoneyField


class ProductShortSerializer(serializers.ModelSerializer):
	name = serializers.CharField(required=True, max_length=255)
	price = MoneyField(required=True, max_digits=10, decimal_places=2)
	self = serializers.SerializerMethodField('get_self_link')

	class Meta:
		model = Product
		fields = [
			'id',
			'name',
			'price',
			'self'
		]

	def get_self_link(self, obj):
		return reverse('products:product-detail', request=self.context['request'],
					   args=(obj.id,))


class ProductSerializer(serializers.ModelSerializer):
	name = serializers.CharField(required=True, max_length=255)
	cost = MoneyField(required=True, max_digits=10, decimal_places=2)
	price = MoneyField(required=True, max_digits=10, decimal_places=2)
	quantity = serializers.IntegerField(required=True)
	cost_currency = serializers.CharField(read_only=True)
	price_currency = serializers.CharField(read_only=True)
	self = serializers.SerializerMethodField('get_self_link')

	class Meta:
		model = Product
		fields = [
			'id',
			'name',
			'cost',
			'price',
			'quantity',
			'cost_currency',
			'price_currency',
			'self'
		]

	def get_self_link(self, obj):
		return reverse('products:product-detail', request=self.context['request'],
					   args=(obj.id,))


class ProductUpdateSerializer(serializers.ModelSerializer):
	name = serializers.CharField(read_only=True, max_length=255)
	cost = MoneyField(required=False, max_digits=10, decimal_places=2)
	price = MoneyField(required=False, max_digits=10, decimal_places=2)
	quantity = serializers.IntegerField(required=False)
	cost_currency = serializers.CharField(read_only=True)
	price_currency = serializers.CharField(read_only=True)
	self = serializers.SerializerMethodField('get_self_link')

	class Meta:
		model = Product
		fields = [
			'id',
			'name',
			'cost',
			'price',
			'quantity',
			'cost_currency',
			'price_currency',
			'self'
		]
		read_only_fields = [
			'id',
			'name',
			'cost_currency',
			'price_currency',
			'self'
		]

	def get_self_link(self, obj):
		return reverse('products:product-detail', request=self.context['request'],
					   args=(obj.id,))


class ProductStatsSerializer(serializers.Serializer):
	total_ordered = serializers.SerializerMethodField('get_ordered')
	orders_by_status = serializers.SerializerMethodField('get_returned')
	orders_by_monetary_stats = serializers.SerializerMethodField('get_total_billed')

	class Meta:
		fields = [
			'total_ordered',
			'orders_by_status',
			'orders_by_monetary_stats'
		]
