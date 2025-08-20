from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from django.views import View
from django.http import JsonResponse
from django.db.models import Count, Q
import logging

from .models import ImprovementIdea, IdeaComment, IdeaVote
from .forms import IdeaForm, CommentForm

logger = logging.getLogger(__name__)


class AllIdeas(ListView):
    template_name = 'ideas/all_ideas.html'
    context_object_name = "ideas"
    paginate_by = 12
    title_page = 'Идеи улучшений'

    def get_queryset(self):
        queryset = ImprovementIdea.objects.filter(status__in=['collection', 'pending', 'approved', 'implemented']).annotate(
            vote_count=Count('ideavote'),
            comment_count=Count('ideacomment')
        ).order_by('-created_at')

        # Фильтрация по категории
        category = self.request.GET.get('category')
        if category and category != 'all':
            queryset = queryset.filter(category=category)
            self.cat_selected = category
        else:
            self.cat_selected = None

        # Фильтрация по статусу
        status = self.request.GET.get('status')
        if status and status != 'all':
            queryset = queryset.filter(status=status)
            self.status_selected = status
        else:
            self.status_selected = None

        # Поиск (без учета регистра)
        search = self.request.GET.get('search')
        if search:
            search_term = search.strip()  # Убираем лишние пробелы
            queryset = queryset.filter(
                Q(title__icontains=search_term) | 
                Q(description__icontains=search_term) |
                Q(location__icontains=search_term)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Добавляем категории для фильтра
        context['categories'] = ImprovementIdea.CATEGORY_CHOICES
        context['statuses'] = ImprovementIdea.STATUS_CHOICES
        context['cat_selected'] = self.cat_selected
        context['status_selected'] = self.status_selected
        context['title_page'] = self.title_page
        context['search_query'] = self.request.GET.get('search', '')
        
        return context


class IdeaDetail(DetailView):
    template_name = 'ideas/idea_detail.html'
    slug_url_kwarg = 'idea_slug'
    context_object_name = 'idea'

    def get_object(self, queryset=None):
        return get_object_or_404(ImprovementIdea, slug=self.kwargs[self.slug_url_kwarg])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        idea = self.get_object()
        
        # Комментарии к идее
        context['comments'] = IdeaComment.objects.filter(idea=idea).order_by('-created_at')
        
        # Статистика голосов
        votes = IdeaVote.objects.filter(idea=idea)
        context['votes_up'] = votes.filter(vote_type='up').count()
        context['votes_down'] = votes.filter(vote_type='down').count()
        context['total_votes'] = votes.count()
        
        # Проверяем, голосовал ли текущий пользователь
        if self.request.user.is_authenticated:
            user_vote = votes.filter(user=self.request.user).first()
            context['user_vote'] = user_vote.vote_type if user_vote else None
        else:
            context['user_vote'] = None
            
        # Форма для комментариев
        context['comment_form'] = CommentForm()
        
        return context


class AddIdea(LoginRequiredMixin, CreateView):
    model = ImprovementIdea
    form_class = IdeaForm
    template_name = 'ideas/add_idea.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Ваша идея успешно отправлена на рассмотрение!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_page'] = 'Предложить идею'
        return context


class AddComment(LoginRequiredMixin, CreateView):
    model = IdeaComment
    form_class = CommentForm
    template_name = 'ideas/add_comment.html'

    def get_success_url(self):
        messages.success(self.request, 'Ваш комментарий успешно добавлен!')
        return reverse_lazy('ideas:idea_detail', kwargs={'idea_slug': self.kwargs['idea_slug']})

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.idea = get_object_or_404(ImprovementIdea, slug=self.kwargs['idea_slug'])
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['idea'] = get_object_or_404(ImprovementIdea, slug=self.kwargs['idea_slug'])
        return context


class VoteIdea(LoginRequiredMixin, View):
    def post(self, request, idea_slug):
        try:
            logger.info(f"Vote request from user {request.user.id} for idea {idea_slug}")
            
            idea = get_object_or_404(ImprovementIdea, slug=idea_slug)
            vote_type = request.POST.get('vote_type')
            
            logger.info(f"Vote type: {vote_type}")
            
            if vote_type not in ['up', 'down']:
                return JsonResponse({'error': 'Неверный тип голоса'}, status=400)
            
            # Проверяем, есть ли уже голос от этого пользователя
            existing_vote = IdeaVote.objects.filter(user=request.user, idea=idea).first()
            
            if existing_vote:
                if existing_vote.vote_type == vote_type:
                    # Если голос такой же - удаляем (отмена голоса)
                    existing_vote.delete()
                    action = 'removed'
                    logger.info(f"Vote removed for user {request.user.id}")
                else:
                    # Если голос другой - меняем
                    existing_vote.vote_type = vote_type
                    existing_vote.save()
                    action = 'changed'
                    logger.info(f"Vote changed to {vote_type} for user {request.user.id}")
            else:
                # Создаем новый голос
                IdeaVote.objects.create(user=request.user, idea=idea, vote_type=vote_type)
                action = 'added'
                logger.info(f"New vote {vote_type} added for user {request.user.id}")
            
            # Пересчитываем голоса
            votes = IdeaVote.objects.filter(idea=idea)
            votes_up = votes.filter(vote_type='up').count()
            votes_down = votes.filter(vote_type='down').count()
            
            response_data = {
                'action': action,
                'votes_up': votes_up,
                'votes_down': votes_down,
                'total_votes': votes_up + votes_down
            }
            
            logger.info(f"Sending response: {response_data}")
            return JsonResponse(response_data)
            
        except Exception as e:
            logger.error(f"Error in voting: {e}")
            return JsonResponse({'error': f'Произошла ошибка: {str(e)}'}, status=500)
