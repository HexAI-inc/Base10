# Admin Profile Frontend Integration Guide

Quick reference for integrating admin profile and settings into web and mobile applications.

## 🚀 Quick Start

### Endpoints Summary
```
GET    /api/v1/admin/profile      # Get profile
PATCH  /api/v1/admin/profile      # Update profile
PATCH  /api/v1/admin/settings     # Update settings
GET    /api/v1/admin/activity     # Get activity logs
```

---

## 📱 Mobile Implementation (React Native)

### 1. Admin Profile Screen

```jsx
import React, { useState, useEffect } from 'react';
import { View, Text, TextInput, TouchableOpacity, Image, ScrollView } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

const AdminProfileScreen = () => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const token = await AsyncStorage.getItem('adminToken');
      const response = await fetch('https://api.base10.app/api/v1/admin/profile', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const data = await response.json();
      setProfile(data);
    } catch (error) {
      console.error('Failed to load profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateProfile = async (updates) => {
    try {
      const token = await AsyncStorage.getItem('adminToken');
      const response = await fetch('https://api.base10.app/api/v1/admin/profile', {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(updates)
      });
      const data = await response.json();
      setProfile(data);
      setEditing(false);
      // Show success message
    } catch (error) {
      console.error('Failed to update profile:', error);
      // Show error message
    }
  };

  if (loading) return <Text>Loading...</Text>;

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Image 
          source={{ uri: profile.avatar_url || 'https://via.placeholder.com/100' }}
          style={styles.avatar}
        />
        <Text style={styles.name}>{profile.full_name || 'Admin User'}</Text>
        <Text style={styles.email}>{profile.email}</Text>
        <Text style={styles.role}>{profile.role}</Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Profile Information</Text>
        
        {editing ? (
          <>
            <TextInput
              style={styles.input}
              placeholder="Full Name"
              value={profile.full_name}
              onChangeText={(text) => setProfile({...profile, full_name: text})}
            />
            <TextInput
              style={styles.input}
              placeholder="Username"
              value={profile.username}
              onChangeText={(text) => setProfile({...profile, username: text})}
            />
            <TextInput
              style={styles.input}
              placeholder="Bio"
              value={profile.bio}
              multiline
              numberOfLines={4}
              onChangeText={(text) => setProfile({...profile, bio: text})}
            />
            <TouchableOpacity 
              style={styles.saveButton}
              onPress={() => updateProfile({
                full_name: profile.full_name,
                username: profile.username,
                bio: profile.bio
              })}
            >
              <Text style={styles.buttonText}>Save Changes</Text>
            </TouchableOpacity>
            <TouchableOpacity 
              style={styles.cancelButton}
              onPress={() => setEditing(false)}
            >
              <Text style={styles.buttonText}>Cancel</Text>
            </TouchableOpacity>
          </>
        ) : (
          <>
            <View style={styles.infoRow}>
              <Text style={styles.label}>Username:</Text>
              <Text style={styles.value}>{profile.username || 'Not set'}</Text>
            </View>
            <View style={styles.infoRow}>
              <Text style={styles.label}>Bio:</Text>
              <Text style={styles.value}>{profile.bio || 'No bio'}</Text>
            </View>
            <View style={styles.infoRow}>
              <Text style={styles.label}>Last Login:</Text>
              <Text style={styles.value}>
                {profile.last_login ? new Date(profile.last_login).toLocaleString() : 'Never'}
              </Text>
            </View>
            <TouchableOpacity 
              style={styles.editButton}
              onPress={() => setEditing(true)}
            >
              <Text style={styles.buttonText}>Edit Profile</Text>
            </TouchableOpacity>
          </>
        )}
      </View>
    </ScrollView>
  );
};

const styles = {
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    alignItems: 'center',
    padding: 20,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  avatar: {
    width: 100,
    height: 100,
    borderRadius: 50,
    marginBottom: 10,
  },
  name: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  email: {
    fontSize: 16,
    color: '#666',
    marginBottom: 5,
  },
  role: {
    fontSize: 14,
    color: '#007bff',
    fontWeight: '600',
  },
  section: {
    backgroundColor: 'white',
    margin: 10,
    padding: 15,
    borderRadius: 8,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
  },
  infoRow: {
    flexDirection: 'row',
    marginBottom: 10,
  },
  label: {
    fontWeight: '600',
    width: 100,
  },
  value: {
    flex: 1,
    color: '#666',
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 5,
    padding: 10,
    marginBottom: 10,
  },
  editButton: {
    backgroundColor: '#007bff',
    padding: 15,
    borderRadius: 5,
    alignItems: 'center',
    marginTop: 10,
  },
  saveButton: {
    backgroundColor: '#28a745',
    padding: 15,
    borderRadius: 5,
    alignItems: 'center',
    marginTop: 10,
  },
  cancelButton: {
    backgroundColor: '#6c757d',
    padding: 15,
    borderRadius: 5,
    alignItems: 'center',
    marginTop: 10,
  },
  buttonText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 16,
  },
};

export default AdminProfileScreen;
```

