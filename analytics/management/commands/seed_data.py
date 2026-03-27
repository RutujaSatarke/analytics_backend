import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from analytics.models import FeatureClick

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed the database with test users and feature clicks'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='Number of users to create (default: 10)'
        )
        parser.add_argument(
            '--clicks',
            type=int,
            default=150,
            help='Number of feature clicks to create (default: 150)'
        )

    def handle(self, *args, **options):
        users_count = options['users']
        clicks_count = options['clicks']

        self.stdout.write(self.style.HTTP_INFO(f'Starting data seeding...'))

        # ============================================================
        # CREATE USERS
        # ============================================================
        self.stdout.write(self.style.HTTP_INFO(f'Creating {users_count} users...'))
        
        users = []
        for i in range(1, users_count + 1):
            username = f'user{i}'
            email = f'user{i}@example.com'
            age = random.randint(15, 70)
            gender = random.choice(['Male', 'Female', 'Other'])
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'age': age,
                    'gender': gender,
                    'first_name': f'Test{i}',
                    'last_name': f'User{i}',
                }
            )
            
            if created:
                user.set_password('testpass123')
                user.save()
                users.append(user)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Created user: {username} (Age: {age}, Gender: {gender})'
                    )
                )
            else:
                users.append(user)
                self.stdout.write(
                    self.style.WARNING(f'⚠ User already exists: {username}')
                )

        # ============================================================
        # CREATE FEATURE CLICKS
        # ============================================================
        self.stdout.write(self.style.HTTP_INFO(f'Creating {clicks_count} feature clicks...'))
        
        features = [choice[0] for choice in FeatureClick.FEATURE_CHOICES]
        feature_clicks_created = 0
        
        for i in range(clicks_count):
            user = random.choice(users)
            feature_name = random.choice(features)
            
            # Random timestamp within last 30 days
            days_back = random.randint(0, 30)
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
            
            if (i + 1) % 25 == 0:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created {i + 1}/{clicks_count} feature clicks')
                )

        # ============================================================
        # SUMMARY
        # ============================================================
        self.stdout.write(self.style.SUCCESS('✓ Data seeding completed!'))
        self.stdout.write(
            self.style.SUCCESS(
                f'Summary:\n'
                f'  • Users created: {len(users)}\n'
                f'  • Feature clicks created: {feature_clicks_created}\n'
            )
        )