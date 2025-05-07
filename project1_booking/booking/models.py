from django.conf import settings
from django.db import models
from django.utils import timezone

class Schedule(models.Model):
    """予約スケジュール"""
    start     = models.DateTimeField('開始時間')
    class_num = models.IntegerField(default=14)   #組
    id_num    = models.IntegerField(default=1)    #番号
    name      = models.CharField('予約者名', max_length=255)

    def __str__(self):
        start = timezone.localtime(self.start).strftime('%Y/%m/%d %H:%M:%S')

        #ex). 山田太郎,14組1番:2025/04/01 12:00:00
        return f'{self.name},{self.class_num} 組 {self.id_num} 番 : {start}'