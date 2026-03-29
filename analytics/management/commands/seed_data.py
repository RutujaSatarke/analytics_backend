import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from analytics.models import FeatureClick

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed the database with test users and feature clicks for analytics demo'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=75,  # Increased from 10 to 75 for better analytics
            help='Number of users to create (default: 75)'
        )
        parser.add_argument(
            '--clicks',
            type=int,
            default=1500,  # Increased from 150 to 1500 for richer analytics
            help='Number of feature clicks to create (default: 1500)'
        )

    def handle(self, *args, **options):
        users_count = options['users']
        clicks_count = options['clicks']

        self.stdout.write(self.style.HTTP_INFO(f'Starting data seeding...'))

        # ============================================================
        # CREATE USERS WITH REALISTIC DEMOGRAPHICS
        # ============================================================
        self.stdout.write(self.style.HTTP_INFO(f'Creating {users_count} users with realistic demographics...'))

        users = []

        # Age distribution: More realistic bell curve
        age_ranges = {
            '18-25': 25,   # Young adults
            '26-35': 30,   # Working professionals
            '36-45': 25,   # Mid-career
            '46-60': 15,   # Senior professionals
            '61+': 5,      # Older users
        }

        # Gender distribution: More balanced
        gender_weights = {
            'Male': 45,
            'Female': 45,
            'Other': 10,
        }

        # Create users with weighted demographics
        for i in range(1, users_count + 1):
            username = f'user{i}'
            email = f'user{i}@example.com'

            # Weighted age selection
            age_range = random.choices(
                list(age_ranges.keys()),
                weights=list(age_ranges.values())
            )[0]

            if age_range == '18-25':
                age = random.randint(18, 25)
            elif age_range == '26-35':
                age = random.randint(26, 35)
            elif age_range == '36-45':
                age = random.randint(36, 45)
            elif age_range == '46-60':
                age = random.randint(46, 60)
            else:  # 61+
                age = random.randint(61, 80)

            # Weighted gender selection
            gender = random.choices(
                list(gender_weights.keys()),
                weights=list(gender_weights.values())
            )[0]

            # More realistic names
            first_names = [
                'Alex', 'Jordan', 'Taylor', 'Morgan', 'Casey', 'Riley', 'Avery', 'Quinn',
                'Jamie', 'Cameron', 'Dakota', 'Skyler', 'Reese', 'Rowan', 'Sage', 'Logan',
                'Emma', 'Olivia', 'Sophia', 'Ava', 'Isabella', 'Mia', 'Charlotte', 'Amelia',
                'Harper', 'Evelyn', 'Abigail', 'Emily', 'Elizabeth', 'Sofia', 'Grace', 'Chloe',
                'Liam', 'Noah', 'Oliver', 'James', 'Elijah', 'William', 'Benjamin', 'Lucas',
                'Henry', 'Theodore', 'Jack', 'Levi', 'Alexander', 'Jackson', 'Mateo', 'Daniel'
            ]

            last_names = [
                'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
                'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson',
                'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson',
                'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson', 'Walker'
            ]

            first_name = random.choice(first_names)
            last_name = random.choice(last_names)

            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'age': age,
                    'gender': gender,
                    'first_name': first_name,
                    'last_name': last_name,
                }
            )

            if created:
                user.set_password('testpass123')
                user.save()
                users.append(user)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Created user: {username} ({first_name} {last_name}, Age: {age}, Gender: {gender})'
                    )
                )
            else:
                users.append(user)
                self.stdout.write(
                    self.style.WARNING(f'⚠ User already exists: {username}')
                )

        # ============================================================
        # CREATE FEATURE CLICKS WITH REALISTIC PATTERNS
        # ============================================================
        self.stdout.write(self.style.HTTP_INFO(f'Creating {clicks_count} feature clicks with realistic usage patterns...'))

        features = [choice[0] for choice in FeatureClick.FEATURE_CHOICES]

        # Feature popularity weights (some features used more than others)
        feature_weights = {
            'date_filter': 25,      # Most popular
            'gender_filter': 20,    # Very common
            'age_filter': 20,       # Very common
            'bar_chart_click': 15,  # Popular
            'line_chart_click': 12, # Popular
            'export_data': 8,       # Less common
        }

        # User activity levels (power law distribution - few very active, many less active)
        activity_levels = {
            'power_user': {'weight': 10, 'clicks_per_user': 50},    # 10% of users, very active
            'active': {'weight': 25, 'clicks_per_user': 20},        # 25% of users, active
            'regular': {'weight': 35, 'clicks_per_user': 8},        # 35% of users, regular
            'casual': {'weight': 30, 'clicks_per_user': 3},         # 30% of users, casual
        }

        # Assign activity levels to users
        user_activity = {}
        for user in users:
            activity_type = random.choices(
                list(activity_levels.keys()),
                weights=[level['weight'] for level in activity_levels.values()]
            )[0]
            user_activity[user.id] = activity_levels[activity_type]

        feature_clicks_created = 0
        total_clicks_needed = clicks_count

        # Create clicks based on user activity levels
        for user in users:
            activity = user_activity[user.id]
            user_clicks = min(activity['clicks_per_user'], total_clicks_needed)

            for _ in range(user_clicks):
                if total_clicks_needed <= 0:
                    break

                # Weighted feature selection
                feature_name = random.choices(
                    list(feature_weights.keys()),
                    weights=list(feature_weights.values())
                )[0]

                # More recent clicks more likely (recency bias)
                days_back = random.choices(
                    [0, 1, 2, 3, 7, 14, 30],
                    weights=[30, 25, 20, 15, 5, 3, 2]  # Recent days more likely
                )[0]

                hours_back = random.randint(0, 23)
                minutes_back = random.randint(0, 59)

                timestamp = timezone.now() - timedelta(
                    days=days_back,
                    hours=hours_back,
                    minutes=minutes_back
                )

                FeatureClick.objects.create(
                    user=user,
                    feature_name=feature_name,
                    timestamp=timestamp
                )

                feature_clicks_created += 1
                total_clicks_needed -= 1

                if feature_clicks_created % 100 == 0:
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Created {feature_clicks_created}/{clicks_count} feature clicks')
                    )

        # ============================================================
        # SUMMARY
        # ============================================================
        self.stdout.write(self.style.SUCCESS(
            f'\n🎉 Data seeding completed!'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'   📊 Users created: {len(users)}'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'   🖱️  Feature clicks created: {feature_clicks_created}'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'   📈 Average clicks per user: {feature_clicks_created / len(users):.1f}'
        ))

        # Show feature distribution
        feature_counts = {}
        for feature in features:
            count = FeatureClick.objects.filter(feature_name=feature).count()
            feature_counts[feature] = count

        self.stdout.write(self.style.HTTP_INFO('\n📊 Feature usage distribution:'))
        for feature, count in sorted(feature_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / feature_clicks_created) * 100
            self.stdout.write(f'   {feature}: {count} clicks ({percentage:.1f}%)')