from django.contrib import admin, messages
from website_about_novaya_lyada.apps.places.models import Place, PlacePhoto, CategoryPlace, PlaceReview

# Register your models here.

@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ("name", "is_published")
    list_display_links = ("name", "is_published" )
    ordering = ["name"]
    actions = ["set_published", "set_draft"]
    search_fields = ["name__startswith", "categories__name"]
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


@admin.register(CategoryPlace)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    list_display_links = ("id", "name")

@admin.register(PlacePhoto)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ("id", "place", "photo", "is_main")
    list_display_links = ("id", "place" )


@admin.register(PlaceReview)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ("id", "place", "author", "rating")
    list_display_links = ("id", "place", "rating")
    list_filter = [
        "place", "author", "rating", "place__categories__name"
    ]