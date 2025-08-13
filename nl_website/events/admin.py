from django.contrib import admin, messages
from events.models import Event, Category

# Register your models here.


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    # fields = ["image", "title", "slug", "content", "cat", "status", "date_of_event"]
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("title", "cat", "status", "date_of_event")
    list_display_links = ("title", "date_of_event")
    ordering = ["-date_of_event", "title"]
    actions = ["set_published", "set_draft", "set_archive"]
    search_fields = ["title__startswith", "cat__name"]
    list_filter = [
        "cat__name",
    ]
    save_on_top = True

    @admin.action(description="Опубликовать выбранные записи")
    def set_published(self, request, queryset):
        count = queryset.update(status="published")
        self.message_user(request, f"Изменено {count} записей.")

    @admin.action(description="Снять с публикации выбранные записи")
    def set_draft(self, request, queryset):
        count = queryset.update(status="draft")
        self.message_user(
            request, f"{count} записей сняты с публикации!", messages.WARNING
        )

    @admin.action(description="Отправить в архив выбранные записи")
    def set_archive(self, request, queryset):
        count = queryset.update(status="archive")
        self.message_user(request, f"{count} отправлены в архив", messages.INFO)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    list_display_links = ("id", "name")
