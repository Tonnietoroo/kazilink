from urllib import request
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from accounts.models import Notification
from .models import JobApproved, JobProfile
from .models import Job, JobApplication
from django.http import Http404, JsonResponse


@login_required
def user_dashboard(request):
    """Display all approved jobs."""
    jobs = Job.objects.filter(approved=True) 

    context = {
        'jobs': jobs
    }

    return render(request, 'portal/user_dashboard.html', context)

@login_required
def create_job_profile(request):
    """Handle Job Profile creation."""
    if request.method == 'POST':
        ########################################### Retrieve form data using request.POST[]
        service_offered = request.POST['service_offered'].strip()
        location = request.POST['location'].strip()
        service_description = request.POST['service_description'].strip()
        institution_name = request.POST['institution_name'].strip() 
        certification = request.POST['certification'].strip()  
        document = request.FILES['document'] if 'document' in request.FILES else None  

        #########################################Check if the user already has a job profile
        if hasattr(request.user, 'job_profile'):
            messages.error(request, "You already have a job profile. Update it instead.")
            return redirect('portal_update_job_profile')  # Redirect to update view

        ###################### Create the JobProfile instance
        job_profile = JobProfile.objects.create(
            user=request.user,
            service_offered=service_offered,
            location=location,
            service_description=service_description,
            institution_name=institution_name,
            certification=certification,
            document=document
        )
        messages.success(request, "Job profile created successfully!")
        return redirect('portal_user_dashboard')

    return render(request, 'portal/create_job_profile.html')


@login_required
def update_job_profile(request):
    """Handle Job Profile updates."""
    try:
        job_profile = request.user.job_profile
    except JobProfile.DoesNotExist:
        messages.error(request, "You don't have a job profile yet. Create one first.")
        return redirect('portal_create_job_profile')  

    if request.method == 'POST':
        ##################### Update form data
        job_profile.service_offered = request.POST['service_offered'].strip()
        job_profile.location = request.POST['location'].strip()
        job_profile.service_description = request.POST['service_description'].strip()
        job_profile.institution_name = request.POST['institution_name'].strip()
        job_profile.certification = request.POST['certification'].strip()

        ############## Handles document upload when new file is being uploaded
        if 'document' in request.FILES:
            job_profile.document = request.FILES['document']

        job_profile.save()
        messages.success(request, "Job profile updated successfully!")
        return redirect('portal_user_dashboard') 

    context = {
        'job_profile': job_profile
    }
    return render(request, 'portal/update_job_profile.html', context)


################### JOB CREATION #########################


@login_required
def create_job(request):
    """Handle job creation."""
    if request.method == 'POST':
        # Variables to capture input fields
        job = Job(
            user=request.user,
            job_name=request.POST['job_name'],
            job_description=request.POST['job_description'],
            location=request.POST['location'],
            amount=request.POST['amount'],
        )

        try:
            # Save the job
            job.save()

            # Success message for job creation
            messages.success(request, "Job created successfully!")
        except Exception as e:
            # Error message for job creation failure
            messages.error(request, f"An error occurred while creating the job: {str(e)}")

        return redirect('portal_user_dashboard')

    # Render the job creation page for GET requests
    return render(request, 'portal/create_job.html')

@login_required
def job_list(request):
    """Display all approved jobs."""
    jobs = Job.objects.filter(approved=True) 

    context = {
        'jobs': jobs
    }

    return render(request, 'portal/job_list.html', context)


@login_required
def job_details(request, job_id):
    """Display detailed information about a specific job."""
    try:
        job = Job.objects.get(job_id=job_id)
    except Job.DoesNotExist:
        raise Http404("Job not found.")

    context = {
        'job': job,
        'can_apply': not JobApplication.objects.filter(user=request.user, job=job).exists(),  
    }

    return render(request, 'portal/job_details.html', context)


################## JOB APPLICATION ###################


