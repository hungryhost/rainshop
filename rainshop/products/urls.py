from . import views
from django.urls import path

app_name = 'products'
urlpatterns = [
	path('', views.ProductListCreateView.as_view(), name='products-list-create'),
	path('<int:pk>/', views.ProductRetrieveUpdateDestroyView.as_view(), name='product-detail'),
	path('stats/', views.stats, name='product-stats'),

]