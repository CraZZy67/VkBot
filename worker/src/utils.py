from .models import User


def format_template(template: str, user: User) -> str:
    if '{first_name}' in template and "{last_name}" in template:
        return template.format(first_name=user.first_name, last_name=user.last_name)
    
    elif '{first_name}' in template: 
        return template.format(first_name=user.first_name)
    
    elif '{last_name}' in template: 
        return template.format(last_name=user.last_name)
    
    return template