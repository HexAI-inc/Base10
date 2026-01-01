# Admin Profile & Settings API Documentation

## Overview
This document describes the API endpoints for admin profile management and settings configuration. These endpoints are designed for both web and mobile admin dashboards.

## Authentication
All endpoints require admin authentication via JWT token:
```
Authorization: Bearer <admin_jwt_token>
```

## Base URL
```
/api/v1/admin
```

---

## Endpoints

### 1. Get Admin Profile
**GET** `/admin/profile`

Get the authenticated admin's profile information including settings and preferences.

#### Response
```json
{
  "id": 1,
  "email": "admin@base10.app",
  "phone_number": "+2207777777",
  "username": "admin_user",
  "full_name": "John Doe",
  "role": "ADMIN",
  "avatar_url": "https://storage.example.com/avatars/admin.jpg",
  "bio": "System administrator for Base10",
  "is_active": true,
  "is_verified": true,
  "created_at": "2024-01-15T10:30:00Z",
  "last_login": "2024-12-30T08:15:00Z",
  "notification_settings": {
    "email_enabled": true,
    "system_alerts": true,
    "user_reports": true,
    "new_registrations": false,
    "performance_alerts": true,
    "security_alerts": true
  },
  "preferences": {
    "theme": "light",
    "default_view": "dashboard",
    "items_per_page": 25,
    "auto_refresh_interval": 60,
    "show_advanced_metrics": true,
    "timezone": "UTC"
  },
  "total_actions_performed": 0,
  "last_action_at": null
}
```

#### Status Codes
- `200 OK` - Profile retrieved successfully
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Not an admin user

---

### 2. Update Admin Profile
**PATCH** `/admin/profile`

Update admin's basic profile information.

#### Request Body
```json
{
  "full_name": "John Doe",
  "username": "admin_john",
  "email": "john@base10.app",
  "phone_number": "+2207777777",
  "avatar_url": "https://storage.example.com/avatars/new_avatar.jpg",
  "bio": "Senior system administrator"
}
```

All fields are optional. Only include fields you want to update.

#### Field Validations
- `full_name`: 2-100 characters
- `username`: 3-50 characters, must be unique
- `email`: Valid email format, must be unique
- `phone_number`: Must be unique
- `bio`: Max 500 characters

#### Response
Same as Get Admin Profile response (200 OK)

#### Status Codes
- `200 OK` - Profile updated successfully
- `400 Bad Request` - Validation error (duplicate username/email/phone, invalid format)
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Not an admin user

#### Example Error Response
```json
{
  "detail": "Username already taken"
}
```

---

### 3. Update Admin Settings
**PATCH** `/admin/settings`

Update admin's notification preferences and dashboard settings.

#### Request Body
```json
{
  "notification_settings": {
    "email_enabled": true,
    "system_alerts": true,
    "user_reports": true,
    "new_registrations": false,
    "performance_alerts": true,
    "security_alerts": true
  },
  "preferences": {
    "theme": "dark",
    "default_view": "users",
    "items_per_page": 50,
    "auto_refresh_interval": 30,
    "show_advanced_metrics": true,
    "timezone": "Africa/Freetown"
  }
}
```

All fields are optional. Only include settings you want to update.

#### Notification Settings Fields
- `email_enabled`: Enable/disable email notifications
- `system_alerts`: Critical system issues alerts
- `user_reports`: Content moderation report notifications
- `new_registrations`: Daily digest of new user registrations
- `performance_alerts`: System performance degradation alerts
- `security_alerts`: Suspicious activity notifications

#### Preferences Fields
- `theme`: "light" or "dark"
- `default_view`: Default page after login (e.g., "dashboard", "users", "questions")
- `items_per_page`: Pagination size (1-100)
- `auto_refresh_interval`: Dashboard auto-refresh in seconds (0 = disabled)
- `show_advanced_metrics`: Show/hide advanced analytics
- `timezone`: Timezone for date/time display (IANA format)

#### Response
Same as Get Admin Profile response (200 OK)

#### Status Codes
- `200 OK` - Settings updated successfully
- `400 Bad Request` - Invalid settings format
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Not an admin user

---

### 4. Get Admin Activity Logs
**GET** `/admin/activity`

Get paginated list of admin actions for audit purposes.

#### Query Parameters
- `page` (optional): Page number (default: 1, min: 1)
- `page_size` (optional): Items per page (default: 25, min: 1, max: 100)
- `action_type` (optional): Filter by action type

#### Response
```json
{
  "activities": [],
  "total": 0,
  "page": 1,
  "page_size": 25
}
```

**Note**: This endpoint currently returns empty data. Activity logging will be implemented in future updates with a dedicated database table.

#### Future Activity Log Structure
When implemented, each activity will include:
```json
{
  "id": 1,
  "admin_id": 1,
  "admin_name": "John Doe",
  "action_type": "user_update",
  "action_description": "Updated user role to TEACHER",
  "target_type": "user",
  "target_id": 42,
  "metadata": {
    "previous_role": "STUDENT",
    "new_role": "TEACHER"
  },
  "ip_address": "192.168.1.100",
  "timestamp": "2024-12-30T10:30:00Z"
}
```

