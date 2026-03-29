from django.db.models import Count, Q
from django.db.models.functions import TruncDay
from django.utils import timezone
from datetime import timedelta
from analytics.models import FeatureClick
from django.contrib.auth import get_user_model
from django.core.cache import cache

User = get_user_model()

class AnalyticsService:
    # Cache timeout for analytics queries (balance freshness vs memory)
    CACHE_TIMEOUT = 60  # seconds
    
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
    def _build_base_queryset(filters):
        
        # Apply date filters EARLY (critical for memory efficiency)
        if filters.get('start_date'):
            queryset = queryset.filter(timestamp__date__gte=filters['start_date'])
        if filters.get('end_date'):
            queryset = queryset.filter(timestamp__date__lte=filters['end_date'])
        
        # Apply demographic filters EARLY
        if filters.get('age_group'):
            age_filter = AnalyticsService.get_age_group_filter(filters['age_group'])
            queryset = queryset.filter(age_filter)
        
        if filters.get('gender'):
            queryset = queryset.filter(user__gender=filters['gender'])
        
        return queryset

    @staticmethod
    def get_bar_chart_data(filters):
        # Check cache first
        cache_key = f"bar_chart_{hash(str(sorted(filters.items())))}"
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Build base queryset with filters
        queryset = AnalyticsService._build_base_queryset(filters)
        
        # Aggregate by feature_name at DB level - single query
        data = queryset.values('feature_name').annotate(count=Count('id')).order_by('-count')
        
        # Convert to list of dicts ONLY when serializing (forced by DRF)
        result = [
            {'feature_name': item['feature_name'], 'count': item['count']}
            for item in data
        ]
        
        # Cache result
        cache.set(cache_key, result, AnalyticsService.CACHE_TIMEOUT)
        return result

    @staticmethod
    def get_line_chart_data(filters):
        # Check cache first
        cache_key = f"line_chart_{hash(str(sorted(filters.items())))}"
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Build base queryset with filters
        queryset = AnalyticsService._build_base_queryset(filters)
        
        # Filter by specific feature if provided
        if filters.get('feature_name'):
            queryset = queryset.filter(feature_name=filters['feature_name'])
        
        # Aggregate by date using TruncDay - single query at DB
        data = (
            queryset
            .annotate(date=TruncDay('timestamp'))
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date')
        )
        
        # Format dates for JSON serialization
        result = [
            {
                'date': item['date'].strftime('%Y-%m-%d') if item['date'] else None,
                'count': item['count']
            }
            for item in data
        ]
        
        # Cache result
        cache.set(cache_key, result, AnalyticsService.CACHE_TIMEOUT)
        return result

    @staticmethod
    def get_user_stats(filters):
        # Check cache first
        cache_key = f"stats_{hash(str(sorted(filters.items())))}"
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Build base queryset with filters
        queryset = AnalyticsService._build_base_queryset(filters)
        
        # Get unique users - efficient: queries user_id column only
        unique_users = queryset.values('user_id').distinct().count()
        
        # Get total clicks
        total_clicks = queryset.count()
        
        result = {
            'unique_users': unique_users,
            'total_clicks': total_clicks
        }
        
        # Cache result
        cache.set(cache_key, result, AnalyticsService.CACHE_TIMEOUT)
        return result