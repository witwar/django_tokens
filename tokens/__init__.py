import re
from django.template.loader import render_to_string


class TokenParser:
    """Parse and replace tokens."""

    ALLOWED_OVERRIDE = {"ids", "class", "style", "wrapper", "alt", "width", "height", "sizes"}

    def __init__(self):
        self.pattern = r'\[\[(\w+)\s*(?:[a-z-]+="[^"]*"\s*)*\]\]'
        self.handlers = {}

    def register_handler(self, tag_name):
        """Decorator for registering token handlers."""

        def decorator(func):
            self.handlers[tag_name] = func
            return func

        return decorator

    def parse_attributes(self, token: str) -> dict:
        """Get attrs from token."""
        return dict(re.findall(r'([a-z-]+)="([^"]*)"', token))

    def replace_tokens(self, text: str, context: dict = {}) -> str:
        """Replace token."""

        def replacer(match):
            token = match.group(0)
            tag_name = match.group(1)

            if tag_name not in self.handlers:
                return token

            handler = self.handlers[tag_name]
            attrs = self.parse_attributes(token)

            token_attrs = {k: v for k, v in attrs.items() if k in self.ALLOWED_OVERRIDE}
            context.update(token_attrs)
            context["_original_token"] = token

            return handler(context)

        return re.sub(self.pattern, replacer, text)


token_parser = TokenParser()


@token_parser.register_handler("img")
def img_handler(attrs):
    image_ids = attrs.get("ids")
    object_images = attrs.get("object_images")

    if not image_ids or not object_images:
        return attrs.get("_original_token", "")

    try:
        image_ids = [int(x.strip()) for x in image_ids.split(",")]
    except ValueError:
        return attrs.get("_original_token", "")

    images = {img.id: img for img in object_images}
    attrs["object_images"] = [images[id] for id in image_ids if id in images]

    return render_to_string("tokens/img.html", attrs)