@login_required
def apply_for_job(request, job_id):
    """Allow a user to apply for a job."""
    try:
        job = Job.objects.get(job_id=job_id)
    except Job.DoesNotExist:
        raise Http404("Job not found.") 

    if request.method == 'POST':
        # for job application
        job_application = JobApplication(
            user=request.user, 
            job=job,  
        )
        job_application.save()  

        messages.success(request, "Application submitted successfully!")
        return redirect('portal_job_applications')  

    context = {
        'job': job
    }
    return render(request, 'portal/apply_for_job.html', context)


@login_required
def job_applications(request):
    """Display all job applications by the logged-in user."""
    applications = JobApplication.objects.filter(user=request.user)  

    context = {
        'applications': applications
    }

    return render(request, 'portal/job_applications.html', context)

@login_required
def application_approval(request, application_id):
    """Allow the job poster to approve or reject a job application."""
    application = get_object_or_404(JobApplication.objects.select_related('job', 'user'), id=application_id)

    # Ensure only the job poster can approve/reject applications
    if application.job.user != request.user:
        messages.error(request, "You are not authorized to approve this application.")
        return redirect('portal_my_posted_jobs')

    if request.method == 'POST':
        if 'approve' in request.POST:
            application.approved = True
            application.save()

            messages.success(
                request,
                f"Application for '{application.job.job_name}' approved! The applicant has been notified."
            )

            # Redirect to applicant details page
            return redirect('portal_applicant_details', application_id=application.id)
        
        elif 'reject' in request.POST:
            application.approved = False
            application.save()
            messages.warning(request, f"Application for '{application.job.job_name}' rejected! The applicant has been notified.")
        
        return redirect('portal_user_dashboard')

    context = {
        'application': application,
    }
    return render(request, 'portal/application_approval.html', context)


################JOB APPROVAL ##############


@login_required
def create_job_approval(request, application_id):
    """Allow an admin or employer to approve a job application and set payment details."""
    try:
        job_application = JobApplication.objects.get(id=application_id)
    except JobApplication.DoesNotExist:
        raise Http404("Job application not found.")

    if request.method == 'POST':
        # Get the values from the form
        amount = request.POST['amount']
        paid_status = 'paid_status' in request.POST

        
        job_approval = JobApproved(
            application=job_application,
            amount=amount,
            paid_status=paid_status
        )
        job_approval.save() 

        messages.success(request, "Job application approved successfully!")
        return redirect('portal_job_applications')  

    context = {
        'job_application': job_application
    }
    return render(request, 'portal/create_job_approval.html', context)


@login_required
def job_approval_list(request):
    """Display a list of all job approvals."""
    job_approvals = JobApproved.objects.all()  

    context = {
        'job_approvals': job_approvals
    }

    return render(request, 'portal/job_approval_list.html', context)


@login_required
def update_job_approval(request, approval_id):
    """Allow admin or employer to update job approval details."""
    try:
        job_approval = JobApproved.objects.get(id=approval_id)
    except JobApproved.DoesNotExist:
        raise Http404("Job approval not found.")

    if request.method == 'POST':
        
        job_approval.amount = request.POST['amount']
        job_approval.paid_status = 'paid_status' in request.POST 
        job_approval.save()  

        messages.success(request, "Job approval details updated successfully!")
        return redirect('portal_job_approval_list') 

    context = {
        'job_approval': job_approval
    }
    return render(request, 'portal/update_job_approval.html', context)

@login_required
def service_provider_applications(request):
    """Display all applications for jobs posted by the logged-in user."""
    applications = JobApplication.objects.filter(job__user=request.user).select_related('job', 'user', 'approved_job')

    context = {
        'applications': applications,
    }
    return render(request, 'portal/service_provider_applications.html', context)

@login_required
def my_posted_jobs(request):
    """Display jobs posted by the logged-in user and their application statuses."""
    jobs = Job.objects.filter(user=request.user).prefetch_related('applications__user')

    context = {
        'jobs': jobs,
    }
    return render(request, 'portal/my_posted_jobs.html', context)


