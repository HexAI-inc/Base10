'use client'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/store/authStore'
import { moderationApi, assetApi } from '@/lib/api'
import AppLayout from '@/components/AppLayout'
import { 
  Plus, 
  Upload, 
  Image as ImageIcon, 
  FileText, 
  Trash2, 
  Edit, 
  Save, 
  X, 
  Check,
  XCircle,
  Loader2, 
  Search,
  Layers,
  BookOpen,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  ExternalLink,
  Copy,
  RefreshCw
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '@/lib/utils'

type Tab = 'questions' | 'assets' | 'flashcards'

export default function ModerationPage() {
  const router = useRouter()
  const { user } = useAuthStore()
  const [activeTab, setActiveTab] = useState<Tab>('questions')
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    const adminEmails = ['cjalloh25@gmail.com', 'esjallow03@gmail.com', 'esjallow@gmail.com']
    const isAdmin = user?.role === 'admin' || (user?.email && adminEmails.includes(user.email))
    
    if (!user || !isAdmin) {
      router.push('/dashboard')
      return
    }
  }, [user, router])

  // Questions State
  const [questions, setQuestions] = useState<any[]>([])
  const [isCreatingQuestion, setIsCreatingQuestion] = useState(false)
  const [newQuestion, setNewQuestion] = useState({
    subject: '',
    topic: '',
    difficulty: 'medium',
    question_text: '',
    options: ['', '', '', ''],
    correct_answer: '',
    explanation: '',
    asset_id: ''
  })

  // Assets State
  const [assets, setAssets] = useState<any[]>([])
  const [uploading, setUploading] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [assetMetadata, setAssetMetadata] = useState({
    description: '',
    ocr_text: '',
    tags: ''
  })

  // Flashcards State
  const [decks, setDecks] = useState<any[]>([])
  const [isCreatingDeck, setIsCreatingDeck] = useState(false)
  const [newDeck, setNewDeck] = useState({ title: '', subject: '', description: '' })
  const [selectedDeckId, setSelectedDeckId] = useState<number | null>(null)
  const [newFlashcard, setNewFlashcard] = useState({ front: '', back: '', asset_id: '' })

  useEffect(() => {
    if (activeTab === 'assets') loadAssets()
    // Add other loaders as needed
  }, [activeTab])

  const loadAssets = async () => {
    setLoading(true)
    try {
      const res = await moderationApi.listAssets()
      setAssets(res.data)
    } catch (err) {
      setError('Failed to load assets')
    } finally {
      setLoading(false)
    }
  }

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedFile) return
    
    setUploading(true)
    setError('')
    const formData = new FormData()
    formData.append('file', selectedFile)
    formData.append('description', assetMetadata.description)
    formData.append('ocr_text', assetMetadata.ocr_text)
    
    try {
      await moderationApi.uploadAsset(formData)
      setSuccess('Asset uploaded successfully!')
      setSelectedFile(null)
      setAssetMetadata({ description: '', ocr_text: '', tags: '' })
      loadAssets()
    } catch (err) {
      setError('Upload failed')
    } finally {
      setUploading(false)
    }
  }

  const handleCreateQuestion = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      await moderationApi.createQuestion(newQuestion)
      setSuccess('Question created!')
      setIsCreatingQuestion(false)
      setNewQuestion({
        subject: '', topic: '', difficulty: 'medium',
        question_text: '', options: ['', '', '', ''],
        correct_answer: '', explanation: '', asset_id: ''
      })
    } catch (err) {
      setError('Failed to create question')
    } finally {
      setLoading(false)
    }
  }

  const handleReviewAsset = async (id: number, status: 'approved' | 'rejected') => {
    const notes = status === 'rejected' ? prompt('Reason for rejection:') : undefined
    if (status === 'rejected' && notes === null) return

    setLoading(true)
    try {
      await moderationApi.reviewAsset(id, status, notes || undefined)
      setSuccess(`Asset ${status} successfully!`)
      loadAssets()
    } catch (err) {
      setError('Failed to review asset')
    } finally {
      setLoading(false)
    }
  }

  return (
    <AppLayout>
      <div className="max-w-7xl mx-auto p-6 space-y-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <h1 className="text-4xl font-outfit font-black text-slate-900 dark:text-white tracking-tight">Content Moderation</h1>
            <p className="text-slate-500 font-medium text-lg">Manage platform content, assets, and flashcards</p>
          </div>
          <div className="flex items-center gap-2 bg-slate-100 dark:bg-slate-900 p-1.5 rounded-2xl border border-slate-200 dark:border-slate-800">
            {(['questions', 'assets', 'flashcards'] as Tab[]).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={cn(
                  "px-6 py-2.5 rounded-xl font-bold text-sm transition-all capitalize",
                  activeTab === tab 
                    ? "bg-white dark:bg-slate-800 text-emerald-600 dark:text-emerald-400 shadow-sm" 
                    : "text-slate-500 hover:text-slate-700 dark:hover:text-slate-300"
                )}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>

        {/* Status Messages */}
        <AnimatePresence>
          {success && (
            <motion.div 
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="bg-emerald-500/10 border border-emerald-500/20 p-4 rounded-2xl flex items-center gap-3 text-emerald-600 dark:text-emerald-400 font-bold"
            >
              <CheckCircle2 className="w-5 h-5" />
              {success}
              <button onClick={() => setSuccess('')} className="ml-auto"><X className="w-4 h-4" /></button>
            </motion.div>
          )}
          {error && (
            <motion.div 
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="bg-red-500/10 border border-red-500/20 p-4 rounded-2xl flex items-center gap-3 text-red-600 dark:text-red-400 font-bold"
            >
              <AlertCircle className="w-5 h-5" />
              {error}
              <button onClick={() => setError('')} className="ml-auto"><X className="w-4 h-4" /></button>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Tab Content */}
        <div className="min-h-[600px]">
          {activeTab === 'questions' && (
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-black text-slate-800 dark:text-white">Static Questions</h2>
                <button 
                  onClick={() => setIsCreatingQuestion(true)}
                  className="bg-emerald-500 hover:bg-emerald-600 text-white px-6 py-3 rounded-2xl font-black flex items-center gap-2 transition-all shadow-lg shadow-emerald-500/20"
                >
                  <Plus className="w-5 h-5" /> Create Question
                </button>
              </div>

              {isCreatingQuestion && (
                <motion.div 
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-[2.5rem] p-8 shadow-xl"
                >
                  <form onSubmit={handleCreateQuestion} className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      <div className="space-y-2">
                        <label className="text-xs font-black text-slate-500 uppercase tracking-widest ml-2">Subject</label>
                        <input 
                          type="text" 
                          value={newQuestion.subject}
                          onChange={e => setNewQuestion({...newQuestion, subject: e.target.value})}
                          className="w-full h-14 px-6 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl outline-none focus:border-emerald-500 transition-all font-bold"
                          placeholder="e.g. Mathematics"
                          required
                        />
                      </div>
                      <div className="space-y-2">
                        <label className="text-xs font-black text-slate-500 uppercase tracking-widest ml-2">Topic</label>
                        <input 
                          type="text" 
                          value={newQuestion.topic}
                          onChange={e => setNewQuestion({...newQuestion, topic: e.target.value})}
                          className="w-full h-14 px-6 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl outline-none focus:border-emerald-500 transition-all font-bold"
                          placeholder="e.g. Algebra"
                          required
                        />
                      </div>
                      <div className="space-y-2">
                        <label className="text-xs font-black text-slate-500 uppercase tracking-widest ml-2">Difficulty</label>
                        <select 
                          value={newQuestion.difficulty}
                          onChange={e => setNewQuestion({...newQuestion, difficulty: e.target.value})}
                          className="w-full h-14 px-6 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl outline-none focus:border-emerald-500 transition-all font-bold appearance-none"
                        >
                          <option value="easy">Easy</option>
                          <option value="medium">Medium</option>
                          <option value="hard">Hard</option>
                        </select>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <label className="text-xs font-black text-slate-500 uppercase tracking-widest ml-2">Question Text</label>
                      <textarea 
                        value={newQuestion.question_text}
                        onChange={e => setNewQuestion({...newQuestion, question_text: e.target.value})}
                        className="w-full min-h-[120px] p-6 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl outline-none focus:border-emerald-500 transition-all font-bold"
                        placeholder="Enter the question content..."
                        required
                      />
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {newQuestion.options.map((opt, i) => (
                        <div key={i} className="space-y-2">
                          <label className="text-xs font-black text-slate-500 uppercase tracking-widest ml-2">Option {String.fromCharCode(65 + i)}</label>
                          <input 
                            type="text" 
                            value={opt}
                            onChange={e => {
                              const newOpts = [...newQuestion.options]
                              newOpts[i] = e.target.value
                              setNewQuestion({...newQuestion, options: newOpts})
                            }}
                            className="w-full h-14 px-6 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl outline-none focus:border-emerald-500 transition-all font-bold"
                            placeholder={`Option ${String.fromCharCode(65 + i)}`}
                            required
                          />
                        </div>
                      ))}
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="space-y-2">
                        <label className="text-xs font-black text-slate-500 uppercase tracking-widest ml-2">Correct Answer</label>
                        <select 
                          value={newQuestion.correct_answer}
                          onChange={e => setNewQuestion({...newQuestion, correct_answer: e.target.value})}
                          className="w-full h-14 px-6 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl outline-none focus:border-emerald-500 transition-all font-bold appearance-none"
                          required
                        >
                          <option value="">Select Correct Option</option>
                          {newQuestion.options.map((opt, i) => (
                            <option key={i} value={opt}>{String.fromCharCode(65 + i)}: {opt}</option>
                          ))}
                        </select>
                      </div>
                      <div className="space-y-2">
                        <label className="text-xs font-black text-slate-500 uppercase tracking-widest ml-2">Linked Asset ID (Optional)</label>
                        <input 
                          type="text" 
                          value={newQuestion.asset_id}
                          onChange={e => setNewQuestion({...newQuestion, asset_id: e.target.value})}
                          className="w-full h-14 px-6 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl outline-none focus:border-emerald-500 transition-all font-bold"
                          placeholder="e.g. 42"
                        />
                      </div>
                    </div>

                    <div className="flex justify-end gap-4 pt-4">
                      <button 
                        type="button"
                        onClick={() => setIsCreatingQuestion(false)}
                        className="px-8 py-3 rounded-2xl font-bold text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 transition-all"
                      >
                        Cancel
                      </button>
                      <button 
                        type="submit"
                        disabled={loading}
                        className="bg-emerald-500 hover:bg-emerald-600 text-white px-10 py-3 rounded-2xl font-black flex items-center gap-2 transition-all shadow-lg shadow-emerald-500/20 disabled:opacity-50"
                      >
                        {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Save Question'}
                      </button>
                    </div>
                  </form>
                </motion.div>
              )}

              <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-[2.5rem] overflow-hidden">
                <div className="p-8 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
                  <h3 className="font-black text-slate-800 dark:text-white">Recent Questions</h3>
                  <div className="relative">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                    <input 
                      type="text" 
                      placeholder="Search questions..."
                      className="pl-10 pr-4 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl outline-none focus:border-emerald-500 transition-all text-sm font-bold"
                    />
                  </div>
                </div>
                <div className="p-8 text-center text-slate-500 font-medium">
                  <BookOpen className="w-12 h-12 mx-auto mb-4 opacity-20" />
                  <p>No questions found. Create your first static question above.</p>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'assets' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Upload Section */}
                <div className="lg:col-span-1 space-y-6">
                  <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-[2.5rem] p-8 shadow-xl">
                    <h3 className="text-xl font-black text-slate-800 dark:text-white mb-6 flex items-center gap-2">
                      <Upload className="w-5 h-5 text-emerald-500" /> Upload Asset
                    </h3>
                    <form onSubmit={handleFileUpload} className="space-y-6">
                      <div 
                        className={cn(
                          "border-2 border-dashed rounded-3xl p-8 text-center transition-all cursor-pointer group",
                          selectedFile ? "border-emerald-500 bg-emerald-500/5" : "border-slate-200 dark:border-slate-800 hover:border-emerald-500/50"
                        )}
                        onClick={() => document.getElementById('file-upload')?.click()}
                      >
                        <input 
                          id="file-upload"
                          type="file" 
                          className="hidden" 
                          onChange={e => setSelectedFile(e.target.files?.[0] || null)}
                        />
                        {selectedFile ? (
                          <div className="space-y-2">
                            <div className="w-12 h-12 bg-emerald-500 rounded-2xl flex items-center justify-center mx-auto text-white">
                              <ImageIcon className="w-6 h-6" />
                            </div>
                            <p className="font-bold text-slate-800 dark:text-white text-sm truncate px-4">{selectedFile.name}</p>
                            <p className="text-xs text-slate-500">{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
                          </div>
                        ) : (
                          <div className="space-y-2">
                            <div className="w-12 h-12 bg-slate-100 dark:bg-slate-800 rounded-2xl flex items-center justify-center mx-auto text-slate-400 group-hover:text-emerald-500 transition-colors">
                              <Plus className="w-6 h-6" />
                            </div>
                            <p className="font-bold text-slate-500 text-sm">Click to select file</p>
                            <p className="text-xs text-slate-400 uppercase tracking-widest font-black">Images or PDFs</p>
                          </div>
                        )}
                      </div>

                      <div className="space-y-2">
                        <label className="text-xs font-black text-slate-500 uppercase tracking-widest ml-2">Description</label>
                        <textarea 
                          value={assetMetadata.description}
                          onChange={e => setAssetMetadata({...assetMetadata, description: e.target.value})}
                          className="w-full h-24 p-4 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl outline-none focus:border-emerald-500 transition-all font-bold text-sm"
                          placeholder="What is this asset for?"
                        />
                      </div>

                      <div className="space-y-2">
                        <label className="text-xs font-black text-slate-500 uppercase tracking-widest ml-2">AI Metadata (OCR/Context)</label>
                        <textarea 
                          value={assetMetadata.ocr_text}
                          onChange={e => setAssetMetadata({...assetMetadata, ocr_text: e.target.value})}
                          className="w-full h-24 p-4 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl outline-none focus:border-emerald-500 transition-all font-bold text-sm"
                          placeholder="OCR text or detailed context for AI..."
                        />
                      </div>

                      <button 
                        type="submit"
                        disabled={!selectedFile || uploading}
                        className="w-full bg-emerald-500 hover:bg-emerald-600 text-white h-14 rounded-2xl font-black flex items-center justify-center gap-2 transition-all shadow-lg shadow-emerald-500/20 disabled:opacity-50"
                      >
                        {uploading ? <Loader2 className="w-5 h-5 animate-spin" /> : (
                          <>
                            <Upload className="w-5 h-5" /> Upload to Cloud
                          </>
                        )}
                      </button>
                    </form>
                  </div>
                </div>

                {/* Assets List */}
                <div className="lg:col-span-2 space-y-6">
                  <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-[2.5rem] overflow-hidden shadow-xl">
                    <div className="p-8 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
                      <h3 className="text-xl font-black text-slate-800 dark:text-white">Cloud Assets</h3>
                      <button onClick={loadAssets} className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition-colors">
                        <RefreshCw className={cn("w-5 h-5 text-slate-400", loading && "animate-spin")} />
                      </button>
                    </div>
                    
                    <div className="p-8">
                      {loading && assets.length === 0 ? (
                        <div className="flex flex-col items-center justify-center py-20 gap-4">
                          <Loader2 className="w-10 h-10 text-emerald-500 animate-spin" />
                          <p className="text-slate-500 font-bold uppercase tracking-widest text-xs">Fetching assets...</p>
                        </div>
                      ) : assets.length === 0 ? (
                        <div className="text-center py-20">
                          <ImageIcon className="w-16 h-16 mx-auto mb-4 opacity-10" />
                          <p className="text-slate-500 font-bold">No assets found in DigitalOcean Spaces.</p>
                        </div>
                      ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                          {assets.map((asset) => (
                            <div key={asset.id} className="group bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 rounded-3xl p-4 hover:border-emerald-500/50 transition-all">
                              <div className="aspect-video bg-slate-200 dark:bg-slate-800 rounded-2xl mb-4 overflow-hidden relative">
                                {asset.file_type?.startsWith('image') ? (
                                  <img 
                                    src={assetApi.getImageUrl(asset.filename, { quality: 'low' })} 
                                    alt={asset.description}
                                    className="w-full h-full object-cover"
                                  />
                                ) : (
                                  <div className="w-full h-full flex items-center justify-center">
                                    <FileText className="w-12 h-12 text-slate-400" />
                                  </div>
                                )}
                                <div className="absolute top-2 right-2 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                  <button className="p-2 bg-white/90 dark:bg-slate-900/90 rounded-lg text-slate-600 dark:text-slate-400 hover:text-emerald-500 transition-colors">
                                    <Edit className="w-4 h-4" />
                                  </button>
                                  <button className="p-2 bg-white/90 dark:bg-slate-900/90 rounded-lg text-slate-600 dark:text-slate-400 hover:text-red-500 transition-colors">
                                    <Trash2 className="w-4 h-4" />
                                  </button>
                                </div>
                              </div>
                              <div className="space-y-1">
                                <div className="flex items-center justify-between">
                                  <span className="text-[10px] font-black text-emerald-500 uppercase tracking-widest">ID: {asset.id}</span>
                                  <div className="flex items-center gap-2">
                                    {asset.status === 'approved' && <span className="text-[8px] font-black bg-emerald-500/10 text-emerald-500 px-2 py-0.5 rounded-full uppercase">Approved</span>}
                                    {asset.status === 'rejected' && <span className="text-[8px] font-black bg-red-500/10 text-red-500 px-2 py-0.5 rounded-full uppercase">Rejected</span>}
                                    {(!asset.status || asset.status === 'pending') && <span className="text-[8px] font-black bg-amber-500/10 text-amber-500 px-2 py-0.5 rounded-full uppercase">Pending</span>}
                                    <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">{asset.file_size_kb} KB</span>
                                  </div>
                                </div>
                                <h4 className="font-bold text-slate-800 dark:text-white truncate">{asset.filename}</h4>
                                <p className="text-xs text-slate-500 line-clamp-1">{asset.description || 'No description'}</p>
                              </div>
                              <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-700 flex flex-col gap-2">
                                <div className="flex items-center gap-2">
                                  <button 
                                    onClick={() => {
                                      navigator.clipboard.writeText(asset.cloud_url)
                                      setSuccess('URL copied to clipboard!')
                                    }}
                                    className="flex-1 h-10 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-[10px] font-black uppercase tracking-widest flex items-center justify-center gap-2 hover:border-emerald-500 transition-all"
                                  >
                                    <Copy className="w-3 h-3" /> Copy URL
                                  </button>
                                  <a 
                                    href={asset.cloud_url} 
                                    target="_blank" 
                                    rel="noopener noreferrer"
                                    className="w-10 h-10 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl flex items-center justify-center hover:border-emerald-500 transition-all"
                                  >
                                    <ExternalLink className="w-4 h-4" />
                                  </a>
                                </div>
                                
                                {(!asset.status || asset.status === 'pending') && (
                                  <div className="flex items-center gap-2">
                                    <button 
                                      onClick={() => handleReviewAsset(asset.id, 'approved')}
                                      className="flex-1 h-10 bg-emerald-500 text-white rounded-xl text-[10px] font-black uppercase tracking-widest flex items-center justify-center gap-2 hover:bg-emerald-600 transition-all"
                                    >
                                      <Check className="w-3 h-3" /> Approve
                                    </button>
                                    <button 
                                      onClick={() => handleReviewAsset(asset.id, 'rejected')}
                                      className="flex-1 h-10 bg-red-500 text-white rounded-xl text-[10px] font-black uppercase tracking-widest flex items-center justify-center gap-2 hover:bg-red-600 transition-all"
                                    >
                                      <XCircle className="w-3 h-3" /> Reject
                                    </button>
                                  </div>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'flashcards' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Decks List */}
                <div className="lg:col-span-1 space-y-6">
                  <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-[2.5rem] p-8 shadow-xl">
                    <div className="flex items-center justify-between mb-6">
                      <h3 className="text-xl font-black text-slate-800 dark:text-white flex items-center gap-2">
                        <Layers className="w-5 h-5 text-emerald-500" /> Official Decks
                      </h3>
                      <button 
                        onClick={() => setIsCreatingDeck(true)}
                        className="p-2 bg-emerald-500/10 text-emerald-500 rounded-xl hover:bg-emerald-500 hover:text-white transition-all"
                      >
                        <Plus className="w-5 h-5" />
                      </button>
                    </div>

                    {isCreatingDeck && (
                      <motion.div 
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="mb-6 p-4 bg-slate-50 dark:bg-slate-800 rounded-2xl border border-emerald-500/20 space-y-4"
                      >
                        <input 
                          type="text" 
                          placeholder="Deck Title"
                          value={newDeck.title}
                          onChange={e => setNewDeck({...newDeck, title: e.target.value})}
                          className="w-full h-12 px-4 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl outline-none focus:border-emerald-500 font-bold text-sm"
                        />
                        <input 
                          type="text" 
                          placeholder="Subject"
                          value={newDeck.subject}
                          onChange={e => setNewDeck({...newDeck, subject: e.target.value})}
                          className="w-full h-12 px-4 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl outline-none focus:border-emerald-500 font-bold text-sm"
                        />
                        <div className="flex gap-2">
                          <button 
                            onClick={() => setIsCreatingDeck(false)}
                            className="flex-1 h-10 rounded-xl font-bold text-xs text-slate-500 hover:bg-slate-200 dark:hover:bg-slate-700 transition-all"
                          >
                            Cancel
                          </button>
                          <button 
                            onClick={async () => {
                              setLoading(true)
                              try {
                                await moderationApi.createDeck(newDeck)
                                setSuccess('Deck created!')
                                setIsCreatingDeck(false)
                                setNewDeck({ title: '', subject: '', description: '' })
                              } catch (err) { setError('Failed to create deck') }
                              finally { setLoading(false) }
                            }}
                            className="flex-1 h-10 bg-emerald-500 text-white rounded-xl font-bold text-xs transition-all"
                          >
                            Create
                          </button>
                        </div>
                      </motion.div>
                    )}

                    <div className="space-y-3">
                      {decks.length === 0 ? (
                        <p className="text-center py-10 text-slate-500 text-sm font-medium">No official decks yet.</p>
                      ) : (
                        decks.map(deck => (
                          <button 
                            key={deck.id}
                            onClick={() => setSelectedDeckId(deck.id)}
                            className={cn(
                              "w-full p-4 rounded-2xl border text-left transition-all group",
                              selectedDeckId === deck.id 
                                ? "bg-emerald-500 border-emerald-500 text-white shadow-lg shadow-emerald-500/20" 
                                : "bg-slate-50 dark:bg-slate-800/50 border-slate-200 dark:border-slate-700 hover:border-emerald-500/50"
                            )}
                          >
                            <div className="flex items-center justify-between mb-1">
                              <span className={cn("text-[10px] font-black uppercase tracking-widest", selectedDeckId === deck.id ? "text-emerald-100" : "text-emerald-500")}>
                                {deck.subject}
                              </span>
                              <span className={cn("text-[10px] font-black uppercase tracking-widest", selectedDeckId === deck.id ? "text-emerald-100" : "text-slate-400")}>
                                {deck.card_count || 0} Cards
                              </span>
                            </div>
                            <h4 className="font-black truncate">{deck.title}</h4>
                          </button>
                        ))
                      )}
                    </div>
                  </div>
                </div>

                {/* Flashcards Management */}
                <div className="lg:col-span-2 space-y-6">
                  {selectedDeckId ? (
                    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-[2.5rem] p-8 shadow-xl">
                      <div className="flex items-center justify-between mb-8">
                        <h3 className="text-2xl font-black text-slate-800 dark:text-white">Add Flashcard</h3>
                        <span className="px-4 py-1.5 bg-emerald-500/10 text-emerald-500 rounded-full text-xs font-black uppercase tracking-widest">
                          Deck ID: {selectedDeckId}
                        </span>
                      </div>

                      <form 
                        onSubmit={async (e) => {
                          e.preventDefault()
                          setLoading(true)
                          try {
                            const payload = {
                              ...newFlashcard,
                              deck_id: selectedDeckId,
                              asset_id: newFlashcard.asset_id ? parseInt(newFlashcard.asset_id) : undefined
                            }
                            await moderationApi.addFlashcard(payload)
                            setSuccess('Flashcard added!')
                            setNewFlashcard({ front: '', back: '', asset_id: '' })
                          } catch (err) { setError('Failed to add flashcard') }
                          finally { setLoading(false) }
                        }}
                        className="space-y-6"
                      >
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                          <div className="space-y-2">
                            <label className="text-xs font-black text-slate-500 uppercase tracking-widest ml-2">Front Side (Question)</label>
                            <textarea 
                              value={newFlashcard.front}
                              onChange={e => setNewFlashcard({...newFlashcard, front: e.target.value})}
                              className="w-full h-32 p-6 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl outline-none focus:border-emerald-500 transition-all font-bold"
                              placeholder="Enter question or term..."
                              required
                            />
                          </div>
                          <div className="space-y-2">
                            <label className="text-xs font-black text-slate-500 uppercase tracking-widest ml-2">Back Side (Answer)</label>
                            <textarea 
                              value={newFlashcard.back}
                              onChange={e => setNewFlashcard({...newFlashcard, back: e.target.value})}
                              className="w-full h-32 p-6 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl outline-none focus:border-emerald-500 transition-all font-bold"
                              placeholder="Enter answer or explanation..."
                              required
                            />
                          </div>
                        </div>

                        <div className="space-y-2">
                          <label className="text-xs font-black text-slate-500 uppercase tracking-widest ml-2">Linked Asset ID (Optional)</label>
                          <div className="relative group">
                            <ImageIcon className="absolute left-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 group-focus-within:text-emerald-500 transition-colors" />
                            <input 
                              type="text" 
                              value={newFlashcard.asset_id}
                              onChange={e => setNewFlashcard({...newFlashcard, asset_id: e.target.value})}
                              className="w-full h-14 pl-14 pr-6 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl outline-none focus:border-emerald-500 transition-all font-bold"
                              placeholder="e.g. 105"
                            />
                          </div>
                          <p className="text-[10px] text-slate-500 font-medium ml-2">Link an image from the Assets tab to show it on the flashcard.</p>
                        </div>

                        <button 
                          type="submit"
                          disabled={loading}
                          className="w-full bg-emerald-500 hover:bg-emerald-600 text-white h-14 rounded-2xl font-black flex items-center justify-center gap-2 transition-all shadow-lg shadow-emerald-500/20 disabled:opacity-50"
                        >
                          {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : (
                            <>
                              <Sparkles className="w-5 h-5" /> Add to Deck
                            </>
                          )}
                        </button>
                      </form>
                    </div>
                  ) : (
                    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-[2.5rem] p-20 text-center shadow-xl">
                      <Layers className="w-20 h-20 mx-auto mb-6 opacity-10" />
                      <h3 className="text-2xl font-black text-slate-800 dark:text-white mb-2">Select a Deck</h3>
                      <p className="text-slate-500 font-medium">Choose an official deck from the left to manage its flashcards.</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  )
}
