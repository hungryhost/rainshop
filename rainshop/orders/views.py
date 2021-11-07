# Create your views here.
from django.db import transaction
from django.http import Http404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status, decorators
from rest_framework import permissions
from rest_framework.response import Response

from .permissions import OrderOwner
from .models import Order
from .serializers import OrderSerializer, OrderCreateSerializer


class OrderListCreateView(generics.ListCreateAPIView):
	# filter_backends = (filters.DjangoFilterBackend, drf_filters.SearchFilter)
	# filterset_class = TeamFilters
	# search_fields = ['title', '=game__name']

	def get_queryset(self):
		if getattr(self, "swagger_fake_view", False):
			return Order.objects.none()
		if self.request is None:
			return Order.objects.none()
		return Order.objects.filter(
			user=self.request.user
		).prefetch_related('items')

	@swagger_auto_schema(
		tags=['Order'],
		operation_summary='List orders',
		operation_id='get_orders',

	)
	def get(self, request, *args, **kwargs):
		return self.list(request, *args, **kwargs)

	def perform_create(self, serializer):
		return serializer.save()

	@swagger_auto_schema(
		operation_id='create_order',
		operation_summary='Create a new order',
		tags=['Order'],
		responses={
			201: OrderSerializer,
		},
	)
	def post(self, request, *args, **kwargs):
		return self.create(request, *args, **kwargs)

	def get_serializer_class(self):
		if self.request.method == 'POST':
			return OrderCreateSerializer
		return OrderSerializer

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


class OrderRetrieveDestroyView(generics.RetrieveDestroyAPIView):
	queryset = Order.objects.all()
	serializer_class = OrderSerializer
	permission_classes = [permissions.IsAuthenticated]
	http_method_names = ['get', 'delete', 'head', 'options', 'trace']

	@swagger_auto_schema(
		operation_id='retrieve_order',
		operation_summary='Get a single order',
		tags=['Order'],
	)
	def get(self, request, *args, **kwargs):
		return self.retrieve(request, *args, **kwargs)

	@swagger_auto_schema(
		operation_id='cancel_order',
		operation_summary='Cancel order',
		tags=['Order'],
	)
	def delete(self, request, *args, **kwargs):
		return self.destroy(request, *args, **kwargs)

	def get_serializer_class(self):
		return OrderSerializer

	def destroy(self, request, *args, **kwargs):
		instance = self.get_object()
		if instance.status == 'RETURNED':
			return Response(status=status.HTTP_400_BAD_REQUEST)
		self.perform_destroy(instance)
		return Response(status=status.HTTP_204_NO_CONTENT)

	def perform_destroy(self, instance):
		order_items = instance.items.all().select_related('product')
		for order_item in order_items:
			order_item.product.quantity += order_item.quantity
		with transaction.atomic():
			for order_item in order_items:
				order_item.product.save()
			instance.status = 'CANCELLED'
			instance.save()

	def get_permissions(self):
		"""
		Instantiates and returns the list of permissions that this view requires.
		"""
		if self.request.method == 'GET':
			permission_classes = []
		else:
			permission_classes = [permissions.IsAuthenticated & OrderOwner]
		return [permission() for permission in permission_classes]


class OrderReturnView(generics.DestroyAPIView):
	queryset = Order.objects.all()
	serializer_class = OrderSerializer
	permission_classes = [permissions.IsAuthenticated]
	http_method_names = ['delete', 'head', 'options', 'trace']

	@swagger_auto_schema(
		operation_id='return_order',
		operation_summary='Return order',
		tags=['Order'],
	)
	def delete(self, request, *args, **kwargs):
		return self.destroy(request, *args, **kwargs)

	def get_serializer_class(self):
		return OrderSerializer

	def destroy(self, request, *args, **kwargs):
		instance = self.get_object()
		if instance.status == 'CANCELLED':
			return Response(status=status.HTTP_400_BAD_REQUEST)
		self.perform_destroy(instance)
		return Response(status=status.HTTP_204_NO_CONTENT)

	def perform_destroy(self, instance):
		order_items = instance.items.all().select_related('product')
		for order_item in order_items:
			order_item.product.quantity += order_item.quantity
		with transaction.atomic():
			for order_item in order_items:
				order_item.product.save()
			instance.status = 'RETURNED'
			instance.save()

	def get_permissions(self):
		"""
		Instantiates and returns the list of permissions that this view requires.
		"""
		if self.request.method == 'GET':
			permission_classes = []
		else:
			permission_classes = [permissions.IsAuthenticated & OrderOwner]
		return [permission() for permission in permission_classes]


@swagger_auto_schema(
	method='get',
	operation_description='Dummy callback for payment. Only works with orders with "CREATED" status.',
	responses={200: OrderSerializer},
	operation_summary='Dummy callback for payment',
	operation_id='callback',
	tags=['Order'],

)
@decorators.api_view(["GET"])
@decorators.permission_classes([permissions.AllowAny])
def payment_callback(request, pk=None):
	try:
		order = Order.objects.get(id=pk, status='CREATED')
	except Order.DoesNotExist:
		return Response({"Invalid or non-existent order"}, status.HTTP_400_BAD_REQUEST)
	order.status = 'PAYED'
	order.save()
	context = {
		'request': request
	}
	return Response(OrderSerializer(order, context=context).data,
					status.HTTP_400_BAD_REQUEST)
