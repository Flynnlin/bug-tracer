import json
import markdown
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from bug_app.forms.wiki_form import WikiModelForm
from bug_app.models import Project, Wiki


"""
wiki 相关功能

"""

def project_wiki_list_view(request, project_id):
    wiki_list=list(Wiki.objects.filter(project=request.tracer.project).order_by('depth','id').values_list('id','title','parent'))
    return  render(request,'platform/wiki/wiki_list.html',{'wiki_list':wiki_list})

def project_wiki_add_view(request, project_id):
    if request.method == 'POST':
        form = WikiModelForm(request.POST,request=request)
        if form.is_valid():
            form.instance.project=request.tracer.project
            if form.cleaned_data['parent']:
                father = Wiki.objects.get(id=form.cleaned_data['parent'].id)
                if father:
                    form.instance.depth = father.depth +1
            form.save()
            url = reverse("project_wiki", args=[project_id])
            return redirect(url)
        else:
            return render(request, 'platform/wiki/wiki_add.html', {'form': form})
    if request.method == 'GET':
        wiki_list=list(Wiki.objects.filter(project=request.tracer.project).order_by('depth').values_list('id','title','parent'))
        form=WikiModelForm(request=request)
        return render(request,'platform/wiki/wiki_add.html',{'form':form,'wiki_list':wiki_list})

def project_wiki_detail_view(request, project_id,wiki_id):
    wiki_list = list(
        Wiki.objects.filter(project=request.tracer.project).order_by('depth', 'id').values_list('id', 'title',
                                                                                                    'parent'))
    wiki = Wiki.objects.get(id=wiki_id)
    wiki.content = markdown.markdown(wiki.content)
    wiki.content = wiki.content.replace('<img', '<img class="markdown-img"')
    return render(request,'platform/wiki/wiki_detail.html',{'wiki':wiki,'wiki_list':wiki_list})


def project_wiki_del_view(request, project_id,wiki_id):
    Wiki.objects.filter(id=wiki_id,project_id=project_id).delete()
    url = reverse("project_wiki", args=[project_id])
    return redirect(url)

def project_wiki_edit_view(request, project_id,wiki_id):
    wiki_list = list(
        Wiki.objects.filter(project=request.tracer.project).order_by('depth', 'id').values_list('id', 'title',
                                                                                                'parent'))
    wiki = Wiki.objects.get(id=wiki_id)
    form = WikiModelForm(instance=wiki, request=request)

    if request.method == "POST":
        form = WikiModelForm(request.POST,instance=wiki,request=request)
        if form.is_valid():
            form.save()
            return redirect(reverse('project_wiki_detail', args=[project_id,wiki_id]))
        else:
            return render(request, 'platform/wiki/wiki_edit.html', {'wiki': wiki, 'wiki_list': wiki_list, 'form': form})

    if request.method == "GET":
        return render(request,'platform/wiki/wiki_edit.html',{'wiki':wiki,'wiki_list':wiki_list,'form':form})
