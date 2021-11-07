# Create your views here.
from django.db import transaction
from django.http import Http404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework import permissions
from rest_framework.response import Response

from .models import Cart
from .serializers import CartSerializer, AddToCartSerializer, CartUpdateSerializer


class CartListCreateView(generics.ListCreateAPIView):

	def get_queryset(self):
		if getattr(self, "swagger_fake_view", False):
			return Cart.objects.none()
		if self.request is None:
			return Cart.objects.none()
		return Cart.objects.filter(
			user=self.request.user
		).select_related('product')

	@swagger_auto_schema(
		tags=['Cart'],
		operation_summary='List cart products',
		operation_id='get_cart',

	)
	def get(self, request, *args, **kwargs):
		return self.list(request, *args, **kwargs)

	def create(self, request, *args, **kwargs):

		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		cart_object = self.perform_create(serializer)
		return_serializer = CartSerializer(
			cart_object, context=self.get_serializer_context())
		headers = self.get_success_headers(return_serializer.data)
		return Response(return_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

	def perform_create(self, serializer):
		return serializer.save()

	@swagger_auto_schema(
		request_body=AddToCartSerializer,
		operation_id='add_to_cart',
		operation_summary='Add a product to the cart',
		tags=['Cart'],
		responses={
			201: CartSerializer,
		},
	)
	def post(self, request, *args, **kwargs):
		return self.create(request, *args, **kwargs)

	def get_serializer_class(self):
		if self.request.method == 'POST':
			return AddToCartSerializer
		return CartSerializer

	def get_serializer_context(self):
		return {
			'request': self.request,
			'format' : self.format_kwarg,
			'view'   : self
		}

	def get_permissions(self):
		"""
		Instantiates and returns the list of permissions that this view requires.
		"""
		permission_classes = [permissions.IsAuthenticated]
		return [permission() for permission in permission_classes]


class CartItemRetrieveUpdateRemoveView(generics.RetrieveUpdateDestroyAPIView):
	queryset = Cart.objects.all()
	serializer_class = CartSerializer
	permission_classes = [permissions.IsAuthenticated]
	http_method_names = ['get', 'put', 'delete', 'head', 'options', 'trace']

	@swagger_auto_schema(
		operation_id='retrieve_cart_item',
		operation_summary='Get a single cart item',
		tags=['Cart'],
	)
	def get(self, request, *args, **kwargs):
		return self.retrieve(request, *args, **kwargs)

	@swagger_auto_schema(
		request_body=openapi.Schema(
			type=openapi.TYPE_OBJECT,
			properties={
				'quantity': openapi.Schema(
					type=openapi.TYPE_NUMBER
				)
			}
		),
		operation_id='update_cart_item',
		operation_summary='Update a cart item',
		tags=['Cart'],
		responses={
			200: CartSerializer,
		},
	)
	def put(self, request, *args, **kwargs):
		return self.update(request, *args, **kwargs)

	@swagger_auto_schema(
		operation_id='remove_cart_item',
		operation_summary='Remove a cart item',
		tags=['Cart'],
	)
	def delete(self, request, *args, **kwargs):
		return self.destroy(request, *args, **kwargs)

	def get_serializer_class(self):
		if self.request.method == "PUT":
			return CartUpdateSerializer
		return CartSerializer

	def get_permissions(self):
		"""
		Instantiates and returns the list of permissions that this view requires.
		"""
		if self.request.method == 'GET':
			permission_classes = []
		else:
			permission_classes = [permissions.IsAuthenticated]
		return [permission() for permission in permission_classes]
