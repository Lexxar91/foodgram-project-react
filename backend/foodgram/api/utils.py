from django.conf import settings
from django.http import HttpResponse

CONTENT_TYPE = 'text/plain,charset=utf8'


def convert_txt(shop_list):
    file_name = settings.SHOPPING_CART_FILE_NAME
    lines = []
    for ing in shop_list:
        name = ing['ingredient__name']
        measurement_unit = ing['ingredient__measurement_unit']
        amount = ing['ingredient_total']
        lines.append(f'{name} ({measurement_unit}) - {amount}')
    content = '\n'.join(lines)
    content_type = CONTENT_TYPE
    response = HttpResponse(content, content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename={file_name}'
    return response
