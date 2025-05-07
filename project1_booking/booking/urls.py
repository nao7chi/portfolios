from django.contrib.auth.views import LoginView, LogoutView  
from django.urls import path
from . import views

app_name = 'booking'

urlpatterns = [
    path('', views.MeetingCalendar.as_view(), name='calendar'),
    path('<int:year>/<int:month>/<int:day>/', views.MeetingCalendar.as_view(), name='calendar'),
    path('<int:year>/<int:month>/<int:day>/<int:hour>/', views.Booking.as_view(), name='booking'),
    path('login/', LoginView.as_view(template_name='admin/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('staffpage/', views.StaffPage.as_view(), name='staff_page'),
    path('staffpage/calendar/', views.StaffCalendar.as_view(), name='staff_calendar'),
    path('staffpage/calendar/<int:year>/<int:month>/<int:day>/', views.StaffCalendar.as_view(), name='staff_calendar'),
    path('staffpage/config/<int:year>/<int:month>/<int:day>/', views.DayDetail.as_view(), name='day_detail'),
    path('staffpage/schedule/<int:pk>/', views.StaffSchedule.as_view(), name='staff_schedule'),
    path('staffpage/schedule/<int:pk>/delete/', views.ScheduleDelete.as_view(), name='schedule_delete'),
    path('staffpage/rest/add/<int:year>/<int:month>/<int:day>/<int:hour>/', views.staff_rest_add, name='staff_rest_add'),
]