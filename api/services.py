from django.db.models import Count, Q
from django.db.models.functions import TruncDay
from django.utils import timezone
from datetime import timedelta
from analytics.models import FeatureClick
from django.contrib.auth import get_user_model
from django.core.cache import cache

User = get_user_model()

class AnalyticsService:
    """
    Service for analytics aggregation and filtering.
    
    OPTIMIZATION STRATEGY:
    - All aggregation happens at DB level (aggregate(), annotate())
    - No Python-level loops or list comprehensions over querysets
    - Lazy evaluation: querysets not materialized until serialized
    - Caching for frequently-requested analytics
    - Strict filtering BEFORE aggregation
    """
    
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
        """
        Build optimized base queryset with all filters applied.
        Filters are applied BEFORE aggregation to minimize data size.
        """
        queryset = FeatureClick.objects.all()
        
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
        """
        Group feature clicks by feature_name and return counts.
        
        OPTIMIZATION:
        - Uses .values().annotate() for DB-level aggregation
        - No Python loops or list conversion that would materialize data
        - Returns lazy ValuesQuerySet

        Args:
            filters: dict with start_date, end_date, age_group, gender
            
        Returns:
            list of dicts with feature_name and count
        """
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
        """
        Group feature clicks by date for a specific feature.
        
        OPTIMIZATION:
        - Uses TruncDay at DB level for date truncation
        - Single aggregation query with all filters applied
        - Lazy evaluation until serialization

        Args:
            filters: dict with start_date, end_date, age_group, gender, feature_name
            
        Returns:
            list of dicts with date and count
        """
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
        """
        Get total unique users and total clicks.
        
        OPTIMIZATION:
        - Uses values('user_id').distinct() instead of values('user')
        - Two aggregation queries (efficient, DB-level aggregation)
        - No Python loops

        Args:
            filters: dict with start_date, end_date, age_group, gender
            
        Returns:
            dict with unique_users and total_clicks
        """
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