################### PENDING JOBS#############################

@login_required
def pending_job_applications(request):
    """Display all pending job applications for the logged-in user."""
    # Fetch all pending job applications for the logged-in user
    pending_applications = JobApplication.objects.filter(user=request.user, approved=False)
    
    context = {
        'pending_applications': pending_applications
    }
    
    return render(request, 'portal/pending_job_applications.html', context)

@login_required
def pending_applications(request):
    """Display all pending job applications for the logged-in user."""
    # Fetch only pending job applications for the logged-in user
    pending_applications = JobApplication.objects.filter(user=request.user, approved=False)
    
    # Check if a POST request has been made to approve or reject an application
    if request.method == 'POST':
        application_id = request.POST.get('application_id')
        application = get_object_or_404(JobApplication, id=application_id)
        
        if 'approve' in request.POST:
            application.approved = True
            application.save()
            messages.success(request, f"Application for {application.job.job_name} approved.")
        elif 'reject' in request.POST:
            application.delete()  # Or handle rejection logic (e.g., change the status)
            messages.success(request, f"Application for {application.job.job_name} rejected.")
    
    # Render the template with pending applications
    return render(request, 'portal/pending_job_applications.html', {'pending_applications': pending_applications})

@login_required
def applicant_details(request, application_id):
    """Display applicant details after approval."""
    try:
        application = JobApplication.objects.select_related('job', 'user').get(id=application_id)
    except JobApplication.DoesNotExist:
        raise Http404("Application not found.")

    # Ensure only the job poster can view the applicant details
    if application.job.user != request.user:
        messages.error(request, "You are not authorized to view this application details.")
        return redirect('portal_my_posted_jobs')

    # Prepare applicant details
    applicant = application.user
    job = application.job

    # Access the related profile
    try:
        user_profile = applicant.job_profile  # Use the related_name from JobProfile
    except JobProfile.DoesNotExist:
        user_profile = None  # Handle users without a profile

    context = {
        'applicant': applicant,
        'user_profile': user_profile,  # Pass None if no profile exists
        'job': job,
    }

    return render(request, 'portal/applicant_details.html', context)

@login_required
def application_status(request):
    """Display the application statuses for the logged-in user."""
    applications = JobApplication.objects.filter(user=request.user).select_related('job')

    context = {
        'applications': applications,
    }
    return render(request, 'portal/application_status.html', context)


def faq(request):
    context = {}
    return render(request, 'portal/faq.html')

@login_required
def edit_job(request, pk):
    job = get_object_or_404(Job, user=request.user, pk=pk)

    if request.method == 'POST':
        job.job_name = request.POST.get('job_name')
        job.job_description = request.POST.get('job_description')
        job.location = request.POST.get('location')
        job.amount = request.POST.get('amount')
        job.save()
        messages.success(request, 'Job updated successfully.')
        return redirect('portal_my_posted_jobs')  # Redirect to the list of posted jobs

    context = {
        'job': job,
    }
    return render(request, 'portal/job_edit.html', context)


@login_required
def delete_job(request, pk):
    job = get_object_or_404(Job, pk=pk, user=request.user)  # Use 'user' instead of 'posted_by'
    if request.method == 'POST':
        job.delete()
        messages.success(request, 'Job deleted successfully!')
        return redirect('portal_my_posted_jobs')  # Redirect to the list of jobs posted by the user
    return redirect('portal_my_posted_jobs')



@login_required
def mark_notifications_as_read(request):
    if request.method == "POST":
        # Update unread notifications for the logged-in user
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'message': 'Notifications marked as read'}, status=200)
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def notifications_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'portal/notification.html', {'notifications': notifications})      

@login_required
def mark_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.notification_text = ""  # Clear the text
    notification.save()
    return redirect('notifications_list')

@login_required
def notifications_details(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'portal/notification_details.html', {'notifications': notifications})      
