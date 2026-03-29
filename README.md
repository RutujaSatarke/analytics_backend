# Analytics Dashboard Backend API

A high-performance Django REST Framework backend optimized for 512MB RAM deployment, featuring JWT authentication, real-time analytics, and memory-efficient data processing.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL (production) or SQLite (development)
- Git

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd analytics-api
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment variables** (optional)
   Create a `.env` file:
   ```bash
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=sqlite:///db.sqlite3  # or PostgreSQL URL
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Generate sample data** (see Seed Instructions below)
   ```bash
   python manage.py seed_data
   ```

7. **Start development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the API**
   - API Documentation: `http://localhost:8000/api/`
   - Admin Panel: `http://localhost:8000/admin/` (if enabled)

## 🏗️ Architecture Overview

### Core Technologies
- **Django 5.2**: Web framework with ORM
- **Django REST Framework**: API development toolkit
- **Simple JWT**: Token-based authentication
- **PostgreSQL**: Production database (with SQLite fallback)
- **Gunicorn**: Production WSGI server
- **WhiteNoise**: Static file serving

### Architectural Choices

#### 1. **Memory-Optimized Design**
- **Single Gunicorn Worker**: Critical for 512MB RAM constraint
- **Minimal Middleware**: Removed Django sessions, admin, messages framework
- **Lazy QuerySets**: Database aggregation instead of Python loops
- **In-Memory Caching**: 60-second cache for analytics queries

#### 2. **Stateless API Design**
- **JWT Authentication**: No server-side sessions required
- **RESTful Endpoints**: Predictable, cacheable API design
- **Database-Level Aggregation**: Analytics computed at DB level, not in Python

#### 3. **Production-Ready Configuration**
- **Environment-Based Settings**: Different configs for dev/prod
- **Connection Pooling**: Efficient database connections
- **Logging Optimization**: WARNING level to reduce memory overhead
- **Static File Optimization**: Compressed serving with WhiteNoise

#### 4. **Scalable Data Model**
- **FeatureClick Model**: Efficient tracking with proper indexing
- **User Demographics**: Age, gender for advanced filtering
- **Timestamp Indexing**: Fast time-based queries

### Database Schema
```sql
-- Users with demographics
CREATE TABLE users_customuser (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE,
    email VARCHAR(254),
    age INTEGER,
    gender VARCHAR(10),
    created_at TIMESTAMP
);

-- Feature clicks with indexing
CREATE TABLE analytics_featureclick (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users_customuser(id),
    feature_name VARCHAR(50),
    timestamp TIMESTAMP,
    INDEX idx_user_timestamp (user_id, timestamp),
    INDEX idx_feature_timestamp (feature_name, timestamp)
);
```

## 🌱 Seed Instructions

Generate realistic dummy data for testing and demonstration:

### Basic Usage
```bash
# Generate default data (75 users, 1500 clicks)
python manage.py seed_data
```

### Custom Data Generation
```bash
# Generate more users and clicks
python manage.py seed_data --users 200 --clicks 5000

# Generate minimal data for testing
python manage.py seed_data --users 10 --clicks 100
```

### What Gets Created
- **75 users** with realistic demographics (age, gender, names)
- **1,500 feature clicks** distributed across 6 feature types
- **Power-law activity distribution**: Few power users, many casual users
- **Realistic feature popularity**: Date filters most used, exports least used
- **Time-based patterns**: Recent activity more likely

### Sample Output
```
🎉 Data seeding completed!
   📊 Users created: 75
   🖱️  Feature clicks created: 1500
   📈 Average clicks per user: 20.0

📊 Feature usage distribution:
   date_filter: 375 clicks (25.0%)
   gender_filter: 300 clicks (20.0%)
   age_filter: 300 clicks (20.0%)
   bar_chart_click: 225 clicks (15.0%)
   line_chart_click: 180 clicks (12.0%)
   export_data: 120 clicks (8.0%)
```

## 📊 API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - Token invalidation
- `GET /api/auth/me/` - Current user details

### Tracking
- `POST /api/tracking/track/` - Record feature click
- `GET /api/tracking/my_clicks/` - User's click history

### Analytics
- `GET /api/analytics/analytics/` - Dashboard data (bar + line charts)
- `GET /api/analytics/features/` - Feature usage summary
- `GET /api/analytics/health/` - Health check

### Query Parameters (Analytics)
- `start_date`: YYYY-MM-DD
- `end_date`: YYYY-MM-DD
- `age_group`: <18, 18-40, >40
- `gender`: Male, Female, Other
- `feature_name`: Specific feature filter

## 🔧 Configuration

