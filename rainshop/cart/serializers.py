from rest_framework import serializers
from rest_framework.reverse import reverse

from products.models import Product
from products.serializers import ProductShortSerializer
from rainshop.custom_drf_errors import CustomError
from .models import Cart


class CartSerializer(serializers.ModelSerializer):
	product = ProductShortSerializer(many=False)
	max_quantity = serializers.SerializerMethodField('get_max_quantity')
	is_available_as_selected = serializers.SerializerMethodField('get_is_available_as_selected')
	self = serializers.SerializerMethodField('get_self_link')
	total_price = serializers.SerializerMethodField('get_total_price')

	class Meta:
		model = Cart
		fields = [
			'id',
			'product',
			'quantity',
			'max_quantity',
			'is_available_as_selected',
			'total_price',
			'self'
		]

	def get_is_available_as_selected(self, obj):
		if obj.product.quantity >= obj.quantity:
			return True
		else:
			return False

	def get_total_price(self, obj):
		return str((obj.quantity * obj.product.price).amount)

	def get_max_quantity(self, obj):
		return obj.product.quantity

	def get_self_link(self, obj):
		return reverse('cart:cart-detail', request=self.context['request'],
					   args=(obj.id,))


class AddToCartSerializer(serializers.ModelSerializer):
	product_id = serializers.IntegerField(required=True, min_value=1)
	quantity = serializers.IntegerField(required=True, min_value=1, max_value=999)

	class Meta:
		model = Cart
		fields = [
			'product_id',
			'quantity',
		]

	def validate(self, attrs):
		try:
			cart_object = Cart.objects.get(
				user=self.context['request'].user,
				product_id=attrs['product_id']
			)
			attrs['quantity'] = attrs['quantity'] + cart_object.quantity
			self.context['cart'] = cart_object
		except Cart.DoesNotExist:
			self.context['cart'] = None
		try:
			target_product = Product.objects.get(id=attrs['product_id'])
		except Product.DoesNotExist:
			raise CustomError(
				detail='Product does not exist',
				status_code=404,
				field='product_id'
			)
		if target_product.quantity < attrs['quantity']:
			raise CustomError(
				detail=f'Not enough product left. Remaining at the moment: {target_product.quantity}',
				status_code=400,
				field='quantity'
			)
		return attrs

	def create(self, validated_data):
		if self.context['cart'] is not None:
			cart_object = self.context['cart']
			cart_object.quantity = validated_data['quantity']
		else:
			cart_object = Cart(
				user=self.context['request'].user,
				product_id=validated_data['product_id'],
				quantity=validated_data['quantity']
			)
		cart_object.save()
		return cart_object


class CartUpdateSerializer(serializers.ModelSerializer):
	product = ProductShortSerializer(many=False, read_only=True)
	max_quantity = serializers.SerializerMethodField('get_max_quantity')
	is_available_as_selected = serializers.SerializerMethodField('get_is_available_as_selected')

	class Meta:
		model = Cart
		fields = [
			'id',
			'product',
			'quantity',
			'max_quantity',
			'is_available_as_selected',
		]
		read_only_fields = [
			'id',
			'product',
			'max_quantity',
			'is_available_as_selected',
		]

	def get_is_available_as_selected(self, obj):
		if obj.product.quantity >= obj.quantity:
			return True
		else:
			return False

	def get_max_quantity(self, obj):
		return obj.product.quantity
