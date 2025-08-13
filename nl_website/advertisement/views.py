from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404

from advertisement.models import Advertisement, AdvertisementCategory
from advertisement.forms import AddAdvertisementForm, UpdateAdvertisementForm


class AllAdvertisement(ListView):
    template_name = 'advertisement/advertisement_all.html'
    context_object_name = 'ads'
    paginate_by = 12
    title_page = 'Объявления'

    def get_queryset(self):
        queryset = Advertisement.objects.filter(status='published').select_related('category')
        category_slug = self.request.GET.get('category')
        if category_slug:
            self.cat_selected = AdvertisementCategory.objects.filter(slug=category_slug).first()
            if self.cat_selected:
                queryset = queryset.filter(category=self.cat_selected)
        else:
            self.cat_selected = None
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title_page if not getattr(self, 'cat_selected', None) else f"{self.title_page} — {self.cat_selected.name}"
        context['all_categories'] = AdvertisementCategory.objects.all()
        context['cat_selected'] = getattr(self, 'cat_selected', None)
        return context


class ShowAdvertisement(DetailView):
    template_name = 'advertisement/advertisement_detail.html'
    slug_url_kwarg = 'advertisement_slug'
    context_object_name = 'ad'

    def get_object(self, queryset=None):
        return get_object_or_404(Advertisement, status='published', slug=self.kwargs[self.slug_url_kwarg])


class UpdateAdvertisement(PermissionRequiredMixin, UpdateView):
    model = Advertisement
    form_class = UpdateAdvertisementForm
    template_name = 'advertisement/advertisement_form.html'
    permission_required = 'advertisement.change_advertisement'
    slug_field = 'slug'
    slug_url_kwarg = 'advertisement_slug'

    def get_success_url(self):
        return self.object.get_absolute_url()


class AddAdvertisement(LoginRequiredMixin, CreateView):
    model = Advertisement
    form_class = AddAdvertisementForm
    template_name = 'advertisement/advertisement_form.html'
    success_url = reverse_lazy('advertisement:advertisement_all')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class DeleteAdvertisement(PermissionRequiredMixin, DeleteView):
    model = Advertisement
    template_name = 'advertisement/advertisement_confirm_delete.html'
    success_url = reverse_lazy('advertisement:advertisement_all')
    permission_required = 'advertisement.delete_advertisement'
    slug_field = 'slug'
    slug_url_kwarg = 'advertisement_slug'
