from django import template
import re
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter()
def highlight_search(docx_text, value):
    if docx_text is not None:
        docx_text = str(docx_text)
        src_str = re.compile(value, re.IGNORECASE)
        str_replaced = src_str.sub(f'<span class="highlight">{value}</span>', docx_text)
    else:
        str_replaced = ""
    return mark_safe(str_replaced)

# Jesus Saves