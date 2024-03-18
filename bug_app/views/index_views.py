from django.shortcuts import render

# Create your views here.


"""
官网首页

四个页面
"""


def index_view(request):
    return render(request,'index/index.html')
def index_doc_view(request):
    return render(request,'index/index_doc.html')

def index_function_view(request):
    return render(request,'index/index_function.html')

def index_price_view(request):
    return render(request, 'index/index_price.html')

def index_scheme_view(request):
    return render(request, 'index/index_scheme.html')