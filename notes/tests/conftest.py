from django.contrib.auth import get_user_model

User = get_user_model()

FORM_DATA = {
    'title': 'new title',
    'text': 'new text',
    'slug': 'new-slug'
}
