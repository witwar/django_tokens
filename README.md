# Django Tokens

---

<a name="russian"></a>
🇷🇺 **Документация на русском** | 🇬🇧 [English Documentation](#english)

Django Tokens — это простая и расширяемая Django-библиотека для парсинга и замены пользовательских токенов (шорткодов) в тексте на отрендеренный HTML-контент.

## Описание

Сразу после установки `django-tokens` позволяет заменять специальные токены вида `[[img ids="11"]]` на реальные изображения или любой другой контент. Библиотека предоставляет гибкую систему для определения собственных обработчиков токенов. 

## Установка

```bash
pip install django-tokens
```

Добавьте `tokens` в `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    'tokens',
]
```

## Быстрый старт

Библиотека уже содержит обработчик изображений с дефолтным шаблоном. Поэтому сразу после установки можно выстроить замену токенов на изображения. Вот как это сделать. 

### Использование в шаблонах

```django
{% load tokens %}

{{ article.content|render_tokens:object_images=images }}
```

### Использование в Python-коде

```python
from tokens import token_parser

text = 'Посмотрите на эти изображения: [[img ids="1,2,3" class="gallery"]]'
context = {
    'object_images': Image.objects.all()
}
rendered_text = token_parser.replace_tokens(text, context)
```

## Формат токенов

Токены имеют следующий формат:
```
[[tag_name attr_1="value" attr_2="value"]]
```

### Примеры:
- `[[img ids="11"]]` - одно изображение
- `[[img ids="1,2,3" class="gallery"]]` - несколько изображений с CSS-классом
- `[[img ids="5" wrapper="image-container" alt="Описание"]]` - изображение с обёрткой

## Встроенный обработчик изображений

Библиотека поставляется с готовым обработчиком для изображений, который поддерживает следующие атрибуты:

- `ids` - ID изображений через запятую (обязательный)
- `class` - CSS-класс для тега `<img>`
- `style` - инлайн-стили
- `wrapper` - CSS-класс для div-обёртки
- `alt` - альтернативный текст
- `width` - ширина изображения
- `height` - высота изображения
- `sizes` - атрибут sizes для responsive изображений

Чтобы определить srcset с вашими тумбинашками, нужно переопределить шаблон tokens/img.html в директории templates проекта.

### Пример использования:

Представим, что у нас есть модель Article, к которой можно прикрепить изображения. Тогда в персер нужно передать контекст с object_images, в котором будет список изображений.

```python
# В модели
class Article(models.Model):
    content = models.TextField()
    images = models.ManyToManyField('Image')
    
    def get_rendered_content(self):
        from tokens import token_parser
        return token_parser.replace_tokens(
            self.content, 
            context={'object_images': self.images.all()}
        )

# В шаблоне
{% load tokens %}
{{ article.content|render_tokens:object_images=article.images.all }}
```

## Создание собственных обработчиков

Вы можете легко создавать обработчики для любых типов токенов:

```python
from tokens import token_parser
from django.template.loader import render_to_string

@token_parser.register_handler("video")
def video_handler(attrs):
    video_id = attrs.get("id")
    if not video_id:
        return attrs.get("_original_token", "")
    
    try:
        video = Video.objects.get(id=video_id)
        return render_to_string("tokens/video.html", {
            "video": video,
            "width": attrs.get("width", "100%"),
            "height": attrs.get("height", "auto"),
        })
    except Video.DoesNotExist:
        return attrs.get("_original_token", "")

# Использование: [[video id="123" width="600" height="400"]]
```

### Пример обработчика для пользователей:

```python
@token_parser.register_handler("user")
def user_handler(attrs):
    user_id = attrs.get("id")
    if not user_id:
        return ""
    
    try:
        user = User.objects.get(id=user_id)
        return render_to_string("tokens/user_card.html", {
            "user": user,
            "mode": attrs.get("mode", "default")
        })
    except User.DoesNotExist:
        return ""

# Использование: [[user id="42" mode="compact"]]
```

## Шаблоны

Создайте шаблоны для ваших токенов в `templates/tokens/`:

```django
<!-- templates/tokens/video.html -->
<div class="video-container">
    <video width="{{ width }}" height="{{ height }}" controls>
        <source src="{{ video.file.url }}" type="video/mp4">
        Ваш браузер не поддерживает видео.
    </video>
</div>

<!-- templates/tokens/user_card.html -->
<div class="user-card user-card--{{ mode }}">
    <img src="{{ user.avatar.url }}" alt="{{ user.get_full_name }}">
    <span>{{ user.get_full_name }}</span>
</div>
```

## Безопасность

Библиотека автоматически ограничивает атрибуты, которые можно переопределить через токены. По умолчанию разрешены только:
- `ids`, `class`, `style`, `wrapper`, `alt`, `width`, `height`, `sizes`

## Продвинутое использование

### Собственные парсеры

Если вы добавили tokens в INSTALLED_APPS, то при запуске вашего приложения будет создан дефолтный token_parser — это экземпляр класса TokenParser. Можно создать свои вариации класса и парсеры. 

### Передача дополнительного контекста

```python
context = {
    'object_images': Image.objects.all(),
    'current_user': request.user,
    'site_settings': settings,
}
rendered = token_parser.replace_tokens(text, context)
```

### Обработка ошибок

Если токен не может быть обработан, он остаётся в тексте без изменений:

```python
text = "[[unknown_token id='123']]"  # Останется как есть
text = "[[img ids='999']]"  # Останется, если изображение не найдено
```

## Примеры использования

### Блог с медиа-контентом

```python
# models.py
class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    images = models.ManyToManyField('Image')
    videos = models.ManyToManyField('Video')
    
    def get_rendered_content(self):
        return token_parser.replace_tokens(self.content, {
            'object_images': self.images.all(),
            'object_videos': self.videos.all(),
        })

# views.py
def post_detail(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    return render(request, 'blog/post_detail.html', {
        'post': post,
        'rendered_content': post.get_rendered_content(),
    })
```

### Документация с примерами кода

```python
@token_parser.register_handler("code")
def code_handler(attrs):
    snippet_id = attrs.get("id")
    language = attrs.get("lang", "python")
    
    snippet = CodeSnippet.objects.get(id=snippet_id)
    return render_to_string("tokens/code.html", {
        "code": snippet.code,
        "language": language,
    })

# Использование: [[code id="15" lang="javascript"]]
```

## Требования

- Python 3.8+
- Django 3.2+

## Лицензия

MIT License

## Автор

witwar (witwar@gmail.com)

## Ссылки

- [GitHub](https://github.com/witwar/django-tokens)
- [Issues](https://github.com/witwar/django-tokens/issues)

---

<a name="english"></a>
🇷🇺 [Документация на русском](#russian) | 🇬🇧 **English Documentation**

Django Tokens — simple and extensible Django library for parsing and replacing custom tokens (shortcodes) in text with rendered HTML content.

## Description

Right after installation, `django-tokens` allows you to replace special tokens like `[[img ids="11"]]` with actual images or any other content. The library provides a flexible system for defining custom token handlers.

## Installation

```bash
pip install django-tokens
```

Add `tokens` to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    'tokens',
]
```

## Quick Start

The library already includes an image handler with a default template. So immediately after installation, you can set up token replacement for images. Here's how to do it.

### Usage in Templates

```django
{% load tokens %}

{{ article.content|render_tokens:object_images=images }}
```

### Usage in Python Code

```python
from tokens import token_parser

text = 'Check out these images: [[img ids="1,2,3" class="gallery"]]'
context = {
    'object_images': Image.objects.all()
}
rendered_text = token_parser.replace_tokens(text, context)
```

## Token Format

Tokens have the following format:
```
[[tag_name attr_1="value" attr_2="value"]]
```

### Examples:
- `[[img ids="11"]]` - single image
- `[[img ids="1,2,3" class="gallery"]]` - multiple images with CSS class
- `[[img ids="5" wrapper="image-container" alt="Description"]]` - image with wrapper

## Built-in Image Handler

The library comes with a ready-to-use image handler that supports the following attributes:

- `ids` - comma-separated image IDs (required)
- `class` - CSS class for the `<img>` tag
- `style` - inline styles
- `wrapper` - CSS class for div wrapper
- `alt` - alternative text
- `width` - image width
- `height` - image height
- `sizes` - sizes attribute for responsive images

To define srcset with your thumbnails, you need to override the tokens/img.html template in your project's templates directory.

### Usage Example:

Let's imagine we have an Article model with attached images. Then we need to pass a context with object_images containing the list of images to the parser.

```python
# In the model
class Article(models.Model):
    content = models.TextField()
    images = models.ManyToManyField('Image')
    
    def get_rendered_content(self):
        from tokens import token_parser
        return token_parser.replace_tokens(
            self.content, 
            context={'object_images': self.images.all()}
        )

# In the template
{% load tokens %}
{{ article.content|render_tokens:object_images=article.images.all }}
```

## Creating Custom Handlers

You can easily create handlers for any type of tokens:

```python
from tokens import token_parser
from django.template.loader import render_to_string

@token_parser.register_handler("video")
def video_handler(attrs):
    video_id = attrs.get("id")
    if not video_id:
        return attrs.get("_original_token", "")
    
    try:
        video = Video.objects.get(id=video_id)
        return render_to_string("tokens/video.html", {
            "video": video,
            "width": attrs.get("width", "100%"),
            "height": attrs.get("height", "auto"),
        })
    except Video.DoesNotExist:
        return attrs.get("_original_token", "")

# Usage: [[video id="123" width="600" height="400"]]
```

### Example User Handler:

```python
@token_parser.register_handler("user")
def user_handler(attrs):
    user_id = attrs.get("id")
    if not user_id:
        return ""
    
    try:
        user = User.objects.get(id=user_id)
        return render_to_string("tokens/user_card.html", {
            "user": user,
            "mode": attrs.get("mode", "default")
        })
    except User.DoesNotExist:
        return ""

# Usage: [[user id="42" mode="compact"]]
```

## Templates

Create templates for your tokens in `templates/tokens/`:

```django
<!-- templates/tokens/video.html -->
<div class="video-container">
    <video width="{{ width }}" height="{{ height }}" controls>
        <source src="{{ video.file.url }}" type="video/mp4">
        Your browser does not support video.
    </video>
</div>

<!-- templates/tokens/user_card.html -->
<div class="user-card user-card--{{ mode }}">
    <img src="{{ user.avatar.url }}" alt="{{ user.get_full_name }}">
    <span>{{ user.get_full_name }}</span>
</div>
```

## Security

The library automatically restricts attributes that can be overridden through tokens. By default, only the following are allowed:
- `ids`, `class`, `style`, `wrapper`, `alt`, `width`, `height`, `sizes`

## Advanced Usage

### Custom Parsers

If you've added tokens to INSTALLED_APPS, a default token_parser will be created when your application starts — this is an instance of the TokenParser class. You can create your own variations of the class and parsers.

### Passing Additional Context

```python
context = {
    'object_images': Image.objects.all(),
    'current_user': request.user,
    'site_settings': settings,
}
rendered = token_parser.replace_tokens(text, context)
```

### Error Handling

If a token cannot be processed, it remains unchanged in the text:

```python
text = "[[unknown_token id='123']]"  # Will remain as is
text = "[[img ids='999']]"  # Will remain if image not found
```

## Usage Examples

### Blog with Media Content

```python
# models.py
class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    images = models.ManyToManyField('Image')
    videos = models.ManyToManyField('Video')
    
    def get_rendered_content(self):
        return token_parser.replace_tokens(self.content, {
            'object_images': self.images.all(),
            'object_videos': self.videos.all(),
        })

# views.py
def post_detail(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    return render(request, 'blog/post_detail.html', {
        'post': post,
        'rendered_content': post.get_rendered_content(),
    })
```

### Documentation with Code Examples

```python
@token_parser.register_handler("code")
def code_handler(attrs):
    snippet_id = attrs.get("id")
    language = attrs.get("lang", "python")
    
    snippet = CodeSnippet.objects.get(id=snippet_id)
    return render_to_string("tokens/code.html", {
        "code": snippet.code,
        "language": language,
    })

# Usage: [[code id="15" lang="javascript"]]
```

## Requirements

- Python 3.8+
- Django 3.2+

## License

MIT License

## Author

witwar (witwar@gmail.com)

## Links

- [GitHub](https://github.com/witwar/django-tokens)
- [Issues](https://github.com/witwar/django-tokens/issues)
