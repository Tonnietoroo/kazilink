from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from accounts.models import Notification
from kazilink.models import Contact
from portal.models import Job, JobProfile
from django.contrib.auth.models import User
from django.core.mail import send_mail



@staff_member_required
def manage_users(request):
    """Display all users and allow suspension, activation, or deletion."""
    users = User.objects.all()

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        user = get_object_or_404(User, id=user_id)

        if action == 'suspend':
            user.profile.suspended = True
            user.profile.save()
            messages.success(request, f"{user.username} has been suspended.")
        elif action == 'activate':
            user.profile.suspended = False
            user.profile.save()
            messages.success(request, f"{user.username} has been activated.")
        elif action == 'delete':
            user.delete()
            messages.success(request, f"User {user.username} has been deleted.")

    context = {'users': users}
    return render(request, 'administration/manage_users.html', context)

# displays all job profiles
@staff_member_required
def admin_dashboard(request):
    """
    Admin dashboard displaying job profiles and unapproved jobs.
    """
    job_profiles = JobProfile.objects.all()
    unapproved_jobs = Job.objects.filter(approved=False)

    context = {
        'job_profiles': job_profiles,
        'unapproved_jobs': unapproved_jobs,
    }

    return render(request, 'administration/admin_dashboard.html', context)



@staff_member_required
def delete_job_profile(request, profile_id):
    """
    Allow the admin to delete a specific job profile.
    """
    try:
        job_profile = JobProfile.objects.get(id=profile_id)
        job_profile.delete() 
        messages.success(request, f"Job profile for {job_profile.user.username} has been deleted successfully.")
    except JobProfile.DoesNotExist:
        messages.error(request, "Job profile not found.")
    
    return redirect('administration_admin_dashboard')  



@staff_member_required
def view_job_profile(request, profile_id):
    """
    Fetch and display all details of a specific job profile.
    """
    job_profile = get_object_or_404(JobProfile, id=profile_id)

    context = {
        'job_profile': job_profile,  
    }

    return render(request, 'administration/job_profile_details.html', context)

@staff_member_required
def user_account_dashboard(request):
    """
    Display all user accounts in the admin dashboard.
    """
    users = User.objects.all()

    context = {
        'users': users
    }
    return render(request, 'administration/user_account_dashboard.html', context)


@staff_member_required
def delete_user_account(request, user_id):
    """
    Allow the admin to delete a specific user account.
    """
    try:
        user = User.objects.get(id=user_id)
        user.delete()
        messages.success(request, f"User {user.username} has been deleted successfully.")
    except User.DoesNotExist:
        messages.error(request, "User not found.")
    
    return redirect('admin_user_account_dashboard')


@staff_member_required
def view_user_account(request, user_id):
    """
    Display details of a specific user account.
    """
    user = get_object_or_404(User, id=user_id)
    user_profile = user.profile if hasattr(user, 'profile') else None

    context = {
        'user': user,
        'user_profile': user_profile,
    }
    return render(request, 'administration/user_account_detail.html', context)

@login_required
def notifications_view(request):
    """View for users to see their notifications."""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'notifications/notifications.html', {'notifications': notifications})

@staff_member_required
def approve_job(request, job_id):
    """Admin view to approve or reject a job."""
    job = get_object_or_404(Job, job_id=job_id)

    if request.method == 'POST':
        if 'approve' in request.POST:
            job.approved = True
            job.save()

            # Create a notification for the job owner
            Notification.objects.create(
                user=job.user,  # Assuming `user` is the owner of the job in the Job model
                notification_text=f"Your job '{job.job_name}' has been approved!",
                link=f"/jobs/{job_id}/",  # Adjust the URL as per your job detail view
            )
            messages.success(request, f"Job '{job.job_name}' approved!")

        elif 'reject' in request.POST:
            job.approved = False
            job.save()

            # Create a notification for the job owner
            Notification.objects.create(
                user=job.user,
                notification_text=f"Your job '{job.job_name}' has been rejected.",
            )
            messages.warning(request, f"Job '{job.job_name}' rejected!")

        return redirect('administration_admin_dashboard')

    context = {
        'job': job
    }
    return render(request, 'administration/approve_job.html', context)

def view_contacts(request):
    """View for admin to see all contact messages"""
    contacts = Contact.objects.all()
    context = {'contacts': contacts}
    return render(request, 'administration/admin_contacts.html', context)

def pending_request(request):
    context = {}
    return render(request, 'administration/pending_request.html')


def reply_contact(request, id):
    contact = get_object_or_404(Contact, id=id)

    if request.method == 'POST':
        reply_subject = "Re: " + contact.subject
        reply_message = request.POST.get('reply_message')
        
        
        send_mail(
            reply_subject,
            reply_message,
            'tonnytoroitich06@gmail.com', 
            [contact.email],
            fail_silently=False,
        )
        contact.replied = True
        contact.save()

        messages.success(request, "Reply sent successfully!")
        return redirect('admin_contact_messages')  

    return render(request, 'administration/reply_contact.html', {'contact': contact})