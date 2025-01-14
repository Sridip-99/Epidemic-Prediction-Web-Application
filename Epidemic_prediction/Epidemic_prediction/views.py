from django.shortcuts import render
from django.contrib import messages

def homePage(request):
    data={
        'title':'Home Page'
    }
    return render(request,"Index.html",data)

def aboutUs(request):
    data2={
        'title':'About-Us'
    }
    return render(request,"aboutUs.html",data2)

def mentor(request):
    data4={
        'title':'Mentor'
    }
    return render(request,"Mentor.html",data4)

def team(request):
    data5={
        'title':'Team Members'
    }
    return render(request,"Team.html",data5)

def custom_permission_denied_view(request, exception):
    return render(request, 'errors/403.html', status=403)

def custom_page_not_found_view(request, exception):
    return render(request, 'errors/404.html', status=404)

def custom_server_error_view(request):
    return render(request, 'errors/500.html', status=500)
