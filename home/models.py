from django.db import models

# Create your models here.

class Road(models.Model):
    road_id = models.CharField(max_length=50, unique=True)
    pci = models.IntegerField(verbose_name='Pavement Condition Index')
    location = models.CharField()

    def __str__(self):
        return self.road_id

class Image(models.Model):
    road = models.ForeignKey(Road, on_delete=models.CASCADE, related_name='images')
    image_id = models.CharField(max_length=50)
    # image = models.ImageField()

    class Meta:
        unique_together = (('road', 'image_id'),)

    def __str__(self):
        return f'{self.image_id} ({self.road.road_id})'

class Issue(models.Model):
    issue_id = models.CharField(max_length=50, unique=True)  # For ordering and grouping
    name = models.CharField()

    def __str__(self):
        return self.name

class IssueDetail(models.Model):
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='issues')
    issue = models.ForeignKey(Issue, on_delete=models.PROTECT, related_name='details')
    count = models.IntegerField()
    quality = models.IntegerField()  # On a scale of 1-10

    class Meta:
        unique_together = (('image', 'issue'),)

    def __str__(self):
        return f'{self.image.image_id} - {self.issue.name}'

