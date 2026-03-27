from django.db.models import Count, Q
from django.db.models.functions import TruncDay
from django.utils import timezone
from datetime import timedelta
from analytics.models import FeatureClick
from django.contrib.auth import get_user_model

User = get_user_model()

class AnalyticsService:
    """Service for analytics aggregation and filtering."""
    
    @staticmethod
    def get_age_group_filter(age_group):
        """Return Q object for age group filtering."""
        if age_group == '<18':
            return Q(user__age__lt=18)
        elif age_group == '18-40':
            return Q(user__age__gte=18, user__age__lte=40)
        elif age_group == '>40':
            return Q(user__age__gt=40)
        return Q()

    @staticmethod
    def get_bar_chart_data(filters):
        """
        Group feature clicks by feature_name and return counts.
        
        Args:
            filters: dict with start_date, end_date, age_group, gender
            
        Returns:
            list of dicts with feature_name and count
        """
        queryset = FeatureClick.objects.all()
        
        # Apply date filters
        if filters.get('start_date'):
            queryset = queryset.filter(timestamp__date__gte=filters['start_date'])
        if filters.get('end_date'):
            queryset = queryset.filter(timestamp__date__lte=filters['end_date'])
        
        # Apply demographic filters
        if filters.get('age_group'):
            age_filter = AnalyticsService.get_age_group_filter(filters['age_group'])
            queryset = queryset.filter(age_filter)
        
        if filters.get('gender'):
            queryset = queryset.filter(user__gender=filters['gender'])
        
        # Aggregate by feature_name
        data = (
            queryset
            .values('feature_name')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        return [
            {'feature_name': item['feature_name'], 'count': item['count']}
            for item in data
        ]

    @staticmethod
    def get_line_chart_data(filters):
        """
        Group feature clicks by date for a specific feature.
        
        Args:
            filters: dict with start_date, end_date, age_group, gender, feature_name
            
        Returns:
            list of dicts with date and count
        """
        queryset = FeatureClick.objects.all()
        
        # Apply date filters
        if filters.get('start_date'):
            queryset = queryset.filter(timestamp__date__gte=filters['start_date'])
        if filters.get('end_date'):
            queryset = queryset.filter(timestamp__date__lte=filters['end_date'])
        
        # Apply demographic filters
        if filters.get('age_group'):
            age_filter = AnalyticsService.get_age_group_filter(filters['age_group'])
            queryset = queryset.filter(age_filter)
        
        if filters.get('gender'):
            queryset = queryset.filter(user__gender=filters['gender'])
        
        # Filter by specific feature if provided
        if filters.get('feature_name'):
            queryset = queryset.filter(feature_name=filters['feature_name'])
        
        # Aggregate by date using TruncDay
        data = (
            queryset
            .annotate(date=TruncDay('timestamp'))
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date')
        )
        
        return [
            {
                'date': item['date'].strftime('%Y-%m-%d') if item['date'] else None,
                'count': item['count']
            }
            for item in data
        ]

    @staticmethod
    def get_user_stats(filters):
        """
        Get total unique users and total clicks.
        
        Args:
            filters: dict with start_date, end_date, age_group, gender
            
        Returns:
            dict with user_count and total_clicks
        """
        queryset = FeatureClick.objects.all()
        
        if filters.get('start_date'):
            queryset = queryset.filter(timestamp__date__gte=filters['start_date'])
        if filters.get('end_date'):
            queryset = queryset.filter(timestamp__date__lte=filters['end_date'])
        
        if filters.get('age_group'):
            age_filter = AnalyticsService.get_age_group_filter(filters['age_group'])
            queryset = queryset.filter(age_filter)
        
        if filters.get('gender'):
            queryset = queryset.filter(user__gender=filters['gender'])
        
        unique_users = queryset.values('user').distinct().count()
        total_clicks = queryset.count()
        
        return {
            'unique_users': unique_users,
            'total_clicks': total_clicks
        }