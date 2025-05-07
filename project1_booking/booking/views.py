import datetime
from django.shortcuts import render
from django.conf import settings
from django.db.models import Q
from django.shortcuts import get_object_or_404,redirect
from django.utils import timezone
from django.views import generic
from .models import Schedule
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST


class MeetingCalendar(generic.TemplateView):
    template_name = 'booking/calendar.html'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        today = datetime.date.today()

        # どの日を基準にカレンダーを表示するかの処理。
        # 年月日の指定があればそれを、なければ今日からの表示。
        year  = self.kwargs.get('year')
        month = self.kwargs.get('month')
        day   = self.kwargs.get('day')
        if year and month and day:
            base_date = datetime.date(year=year, month=month, day=day)
        else:
            base_date = today

        # カレンダーは1週間分表示するので、基準日から1週間の日付を作成しておく
        days = [base_date + datetime.timedelta(days=day) for day in range(7)]
        start_day = days[0]
        end_day = days[-1]

        # 13時から19時まで1時間刻み、1週間分の、値がTrueなカレンダーを作る
        calendar = {}
        for hour in range(13, 20):
            row = {}
            for day in days:
                row[day] = True
            calendar[hour] = row

        # カレンダー表示する最初と最後の日時の間にある予約を取得する
        start_time = datetime.datetime.combine(start_day, datetime.time(hour=12, minute=59, second=59))
        end_time   = datetime.datetime.combine(end_day,   datetime.time(hour=20, minute=0, second=0))


        for schedule in Schedule.objects.exclude(Q(start__gt=end_time) | Q(start__lt=start_time)):
            local_dt = timezone.localtime(schedule.start)
            booking_date = local_dt.date()
            booking_hour = local_dt.hour
            if booking_hour in calendar and booking_date in calendar[booking_hour]:
                calendar[booking_hour][booking_date] = False

        context['calendar'] = calendar
        context['days'] = days
        context['start_day'] = start_day
        context['end_day'] = end_day
        context['before'] = days[0] - datetime.timedelta(days=7)
        context['next'] = days[-1] + datetime.timedelta(days=1)
        context['today'] = today
        context['public_holidays'] = settings.PUBLIC_HOLIDAYS
        return context

class Booking(generic.CreateView):
    model = Schedule
    fields = ('name','class_num','id_num')
    template_name = 'booking/booking.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):

        year  = self.kwargs.get('year')
        month = self.kwargs.get('month')
        day   = self.kwargs.get('day')
        hour  = self.kwargs.get('hour')
        start = datetime.datetime(year=year, month=month, day=day, hour=hour)

        if Schedule.objects.filter( start=start).exists():
            messages.error(self.request, 'ダブルブッキングしてしまいました。別の日時はどうですか。')
        else:
            schedule = form.save(commit=False)
            schedule.start = start
            schedule.save()
        return redirect('booking:calendar')

class StaffPage(LoginRequiredMixin, generic.TemplateView):
    template_name = 'booking/staff.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['schedule_list'] = Schedule.objects.filter(start__gte=timezone.now()).order_by('start')
        return context

class StaffCalendar(MeetingCalendar):
    template_name = 'booking/staff_calendar.html'

class DayDetail(generic.TemplateView):
    template_name = 'booking/day_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        day = self.kwargs.get('day')
        date = datetime.date(year=year, month=month, day=day)

        # 9時から17時まで1時間刻みのカレンダーを作る
        calendar = {}
        for hour in range(13, 20):
            calendar[hour] = []

        # カレンダー表示する最初と最後の日時の間にある予約を取得する
        start_time = datetime.datetime.combine(date, datetime.time(hour=12, minute=59, second=59))
        end_time = datetime.datetime.combine(date, datetime.time(hour=20, minute=0, second=0))
        for schedule in Schedule.objects.exclude(Q(start__gt=end_time) | Q(start__lt=start_time)):
            local_dt = timezone.localtime(schedule.start)
            booking_date = local_dt.date()
            booking_hour = local_dt.hour
            if booking_hour in calendar:
                calendar[booking_hour].append(schedule)

        context['calendar'] = calendar
        return context

class StaffSchedule(generic.UpdateView):
    model = Schedule
    fields = ('start', 'name')
    success_url = reverse_lazy('booking:staff_page')

class ScheduleDelete(generic.DeleteView):
    model = Schedule
    success_url = reverse_lazy('booking:staff_page')

@require_POST
def staff_rest_add(request,year, month, day, hour):
    
    start = datetime.datetime(year=year, month=month, day=day, hour=hour)
    Schedule.objects.create(start=start, class_num=0, id_num = 0,name='お休み(システムによる追加)')
    return redirect('booking:day_detail', year=year, month=month, day=day)
