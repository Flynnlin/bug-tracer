from django.shortcuts import render

def statistic_view(request,project_id):
    return render(request,'platform/statistics/statistic.html')