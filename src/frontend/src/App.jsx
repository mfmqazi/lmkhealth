import { useState, useEffect } from 'react'
import axios from 'axios'
import ReactPlayer from 'react-player'
import { Search, Sparkles, MessageSquare, Calendar, BookOpen, ChevronDown, ChevronUp, Image as ImageIcon, Layers } from 'lucide-react'

const API_BASE = 'http://localhost:8001/api'
const IMAGE_BASE = 'http://localhost:8001'

function App() {
  const [timeline, setTimeline] = useState([])
  const [filteredTimeline, setFilteredTimeline] = useState([])
  const [search, setSearch] = useState('')
  const [selectedDate, setSelectedDate] = useState(null)
  const [summary, setSummary] = useState('')
  const [loadingSummary, setLoadingSummary] = useState(false)
  const [expandedTranscripts, setExpandedTranscripts] = useState({})

  useEffect(() => {
    fetchTimeline()
  }, [])

  useEffect(() => {
    // 1. Filter by Search
    let result = timeline
    if (search) {
      const lower = search.toLowerCase()
      result = result.map(day => {
        const matchingMsgs = day.messages.filter(m =>
          m.content.toLowerCase().includes(lower) ||
          m.sender.toLowerCase().includes(lower)
        )
        if (matchingMsgs.length > 0) {
          return { ...day, messages: matchingMsgs }
        }
        return null
      }).filter(Boolean)
    }

    // 2. Filter by Date (if selected)
    if (selectedDate) {
      result = result.filter(day => day.date === selectedDate)
    }

    setFilteredTimeline(result)
  }, [search, timeline, selectedDate])

  const fetchTimeline = async () => {
    try {
      const res = await axios.get(`${API_BASE}/timeline`)
      setTimeline(res.data)
      setFilteredTimeline(res.data)
    } catch (err) {
      console.error("Failed to fetch timeline", err)
    }
  }

  const handleSummarize = async (text) => {
    setLoadingSummary(true)
    setSummary('')
    window.scrollTo({ top: 0, behavior: 'smooth' })
    try {
      const res = await axios.post(`${API_BASE}/summary`, { text })
      setSummary(res.data.summary)
    } catch (err) {
      console.error(err)
      alert("Failed to generate summary")
    } finally {
      setLoadingSummary(false)
    }
  }

  const toggleTranscript = (idx) => {
    setExpandedTranscripts(prev => ({
      ...prev,
      [idx]: !prev[idx]
    }))
  }

  // Fallback URL extractor if backend didn't provide one
  const extractUrl = (text) => {
    if (!text) return null
    const urlLineMatch = text.match(/URL:\s*(https?:\/\/[^\s]+)/)
    if (urlLineMatch) return urlLineMatch[1]

    const match = text.match(/(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/[^\s]+)/)
    return match ? match[0] : null
  }

  return (
    <div className="min-h-screen pb-20 bg-slate-50 font-sans text-slate-800">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-slate-200 shadow-sm">
        <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2 cursor-pointer" onClick={() => { setSelectedDate(null); window.scrollTo({ top: 0, behavior: 'smooth' }) }}>
            <div className="bg-emerald-100 p-2 rounded-lg">
              <MessageSquare className="w-5 h-5 text-emerald-700" />
            </div>
            <h1 className="text-xl font-bold text-slate-800 tracking-tight hidden sm:block">
              LMKHealth<span className="text-emerald-600">Archive</span>
            </h1>
          </div>

          <div className="flex-1 max-w-lg mx-6 relative group">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 group-focus-within:text-emerald-500 transition-colors" />
            <input
              type="text"
              placeholder="Search transcripts, topics, images..."
              className="w-full pl-10 pr-4 py-2 rounded-xl bg-slate-100 border-transparent focus:bg-white focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200 outline-none transition-all"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
        </div>
      </header>

      {/* Navigation / Filter Bar */}
      <div className="bg-white border-b border-slate-200 sticky top-16 z-40 shadow-sm">
        <div className="max-w-6xl mx-auto px-4 py-3">
          {/* Top Row: Month Label & Batch Button */}
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-bold text-slate-500 uppercase tracking-wider flex items-center gap-2">
              <Calendar className="w-4 h-4" />
              October 2025
            </h2>
            <button
              onClick={() => setSelectedDate(null)}
              className={`px-3 py-1.5 rounded-md text-xs font-semibold flex items-center gap-1.5 transition-all
                    ${selectedDate === null
                  ? 'bg-emerald-600 text-white shadow-sm ring-2 ring-emerald-600 ring-offset-1'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}`}
            >
              <Layers className="w-3.5 h-3.5" />
              Show Full Batch
            </button>
          </div>

          {/* Bottom Row: Date Buttons (Scrollable) */}
          <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-hide -mx-4 px-4 sm:mx-0 sm:px-0">
            {timeline.map((day, idx) => {
              // Format date to M/D (e.g., 10/21)
              let label = day.date;
              if (day.date === "Resources & Archive") {
                label = "Resources";
              } else {
                const parts = day.date.split('/');
                if (parts.length === 3) {
                  label = `${parts[0]}/${parts[1]}`;
                }
              }

              return (
                <button
                  key={idx}
                  onClick={() => setSelectedDate(day.date)}
                  className={`whitespace-nowrap px-3 py-1.5 rounded-md text-xs font-medium transition-all border
                      ${selectedDate === day.date
                      ? 'bg-slate-800 text-white border-slate-800 shadow-sm'
                      : 'bg-white border-slate-200 text-slate-500 hover:border-emerald-300 hover:text-emerald-600'
                    }`}
                >
                  {label}
                </button>
              )
            })}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-4 mt-8 space-y-12">

        {/* Summary Modal */}
        {(summary || loadingSummary) && (
          <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/20 backdrop-blur-sm">
            <div className="bg-white p-8 rounded-3xl shadow-2xl max-w-2xl w-full border border-emerald-100 relative animate-in fade-in zoom-in duration-300 max-h-[90vh] overflow-y-auto">
              <button onClick={() => { setSummary(''); setLoadingSummary(false) }} className="absolute top-4 right-4 p-2 hover:bg-slate-100 rounded-full text-slate-400">✕</button>

              <h2 className="text-2xl font-bold flex items-center gap-3 text-emerald-800 mb-6">
                <div className="bg-emerald-100 p-2 rounded-xl">
                  {loadingSummary ? <Sparkles className="w-6 h-6 animate-pulse text-emerald-600" /> : <Sparkles className="w-6 h-6 text-emerald-600" />}
                </div>
                {loadingSummary ? "Generating AI Summary..." : "AI Summary"}
              </h2>

              {loadingSummary ? (
                <div className="space-y-3">
                  <div className="h-4 bg-slate-100 rounded animate-pulse w-3/4"></div>
                  <div className="h-4 bg-slate-100 rounded animate-pulse"></div>
                  <div className="h-4 bg-slate-100 rounded animate-pulse w-5/6"></div>
                </div>
              ) : (
                <div className="prose prose-emerald prose-lg max-w-none text-slate-600 leading-relaxed whitespace-pre-wrap">
                  {summary}
                </div>
              )}
            </div>
          </div>
        )}

        {filteredTimeline.map((day, dIdx) => {
          const isLibrary = day.date === "Resources & Archive";

          return (
            <div key={dIdx} className="relative animate-in fade-in slide-in-from-bottom-4 duration-500 fill-mode-backwards" style={{ animationDelay: `${dIdx * 50}ms` }}>
              {/* Date Header */}
              <div className="flex items-center gap-4 mb-8">
                <span className={`px-4 py-1.5 rounded-full text-sm font-semibold shadow-sm border flex items-center gap-2 
                      ${isLibrary ? 'bg-indigo-50 text-indigo-700 border-indigo-100' : 'bg-emerald-50 text-emerald-700 border-emerald-100'}`}>
                  {isLibrary ? <BookOpen className="w-4 h-4" /> : <Calendar className="w-4 h-4" />}
                  {day.date}
                </span>
                <div className="h-px bg-slate-200 flex-1"></div>
              </div>

              {/* Messages Grid */}
              <div className="flex flex-col gap-2">
                {day.messages.map((msg, mIdx) => {
                  const url = msg.video_url || extractUrl(msg.content);
                  // Simplified: just check if we have a video_url
                  const showPlayer = Boolean(msg.video_url);

                  // Debug logging for video messages
                  if (msg.video_url) {
                    console.log('Video message:', {
                      sender: msg.sender,
                      time: msg.time,
                      is_video: msg.is_video,
                      video_url: msg.video_url,
                      url: url,
                      showPlayer: showPlayer
                    });
                  }

                  const isTranscript = msg.content && typeof msg.content === 'string' && msg.content.includes("[Video Transcript]");
                  const isImage = msg.type === 'image';
                  const uniqueId = `${dIdx}-${mIdx}`;
                  const expanded = expandedTranscripts[uniqueId];

                  // Color hash for sender name
                  const senderColors = [
                    'text-red-500', 'text-orange-500', 'text-amber-500',
                    'text-green-500', 'text-emerald-500', 'text-teal-500',
                    'text-cyan-500', 'text-blue-500', 'text-indigo-500',
                    'text-violet-500', 'text-purple-500', 'text-fuchsia-500',
                    'text-pink-500', 'text-rose-500'
                  ];
                  const colorIndex = msg.sender.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0) % senderColors.length;
                  const senderColorClass = senderColors[colorIndex];

                  return (
                    <div key={mIdx} className={`max-w-3xl w-full mx-auto bg-white rounded-lg shadow-[0_1px_0.5px_rgba(0,0,0,0.13)] p-2 relative group mb-1 border-l-4 ${isTranscript ? 'border-l-indigo-400' : 'border-l-transparent'}`}>

                      {/* Sender Name */}
                      {!isImage && (
                        <div className={`text-xs font-bold mb-1 ${senderColorClass}`}>
                          {isTranscript ? "Archive Bot" : msg.sender}
                        </div>
                      )}

                      {/* Content Body */}
                      <div className="text-[14.2px] text-slate-900 leading-[19px] whitespace-pre-wrap">

                        {/* Text Content */}
                        {msg.type === 'text' && (
                          <div className={`${!expanded && isTranscript ? 'max-h-60 overflow-hidden mask-linear relative' : ''}`}>
                            {isTranscript && typeof msg.content === 'string' ? (
                              <div className="prose prose-sm max-w-none text-slate-800">
                                {msg.content.split('\n').map((line, i) => {
                                  if (line.startsWith('###')) return <h3 key={i} className="text-base font-bold text-slate-800 mt-2 mb-1">{line.replace('###', '').trim()}</h3>
                                  if (line.startsWith('**Source URL:**')) {
                                    const linkMatch = line.match(/\((.*?)\)/);
                                    const link = linkMatch ? linkMatch[1] : "#";
                                    return <a key={i} href={link} target="_blank" rel="noreferrer" className="block text-sky-500 hover:underline mb-2 break-all">{link}</a>
                                  }
                                  return <p key={i} className="mb-2 empty:hidden">{line}</p>
                                })}
                              </div>
                            ) : (
                              // Regular messages - Handle links
                              msg.content.split(/(https?:\/\/[^\s]+)/g).map((part, i) => (
                                part.match(/https?:\/\//) ?
                                  <a key={i} href={part} target="_blank" rel="noreferrer" className="text-sky-500 hover:underline break-all">{part}</a> :
                                  part
                              ))
                            )}

                            {isTranscript && !expanded && (
                              <div className="absolute bottom-0 left-0 w-full h-8 bg-gradient-to-t from-white to-transparent"></div>
                            )}
                          </div>
                        )}

                        {/* Video Player (Fallback to Thumbnail Link) */}
                        {showPlayer && (() => {
                          // Extract video ID for thumbnail
                          const videoIdMatch = msg.video_url.match(/(?:v=|youtu\.be\/|embed\/)([\w\-]+)/);
                          const videoId = videoIdMatch ? videoIdMatch[1] : null;
                          const thumbnailUrl = videoId
                            ? `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`
                            : null;

                          return (
                            <div className="mt-2 bg-slate-100 rounded-lg overflow-hidden border border-slate-200 w-full max-w-[480px]">
                              <a
                                href={msg.video_url}
                                target="_blank"
                                rel="noreferrer"
                                className="block relative group aspect-video bg-black"
                              >
                                {thumbnailUrl ? (
                                  <img
                                    src={thumbnailUrl}
                                    alt="Video thumbnail"
                                    className="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity"
                                  />
                                ) : (
                                  <div className="w-full h-full flex items-center justify-center text-white text-opacity-50">
                                    No Thumbnail
                                  </div>
                                )}
                                {/* Play Button Overlay */}
                                <div className="absolute inset-0 flex items-center justify-center">
                                  <div className="w-16 h-16 bg-red-600 rounded-full flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="white" className="w-8 h-8 ml-1">
                                      <path d="M8 5v14l11-7z" />
                                    </svg>
                                  </div>
                                </div>
                              </a>
                              <div className="p-3 bg-slate-50 border-t border-slate-200">
                                <div className="flex items-center gap-2 mb-1">
                                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="red" className="w-5 h-5">
                                    <path d="M19.615 3.184c-3.604-.246-11.631-.245-15.23 0-3.897.266-4.356 2.62-4.385 8.816.029 6.185.484 8.549 4.385 8.816 3.6.245 11.626.246 15.23 0 3.897-.266 4.356-2.62 4.385-8.816-.029-6.185-.484-8.549-4.385-8.816zm-10.615 12.816v-8l8 3.993-8 4.007z" />
                                  </svg>
                                  <span className="text-sm font-semibold text-slate-700">Watch on YouTube</span>
                                </div>
                                <a href={msg.video_url} target="_blank" rel="noreferrer" className="text-xs text-blue-600 hover:underline truncate block">
                                  {msg.video_url}
                                </a>
                              </div>
                            </div>
                          );
                        })()}

                        {/* Image Display */}
                        {isImage && (
                          <div className="mt-1 rounded-lg overflow-hidden">
                            <img
                              src={`${IMAGE_BASE}${msg.content}`}
                              alt="Gallery Item"
                              className="w-full h-auto max-h-[500px] object-cover"
                              loading="lazy"
                            />
                          </div>
                        )}

                      </div>

                      {/* Footer: Timestamp & Actions */}
                      <div className="flex justify-between items-end mt-1">
                        <div className="flex gap-2">
                          {isTranscript && (
                            <button
                              onClick={() => toggleTranscript(uniqueId)}
                              className="text-[11px] font-medium text-slate-400 hover:text-slate-600 uppercase tracking-wide"
                            >
                              {expanded ? "Show Less" : "Read More"}
                            </button>
                          )}
                          {msg.type === 'text' && !isTranscript && (
                            <button
                              onClick={() => handleSummarize(msg.content)}
                              className="text-[10px] text-slate-300 hover:text-emerald-500"
                              title="Summarize"
                            >
                              <Sparkles className="w-3 h-3" />
                            </button>
                          )}
                        </div>
                        <div className="text-[11px] text-slate-400 select-none">
                          {msg.time}
                        </div>
                      </div>

                    </div>
                  )
                })}
              </div>
            </div>
          )
        })}

        {filteredTimeline.length === 0 && (
          <div className="text-center py-24">
            <div className="inline-block p-4 rounded-full bg-slate-100 mb-4">
              <Search className="w-8 h-8 text-slate-400" />
            </div>
            <h3 className="text-lg font-medium text-slate-900">No matching results</h3>
            <p className="text-slate-500">Try searching for a different keyword or date.</p>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
