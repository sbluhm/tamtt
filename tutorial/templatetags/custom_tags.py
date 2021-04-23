from django import template


register = template.Library()


@register.filter
def duration(td):
    total_seconds = int(td.total_seconds())
    hours = f'{total_seconds // 3600:02d}'
    minutes = f'{(total_seconds % 3600) // 60:02d}'
    return '{}:{}'.format(hours, minutes)

