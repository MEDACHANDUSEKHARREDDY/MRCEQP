from django import template

register = template.Library()

@register.filter
def get_question_status(question_status_dict, q_number):
    print(type(question_status_dict))
    return question_status_dict.get(q_number, None)
