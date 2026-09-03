'use client'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/store/authStore'
import AppLayout from '@/components/AppLayout'
import { adminApi } from '@/lib/api'
import { Loader2, Shield, Search, Users } from 'lucide-react'
import { useModalStore } from '@/store/modalStore'

type Role = 'student' | 'teacher' | 'admin'

export default function AdminRolesPage() {
  const router = useRouter()
  const { user } = useAuthStore()
  const [users, setUsers] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [selectedRole, setSelectedRole] = useState<Role>('student')
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<any[]>([])
  const [searching, setSearching] = useState(false)
  const { showSuccess, showError, showConfirm } = useModalStore()

  useEffect(() => {
    const adminEmails = ['cjalloh25@gmail.com', 'esjallow03@gmail.com', 'esjallow@gmail.com']
    const isAdmin = user?.role === 'admin' || (user?.email && adminEmails.includes(user.email))
    
    if (!user || !isAdmin) {
      router.push('/dashboard')
      return
    }
    loadUsersByRole()
  }, [selectedRole, user, router])

  const loadUsersByRole = async () => {
    try {
      setLoading(true)
      const res = await adminApi.getUsersByRole(selectedRole)
      setUsers(res.data || [])
    } catch (err: any) {
      showError(
        err.response?.data?.detail || 'Failed to load users',
        'Load Failed'
      )
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setSearchResults([])
      return
    }

    try {
      setSearching(true)
      const res = await adminApi.searchUsers(searchQuery, 20)
      setSearchResults(res.data || [])
    } catch (err) {
      console.error('Search failed', err)
    } finally {
      setSearching(false)
    }
  }

  const handleChangeRole = (userId: number, currentRole: string, userName: string) => {
    showConfirm(
      `Change role for ${userName}? This will affect their permissions and access to features.`,
      async () => {
        const newRole = prompt(`Enter new role for ${userName} (student/teacher/admin):`)
        if (!newRole || !['student', 'teacher', 'admin'].includes(newRole)) {
          showError('Invalid role. Must be one of: student, teacher, admin', 'Invalid Role')
          return
        }

        const reason = prompt('Reason for role change:') || 'Admin role update'

        try {
          await adminApi.changeUserRole(userId, newRole as Role, reason)
          showSuccess(`Role changed to ${newRole}`, 'Role Updated')
          loadUsersByRole()
          if (searchQuery) handleSearch()
        } catch (err: any) {
          showError(
            err.response?.data?.detail || 'Failed to change role',
            'Update Failed'
          )
        }
      },
      'Change User Role'
    )
  }

  const handleDeleteUser = (userId: number, userName: string, userEmail: string) => {
    showConfirm(
      `⚠️ Permanently delete ${userName} (${userEmail})? This action cannot be undone and will delete all associated data.`,
      async () => {
        try {
          await adminApi.deleteUser(userId)
          showSuccess(`User ${userName} has been deleted`, 'User Deleted')
          loadUsersByRole()
          if (searchQuery) handleSearch()
        } catch (err: any) {
          showError(
            err.response?.data?.detail || 'Failed to delete user',
            'Delete Failed'
          )
        }
      },
      'Delete User'
    )
  }

  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case 'admin': return 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400'
      case 'teacher': return 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400'
      default: return 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400'
    }
  }

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'admin': return '👑'
      case 'teacher': return '👨‍🏫'
      default: return '🎓'
    }
  }

  const UserCard = ({ user, showChangeButton = true }: { user: any; showChangeButton?: boolean }) => (
    <div className="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-slate-100 dark:bg-slate-700 flex items-center justify-center">
            <span className="text-xl">{getRoleIcon(user.role)}</span>
          </div>
          <div>
            <h3 className="font-semibold text-slate-900 dark:text-slate-100">{user.full_name}</h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">@{user.username}</p>
          </div>
        </div>
        <span className={`px-3 py-1 rounded-full text-xs font-medium ${getRoleBadgeColor(user.role)}`}>
          {user.role}
        </span>
      </div>
      <div className="space-y-1 text-xs text-slate-600 dark:text-slate-400 mb-3">
        {user.email && <p>📧 {user.email}</p>}
        {user.phone_number && <p>📱 {user.phone_number}</p>}
        <p>🆔 User ID: {user.id}</p>
      </div>
      {showChangeButton && (
        <div className="flex gap-2">
          <button
            onClick={() => handleChangeRole(user.id, user.role, user.full_name)}
            className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/30 transition text-sm font-medium"
          >
            <Users className="w-4 h-4" />
            Change Role
          </button>
          <button
            onClick={() => handleDeleteUser(user.id, user.full_name, user.email)}
            className="px-3 py-2 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-lg hover:bg-red-100 dark:hover:bg-red-900/30 transition text-sm font-medium"
            title="Delete User"
          >
            🗑️
          </button>
        </div>
      )}
    </div>
  )

  return (
    <AppLayout>
      <div className="p-8 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-outfit font-bold text-slate-900 dark:text-slate-100 mb-1">
              Role Management
            </h1>
            <p className="text-slate-600 dark:text-slate-400">
              Manage user roles and permissions
            </p>
          </div>
          <Shield className="w-8 h-8 text-emerald-500" />
        </div>

        {/* Search Section */}
        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-slate-200 dark:border-slate-700">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-4">Search Users</h2>
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                placeholder="Search by name, email, or phone..."
                className="w-full pl-10 pr-4 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100"
              />
            </div>
            <button
              onClick={handleSearch}
              disabled={searching}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition"
            >
              {searching ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Search'}
            </button>
          </div>

          {searchResults.length > 0 && (
            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {searchResults.map(user => (
                <UserCard key={user.id} user={user} />
              ))}
            </div>
          )}
        </div>

        {/* Role Tabs */}
        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-1 flex gap-1">
          {(['student', 'teacher', 'admin'] as Role[]).map(role => (
            <button
              key={role}
              onClick={() => setSelectedRole(role)}
              className={`flex-1 px-4 py-2.5 rounded-lg text-sm font-medium transition capitalize ${
                selectedRole === role
                  ? 'bg-emerald-600 text-white'
                  : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700'
              }`}
            >
              {getRoleIcon(role)} {role}s
            </button>
          ))}
        </div>

        {/* Users List */}
        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-slate-200 dark:border-slate-700">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100 capitalize">
              {selectedRole}s ({users.length})
            </h2>
            <button
              onClick={loadUsersByRole}
              className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
            >
              Refresh
            </button>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-emerald-500" />
            </div>
          ) : users.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-slate-500 dark:text-slate-400">No {selectedRole}s found</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {users.map(user => (
                <UserCard key={user.id} user={user} />
              ))}
            </div>
          )}
        </div>

        {/* Info Box */}
        <div className="bg-blue-50 dark:bg-blue-900/20 rounded-xl p-4 border border-blue-200 dark:border-blue-800">
          <h3 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">Role Permissions</h3>
          <ul className="space-y-1 text-sm text-blue-800 dark:text-blue-200">
            <li>• <strong>Student:</strong> Access quizzes, join classrooms, submit assignments</li>
            <li>• <strong>Teacher:</strong> Create classrooms, manage assignments, track student progress</li>
            <li>• <strong>Admin:</strong> Full system access, manage users and content</li>
          </ul>
          <p className="text-xs text-blue-700 dark:text-blue-300 mt-3">
            ⚠️ Role changes take effect immediately. Users cannot change their own role. Deleting a user is permanent and cannot be undone.
          </p>
        </div>
      </div>
    </AppLayout>
  )
}