### 2. Admin Settings Screen

```jsx
import React, { useState, useEffect } from 'react';
import { View, Text, Switch, ScrollView, TouchableOpacity, Picker } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

const AdminSettingsScreen = () => {
  const [profile, setProfile] = useState(null);
  const [notifications, setNotifications] = useState({
    email_enabled: true,
    system_alerts: true,
    user_reports: true,
    new_registrations: false,
    performance_alerts: true,
    security_alerts: true,
  });
  const [preferences, setPreferences] = useState({
    theme: 'light',
    items_per_page: 25,
    auto_refresh_interval: 60,
    timezone: 'UTC',
  });

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const token = await AsyncStorage.getItem('adminToken');
      const response = await fetch('https://api.base10.app/api/v1/admin/profile', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const data = await response.json();
      setProfile(data);
      if (data.notification_settings) {
        setNotifications(data.notification_settings);
      }
      if (data.preferences) {
        setPreferences(data.preferences);
      }
    } catch (error) {
      console.error('Failed to load settings:', error);
    }
  };

  const saveSettings = async () => {
    try {
      const token = await AsyncStorage.getItem('adminToken');
      const response = await fetch('https://api.base10.app/api/v1/admin/settings', {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          notification_settings: notifications,
          preferences: preferences
        })
      });
      const data = await response.json();
      // Show success message
      alert('Settings saved successfully!');
    } catch (error) {
      console.error('Failed to save settings:', error);
      alert('Failed to save settings');
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Notifications</Text>
        
        <View style={styles.settingRow}>
          <Text style={styles.settingLabel}>Email Notifications</Text>
          <Switch
            value={notifications.email_enabled}
            onValueChange={(value) => setNotifications({...notifications, email_enabled: value})}
          />
        </View>

        <View style={styles.settingRow}>
          <Text style={styles.settingLabel}>System Alerts</Text>
          <Switch
            value={notifications.system_alerts}
            onValueChange={(value) => setNotifications({...notifications, system_alerts: value})}
          />
        </View>

        <View style={styles.settingRow}>
          <Text style={styles.settingLabel}>User Reports</Text>
          <Switch
            value={notifications.user_reports}
            onValueChange={(value) => setNotifications({...notifications, user_reports: value})}
          />
        </View>

        <View style={styles.settingRow}>
          <Text style={styles.settingLabel}>New Registrations</Text>
          <Switch
            value={notifications.new_registrations}
            onValueChange={(value) => setNotifications({...notifications, new_registrations: value})}
          />
        </View>

        <View style={styles.settingRow}>
          <Text style={styles.settingLabel}>Performance Alerts</Text>
          <Switch
            value={notifications.performance_alerts}
            onValueChange={(value) => setNotifications({...notifications, performance_alerts: value})}
          />
        </View>

        <View style={styles.settingRow}>
          <Text style={styles.settingLabel}>Security Alerts</Text>
          <Switch
            value={notifications.security_alerts}
            onValueChange={(value) => setNotifications({...notifications, security_alerts: value})}
          />
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Dashboard Preferences</Text>
        
        <View style={styles.settingRow}>
          <Text style={styles.settingLabel}>Theme</Text>
          <Picker
            selectedValue={preferences.theme}
            style={styles.picker}
            onValueChange={(value) => setPreferences({...preferences, theme: value})}
          >
            <Picker.Item label="Light" value="light" />
            <Picker.Item label="Dark" value="dark" />
          </Picker>
        </View>

        <View style={styles.settingRow}>
          <Text style={styles.settingLabel}>Items Per Page</Text>
          <Picker
            selectedValue={preferences.items_per_page}
            style={styles.picker}
            onValueChange={(value) => setPreferences({...preferences, items_per_page: value})}
          >
            <Picker.Item label="10" value={10} />
            <Picker.Item label="25" value={25} />
            <Picker.Item label="50" value={50} />
            <Picker.Item label="100" value={100} />
          </Picker>
        </View>

        <View style={styles.settingRow}>
          <Text style={styles.settingLabel}>Auto Refresh (seconds)</Text>
          <Picker
            selectedValue={preferences.auto_refresh_interval}
            style={styles.picker}
            onValueChange={(value) => setPreferences({...preferences, auto_refresh_interval: value})}
          >
            <Picker.Item label="Disabled" value={0} />
            <Picker.Item label="30s" value={30} />
            <Picker.Item label="60s" value={60} />
            <Picker.Item label="120s" value={120} />
          </Picker>
        </View>
      </View>

      <TouchableOpacity style={styles.saveButton} onPress={saveSettings}>
        <Text style={styles.buttonText}>Save All Settings</Text>
      </TouchableOpacity>
    </ScrollView>
  );
};

export default AdminSettingsScreen;
```

