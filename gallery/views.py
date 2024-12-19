from django.shortcuts import render
from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from .models import Category, SPU, SKU
from .forms import CategoryForm, SPUForm, SKUForm
from django.views import View
from .sync import ProductSync

# Create your views here.

class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'gallery/category_list.html'
    context_object_name = 'categories'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Category.objects.all()
        # 添加搜索功能
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                category_name_zh__icontains=search_query
            ) | queryset.filter(
                category_name_en__icontains=search_query
            )
        return queryset.order_by('rank_id', 'id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context

class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'gallery/category_form.html'
    success_url = reverse_lazy('gallery:category_list')

    def form_valid(self, form):
        messages.success(self.request, '类目创建成功！')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '类目创建失败，请检查输入！')
        return super().form_invalid(form)

class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    success_url = reverse_lazy('gallery:category_list')
    template_name = 'gallery/category_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        try:
            result = super().delete(request, *args, **kwargs)
            messages.success(request, '类目删除成功！')
            return result
        except Exception as e:
            messages.error(request, f'删除失败：{str(e)}')
            return redirect('gallery:category_list')

class SPUListView(LoginRequiredMixin, ListView):
    model = SPU
    template_name = 'gallery/spu_list.html'
    context_object_name = 'spus'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = SPU.objects.select_related('category').all()
        # 添加搜索功能
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                spu_name__icontains=search_query
            ) | queryset.filter(
                spu_code__icontains=search_query
            )
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context

class SPUCreateView(LoginRequiredMixin, CreateView):
    model = SPU
    form_class = SPUForm
    template_name = 'gallery/spu_form.html'
    success_url = reverse_lazy('gallery:spu_list')

    def form_valid(self, form):
        messages.success(self.request, 'SPU创建成功！')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'SPU创建失败，请检查输入！')
        return super().form_invalid(form)

class SPUDeleteView(LoginRequiredMixin, DeleteView):
    model = SPU
    success_url = reverse_lazy('gallery:spu_list')
    template_name = 'gallery/spu_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        try:
            result = super().delete(request, *args, **kwargs)
            messages.success(request, 'SPU删除成功！')
            return result
        except Exception as e:
            messages.error(request, f'删除失败：{str(e)}')
            return redirect('gallery:spu_list')

class SPUUpdateView(LoginRequiredMixin, UpdateView):
    model = SPU
    form_class = SPUForm
    template_name = 'gallery/spu_form.html'
    success_url = reverse_lazy('gallery:spu_list')

    def form_valid(self, form):
        messages.success(self.request, 'SPU更新成功！')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'SPU更新失败，请检查输入！')
        return super().form_invalid(form)

class SKUListView(LoginRequiredMixin, ListView):
    model = SKU
    template_name = 'gallery/sku_list.html'
    context_object_name = 'skus'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = SKU.objects.select_related('spu', 'spu__category').all()
        
        # 添加类目筛选
        category_id = self.request.GET.get('category')
        if category_id:
            try:
                queryset = queryset.filter(spu__category_id=category_id)
            except ValueError:
                pass

        # 添加搜索功能
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                sku_name__icontains=search_query
            ) | queryset.filter(
                sku_code__icontains=search_query
            )

        # 获取筛选参数
        selected_color = self.request.GET.get('color', '')
        selected_material = self.request.GET.get('material', '')
        selected_plating = self.request.GET.get('plating', '')
        
        # 应用筛选
        if selected_color:
            queryset = queryset.filter(color=selected_color)
        if selected_material:
            queryset = queryset.filter(material=selected_material)
        if selected_plating:
            queryset = queryset.filter(plating_process=selected_plating)
        
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 获取所有不重复的选项
        colors = SKU.objects.values_list('color', flat=True).distinct().order_by('color')
        materials = SKU.objects.values_list('material', flat=True).distinct().order_by('material')
        platings = SKU.objects.values_list('plating_process', flat=True).distinct().order_by('plating_process')
        
        # 添加类目列表到上下文
        categories = Category.objects.filter(
            spus__skus__isnull=False
        ).distinct().order_by('category_name_en')
        
        # 获取当前选中的类目ID
        try:
            category_id = int(self.request.GET.get('category', ''))
        except (ValueError, TypeError):
            category_id = None
            
        context.update({
            'categories': categories,
            'colors': colors,
            'materials': materials,
            'platings': platings,
            'category_id': category_id,
            'selected_color': self.request.GET.get('color', ''),
            'selected_material': self.request.GET.get('material', ''),
            'selected_plating': self.request.GET.get('plating', ''),
            'search_query': self.request.GET.get('search', ''),
        })
        
        return context

class SKUUpdateView(LoginRequiredMixin, UpdateView):
    model = SKU
    form_class = SKUForm
    template_name = 'gallery/sku_form.html'
    success_url = reverse_lazy('gallery:sku_list')

    def form_valid(self, form):
        messages.success(self.request, 'SKU更新成功！')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'SKU更新失败，请检查输入！')
        return super().form_invalid(form)

class SKUDeleteView(LoginRequiredMixin, DeleteView):
    model = SKU
    success_url = reverse_lazy('gallery:sku_list')
    template_name = 'gallery/sku_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        try:
            result = super().delete(request, *args, **kwargs)
            messages.success(request, 'SKU删除成功！')
            return result
        except Exception as e:
            messages.error(request, f'删除失败：{str(e)}')
            return redirect('gallery:sku_list')

class SKUCreateView(LoginRequiredMixin, CreateView):
    model = SKU
    form_class = SKUForm
    template_name = 'gallery/sku_form.html'
    success_url = reverse_lazy('gallery:sku_list')

    def dispatch(self, request, *args, **kwargs):
        spu_id = request.GET.get('spu')
        if not spu_id:
            messages.error(request, '请从SPU详情页添加SKU')
            return redirect('gallery:spu_list')
        try:
            self.spu = SPU.objects.get(id=spu_id)
        except SPU.DoesNotExist:
            messages.error(request, 'SPU不存在！')
            return redirect('gallery:spu_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.spu = self.spu
        messages.success(self.request, 'SKU创建成功！')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'SKU创建失败，请检查输入！')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['spu'] = self.spu
        return context

class SKUSyncView(LoginRequiredMixin, View):
    def get(self, request):
        try:
            sync = ProductSync()
            count = sync.sync_products()
            sync.clean_old_images()  # 清理旧图片
            messages.success(request, f'成功同步 {count} 条数据')
        except Exception as e:
            messages.error(request, f'同步失败：{str(e)}')
        return redirect('gallery:sku_list')
