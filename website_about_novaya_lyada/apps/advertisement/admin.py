from django.contrib import admin, messages
from advertisement.models import Advertisement, AdvertisementCategory


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "created", "author", "dedline_publish")
    list_filter = ("status", "created")
    search_fields = ("title", "content")
    prepopulated_fields = {"slug": ("title",)}
    actions = ["set_published", "set_draft", "set_archive"]  # Добавлены actions

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
        self.message_user(request, f"{count} записей отправлены в архив", messages.INFO)


@admin.register(AdvertisementCategory)
class AdvertisementCategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    prepopulated_fields = {"slug": ("name",)}