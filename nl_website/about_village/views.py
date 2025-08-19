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


class HistoryPage(TemplateView):
    template_name = 'history/history.html'
    extra_context = {"title": "История поселка"}


class HistoryBookPage(TemplateView):
    template_name = 'history/history_book.html'
    extra_context = {"title": "Историческая хроника - Новая Старая Ляда"}
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Читаем файл с книгой
        import os
        from django.conf import settings
        
        # Ищем файл книги в MEDIA в приоритете, затем в корне проекта (совместимость)
        possible_book_paths = [
            os.path.join(settings.MEDIA_ROOT, 'book', 'assemble_book_with_images.txt'),
            os.path.join(settings.MEDIA_ROOT, 'assemble_book_with_images.txt'),
            os.path.join(settings.BASE_DIR, 'assemble_book_with_images.txt'),
            os.path.join(settings.BASE_DIR.parent, 'assemble_book_with_images.txt'),
        ]
        book_file_path = None
        for _p in possible_book_paths:
            if os.path.exists(_p):
                book_file_path = _p
                break
        
        try:
            if not book_file_path:
                raise FileNotFoundError('Файл книги не найден в MEDIA или в корне проекта')
            with open(book_file_path, 'r', encoding='utf-8') as f:
                book_content = f.read()
            
            # Разбиваем на страницы
            pages = book_content.split("══════════════════════════════════════════════════════════════════════\nСТРАНИЦА ")
            
            # Первая часть - заголовок книги
            book_header = pages[0] if pages else ""
            
            # Остальные части - страницы
            book_pages = []
            for i, page_content in enumerate(pages[1:], 1):
                lines = page_content.split('\n')
                page_number = lines[0] if lines else str(i)
                
                # Обрабатываем содержимое страницы
                page_text = '\n'.join(lines[2:]) if len(lines) > 2 else ""
                
                # Извлекаем изображения
                images = []
                if "📷 **ИЗОБРАЖЕНИЯ НА ЭТОЙ СТРАНИЦЕ:**" in page_text:
                    lines_split = page_text.split('\n')
                    collecting_images = False
                    for line in lines_split:
                        if "📷 **ИЗОБРАЖЕНИЯ НА ЭТОЙ СТРАНИЦЕ:**" in line:
                            collecting_images = True
                            continue
                        elif collecting_images and line.strip() and not line.startswith('   '):
                            collecting_images = False
                        elif collecting_images and line.strip().startswith('   '):
                            # Извлекаем путь к изображению
                            if 'book_images/' in line:
                                img_path = line.split('book_images/')[-1].strip()
                                images.append(img_path)
                
                # Удаляем секцию изображений и ссылки на изображения из текста для отображения
                if "📷 **ИЗОБРАЖЕНИЯ НА ЭТОЙ СТРАНИЦЕ:**" in page_text:
                    parts = page_text.split("📷 **ИЗОБРАЖЕНИЯ НА ЭТОЙ СТРАНИЦЕ:**")
                    if len(parts) > 1:
                        # Находим конец списка изображений
                        after_images = parts[1].split('\n')
                        clean_lines = []
                        skip_images = True
                        for line in after_images:
                            if skip_images and (not line.strip() or line.startswith('   ')):
                                continue
                            else:
                                skip_images = False
                                clean_lines.append(line)
                        page_text = parts[0] + '\n'.join(clean_lines)
                
                # Убираем строки с ссылками на изображения (📎 Изображение:)
                lines = page_text.split('\n')
                clean_lines = []
                for line in lines:
                    if not line.strip().startswith('📎 Изображение:'):
                        clean_lines.append(line)
                page_text = '\n'.join(clean_lines)
                
                book_pages.append({
                    'number': page_number,
                    'content': page_text.strip(),
                    'images': images
                })
            
            # Добавляем изображения к страницам на основе содержимого каталога media/book
            # Имена файлов вида: page_001_image_*.jpg → сопоставляем по номеру страницы
            media_book_dir = os.path.join(settings.MEDIA_ROOT, 'book')
            page_to_images = {}
            if os.path.exists(media_book_dir):
                try:
                    for file_name in sorted(os.listdir(media_book_dir)):
                        if not file_name.lower().endswith('.jpg'):
                            continue
                        # Ожидаемый формат: page_XXX_image_YYY.jpg
                        # Извлечём номер страницы XXX (с ведущими нулями)
                        if file_name.startswith('page_') and '_image_' in file_name:
                            page_part = file_name.split('_')[1]  # '001'
                            try:
                                page_num_int = int(page_part)
                            except ValueError:
                                continue
                            page_to_images.setdefault(page_num_int, []).append(file_name)
                except Exception:
                    # Игнорируем ошибки чтения директории, изображения просто не будут добавлены
                    pass

            # Сопоставляем найденные изображения со страницами книги
            for page in book_pages:
                # Номер страницы в тексте может быть в разных форматах — берём первую числовую группу
                import re
                match = re.search(r"(\d+)", str(page['number']))
                if match:
                    page_num_int = int(match.group(1))
                    images_for_page = page_to_images.get(page_num_int, [])
                    if images_for_page:
                        # Если ранее уже нашли изображения в тексте — объединим уникально и отсортируем
                        existing = page.get('images') or []
                        merged = sorted(set(existing) | set(images_for_page))
                        page['images'] = merged
                
            total_pages = len(book_pages)
            # Запрашиваемая страница из query params
            try:
                requested_page = int(self.request.GET.get('page', '1'))
            except ValueError:
                requested_page = 1
            if requested_page < 1:
                requested_page = 1
            if total_pages and requested_page > total_pages:
                requested_page = total_pages

            # Текущая страница по индексу
            if total_pages > 0:
                current_page = book_pages[requested_page - 1]
            else:
                current_page = {'number': 1, 'content': '', 'images': []}

            # Навигация
            has_prev = requested_page > 1
            has_next = total_pages and requested_page < total_pages
            prev_page = requested_page - 1 if has_prev else None
            next_page = requested_page + 1 if has_next else None

            context['book_header'] = book_header
            context['current_page'] = current_page
            context['current_page_index'] = requested_page
            context['total_pages'] = total_pages
            context['has_prev'] = has_prev
            context['has_next'] = has_next
            context['prev_page'] = prev_page
            context['next_page'] = next_page
            
        except FileNotFoundError:
            context['error'] = "Файл книги не найден"
            context['current_page'] = None
            context['total_pages'] = 0
        except Exception as e:
            context['error'] = f"Ошибка при загрузке книги: {str(e)}"
            context['current_page'] = None
            context['total_pages'] = 0
        
        return context


