from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError

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
    """
    Authentication endpoints: register and login.
    """
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'])
    def register(self, request):
        """
        POST /api/auth/register/
        Create a new user account.
        """
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
        """
        POST /api/auth/login/
        Authenticate user and return JWT tokens.
        """
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
        """
        POST /api/auth/logout/
        Invalidate refresh token (optional).
        """
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
        """
        GET /api/auth/me/
        Get current authenticated user details.
        """
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TrackingViewSet(viewsets.ViewSet):
    """
    Feature tracking endpoint.
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def track(self, request):
        """
        POST /api/tracking/track/
        Record a feature click for the authenticated user.
        """
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
        """
        GET /api/tracking/my_clicks/?limit=10
        Get all feature clicks for the authenticated user.
        """
        limit = request.query_params.get('limit', 50)
        try:
            limit = int(limit)
        except ValueError:
            limit = 50
        
        clicks = FeatureClick.objects.filter(user=request.user)[:limit]
        serializer = FeatureClickSerializer(clicks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AnalyticsViewSet(viewsets.ViewSet):
    """
    Analytics endpoints for dashboard data.
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """
        GET /api/analytics/analytics/
        
        Query Parameters:
        - start_date (YYYY-MM-DD)
        - end_date (YYYY-MM-DD)
        - age_group (<18, 18-40, >40)
        - gender (Male, Female, Other)
        - feature_name (optional, for line chart filtering)
        
        Returns:
            {
                "bar_chart": [...],
                "line_chart": [...],
                "stats": {"unique_users": X, "total_clicks": Y}
            }
        """
        # Validate query parameters
        serializer = AnalyticsFilterSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        filters = serializer.validated_data
        
        try:
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
        """
        GET /api/analytics/features/
        Get distinct feature names with their click counts.
        """
        features = (
            FeatureClick.objects
            .values('feature_name')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        return Response({
            'features': list(features)
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def health(self, request):
        """
        GET /api/analytics/health/
        Health check endpoint.
        """
        return Response({
            'status': 'healthy',
            'message': 'Analytics API is running.'
        }, status=status.HTTP_200_OK)