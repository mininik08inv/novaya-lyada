from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import DetailView, UpdateView, CreateView
from events.models import Event, Category
from events.forms import AddEventForm


class ShowEvent(DetailView):
    template_name = 'events/event_detail.html'
    slug_url_kwarg = 'event_slug'
    context_object_name = 'event'

    def get_object(self, queryset=None):
        return get_object_or_404(Event.published, slug=self.kwargs[self.slug_url_kwarg])


def events(request):
    events_all = Event.published.all()

    context = {
        'title': 'Все события',
        'events': events_all
    }
    return render(request, template_name='events/events_all.html', context=context)


class UpdateEvent(PermissionRequiredMixin, UpdateView):
    model = Event
    fields = ['title', 'content', 'image', 'status', 'cat']
    template_name = 'events/addevent.html'
    title_page = 'Редактирование статьи'
    permission_required = 'events.change_event'

    # Используем те же параметры, что и в ShowEvent
    slug_field = 'slug'
    slug_url_kwarg = 'event_slug'  # Изменено с 'slug' на 'event_slug'

    def get_success_url(self):
        # Используем тот же параметр, что и в get_absolute_url()
        return reverse('events:event_detail', kwargs={'event_slug': self.object.slug})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title_page
        return context


class AddEvent(LoginRequiredMixin, CreateView):
    model = Event
    fields = ['title', 'content', 'image', 'status', 'cat']
    template_name = 'events/addevent.html'
    success_url = reverse_lazy('events:events_all')  # Убедитесь, что это правильный URL

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Событие успешно создано!')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)