# 🚀 Render Deployment - Quick Start

## Critical Settings for 512MB RAM

### 1. Set Environment Variables

In Render Dashboard → Your Service → Environment:

```
DEBUG=False
SECRET_KEY=your-very-secret-key-here
GUNICORN_WORKERS=1
GUNICORN_LOG_LEVEL=warning
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

**DO NOT CHANGE**:
- Leave `DATABASE_URL` as auto-configured by Render
- Leave `ALLOWED_HOSTS` to populate from Render settings

### 2. Deploy & Monitor

```bash
# Render uses: gunicorn -c gunicorn_config.py config.wsgi:application
# (configured in render.yaml or Render dashboard)
```

### 3. Check RAM Usage

In Render Dashboard → Logs:
```
// Watch for memory warnings
// Target: <250MB at peak
// Idle: 120-150MB
```

### 4. If Memory Still Spikes

**Option A**: Reduce PAGE_SIZE
```python
# settings.py
PAGE_SIZE = 10  # Further reduced from 25
MAX_PAGE_SIZE = 25
```

**Option B**: Increase Workers Carefully
```
GUNICORN_WORKERS=2  # Max for 512MB
```

**Option C**: Add Worker Timeout
```
GUNICORN_TIMEOUT=30  # Prevent hung requests
```

## Expected Performance

| Metric | Target |
|--------|--------|
| Idle RAM | 80-120MB |
| Loaded RAM | 180-220MB |
| Request latency | <200ms |
| Analytics response | <100ms (cached) |

## Pre-Deployment Checklist

- [ ] All migrations applied: `python manage.py migrate`
- [ ] Static files collected: `python manage.py collectstatic`
- [ ] DEBUG environment variable set correctly
- [ ] SECRET_KEY provided (not in code)
- [ ] Database URL configured
- [ ] GUNICORN_WORKERS=1 set

## Rollback

If you need to revert:

```bash
git revert HEAD~5  # Adjust commit count
git push
# Render auto-redeploys
```

---

**Memory budget depleted? Check these first**:

1. ✅ `GUNICORN_WORKERS` is 1?
2. ✅ `DEBUG` is False?
3. ✅ `PAGE_SIZE` is ≤25?
4. ✅ Logging level is WARNING?
5. ✅ No custom middleware added?

If all ✅ but still hitting limit → Contact Render support for higher tier.
