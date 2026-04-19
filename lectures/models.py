from django.db import models


class Course(models.Model):
    name = models.CharField(max_length=255)


class Lecture(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lectures')
    moodle_url = models.URLField()
    date = models.DateField()
    raw_transcript = models.TextField()


class Summary(models.Model):
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, related_name='summaries')
    executive_summary = models.TextField()
    intuition_and_concepts = models.TextField()
    practical_examples = models.TextField()
