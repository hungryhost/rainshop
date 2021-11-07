from . import views
from django.urls import path

app_name = 'orders'
urlpatterns = [
	path('', views.OrderListCreateView.as_view(), name='order-list-create'),
	path('<int:pk>/return/', views.OrderReturnView.as_view(), name='order-return'),
	path('<int:pk>/', views.OrderRetrieveDestroyView.as_view(), name='order-detail'),
	path('<int:pk>/payment-callback/', views.payment_callback, name='order-payment-callback'),


]