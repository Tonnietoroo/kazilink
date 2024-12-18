from django.shortcuts import redirect, render

from kazilink.models import Contact

from portal.models import Job, JobProfile


def home_page(request):
    jobs = Job.objects.filter(approved=True).order_by('-time_created')[:6]  # Fetch top 5 approved jobs
    context = {
        'jobs': jobs, 
    }
    return render(request, "kazilink/home.html", context)

def about_page(request):
    context = {}
    return render(request, "kazilink/about.html")

def services_page(request):
     # Fetch the latest jobs
    jobs = Job.objects.filter(approved=True).order_by('-time_created')[:6]  # Fetch top 5 approved jobs
    
    # Fetch the latest job profiles
    job_profiles = JobProfile.objects.all().order_by('-id')[:6]  # Fetch top 5 job profiles
    
    context = {
        'jobs': jobs,
        'job_profiles': job_profiles,
    }
    return render(request, 'kazilink/services.html', context)


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
        