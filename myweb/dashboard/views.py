from django.shortcuts import render

from django.shortcuts import render
from .models import DataPoint

def dashboard_view(request):
    
    data_points = DataPoint.objects.all().order_by('-date')[:10]
    context = {
        'data_points': data_points
    }
    return render(request, 'dashboard.html', context)
def main(request):
    
    
    return render(request, 'main.html')

