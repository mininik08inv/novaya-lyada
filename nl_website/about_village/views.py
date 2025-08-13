from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from about_village.models import FamousPerson

from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from .models import FamousPerson, CategoryPeople


class FamousPeopleAll(ListView):
    template_name = 'famous_people/famous_people_all.html'
    context_object_name = "people"
    paginate_by = 12  # Количество элементов на странице
    title_page = 'Известные люди'

    def get_queryset(self):
        queryset = FamousPerson.published.all().prefetch_related('categories')

        # Фильтрация по категории если передана
        category_id = self.request.GET.get('cat')
        if category_id:
            self.cat_selected = get_object_or_404(CategoryPeople, id=category_id)
            queryset = queryset.filter(categories=self.cat_selected)
        else:
            self.cat_selected = None

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Добавляем все категории для фильтра
        context['all_categories'] = CategoryPeople.objects.all()

        # Добавляем выбранную категорию (если есть)
        context['cat_selected'] = self.cat_selected

        # Добавляем заголовок страницы
        context['title_page'] = self.title_page

        # Если выбрана категория, уточняем заголовок
        if self.cat_selected:
            context['title_page'] = f'{self.title_page} - {self.cat_selected.name}'

        return context


class PersonDetail(DetailView):
    model = FamousPerson
    template_name = 'famous_people/person_detail.html'
    slug_url_kwarg = 'person_slug'
    context_object_name = 'human'
    queryset = FamousPerson.published.all()

    def get_object(self, queryset=None):
        return get_object_or_404(FamousPerson.published, slug=self.kwargs[self.slug_url_kwarg])


class AboutVillage(TemplateView):
    template_name = 'about_village.html'
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['famous_person'] = FamousPerson.published.all()[:3]
        return self.render_to_response(context)