#### Action Types (Future)
- `user_update` - User profile/role modifications
- `user_delete` - User account deletions
- `content_moderation` - Question/content moderation actions
- `system_config` - System configuration changes
- `bulk_operation` - Bulk data operations
- `classroom_management` - Classroom-related actions

#### Status Codes
- `200 OK` - Activities retrieved successfully
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Not an admin user

---

## Integration Examples

### Web Dashboard (React/Next.js)

```javascript
// Fetch admin profile
const getAdminProfile = async () => {
  const response = await fetch('/api/v1/admin/profile', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  return response.json();
};

// Update profile
const updateProfile = async (updates) => {
  const response = await fetch('/api/v1/admin/profile', {
    method: 'PATCH',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(updates)
  });
  return response.json();
};

// Update settings
const updateSettings = async (settings) => {
  const response = await fetch('/api/v1/admin/settings', {
    method: 'PATCH',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(settings)
  });
  return response.json();
};
```

### Mobile (React Native / Flutter)

```dart
// Flutter/Dart example
Future<AdminProfile> getAdminProfile(String token) async {
  final response = await http.get(
    Uri.parse('https://api.base10.app/api/v1/admin/profile'),
    headers: {
      'Authorization': 'Bearer $token',
    },
  );
  
  if (response.statusCode == 200) {
    return AdminProfile.fromJson(jsonDecode(response.body));
  } else {
    throw Exception('Failed to load profile');
  }
}

// Update settings
Future<AdminProfile> updateSettings(
  String token,
  Map<String, dynamic> settings
) async {
  final response = await http.patch(
    Uri.parse('https://api.base10.app/api/v1/admin/settings'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
    body: jsonEncode(settings),
  );
  
  if (response.statusCode == 200) {
    return AdminProfile.fromJson(jsonDecode(response.body));
  } else {
    throw Exception('Failed to update settings');
  }
}
```

---

## UI Recommendations

### Profile Page Components

1. **Basic Info Section**
   - Avatar upload/display
   - Full name input
   - Email input
   - Phone number input
   - Username input
   - Bio textarea

2. **Settings Section**
   - Theme toggle (light/dark)
   - Notification preferences checkboxes
   - Dashboard preferences
   - Timezone selector

3. **Activity Section**
   - Recent actions table
   - Action filters
   - Pagination controls

### Mobile Screen Layout

```
┌─────────────────────────┐
│  Admin Profile          │
├─────────────────────────┤
│  [Avatar]               │
│  John Doe               │
│  admin@base10.app       │
│  Last login: 2h ago     │
├─────────────────────────┤
│  📋 Edit Profile        │
│  ⚙️  Settings           │
│  📊 Activity Log        │
│  🔐 Change Password     │
│  🚪 Logout              │
└─────────────────────────┘
```

---

## Best Practices

1. **Profile Updates**
   - Always validate email/phone uniqueness before submitting
   - Show loading states during updates
   - Display success/error messages clearly

2. **Settings Management**
   - Save settings separately from profile data
   - Apply theme changes immediately
   - Persist timezone preferences

3. **Security**
   - Never store admin tokens in localStorage (use httpOnly cookies)
   - Implement session timeout warnings
   - Log all profile/settings changes for audit

4. **Error Handling**
   - Handle 401 errors by redirecting to login
   - Handle 403 errors by showing "Access Denied"
   - Provide helpful error messages for validation failures

---

## Testing Checklist

- [ ] Get profile returns correct admin data
- [ ] Update profile with valid data succeeds
- [ ] Update profile with duplicate email/username fails
- [ ] Update settings saves preferences correctly
- [ ] Theme changes apply immediately
- [ ] Notification settings persist
- [ ] Non-admin users get 403 error
- [ ] Invalid tokens get 401 error
- [ ] Activity log pagination works
- [ ] All fields validate correctly

---

## Future Enhancements

1. **Activity Logging**
   - Create `admin_activity_logs` database table
   - Implement middleware to log all admin actions
   - Add activity filtering and search

2. **Two-Factor Authentication**
   - Add 2FA settings to profile
   - Support authenticator apps and SMS

3. **Role-Based Permissions**
   - Add granular permission controls
   - Support multiple admin roles (super admin, moderator, etc.)

4. **Audit Trail**
   - Full audit log with before/after states
   - Export audit logs to CSV/PDF
   - Real-time activity feed

5. **Session Management**
   - View active sessions
   - Revoke sessions remotely
   - Session timeout configuration

---

## Support

For questions or issues with the admin profile API:
- Check logs in `/var/log/base10/`
- Review [ADMIN_SYSTEM_SUMMARY.md](./ADMIN_SYSTEM_SUMMARY.md)
- Contact: cjalloh25@gmail.com