class DebugImagesPage(TemplateView):
    template_name = 'history/debug_images.html'
    extra_context = {"title": "Отладка изображений"}
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Берем несколько первых изображений для тестирования
        import os
        from django.conf import settings
        
        static_images_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'book')
        media_images_path = os.path.join(settings.BASE_DIR, 'media', 'book_images')
        
        context['static_path_exists'] = os.path.exists(static_images_path)
        context['media_path_exists'] = os.path.exists(media_images_path)
        
        if context['static_path_exists']:
            context['static_images_count'] = len([f for f in os.listdir(static_images_path) if f.endswith('.jpg')])
            context['static_sample_images'] = sorted([f for f in os.listdir(static_images_path) if f.endswith('.jpg')])[:5]
        else:
            context['static_images_count'] = 0
            context['static_sample_images'] = []
            
        if context['media_path_exists']:
            context['media_images_count'] = len([f for f in os.listdir(media_images_path) if f.endswith('.jpg')])
            context['media_sample_images'] = sorted([f for f in os.listdir(media_images_path) if f.endswith('.jpg')])[:5]
        else:
            context['media_images_count'] = 0
            context['media_sample_images'] = []
        
        return context


from django.http import HttpResponse, Http404
from django.conf import settings

def serve_book_image(request, image_name):
    """
    Подача изображений книги напрямую из файловой системы
    """
    import os
    import mimetypes
    
    # Попробуем найти изображение в static и media папках
    possible_paths = [
        os.path.join(settings.BASE_DIR, 'static', 'images', 'book', image_name),
        os.path.join(settings.MEDIA_ROOT, 'book', image_name),  # Текущая папка с изображениями книги
        os.path.join(settings.BASE_DIR, 'media', 'book', image_name),  # Совместимость
        os.path.join(settings.BASE_DIR.parent, 'book', image_name),  # Возможная оригинальная папка
        os.path.join(settings.BASE_DIR, 'media', 'book_images', image_name),  # Совместимость со старым путём
        os.path.join(settings.BASE_DIR.parent, 'book_images', image_name),  # Старый внешний путь
    ]
    
    for image_path in possible_paths:
        if os.path.exists(image_path):
            try:
                with open(image_path, 'rb') as f:
                    image_data = f.read()
                
                # Определяем MIME тип
                content_type, _ = mimetypes.guess_type(image_path)
                if not content_type:
                    content_type = 'image/jpeg'
                
                response = HttpResponse(image_data, content_type=content_type)
                response['Content-Length'] = len(image_data)
                return response
                
            except Exception as e:
                continue
    
    # Если изображение не найдено
    raise Http404(f"Изображение {image_name} не найдено")