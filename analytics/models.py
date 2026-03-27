from django.db import models
from django.conf import settings
from django.core.validators import MinLengthValidator

class FeatureClick(models.Model):
    FEATURE_CHOICES = [
        ('date_filter', 'Date Filter'),
        ('gender_filter', 'Gender Filter'),
        ('age_filter', 'Age Filter'),
        ('bar_chart_click', 'Bar Chart Click'),
        ('line_chart_click', 'Line Chart Click'),
        ('export_data', 'Export Data'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='feature_clicks'
    )
    feature_name = models.CharField(
        max_length=50,
        choices=FEATURE_CHOICES,
        validators=[MinLengthValidator(1)]
    )
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        verbose_name = "Feature Click"
        verbose_name_plural = "Feature Clicks"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['feature_name', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.feature_name} at {self.timestamp}"