'use client'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/store/authStore'
import { adminApi } from '@/lib/api'
import AppLayout from '@/components/AppLayout'
import { 
  Search, 
  UserX, 
  UserCheck, 
  Loader2, 
  Trophy,
  Mail,
  Phone,
  Calendar,
  TrendingUp,
  Filter,
  Edit2,
  X,
  Save,
  ShieldCheck
} from 'lucide-react'

interface User {
  id: number
  email?: string
  phone_number?: string
  full_name: string
  role?: string
  is_verified: boolean
  is_active: boolean
  created_at: string
  last_activity_date?: string
  study_streak: number
  total_points: number
  level: number
}

interface TopUser extends User {
  total_attempts: number
  accuracy: number
  last_active: string
}

export default function AdminUsersPage() {
  const router = useRouter()
  const { user } = useAuthStore()
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedRole, setSelectedRole] = useState<string>('all')
  const [searchResults, setSearchResults] = useState<User[]>([])
  const [topUsers, setTopUsers] = useState<TopUser[]>([])
  const [loading, setLoading] = useState(false)
  const [hasLoaded, setHasLoaded] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showTopUsers, setShowTopUsers] = useState(false)
  const [actionLoading, setActionLoading] = useState<number | null>(null)
  const [editingUser, setEditingUser] = useState<User | null>(null)
  const [editForm, setEditForm] = useState<Partial<User>>({})

  const loadInitialUsers = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await adminApi.getUsers(0, 50, selectedRole === 'all' ? undefined : selectedRole)
      const data = Array.isArray(response.data) ? response.data : (response.data.users || [])
      setSearchResults(data)
      setShowTopUsers(false)
      setHasLoaded(true)
    } catch (err: any) {
      console.error('Failed to load users:', err)
      setError(err.response?.data?.detail || 'Failed to load users. Please check your permissions.')
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (searchQuery.length > 0 && searchQuery.length < 3) return

    setLoading(true)
    setError(null)
    try {
      const response = searchQuery.length === 0 
        ? await adminApi.getUsers(0, 50, selectedRole === 'all' ? undefined : selectedRole)
        : await adminApi.searchUsers(searchQuery)
      
      const data = Array.isArray(response.data) ? response.data : (response.data.users || [])
      setSearchResults(data)
      setShowTopUsers(false)
      setHasLoaded(true)
    } catch (err: any) {
      console.error('Search failed:', err)
      setError(err.response?.data?.detail || 'Search failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const loadTopUsers = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await adminApi.getTopUsers(20)
      const data = Array.isArray(response.data) ? response.data : (response.data.users || [])
      setTopUsers(data)
      setShowTopUsers(true)
      setSearchResults([])
      setHasLoaded(true)
    } catch (err: any) {
      console.error('Failed to load top users:', err)
      setError(err.response?.data?.detail || 'Failed to load top users.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    const adminEmails = ['cjalloh25@gmail.com', 'esjallow03@gmail.com', 'esjallow@gmail.com']
    const isAdmin = user?.role === 'admin' || (user?.email && adminEmails.includes(user.email))
    
    if (!user || !isAdmin) {
      router.push('/dashboard')
      return
    }

    loadInitialUsers()
  }, [user, router, selectedRole])

  const handleDeactivate = async (userId: number) => {
    if (!confirm('Are you sure you want to deactivate this user?')) return

    const reason = prompt('Reason for deactivation:')
    if (!reason) return

    setActionLoading(userId)
    try {
      await adminApi.deactivateUser(userId, reason)
      // Refresh results
      if (searchQuery.length >= 3) {
        const response = await adminApi.searchUsers(searchQuery)
        setSearchResults(response.data)
      } else {
        loadInitialUsers()
      }
      alert('User deactivated successfully')
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to deactivate user')
    } finally {
      setActionLoading(null)
    }
  }

  const handleActivate = async (userId: number) => {
    if (!confirm('Are you sure you want to activate this user?')) return

    setActionLoading(userId)
    try {
      await adminApi.activateUser(userId)
      // Refresh results
      if (searchQuery.length >= 3) {
        const response = await adminApi.searchUsers(searchQuery)
        setSearchResults(response.data)
      } else {
        loadInitialUsers()
      }
      alert('User activated successfully')
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to activate user')
    } finally {
      setActionLoading(null)
    }
  }

  const handleUpdateUser = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!editingUser) return

    setActionLoading(editingUser.id)
    try {
      await adminApi.updateUser(editingUser.id, {
        full_name: editForm.full_name,
        role: editForm.role,
        total_points: editForm.total_points,
        is_verified: editForm.is_verified,
        is_active: editForm.is_active
      })
      
      // Refresh results
      if (searchQuery.length >= 3) {
        const response = await adminApi.searchUsers(searchQuery)
        setSearchResults(response.data)
      } else {
        loadInitialUsers()
      }
      
      setEditingUser(null)
      alert('User updated successfully')
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to update user')
    } finally {
      setActionLoading(null)
    }
  }

  const UserCard = ({ user, isTopUser = false }: { user: User | TopUser, isTopUser?: boolean }) => {
    const topUser = isTopUser ? user as TopUser : null

    return (
      <div className="bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h3 className="text-lg font-outfit font-bold text-slate-900 dark:text-slate-100 mb-1">
              {user.full_name}
            </h3>
            <div className="space-y-1">
              {user.email && (
                <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400">
                  <Mail className="w-4 h-4" />
                  {user.email}
                </div>
              )}
              {user.phone_number && (
                <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400">
                  <Phone className="w-4 h-4" />
                  {user.phone_number}
                </div>
              )}
            </div>
          </div>

          <div className="flex gap-2">
            <button
              onClick={() => {
                setEditingUser(user)
                setEditForm(user)
              }}
              className="p-2 text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition"
              title="Edit user"
            >
              <Edit2 className="w-5 h-5" />
            </button>
            {user.is_active ? (
              <button
                onClick={() => handleDeactivate(user.id)}
                disabled={actionLoading === user.id}
                className="p-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition disabled:opacity-50"
                title="Deactivate user"
              >
                {actionLoading === user.id ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <UserX className="w-5 h-5" />
                )}
              </button>
            ) : (
              <button
                onClick={() => handleActivate(user.id)}
                disabled={actionLoading === user.id}
                className="p-2 text-emerald-600 hover:bg-emerald-50 dark:hover:bg-emerald-900/20 rounded-lg transition disabled:opacity-50"
                title="Activate user"
              >
                {actionLoading === user.id ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <UserCheck className="w-5 h-5" />
                )}
              </button>
            )}
          </div>
        </div>

        <div className="flex flex-wrap gap-2 mb-4">
          <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
            user.is_active 
              ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400'
              : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
          }`}>
            {user.is_active ? 'Active' : 'Inactive'}
          </span>
          <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
            user.is_verified 
              ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'
              : 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400'
          }`}>
            {user.is_verified ? 'Verified' : 'Unverified'}
          </span>
          {user.role && (
            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400 capitalize">
              {user.role}
            </span>
          )}
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-slate-200 dark:border-slate-700">
          <div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Level</p>
            <p className="text-lg font-bold text-slate-900 dark:text-slate-100">{user.level}</p>
          </div>
          <div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Points</p>
            <p className="text-lg font-bold text-slate-900 dark:text-slate-100">{user.total_points.toLocaleString()}</p>
          </div>
          <div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Streak</p>
            <p className="text-lg font-bold text-slate-900 dark:text-slate-100">{user.study_streak} days</p>
          </div>
          {topUser && (
            <div>
              <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Accuracy</p>
              <p className="text-lg font-bold text-emerald-600 dark:text-emerald-500">{topUser.accuracy.toFixed(1)}%</p>
            </div>
          )}
        </div>

        {topUser && (
          <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-700">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Total Attempts</p>
                <p className="text-sm font-semibold text-slate-900 dark:text-slate-100">{topUser.total_attempts.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Last Active</p>
                <p className="text-sm font-semibold text-slate-900 dark:text-slate-100">
                  {new Date(topUser.last_active).toLocaleDateString()}
                </p>
              </div>
            </div>
          </div>
        )}

        <div className="mt-4 text-xs text-slate-500 dark:text-slate-400 flex items-center gap-2">
          <Calendar className="w-3 h-3" />
          Joined {new Date(user.created_at).toLocaleDateString()}
        </div>
      </div>
    )
  }

  return (
    <AppLayout>
      <div className="p-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-outfit font-bold text-slate-900 dark:text-slate-100">
            User Management
          </h1>
          <p className="text-slate-600 dark:text-slate-400 mt-1">
            Search users, view top performers, and manage accounts
          </p>
        </div>
        {/* Search Bar */}
        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6 mb-8">
          <div className="flex flex-col md:flex-row gap-4">
            <form onSubmit={handleSearch} className="flex-1 flex gap-3">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search by email, phone, or name..."
                  className="w-full pl-10 pr-4 py-3 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 text-slate-900 dark:text-slate-100"
                />
              </div>
              <button
                type="submit"
                disabled={loading || (searchQuery.length > 0 && searchQuery.length < 3)}
                className="px-6 py-3 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Search className="w-5 h-5" />}
                <span className="hidden sm:inline">Search</span>
              </button>
            </form>

            <div className="flex gap-3">
              <div className="relative">
                <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <select
                  value={selectedRole}
                  onChange={(e) => setSelectedRole(e.target.value)}
                  className="pl-9 pr-8 py-3 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 text-slate-900 dark:text-slate-100 appearance-none cursor-pointer font-medium"
                >
                  <option value="all">All Roles</option>
                  <option value="student">Students</option>
                  <option value="teacher">Teachers</option>
                  <option value="admin">Admins</option>
                </select>
              </div>

              <button
                onClick={loadTopUsers}
                disabled={loading}
                className="px-6 py-3 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition disabled:opacity-50 flex items-center gap-2"
              >
                <Trophy className="w-5 h-5" />
                <span className="hidden sm:inline">Top Users</span>
              </button>
            </div>
          </div>
        </div>

        {/* Results */}
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 text-emerald-500 animate-spin" />
          </div>
        ) : error ? (
          <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-8 text-center">
            <UserX className="w-12 h-12 text-red-500 mx-auto mb-4" />
            <h3 className="text-lg font-bold text-red-700 dark:text-red-400 mb-2">Error Loading Users</h3>
            <p className="text-red-600 dark:text-red-500 mb-6">{error}</p>
            <button
              onClick={loadInitialUsers}
              className="px-6 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition"
            >
              Try Again
            </button>
          </div>
        ) : showTopUsers && topUsers.length > 0 ? (
          <div>
            <div className="flex items-center gap-3 mb-6">
              <Trophy className="w-6 h-6 text-purple-500" />
              <h2 className="text-2xl font-outfit font-bold text-slate-900 dark:text-slate-100">
                Top {topUsers.length} Users
              </h2>
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {topUsers.map((user, index) => (
                <div key={user.id} className="relative">
                  {index < 3 && (
                    <div className={`absolute -top-3 -left-3 w-10 h-10 rounded-full flex items-center justify-center text-white font-bold ${
                      index === 0 ? 'bg-amber-500' : index === 1 ? 'bg-slate-400' : 'bg-amber-700'
                    }`}>
                      {index + 1}
                    </div>
                  )}
                  <UserCard user={user} isTopUser={true} />
                </div>
              ))}
            </div>
          </div>
        ) : searchResults.length > 0 ? (
          <div>
            <h2 className="text-2xl font-outfit font-bold text-slate-900 dark:text-slate-100 mb-6">
              {searchQuery ? `Search Results (${searchResults.length})` : `All Users (${searchResults.length})`}
            </h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {searchResults.map(user => (
                <UserCard key={user.id} user={user} />
              ))}
            </div>
          </div>
        ) : hasLoaded ? (
          <div className="text-center py-12">
            <UserX className="w-16 h-16 text-slate-300 dark:text-slate-600 mx-auto mb-4" />
            <p className="text-slate-600 dark:text-slate-400">
              {searchQuery ? `No users found matching "${searchQuery}"` : "No users found in the system"}
            </p>
          </div>
        ) : (
          <div className="text-center py-12">
            <Search className="w-16 h-16 text-slate-300 dark:text-slate-600 mx-auto mb-4" />
            <p className="text-slate-600 dark:text-slate-400">
              Search for users or view top performers
            </p>
          </div>
        )}

        {/* Edit User Modal */}
        {editingUser && (
          <div className="fixed inset-0 z-[60] flex items-center justify-center p-4">
            <div className="absolute inset-0 bg-slate-950/60 backdrop-blur-sm" onClick={() => setEditingUser(null)} />
            <div className="relative w-full max-w-lg bg-white dark:bg-slate-900 rounded-[2rem] shadow-2xl border-2 border-slate-100 dark:border-slate-800 overflow-hidden">
              <div className="p-8 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-2xl bg-blue-500/10 flex items-center justify-center">
                    <Edit2 className="w-6 h-6 text-blue-500" />
                  </div>
                  <div>
                    <h2 className="text-xl font-outfit font-black text-slate-900 dark:text-white">Edit User</h2>
                    <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">ID: {editingUser.id}</p>
                  </div>
                </div>
                <button 
                  onClick={() => setEditingUser(null)}
                  className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition"
                >
                  <X className="w-6 h-6 text-slate-400" />
                </button>
              </div>

              <form onSubmit={handleUpdateUser} className="p-8 space-y-6">
                <div className="space-y-2">
                  <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-2">Full Name</label>
                  <input
                    type="text"
                    value={editForm.full_name || ''}
                    onChange={(e) => setEditForm({ ...editForm, full_name: e.target.value })}
                    className="w-full h-14 px-6 bg-slate-50 dark:bg-slate-950 border-2 border-slate-100 dark:border-slate-800 rounded-2xl focus:outline-none focus:border-blue-500/50 transition-all dark:text-white font-bold"
                  />
                </div>

                <div className="grid grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-2">Role</label>
                    <select
                      value={editForm.role || 'student'}
                      onChange={(e) => setEditForm({ ...editForm, role: e.target.value })}
                      className="w-full h-14 px-6 bg-slate-50 dark:bg-slate-950 border-2 border-slate-100 dark:border-slate-800 rounded-2xl focus:outline-none focus:border-blue-500/50 transition-all dark:text-white font-bold appearance-none"
                    >
                      <option value="student">Student</option>
                      <option value="teacher">Teacher</option>
                      <option value="admin">Admin</option>
                    </select>
                  </div>
                  <div className="space-y-2">
                    <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-2">Total Points</label>
                    <input
                      type="number"
                      value={editForm.total_points || 0}
                      onChange={(e) => setEditForm({ ...editForm, total_points: parseInt(e.target.value) })}
                      className="w-full h-14 px-6 bg-slate-50 dark:bg-slate-950 border-2 border-slate-100 dark:border-slate-800 rounded-2xl focus:outline-none focus:border-blue-500/50 transition-all dark:text-white font-bold"
                    />
                  </div>
                </div>

                <div className="flex items-center gap-6 pt-4">
                  <label className="flex items-center gap-3 cursor-pointer group">
                    <div className="relative">
                      <input
                        type="checkbox"
                        checked={editForm.is_verified}
                        onChange={(e) => setEditForm({ ...editForm, is_verified: e.target.checked })}
                        className="sr-only"
                      />
                      <div className={`w-12 h-6 rounded-full transition-colors ${editForm.is_verified ? 'bg-emerald-500' : 'bg-slate-200 dark:bg-slate-800'}`} />
                      <div className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform ${editForm.is_verified ? 'translate-x-6' : ''}`} />
                    </div>
                    <span className="text-xs font-black text-slate-500 uppercase tracking-widest group-hover:text-slate-700 dark:group-hover:text-slate-300 transition-colors">Verified</span>
                  </label>

                  <label className="flex items-center gap-3 cursor-pointer group">
                    <div className="relative">
                      <input
                        type="checkbox"
                        checked={editForm.is_active}
                        onChange={(e) => setEditForm({ ...editForm, is_active: e.target.checked })}
                        className="sr-only"
                      />
                      <div className={`w-12 h-6 rounded-full transition-colors ${editForm.is_active ? 'bg-emerald-500' : 'bg-slate-200 dark:bg-slate-800'}`} />
                      <div className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform ${editForm.is_active ? 'translate-x-6' : ''}`} />
                    </div>
                    <span className="text-xs font-black text-slate-500 uppercase tracking-widest group-hover:text-slate-700 dark:group-hover:text-slate-300 transition-colors">Active</span>
                  </label>
                </div>

                <button
                  type="submit"
                  disabled={actionLoading === editingUser.id}
                  className="w-full h-16 bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-2xl font-outfit font-black text-xs uppercase tracking-[0.2em] shadow-2xl transition-all hover:scale-[1.02] active:scale-[0.98] flex items-center justify-center gap-3 disabled:opacity-50"
                >
                  {actionLoading === editingUser.id ? (
                    <Loader2 className="w-6 h-6 animate-spin" />
                  ) : (
                    <>
                      <Save className="w-5 h-5" />
                      Save Changes
                    </>
                  )}
                </button>
              </form>
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  )
}
