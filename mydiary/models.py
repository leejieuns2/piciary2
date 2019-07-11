from django.db import models
from imagekit.models import ImageSpecField # 썸네일 만들 수 있게 해줌
from imagekit.processors import ResizeToFill # 썸네일 크기 조정

# Create your models here.
class Blog(models.Model):
    title = models.CharField(max_length = 20, default='제목없음') 
    image = models.FileField(upload_to='images/')
    image_thumbnail = ImageSpecField(source='image', processors=[ResizeToFill(80, 80)])
    text = models.CharField(max_length = 500)
    writer = models.CharField(max_length = 10, blank=True)
    date = models.DateTimeField("date published")
    
    def sum(self):
        return self.text[:10]