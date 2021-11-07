from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers
from rest_framework.reverse import reverse
from .models import Order, OrderItem
from djmoney.contrib.django_rest_framework import MoneyField
from products.serializers import ProductSerializer
from products.models import Product
from rainshop.custom_drf_errors import CustomError
from cart.models import Cart


class OrderItemSerializer(serializers.ModelSerializer):
	class Meta:
		model = OrderItem
		fields = [
			'id',
			'product_id',
			'product_name',
			'product_price',
			'product_final_price',
			'quantity'

		]


class OrderSerializer(serializers.ModelSerializer):
	items = serializers.SerializerMethodField('get_items')
	self = serializers.SerializerMethodField('get_self')

	class Meta:
		model = Order
		fields = [
			'id',
			'status',
			'items',
			'order_price',
			'created_at',
			'updated_at',
			'self'
		]

	@swagger_serializer_method(serializer_or_field=serializers.URLField())
	def get_self(self, obj):
		return reverse('orders:order-detail', request=self.context['request'],
					   args=(obj.id,))

	@swagger_serializer_method(serializer_or_field=OrderItemSerializer(many=True))
	def get_items(self, obj):
		return OrderItemSerializer(
			obj.items.all(), many=True
		).data


class OrderCreateSerializer(serializers.ModelSerializer):
	items = serializers.SerializerMethodField('get_items')
	status = serializers.CharField(read_only=True)
	order_price = MoneyField(read_only=True, max_digits=10, decimal_places=2)

	class Meta:
		model = Order
		fields = [
			'id',
			'status',
			'items',
			'order_price'
		]

	@swagger_serializer_method(serializer_or_field=OrderItemSerializer(many=True))
	def get_items(self, obj):
		return OrderItemSerializer(
			obj.items.all(), many=True
		).data

	def validate(self, attrs):
		cart_objects = Cart.objects.filter(
			user=self.context['request'].user
		).select_related('product')
		if len(cart_objects) == 0:
			raise CustomError(
				detail='Empty Cart.',
				status_code=400,
				field='cart'
			)

		for cart_object in cart_objects:
			if cart_object.product.quantity < cart_object.quantity:
				raise CustomError(
					detail=f'Not enough product left. Remaining at the moment: {cart_object.product.quantity}',
					status_code=400,
					field='quantity'
				)
		self.context['cart_objects'] = cart_objects
		return attrs

	def create(self, validated_data):
		cart_objects = self.context['cart_objects']
		order_items = []
		order = Order(
			user=self.context['request'].user
		)
		order_price = 0.0
		for cart_object in cart_objects:
			new_order_item = OrderItem(
				order=order,
				product=cart_object.product,
				product_name=cart_object.product.name,
				product_price=cart_object.product.price,
				product_final_price=cart_object.product.price * cart_object.quantity,
				quantity=cart_object.quantity
			)
			order_price += cart_object.product.price * cart_object.quantity
			cart_object.product.quantity = cart_object.product.quantity - cart_object.quantity
			order_items.append(new_order_item)
		order.order_price = order_price
		try:
			with transaction.atomic():
				order.save()
				OrderItem.objects.bulk_create(
					order_items
				)
				for cart_object in cart_objects:
					cart_object.product.save()
				cart_objects.delete()
		except Exception as e:
			raise CustomError(
				status_code=400,
				detail='order not created due to related errors: {}'.format(e),
				field='order')
		return order


