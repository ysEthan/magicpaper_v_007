from django.urls import path
from . import views

app_name = 'storage'

urlpatterns = [
    path('stocks/', views.StockListView.as_view(), name='stock-list'),
    path('stocks/<int:pk>/', views.StockDetailView.as_view(), name='stock-detail'),
    path('stocks/<int:pk>/update/', views.StockUpdateView.as_view(), name='stock-update'),
    path('stocks/<int:pk>/delete/', views.StockDeleteView.as_view(), name='stock-delete'),
] 