from django import template


register = template.Library()


@register.filter
def duration(td):
    total_seconds = int(td.total_seconds())
    hours = f'{total_seconds // 3600:02d}'
    minutes = f'{(total_seconds % 3600) // 60:02d}'
    return '{}:{}'.format(hours, minutes)

@register.filter
def duration_decimal(td):
    total_seconds = int(td.total_seconds())
    hours = f'{total_seconds // 3600}'
    minutes = f'{(total_seconds % 3600) // 36:02d}'
    return '{}.{}'.format(hours, minutes)

@register.filter
def get_dict_value(dictionary, key):
    return dictionary[key]

@register.filter
def month_day(date):
    return '{}/{}'.format(date.strftime("%-m"),date.strftime("%-d"))


