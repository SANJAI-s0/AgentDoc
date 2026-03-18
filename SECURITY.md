# Security Guide

## Overview

AgentDoc implements multiple layers of security to protect sensitive document data and ensure compliance with industry standards.

## Security Features

### 1. Authentication & Authorization

- **JWT-based Authentication**: Secure token-based authentication with configurable expiration
- **Role-based Access Control**: Customer and Reviewer roles with different permissions
- **Session Management**: Secure session cookies with HttpOnly and SameSite flags

### 2. Data Protection

- **HTTPS Enforcement**: All production traffic encrypted with TLS/SSL
- **Secure Cookies**: Session and CSRF cookies marked as Secure and HttpOnly
- **CSRF Protection**: Django CSRF middleware enabled for all state-changing operations
- **XSS Protection**: Content Security Policy and XSS filtering headers

### 3. Input Validation

- **File Upload Restrictions**: Limited file types and sizes
- **Data Sanitization**: All user inputs validated and sanitized
- **SQL Injection Prevention**: MongoDB queries parameterized
- **Path Traversal Protection**: File paths validated and restricted

### 4. API Security

- **Rate Limiting**: Configurable rate limits per IP address
- **CORS Configuration**: Strict origin validation
- **API Authentication**: All endpoints require valid JWT tokens
- **Request Size Limits**: Maximum payload sizes enforced

### 5. Infrastructure Security

- **Environment Variables**: Sensitive data stored in environment variables
- **Secret Management**: Secrets never committed to version control
- **Secure Headers**: Security headers configured (HSTS, X-Frame-Options, etc.)
- **Dependency Scanning**: Regular security updates for dependencies

## Security Configuration

### Production Checklist

Before deploying to production, ensure:

- [ ] `DJANGO_DEBUG=0` (Debug mode disabled)
- [ ] Strong `DJANGO_SECRET_KEY` (50+ random characters)
- [ ] `DJANGO_ALLOWED_HOSTS` set to specific domains only
- [ ] `DJANGO_CORS_ALLOWED_ORIGINS` restricted to your domains
- [ ] All cookie security flags enabled (`SECURE=1`, `HTTPONLY=1`)
- [ ] HTTPS enabled (automatic on Render)
- [ ] MongoDB authentication enabled
- [ ] Strong passwords for all accounts
- [ ] `AGENT_INTERNAL_TOKEN` set to random value
- [ ] Rate limiting enabled
- [ ] File upload restrictions configured
- [ ] Monitoring and logging enabled
- [ ] Regular security updates scheduled

### Environment Variables

#### Critical Security Variables

```bash
# Generate strong secret key
DJANGO_SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

# Generate agent token
AGENT_INTERNAL_TOKEN=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# Production settings
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=your-domain.com
DJANGO_CORS_ALLOWED_ORIGINS=https://your-domain.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://your-domain.com
```

#### Cookie Security

```bash
# Enable secure cookies (HTTPS only)
DJANGO_SESSION_COOKIE_SECURE=1
DJANGO_CSRF_COOKIE_SECURE=1
DJANGO_SESSION_COOKIE_HTTPONLY=1
DJANGO_CSRF_COOKIE_HTTPONLY=1
DJANGO_SESSION_COOKIE_SAMESITE=Lax
DJANGO_CSRF_COOKIE_SAMESITE=Lax
```

#### Database Security

```bash
# Use MongoDB Atlas with authentication
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority

# Enable SSL/TLS for MongoDB connection
# (Automatic with MongoDB Atlas)
```

### Security Headers

The following security headers are automatically configured:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload` (production only)

### Rate Limiting

Configure rate limiting to prevent abuse:

```bash
# Requests per minute per IP
RATE_LIMIT_PER_MINUTE=60
```

Rate limiting is applied to:
- Document upload endpoints
- Authentication endpoints
- API endpoints

### File Upload Security

File uploads are restricted by:

- **File Type**: Only allowed document types (PDF, images, etc.)
- **File Size**: Maximum 10MB per file (configurable)
- **Virus Scanning**: Recommended for production (not included in free tier)
- **Storage Isolation**: Files stored with unique identifiers

## Security Best Practices

### 1. Secret Management

- Never commit `.env` files to version control
- Use environment variables for all secrets
- Rotate secrets regularly (every 90 days recommended)
- Use different secrets for development and production

### 2. Access Control

- Implement principle of least privilege
- Review user permissions regularly
- Disable unused accounts
- Use strong password policies

### 3. Monitoring & Logging

- Enable application logging
- Monitor for suspicious activity
- Set up alerts for security events
- Regular security audits

### 4. Dependency Management

- Keep dependencies up to date
- Review security advisories
- Use `pip-audit` to scan for vulnerabilities
- Pin dependency versions in production

### 5. Data Protection

- Encrypt sensitive data at rest
- Use HTTPS for all communications
- Implement data retention policies
- Regular backups with encryption

## Incident Response

### If a Security Issue is Discovered

1. **Assess Impact**: Determine scope and severity
2. **Contain**: Isolate affected systems
3. **Investigate**: Review logs and identify root cause
4. **Remediate**: Apply fixes and patches
5. **Notify**: Inform affected users if required
6. **Document**: Record incident and response
7. **Review**: Update security measures

### Reporting Security Issues

If you discover a security vulnerability:

1. **Do not** disclose publicly
2. Email security contact (configure in production)
3. Provide detailed description
4. Include steps to reproduce
5. Allow time for remediation

## Compliance

### Data Protection

- GDPR compliance considerations
- Data minimization principles
- User consent management
- Right to deletion support

### Audit Trail

- All document operations logged
- User actions tracked
- Immutable audit records
- Compliance reporting available

## Security Testing

### Recommended Tests

1. **Penetration Testing**: Regular security assessments
2. **Vulnerability Scanning**: Automated scanning tools
3. **Code Review**: Security-focused code reviews
4. **Dependency Scanning**: Check for known vulnerabilities
5. **Configuration Review**: Verify security settings

### Testing Tools

```bash
# Scan Python dependencies
pip install pip-audit
pip-audit

# Check Django security
python manage.py check --deploy

# Test SSL/TLS configuration
# Use SSL Labs or similar tools
```

## Additional Resources

- [Django Security Documentation](https://docs.djangoproject.com/en/stable/topics/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [MongoDB Security Checklist](https://docs.mongodb.com/manual/administration/security-checklist/)
- [Render Security Best Practices](https://render.com/docs/security)

## Security Updates

This document should be reviewed and updated:
- After security incidents
- When new features are added
- During security audits
- At least quarterly

Last Updated: 2026-03-17
