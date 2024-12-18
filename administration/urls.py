from django.urls import path
from . import views


urlpatterns = [
    path('', views.admin_dashboard, name="administration_admin_dashboard"),
    path('manage-users/', views.manage_users, name='administration_manage_users'),
    
    path('admin/approve-job/<int:job_id>/', views.approve_job, name='administration_approve_job'),
    path('job-profile/<int:profile_id>/view/', views.view_job_profile, name='administration_view_job_profile'),
    path('admin/job_profile/delete/<int:profile_id>/', views.delete_job_profile, name='admin_delete_job_profile'),
    
    path('users/', views.user_account_dashboard, name='admin_user_account'),
    path('users/<int:user_id>/view/', views.view_user_account, name='admin_view_user_account'),
    path('users/<int:user_id>/delete/', views.delete_user_account, name='admin_delete_user_account'),
    
    path('admin/contacts/', views.view_contacts, name='administration_admin_contacts'),
    path('pending_request/', views.pending_request, name='administration_pending_request'),
    path('reply_contact/<int:id>/', views.reply_contact, name='reply_contact'),
    path('delete_contact/<int:id>/', views.delete_contact, name='delete_contact'),
    ]