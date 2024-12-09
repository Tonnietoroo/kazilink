from django.urls import path
from . import views



urlpatterns = [
    path('', views.user_dashboard, name="portal_user_dashboard"),
    path('job_profile_create/', views.create_job_profile, name='portal_create_job_profile'),
    path('job_profile_update/', views.update_job_profile, name='portal_update_job_profile'),
    
    path('create-job/', views.create_job, name='portal_create_job'),
    path('jobs/', views.job_list, name='portal_job_list'),
    path('job/<int:job_id>/', views.job_details, name='portal_job_details'),
    
    path('job/<int:job_id>/apply/', views.apply_for_job, name='portal_apply_for_job'),
    path('job/applications/', views.job_applications, name='portal_job_applications'),
    path('application/<int:application_id>/approval/', views.application_approval, name='portal_application_approval'),
    path('application/<int:application_id>/details/', views.applicant_details, name='portal_applicant_details'),
    path('applications/service-provider/', views.service_provider_applications, name='portal_service_provider_applications'),
    # path('pending-job-applications/', views.pending_job_applications, name='portal_pending_job_applications'),
    path('my-posted-jobs/', views.my_posted_jobs, name='portal_my_posted_jobs'),
    path('job/approval/create/<int:application_id>/', views.create_job_approval, name='portal_create_job_approval'),
    path('job/approval/list/', views.job_approval_list, name='portal_job_approval_list'),
    path('job/approval/update/<int:approval_id>/', views.update_job_approval, name='portal_update_job_approval'),
    path('application-status/', views.application_status, name='portal_application_status'),
    path('faq/', views.faq, name='portal_faq'),
    path('job/<int:pk>/edit/', views.edit_job, name='portal_job_edit'),
    path('job/<int:pk>/delete/', views.delete_job, name='portal_job_delete'),
    path('notifications/mark-as-read/', views.mark_notifications_as_read, name='mark_notifications_as_read'),
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/mark_as_read/<int:notification_id>/', views.mark_as_read, name='mark_as_read'),
    path('notifications_details/', views.notifications_details, name='notifications_details'),

]