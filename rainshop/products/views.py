import datetime

from django.db.models import Count, Q, Sum
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, decorators, status
from rest_framework.response import Response

from orders.models import Order
from .models import Product
from .serializers import ProductSerializer, ProductUpdateSerializer


class ProductListCreateView(generics.ListCreateAPIView):

	def get_queryset(self):
		if getattr(self, "swagger_fake_view", False):
			return Product.objects.none()
		if self.request is None:
			return Product.objects.none()
		return Product.objects.all()

	@swagger_auto_schema(
		tags=['Products'],
		operation_summary='List products',
		operation_id='get_products_list',

	)
	def get(self, request, *args, **kwargs):
		return self.list(request, *args, **kwargs)

	@swagger_auto_schema(
		request_body=ProductSerializer,
		operation_id='create_product',
		operation_summary='Create a product',
		tags=['Products'],
	)
	def post(self, request, *args, **kwargs):
		return self.create(request, *args, **kwargs)

	def get_serializer_class(self):
		return ProductSerializer

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
		if self.request.method == 'GET':
			permission_classes = []
		else:
			permission_classes = [permissions.IsAuthenticated]
		return [permission() for permission in permission_classes]


class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
	queryset = Product.objects.all()
	serializer_class = ProductSerializer
	permission_classes = [permissions.IsAuthenticated]
	http_method_names = ['get', 'put', 'delete', 'head', 'options', 'trace']

	@swagger_auto_schema(
		operation_id='retrieve_product',
		operation_summary='Get a single product',
		tags=['Products'],
	)
	def get(self, request, *args, **kwargs):
		return self.retrieve(request, *args, **kwargs)

	@swagger_auto_schema(
		operation_id='update_product',
		operation_summary='Update a product',
		tags=['Products'],
	)
	def put(self, request, *args, **kwargs):
		return self.update(request, *args, **kwargs)

	@swagger_auto_schema(
		operation_id='remove_product',
		operation_summary='Remove a product',
		tags=['Products'],
	)
	def delete(self, request, *args, **kwargs):
		return self.destroy(request, *args, **kwargs)

	def get_serializer_class(self):
		if self.request.method == "PUT":
			return ProductUpdateSerializer
		return ProductSerializer

	def get_permissions(self):
		"""
		Instantiates and returns the list of permissions that this view requires.
		"""
		if self.request.method == 'GET':
			permission_classes = []
		else:
			permission_classes = [permissions.IsAuthenticated]
		return [permission() for permission in permission_classes]


@swagger_auto_schema(
	method='get',
	operation_description='Get stats for each product',
	operation_summary='Get stats for each product',
	operation_id='stats',
	tags=['Stats'],
	manual_parameters=[
		openapi.Parameter(
			'start_date',
			in_=openapi.IN_QUERY,
			description='Start date for the report.',
			type=openapi.FORMAT_DATE),
		openapi.Parameter(
			'end_date',
			in_=openapi.IN_QUERY,
			description='End date for the report.',
			type=openapi.FORMAT_DATE),
	],
	responses={200: openapi.Schema(
		type=openapi.TYPE_OBJECT,
		properties={
			'total_ordered'           : openapi.Schema(
				type=openapi.TYPE_OBJECT
			),
			'orders_by_status'        : openapi.Schema(
				type=openapi.TYPE_OBJECT
			),
			'orders_by_monetary_stats': openapi.Schema(
				type=openapi.TYPE_OBJECT
			),
		}
	)}
)
@decorators.api_view(["GET"])
@decorators.permission_classes([permissions.AllowAny])
def stats(request):
	start_date = request.GET.get('start_date', None)
	end_date = request.GET.get('end_date', None)
	try:
		d_start = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
		d_end = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
		date_filter = Q(order_items__order__created_at__gte=d_start,
						order_items__order__created_at__lte=d_end)
	except Exception:
		date_filter = None

	total_ordered = Sum('order_items__quantity')
	total_returned = Sum('order_items__quantity', filter=Q(order_items__order__status__in=['RETURNED', 'CANCELLED']))

	total_created = Count('id', filter=Q(status='CREATED'))
	total_all_statuses = Count('id')
	total_cancelled = Count('id', filter=Q(status='CANCELLED'))
	total_payed = Count('id', filter=Q(status='PAYED'))
	total_returned_orders = Count('id', filter=Q(status='RETURNED'))

	total_gross_income = Sum(
		'order_items__order__order_price',
		filter=Q(order_items__order__status__in=['PAYED'])
	)
	total_cost = Sum(
		'order_items__product__cost',
		filter=Q(order_items__order__status__in=['PAYED'])
	)
	if date_filter:
		products = Product.objects.prefetch_related(
			'order_items', 'order_items__order'
		).filter(date_filter).annotate(
			total_ordered=total_ordered,
			total_returned=total_returned,
			total_gross_income=total_gross_income,
			total_cost=total_cost
		)
		orders = Order.objects.filter(date_filter).aggregate(
			total_created=total_created,
			total_cancelled=total_cancelled,
			total_payed=total_payed,
			total_all_statuses=total_all_statuses,
			total_returned_orders=total_returned_orders
		)
	else:
		products = Product.objects.prefetch_related(
			'order_items', 'order_items__order'
		).annotate(
			total_ordered=total_ordered,
			total_returned=total_returned,
			total_gross_income=total_gross_income,
			total_cost=total_cost
		)
		orders = Order.objects.aggregate(
			total_created=total_created,
			total_cancelled=total_cancelled,
			total_payed=total_payed,
			total_all_statuses=total_all_statuses,
			total_returned_orders=total_returned_orders
		)
	total_ordered_data = {}
	total_returned_data = {}
	total_gross_income_data = {}
	total_cost_data = {}
	total_clean_income = {}

	for product in products:
		total_ordered_data[product.name] = product.total_ordered
		total_returned_data[product.name] = product.total_returned
		total_gross_income_data[product.name] = product.total_gross_income
		total_cost_data[product.name] = product.total_cost
		if product.total_cost is not None and product.total_gross_income is not None:
			total_clean_income[product.name] = product.total_gross_income - product.total_cost
		if product.total_gross_income is None:
			total_clean_income[product.name] = None

	res = {
		'total_orders': orders['total_all_statuses'],
		'total_ordered': total_ordered_data,
		'total_returned': total_returned_data,
		'orders_by_status': {
			'total_created': orders['total_created'],
			'total_returned': orders['total_returned_orders'],
			'total_cancelled': orders['total_cancelled'],
			'total_payed': orders['total_payed'],
		},
		'orders_by_monetary_stats': {
			'total_gross_income': total_gross_income_data,
			'total_cost': total_cost_data,
			'total_income': total_clean_income
		}
	}
	return Response(res, status.HTTP_200_OK)
