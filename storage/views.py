from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Stock

class StockListView(ListView):
    model = Stock
    template_name = 'storage/stock_list.html'
    context_object_name = 'stocks'

class StockDetailView(DetailView):
    model = Stock
    template_name = 'storage/stock_detail.html'

class StockUpdateView(UpdateView):
    model = Stock
    template_name = 'storage/stock_form.html'
    fields = ['stock_num', 'warehouse', 'avg_cost', 'sku']

class StockDeleteView(DeleteView):
    model = Stock
    success_url = reverse_lazy('storage:stock-list')
