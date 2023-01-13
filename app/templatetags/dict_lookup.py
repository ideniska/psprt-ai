from django import template

register = template.Library()


def get_display_name(size, key):
    return size.get(key, {}).get("display_name", "")


def get_size(size, key):
    return size.get(key, {}).get("size", "")


register.filter("get_size", get_size)
register.filter("get_display_name", get_display_name)
