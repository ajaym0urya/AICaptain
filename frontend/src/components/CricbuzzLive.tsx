'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, RefreshCcw, Search, Trophy, User, Crosshair, MapPin } from 'lucide-react';
import CaptainCorner from './CaptainCorner';

interface StaticData {
  matchTitle: string;
  venue: string;
  toss: string;
  format: string;
}

interface LiveData {
  matchStatus: string;
  score: string;
  runRate: string;
  batsmen: { name: string; runs: string; balls: string }[];
  bowlers: { name: string; overs: string; runs: string; wickets: string }[];
  recentBalls: string[];
}

export default function CricbuzzLive() {
  const [url, setUrl] = useState('');
  const [activeUrl, setActiveUrl] = useState('');
  
  const [staticData, setStaticData] = useState<StaticData | null>(null);
  const [liveData, setLiveData] = useState<LiveData | null>(null);
  
  const [loadingStatic, setLoadingStatic] = useState(false);
  const [loadingLive, setLoadingLive] = useState(false);
  const [error, setError] = useState('');
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const fetchStatic = async (targetUrl: string) => {
    setLoadingStatic(true);
    try {
      const res = await fetch('/api/scrape/static', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: targetUrl }),
      });
      if (!res.ok) throw new Error('Failed to fetch static match info');
      const data = await res.json();
      setStaticData(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoadingStatic(false);
    }
  };

  const fetchLive = async (targetUrl: string, isPolling = false) => {
    if (!isPolling) setLoadingLive(true);
    try {
      const res = await fetch('/api/scrape/live', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: targetUrl }),
      });
      if (!res.ok) throw new Error('Failed to fetch live score');
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      
      setLiveData(data);
      setLastUpdated(new Date());
    } catch (err: any) {
      if (!isPolling) setError(err.message);
    } finally {
      if (!isPolling) setLoadingLive(false);
    }
  };

  const handleStart = (e: React.FormEvent) => {
    e.preventDefault();
    if (url) {
      setActiveUrl(url);
      setStaticData(null);
      setLiveData(null);
      setError('');
      fetchStatic(url);
      fetchLive(url);
    }
  };

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (activeUrl && !error) {
      // Poll Live Data every 10 seconds
      interval = setInterval(() => {
        fetchLive(activeUrl, true);
      }, 10000);
    }
    return () => clearInterval(interval);
  }, [activeUrl, error]);

  const isLoading = loadingStatic || loadingLive;

  return (
    <div className="w-full max-w-5xl mx-auto p-4 space-y-8">
      {/* Input Section */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white/5 backdrop-blur-xl rounded-3xl p-6 shadow-2xl border border-white/10"
      >
        <form onSubmit={handleStart} className="flex flex-col md:flex-row gap-4 items-center">
          <div className="relative flex-1 w-full">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 h-5 w-5" />
            <input
              type="url"
              required
              placeholder="Paste Cricbuzz Live Match URL here..."
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="w-full bg-black/30 text-white placeholder-gray-500 rounded-2xl py-4 pl-12 pr-4 outline-none focus:ring-2 focus:ring-indigo-500 transition-all border border-white/5"
            />
          </div>
          <button
            type="submit"
            disabled={isLoading || !url}
            className="w-full md:w-auto bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white px-8 py-4 rounded-2xl font-bold shadow-lg hover:shadow-indigo-500/25 transition-all disabled:opacity-50 flex justify-center items-center gap-2"
          >
            {isLoading && !liveData ? <RefreshCcw className="animate-spin h-5 w-5" /> : <Activity className="h-5 w-5" />}
            Start Tracking
          </button>
        </form>
        {error && <p className="text-red-400 mt-4 text-sm font-medium">{error}</p>}
      </motion.div>

      {(staticData || liveData) && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Static Info Bar (Spans full width above score) */}
          {staticData && (
            <motion.div 
              initial={{ opacity: 0 }} animate={{ opacity: 1 }}
              className="lg:col-span-3 bg-gradient-to-r from-gray-900 to-gray-800 rounded-2xl p-6 border border-white/10 flex flex-col md:flex-row justify-between items-center gap-4"
            >
              <div>
                <h2 className="text-xl font-bold text-white mb-1">{staticData.matchTitle}</h2>
                <div className="flex items-center gap-2 text-gray-400 text-sm">
                  <MapPin className="h-4 w-4" /> {staticData.venue} • {staticData.format}
                </div>
              </div>
              <div className="bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 px-4 py-2 rounded-xl text-sm font-medium">
                {staticData.toss}
              </div>
            </motion.div>
          )}

          {/* Main Score Card */}
          {liveData && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="lg:col-span-2 bg-gradient-to-br from-gray-900 to-black rounded-3xl p-8 border border-white/5 relative overflow-hidden shadow-2xl"
            >
              <div className="absolute -top-10 -right-10 opacity-5">
                <Trophy className="h-64 w-64 text-white" />
              </div>
              
              <div className="flex justify-between items-start mb-8">
                <span className="bg-red-500/10 text-red-400 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-widest border border-red-500/20 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
                  Live Match
                </span>
                {lastUpdated && (
                  <span className="text-gray-500 text-xs font-medium flex items-center gap-1">
                    <RefreshCcw className="h-3 w-3" />
                    Updated {lastUpdated.toLocaleTimeString()}
                  </span>
                )}
              </div>

              <h1 className="text-5xl md:text-7xl font-black text-white mb-4 tracking-tighter">
                {liveData.score}
              </h1>
              <p className="text-2xl font-light text-gray-400 mb-8">{liveData.runRate}</p>
              
              <div className="inline-block bg-white/10 rounded-2xl px-6 py-3 text-emerald-400 font-semibold text-lg border border-white/5 backdrop-blur-md">
                {liveData.matchStatus}
              </div>
            </motion.div>
          )}

          {/* Player Stats Side Panel */}
          {liveData && (
            <div className="space-y-6">
              <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="bg-gray-900/80 rounded-3xl p-6 border border-white/5 backdrop-blur-xl">
                <h3 className="text-gray-400 text-xs uppercase font-bold tracking-widest mb-4 flex items-center gap-2">
                  <User className="h-4 w-4 text-indigo-400" /> Batting
                </h3>
                <div className="space-y-3">
                  {liveData.batsmen?.map((bat, i) => (
                    <div key={i} className="flex justify-between items-center bg-white/5 p-4 rounded-xl">
                      <span className="text-white font-semibold">{bat.name}</span>
                      <span className="text-gray-400 text-sm">
                        <span className="text-white font-bold text-lg">{bat.runs}</span> ({bat.balls})
                      </span>
                    </div>
                  ))}
                </div>
              </motion.div>

              <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.1 }} className="bg-gray-900/80 rounded-3xl p-6 border border-white/5 backdrop-blur-xl">
                <h3 className="text-gray-400 text-xs uppercase font-bold tracking-widest mb-4 flex items-center gap-2">
                  <Crosshair className="h-4 w-4 text-purple-400" /> Bowling
                </h3>
                <div className="space-y-3">
                  {liveData.bowlers?.map((bowl, i) => (
                    <div key={i} className="flex justify-between items-center bg-white/5 p-4 rounded-xl text-sm">
                      <span className="text-white font-semibold">{bowl.name}</span>
                      <span className="text-gray-400 text-sm">
                        {bowl.overs} O | <span className="text-white font-bold text-lg mx-1">{bowl.wickets}</span>-{bowl.runs}
                      </span>
                    </div>
                  ))}
                </div>
              </motion.div>
            </div>
          )}

          {/* Commentary Feed */}
          {liveData && (
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="lg:col-span-3 bg-gray-900/50 rounded-3xl p-6 border border-white/5 backdrop-blur-xl">
              <h3 className="text-gray-400 text-xs uppercase font-bold tracking-widest mb-6 flex items-center gap-2">
                <Activity className="h-4 w-4 text-emerald-400" /> Recent Ball-by-Ball
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <AnimatePresence>
                  {liveData.recentBalls?.map((ball, i) => (
                    <motion.div
                      key={ball + i}
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: i * 0.05 }}
                      className="p-5 bg-black/40 rounded-2xl border-l-4 border-indigo-500 text-gray-300 font-medium leading-relaxed"
                    >
                      {ball}
                    </motion.div>
                  ))}
                </AnimatePresence>
              </div>
            </motion.div>
          )}

          {/* ─── Captain Cool AI Agent Debate ─── */}
          {activeUrl && (
            <CaptainCorner matchUrl={activeUrl} />
          )}

        </div>
      )}
    </div>
  );
}