### Environment Variables
```bash
# Core
DEBUG=False
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgres://user:pass@host:5432/db

# Security
ALLOWED_HOSTS=yourdomain.com,.onrender.com
SECURE_SSL_REDIRECT=True

# Performance
GUNICORN_WORKERS=1  # Critical for 512MB RAM
GUNICORN_LOG_LEVEL=warning
```

### Gunicorn Production Config
```python
# gunicorn_config.py
workers = 1  # Single worker for 512MB constraint
worker_class = 'sync'
threads = 2  # Concurrency without extra processes
timeout = 60
```

## 🚀 Deployment

### Render (Free Tier - 512MB RAM)
1. Connect GitHub repository
2. Set build command: `./build.sh`
3. Set start command: `gunicorn -c gunicorn_config.py config.wsgi:application`
4. Configure environment variables
5. Deploy

### Build Script (render-build.sh)
```bash
#!/bin/bash
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py seed_data --users 50 --clicks 500
```

## 📈 Scaling to 1 Million Write Events/Minute

### Current Architecture Limitations
The current design handles ~100-500 writes/minute comfortably within 512MB RAM. Scaling to 1M writes/minute requires fundamental architectural changes.

### Proposed High-Scale Architecture

#### 1. **Event Streaming Foundation**
Replace synchronous Django writes with **Apache Kafka** for event ingestion:
- **Kafka Topics**: `feature_clicks`, `user_events`
- **Producers**: API Gateway buffers and batches writes
- **Consumers**: Async processing workers
- **Throughput**: 1M+ events/minute with horizontal scaling

#### 2. **Data Lake Architecture**
**Real-time Layer (Hot Data)**:
- **ClickHouse** or **Apache Pinot** for sub-second analytics queries
- **Redis Cluster** for session data and real-time counters
- **Time-series optimization** for dashboard queries

**Batch Layer (Cold Data)**:
- **S3** or **GCS** for long-term storage
- **Apache Spark** for complex aggregations
- **Pre-computed views** for common dashboard queries

#### 3. **Microservices Decomposition**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Gateway   │───▶│ Event Processor │───▶│  Analytics API  │
│  (Nginx/Kong)   │    │  (Kafka/Flink)  │    │ (ClickHouse)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Auth Service   │    │   Cache Layer   │    │   Data Lake     │
│  (JWT/OAuth)    │    │   (Redis)       │    │   (S3/Spark)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

#### 4. **Write-Optimized Database Strategy**
**Dual Write Architecture**:
- **Primary**: Cassandra/ScyllaDB for high-write throughput
- **Secondary**: PostgreSQL for complex queries (eventual consistency)
- **CDC Pipeline**: Debezium for cross-database synchronization

#### 5. **Caching & CDN Strategy**
- **Multi-layer Caching**:
  - **L1**: Application-level (Redis)
  - **L2**: CDN (CloudFlare/CloudFront)
  - **L3**: Browser caching with proper headers
- **Cache Invalidation**: Pub/Sub pattern for real-time updates

#### 6. **Horizontal Scaling Strategy**
- **API Gateway**: Load balancer with auto-scaling groups
- **Worker Pools**: Kubernetes with HPA (Horizontal Pod Autoscaler)
- **Database Sharding**: Hash-based sharding by user_id
- **Regional Replication**: Multi-region deployment for global users

#### 7. **Monitoring & Observability**
- **Metrics**: Prometheus + Grafana dashboards
- **Tracing**: Jaeger/OpenTelemetry for request tracking
- **Alerting**: Real-time alerts for throughput drops
- **Logging**: Structured logging with ELK stack

#### 8. **Cost Optimization**
- **Spot Instances**: Use AWS/GCP spot instances for workers
- **Auto-scaling**: Scale to zero during low-traffic periods
- **Data Tiering**: Hot/warm/cold storage based on access patterns
- **Compression**: Snappy/LZ4 for data at rest and in transit

### Performance Projections
- **Write Throughput**: 1M+ events/minute
- **Query Latency**: <100ms for real-time dashboards
- **Storage Cost**: $0.02-0.05 per 1K events
- **Infrastructure Cost**: $500-2000/month (depending on traffic patterns)

### Migration Strategy
1. **Phase 1**: Implement Kafka for event buffering
2. **Phase 2**: Add ClickHouse for analytics queries
3. **Phase 3**: Migrate write-heavy endpoints to new architecture
4. **Phase 4**: Implement microservices decomposition
5. **Phase 5**: Full migration with A/B testing

This architecture transforms the system from a monolithic Django app to a distributed, event-driven platform capable of handling enterprise-scale analytics workloads.

## 📝 Development

### Code Quality
```bash
# Run tests
python manage.py test

# Check code style
pip install black flake8
black .
flake8 .

# Generate API documentation
pip install drf-spectacular
python manage.py spectacular --file schema.yml
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

---

**Built for scale, optimized for efficiency** 🚀
