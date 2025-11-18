from django.shortcuts import render

# Create your views here.

def index(request):
    """
    View hiển thị trang index của myapp
    """
    context = {
        'user_name': 'Django Developer',  # Dữ liệu truyền vào template
    }
    return render(request, 'myapp/index.html', context)


def detail(request):
    """
    View hiển thị trang detail của myapp
    """
    return render(request, 'myapp/detail.html')
