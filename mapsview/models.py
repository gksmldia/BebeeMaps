from django.db import models
from django.utils import timezone

class BlogData(models.Model):
    name = models.CharField(max_length=100) # 길이 제한이 있는 문자열
    content = models.TextField()             # 길이 제한이 없는 문자열
    link = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True) # 해당 레코드 생성시 현재 시간 자동저장
    updated_at = models.DateTimeField(auto_now=True) # 해당 레코드 갱신시 현재 시간 자동저장
    # DB에서는 길이제한 유무에 따라서 문자열 필드타입이 다른다.
    # 길이 제한이 없는 문자열을 많이 쓰면 성능이 좋지 않다.

    def publish(self):
        self.updated_at = timezone.now()
        self.save()

    def __str__(self):
        return self.name