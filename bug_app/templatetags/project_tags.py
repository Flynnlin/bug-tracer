from django import template

register = template.Library()

@register.inclusion_tag("inclusion/all_project_list_tags.html", takes_context=True)
def all_project_list_tags(context,request):
    # 创建的项目
    user_created_projects = request.tracer.created_projects
    # 参与的项目
    user_joined_projects = request.tracer.joined_projects


    return {'created': user_created_projects,'joined':user_joined_projects}