---

## 🌐 Web Implementation (React/Next.js)

### 1. Profile Page Component

```tsx
// app/admin/profile/page.tsx
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface AdminProfile {
  id: number;
  email: string;
  full_name: string;
  username: string;
  avatar_url: string;
  bio: string;
  role: string;
  notification_settings: NotificationSettings;
  preferences: Preferences;
}

interface NotificationSettings {
  email_enabled: boolean;
  system_alerts: boolean;
  user_reports: boolean;
  new_registrations: boolean;
  performance_alerts: boolean;
  security_alerts: boolean;
}

interface Preferences {
  theme: 'light' | 'dark';
  default_view: string;
  items_per_page: number;
  auto_refresh_interval: number;
  timezone: string;
}

export default function AdminProfilePage() {
  const [profile, setProfile] = useState<AdminProfile | null>(null);
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({
    full_name: '',
    username: '',
    bio: '',
  });
  const router = useRouter();

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const response = await fetch('/api/v1/admin/profile', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.status === 401) {
        router.push('/login');
        return;
      }

      const data = await response.json();
      setProfile(data);
      setFormData({
        full_name: data.full_name || '',
        username: data.username || '',
        bio: data.bio || '',
      });
    } catch (error) {
      console.error('Failed to load profile:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/v1/admin/profile', {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        const data = await response.json();
        setProfile(data);
        setEditing(false);
        alert('Profile updated successfully!');
      } else {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
      }
    } catch (error) {
      console.error('Failed to update profile:', error);
      alert('Failed to update profile');
    }
  };

  if (!profile) return <div>Loading...</div>;

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Admin Profile</h1>
      
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex items-center mb-6">
          <img 
            src={profile.avatar_url || '/default-avatar.png'} 
            alt="Avatar"
            className="w-24 h-24 rounded-full mr-6"
          />
          <div>
            <h2 className="text-2xl font-semibold">{profile.full_name}</h2>
            <p className="text-gray-600">{profile.email}</p>
            <span className="inline-block bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm mt-2">
              {profile.role}
            </span>
          </div>
        </div>

        {editing ? (
          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Full Name</label>
              <input
                type="text"
                value={formData.full_name}
                onChange={(e) => setFormData({...formData, full_name: e.target.value})}
                className="w-full border rounded px-3 py-2"
              />
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Username</label>
              <input
                type="text"
                value={formData.username}
                onChange={(e) => setFormData({...formData, username: e.target.value})}
                className="w-full border rounded px-3 py-2"
              />
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Bio</label>
              <textarea
                value={formData.bio}
                onChange={(e) => setFormData({...formData, bio: e.target.value})}
                rows={4}
                className="w-full border rounded px-3 py-2"
              />
            </div>
            <div className="flex gap-2">
              <button type="submit" className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700">
                Save Changes
              </button>
              <button 
                type="button" 
                onClick={() => setEditing(false)}
                className="bg-gray-300 text-gray-700 px-6 py-2 rounded hover:bg-gray-400"
              >
                Cancel
              </button>
            </div>
          </form>
        ) : (
          <div>
            <div className="mb-3">
              <span className="font-medium">Username:</span> {profile.username || 'Not set'}
            </div>
            <div className="mb-3">
              <span className="font-medium">Bio:</span> {profile.bio || 'No bio'}
            </div>
            <button 
              onClick={() => setEditing(true)}
              className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
            >
              Edit Profile
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
```

