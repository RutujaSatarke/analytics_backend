from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError
from django.core.cache import cache
from django.db.models import Count

from analytics.models import FeatureClick
from api.serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserDetailSerializer,
    FeatureClickSerializer,
    AnalyticsFilterSerializer,
)
from api.services import AnalyticsService

User = get_user_model()


class AuthViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserDetailSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message': 'User registered successfully.'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
            if user is not None:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'user': UserDetailSerializer(user).data,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'message': 'Login successful.'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Invalid username or password.'
                }, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {'message': 'Logout successful.'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TrackingViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def track(self, request):
        serializer = FeatureClickSerializer(data=request.data)
        if serializer.is_valid():
            # Attach the current user to the feature click
            feature_click = FeatureClick.objects.create(
                user=request.user,
                feature_name=serializer.validated_data['feature_name']
            )
            return Response(
                FeatureClickSerializer(feature_click).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def my_clicks(self, request):
        limit = request.query_params.get('limit', 25)  # Default 25, max 50
        try:
            limit = int(limit)
            # Enforce strict limit - never load more than 50 items
            limit = min(limit, 50)
        except (ValueError, TypeError):
            limit = 25
        
        # Optimize query: fetch minimal fields, paginate strictly
        clicks = (
            FeatureClick.objects
            .filter(user=request.user)
            .select_related('user')  # Avoid N+1 on user lookups
            .only('id', 'user_id', 'user__username', 'feature_name', 'timestamp')
            [:limit]
        )
        
        serializer = FeatureClickSerializer(clicks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AnalyticsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def analytics(self, request):
        # Validate query parameters
        serializer = AnalyticsFilterSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        filters = serializer.validated_data
        
        try:
            # All heavy lifting happens in AnalyticsService (DB-level aggregation + caching)
            bar_chart = AnalyticsService.get_bar_chart_data(filters)
            line_chart = AnalyticsService.get_line_chart_data(filters)
            stats = AnalyticsService.get_user_stats(filters)
            
            return Response({
                'bar_chart': bar_chart,
                'line_chart': line_chart,
                'stats': stats,
                'filters': filters
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': f'Analytics error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def features(self, request):
        cache_key = 'features_list'
        features = cache.get(cache_key)
        
        if features is None:
            # DB-level aggregation: single query
            features = list(
                FeatureClick.objects
                .values('feature_name')
                .annotate(count=Count('id'))
                .order_by('-count')
            )
            cache.set(cache_key, features, 300)  # Cache for 5 minutes
        
        return Response({
            'features': features
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def health(self, request):
        return Response({
            'status': 'healthy',
            'message': 'Analytics API is running.'
        }, status=status.HTTP_200_OK)