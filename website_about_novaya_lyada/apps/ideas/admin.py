from django.contrib import admin
from .models import ImprovementIdea, IdeaComment, IdeaVote


@admin.register(ImprovementIdea)
class ImprovementIdeaAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'location', 'created_at', 'updated_at']
    list_filter = ['status', 'category', 'author', 'created_at']
    search_fields = ['title', 'description', 'location', 'author__username', 'author__first_name', 'author__last_name']
    readonly_fields = ['slug', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'author', 'category', 'status')
        }),
        ('Содержание', {
            'fields': ('description', 'proposed_solution', 'location', 'image')
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_ideas', 'reject_ideas', 'set_pending', 'set_collection']

    def set_collection(self, request, queryset):
        count = queryset.update(status='collection')
        self.message_user(request, f'{count} идей переведены в статус "Сбор голосов".')
    set_collection.short_description = "Перевести в статус 'Сбор голосов'"
    
    def approve_ideas(self, request, queryset):
        count = queryset.update(status='approved')
        self.message_user(request, f'Одобрено {count} идей.')
    approve_ideas.short_description = "Одобрить выбранные идеи"
    
    def reject_ideas(self, request, queryset):
        count = queryset.update(status='rejected')
        self.message_user(request, f'Отклонено {count} идей.')
    reject_ideas.short_description = "Отклонить выбранные идеи"
    
    def set_pending(self, request, queryset):
        count = queryset.update(status='pending')
        self.message_user(request, f'{count} идей переведены в статус "На рассмотрении".')
    set_pending.short_description = "Перевести в статус 'На рассмотрении'"


@admin.register(IdeaComment)
class IdeaCommentAdmin(admin.ModelAdmin):
    list_display = ['idea', 'author', 'text_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['idea__title', 'author__username', 'text']
    readonly_fields = ['created_at']
    
    def text_preview(self, obj):
        return obj.text[:50] + ('...' if len(obj.text) > 50 else '')
    text_preview.short_description = 'Превью комментария'


@admin.register(IdeaVote)
class IdeaVoteAdmin(admin.ModelAdmin):
    list_display = ['idea', 'user', 'vote_type', 'created_at']
    list_filter = ['vote_type', 'created_at']
    search_fields = ['idea__title', 'user__username']
    readonly_fields = ['created_at']