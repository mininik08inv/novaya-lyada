from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from website_about_novaya_lyada.apps.places.models import Place, CategoryPlace, PlaceReview
from website_about_novaya_lyada.apps.places.forms import AddPlaceForm, AddReviewForm


class AllPlaces(ListView):
    template_name = 'places/all_places.html'
    context_object_name = "places"
    paginate_by = 12  # Количество элементов на странице
    title_page = 'Все интересые места'

    def get_queryset(self):
        queryset = Place.published.all().prefetch_related('categories')

        # Фильтрация по категории если передана
        category_slug = self.request.GET.get('category')
        if category_slug:
            self.cat_selected = get_object_or_404(CategoryPlace, slug=category_slug)
            queryset = queryset.filter(categories=self.cat_selected)
        else:
            self.cat_selected = None

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Добавляем все категории для фильтра
        context['all_categories'] = CategoryPlace.objects.all()

        # Добавляем выбранную категорию (если есть)
        context['cat_selected'] = self.cat_selected

        # Добавляем заголовок страницы
        context['title_page'] = self.title_page

        # Если выбрана категория, уточняем заголовок
        if self.cat_selected:
            context['title_page'] = f'{self.title_page} - {self.cat_selected.name}'

        return context


class PlaceDetail(DetailView):
    template_name = 'places/place_detail.html'
    slug_url_kwarg = 'place_slug'
    context_object_name = 'place'

    def get_object(self, queryset=None):
        return get_object_or_404(Place.published, slug=self.kwargs[self.slug_url_kwarg])


class PlaceAddReview(LoginRequiredMixin, CreateView):
    model = PlaceReview
    fields = ['rating', 'text']
    template_name = 'places/add_review.html'  # Можно использовать модальное окно вместо отдельного шаблона

    def get_success_url(self):
        messages.success(self.request, 'Ваш отзыв успешно добавлен!')
        return reverse_lazy('places:place_detail', kwargs={'place_slug': self.kwargs['place_slug']})

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.place = Place.objects.get(slug=self.kwargs['place_slug'])
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['place'] = Place.objects.get(slug=self.kwargs['place_slug'])
        return context