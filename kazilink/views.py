from django.shortcuts import redirect, render

from kazilink.models import Contact


def home_page(request):
    context = {}
    return render(request, "kazilink/home.html")

def about_page(request):
    context = {}
    return render(request, "kazilink/about.html")

def services_page(request):
    context = {}
    return render(request, "kazilink/services.html")


def contact_page(request):
    """Function to push the appointment to the DB """
   
    if request.method == 'POST':
        #CREATE A VARIABLE TO PICK THE INPUT FIELDS
        contact = Contact(
            name = request.POST['name'],
            email = request.POST['email'],
            subject = request.POST['subject'],
            message = request.POST['message'],
        )
        
        contact.save()
       
        return redirect('kazilink_home')
    else:
        return render(request, 'kazilink/contact.html')
        