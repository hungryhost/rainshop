from . import views
from django.urls import path

app_name = 'cart'
urlpatterns = [
	path('', views.CartListCreateView.as_view(), name='cart-list-create'),
	path('<int:pk>/', views.CartItemRetrieveUpdateRemoveView.as_view(), name='cart-detail'),

]