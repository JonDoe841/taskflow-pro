from django import template

register = template.Library()

@register.filter
def status_color(status):
    colors = {
        'planning': 'secondary',
        'active': 'success',
        'on_hold': 'warning',
        'completed': 'primary',
        'cancelled': 'danger',
    }
    return colors.get(status, 'secondary')

@register.filter
def priority_color(priority):
    colors = {
        'low': 'info',
        'medium': 'warning',
        'high': 'danger',
        'critical': 'dark',
    }
    return colors.get(priority, 'secondary')

@register.simple_tag
def project_progress_class(percentage):
    if percentage < 30:
        return 'bg-danger'
    elif percentage < 70:
        return 'bg-warning'
    else:
        return 'bg-success'