### 2. Settings Page Component

```tsx
// app/admin/settings/page.tsx
'use client';

import { useState, useEffect } from 'react';

export default function AdminSettingsPage() {
  const [notifications, setNotifications] = useState({
    email_enabled: true,
    system_alerts: true,
    user_reports: true,
    new_registrations: false,
    performance_alerts: true,
    security_alerts: true,
  });

  const [preferences, setPreferences] = useState({
    theme: 'light',
    items_per_page: 25,
    auto_refresh_interval: 60,
    timezone: 'UTC',
  });

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const response = await fetch('/api/v1/admin/profile', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await response.json();
      
      if (data.notification_settings) {
        setNotifications(data.notification_settings);
      }
      if (data.preferences) {
        setPreferences(data.preferences);
      }
    } catch (error) {
      console.error('Failed to load settings:', error);
    }
  };

  const saveSettings = async () => {
    try {
      const response = await fetch('/api/v1/admin/settings', {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          notification_settings: notifications,
          preferences: preferences
        })
      });

      if (response.ok) {
        alert('Settings saved successfully!');
      }
    } catch (error) {
      console.error('Failed to save settings:', error);
      alert('Failed to save settings');
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Settings</h1>

      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Notifications</h2>
        
        {Object.entries(notifications).map(([key, value]) => (
          <div key={key} className="flex items-center justify-between mb-3">
            <label className="text-gray-700">
              {key.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
            </label>
            <input
              type="checkbox"
              checked={value}
              onChange={(e) => setNotifications({...notifications, [key]: e.target.checked})}
              className="w-5 h-5"
            />
          </div>
        ))}
      </div>

      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Dashboard Preferences</h2>
        
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">Theme</label>
          <select
            value={preferences.theme}
            onChange={(e) => setPreferences({...preferences, theme: e.target.value})}
            className="w-full border rounded px-3 py-2"
          >
            <option value="light">Light</option>
            <option value="dark">Dark</option>
          </select>
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">Items Per Page</label>
          <select
            value={preferences.items_per_page}
            onChange={(e) => setPreferences({...preferences, items_per_page: parseInt(e.target.value)})}
            className="w-full border rounded px-3 py-2"
          >
            <option value={10}>10</option>
            <option value={25}>25</option>
            <option value={50}>50</option>
            <option value={100}>100</option>
          </select>
        </div>
      </div>

      <button 
        onClick={saveSettings}
        className="bg-blue-600 text-white px-8 py-3 rounded hover:bg-blue-700"
      >
        Save All Settings
      </button>
    </div>
  );
}
```

---

## 🔑 Key Points

1. **Always handle authentication errors** (401/403)
2. **Validate inputs** before sending to API
3. **Show loading states** during API calls
4. **Display clear error messages** to users
5. **Persist settings** across sessions
6. **Apply theme changes** immediately when saved

---

## 📚 Additional Resources

- [ADMIN_PROFILE_API.md](./ADMIN_PROFILE_API.md) - Full API documentation
- [ADMIN_SYSTEM_SUMMARY.md](./ADMIN_SYSTEM_SUMMARY.md) - System overview
- [ADMIN_DASHBOARD_API.md](./ADMIN_DASHBOARD_API.md) - Dashboard endpoints
