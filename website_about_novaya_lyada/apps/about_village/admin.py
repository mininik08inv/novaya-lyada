from django.contrib import admin, messages
from website_about_novaya_lyada.apps.about_village.models import FamousPerson, CategoryPeople

# Register your models here.


@admin.register(FamousPerson)
class FamousPersonAdmin(admin.ModelAdmin):
    list_display = ("last_name","first_name",  "date_of_birth", "is_published")
    list_display_links = ("last_name","first_name", )
    ordering = ["last_name","first_name"]
    actions = ["set_published", "set_draft"]
    search_fields = ["last_name__startswith", "first_name__startswith", "categories__name"]
    list_filter = [
        "categories__name",
    ]
    save_on_top = True

    @admin.action(description="Опубликовать выбранные записи")
    def set_published(self, request, queryset):
        count = queryset.update(is_published=True)
        self.message_user(request, f"Опубликовано {count} записей.")

    @admin.action(description="Снять с публикации выбранные записи")
    def set_draft(self, request, queryset):
        count = queryset.update(is_published=False)
        self.message_user(
            request, f"{count} записей сняты с публикации!", messages.WARNING
        )



@admin.register(CategoryPeople)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    list_display_links = ("id", "name")
