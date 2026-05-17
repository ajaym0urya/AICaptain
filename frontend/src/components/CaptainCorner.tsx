'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Trophy, Zap, Brain, MessageSquare, Shield, Loader2,
  ChevronDown, ChevronUp, BarChart2, Volume2, VolumeX, Wrench, RefreshCcw
} from 'lucide-react';

interface AgentOutput {
  agent: string;
  role: string;
  output: string;
  toolCall: string | null;
  step: number;
}

interface CaptainResponse {
  agentDebate: AgentOutput[];
  finalDecision: {
    initialDecision: string;
    finalCall: string;
    verdict: string;
    dissentingView: string;
    winProbability: string;
    commentatorVerdict: string;
  };
}

const AGENT_META: Record<string, { icon: React.ReactNode; color: string; border: string }> = {
  'Stats Analyst':               { icon: <Brain className="h-5 w-5" />,         color: 'text-blue-400',    border: 'border-blue-500/30 bg-blue-500/5' },
  'The Strategist':              { icon: <Trophy className="h-5 w-5" />,         color: 'text-yellow-400',  border: 'border-yellow-500/30 bg-yellow-500/5' },
  "Devil's Advocate":            { icon: <Shield className="h-5 w-5" />,         color: 'text-red-400',     border: 'border-red-500/30 bg-red-500/5' },
  'The Strategist (Rebuttal)':   { icon: <RefreshCcw className="h-5 w-5" />,     color: 'text-amber-400',   border: 'border-amber-500/30 bg-amber-500/5' },
  'Match Predictor':             { icon: <BarChart2 className="h-5 w-5" />,      color: 'text-purple-400',  border: 'border-purple-500/30 bg-purple-500/5' },
  'Match Commentator':           { icon: <MessageSquare className="h-5 w-5" />,  color: 'text-emerald-400', border: 'border-emerald-500/30 bg-emerald-500/5' },
};

function getAgentMeta(name: string) {
  return AGENT_META[name] || { icon: <Brain className="h-5 w-5" />, color: 'text-gray-400', border: 'border-white/10 bg-white/5' };
}

// Web Speech API voice output
function speak(text: string) {
  if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
    window.speechSynthesis.cancel();
    const utt = new SpeechSynthesisUtterance(
      text.replace(/[🏟️⚡🤔📊🏆👀🔴📚🔄]/gu, '') // strip emojis for cleaner TTS
    );
    utt.rate = 0.92;
    utt.pitch = 1.05;
    window.speechSynthesis.speak(utt);
  }
}
function stopSpeaking() {
  if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
    window.speechSynthesis.cancel();
  }
}

interface Props { matchUrl: string; }

export default function CaptainCorner({ matchUrl }: Props) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<CaptainResponse | null>(null);
  const [error, setError] = useState('');
  const [expandedAgent, setExpandedAgent] = useState<number | null>(null);
  const [isSpeaking, setIsSpeaking] = useState(false);

  const handleAskCaptain = async () => {
    setLoading(true);
    setError('');
    setResult(null);
    setExpandedAgent(null);
    stopSpeaking();

    try {
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const res = await fetch(`${backendUrl}/api/captain`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: matchUrl }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Agent pipeline failed');
      }
      const data: CaptainResponse = await res.json();
      setResult(data);
      setExpandedAgent(5); // Auto-expand commentator
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleVoice = () => {
    if (isSpeaking) {
      stopSpeaking();
      setIsSpeaking(false);
    } else {
      const text = result?.finalDecision?.commentatorVerdict ?? '';
      speak(text);
      setIsSpeaking(true);
      // Reset state when done
      setTimeout(() => setIsSpeaking(false), text.length * 55);
    }
  };

  const STEP_LABELS: Record<number, string> = {
    1: 'Data Fetch',
    2: 'Initial Proposal',
    3: 'Challenge',
    4: 'Rebuttal',
    5: 'Win Probability',
    6: 'Final Verdict',
  };

  return (
    <div className="lg:col-span-3 space-y-6">

      {/* Trigger Panel */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative bg-gradient-to-r from-yellow-950/60 to-amber-950/40 rounded-3xl p-6 border border-yellow-500/20 overflow-hidden"
      >
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_left,rgba(234,179,8,0.08),transparent_70%)]" />
        <div className="relative z-10 flex flex-col md:flex-row justify-between items-center gap-4">
          <div>
            <h2 className="text-2xl font-black text-white flex items-center gap-3">
              <Trophy className="h-7 w-7 text-yellow-400" />
              Captain Cool AI
            </h2>
            <p className="text-gray-400 mt-1 text-sm">
              5 Gemini agents debate • Multi-turn loop • Win probability • Live tool call
            </p>
            <div className="flex flex-wrap gap-2 mt-3">
              {['Stats Analyst', 'Strategist', "Devil's Advocate", 'Rebuttal', 'Win Predictor', 'Commentator'].map(a => (
                <span key={a} className="text-[10px] bg-white/5 border border-white/10 text-gray-400 px-2 py-0.5 rounded-full">{a}</span>
              ))}
            </div>
          </div>
          <button
            onClick={handleAskCaptain}
            disabled={loading || !matchUrl}
            className="flex items-center gap-3 bg-gradient-to-r from-yellow-500 to-amber-500 hover:from-yellow-400 hover:to-amber-400 text-black font-black px-8 py-4 rounded-2xl shadow-lg shadow-yellow-500/25 hover:shadow-yellow-500/40 transition-all disabled:opacity-40 disabled:cursor-not-allowed text-sm uppercase tracking-wider whitespace-nowrap"
          >
            {loading
              ? <><Loader2 className="h-5 w-5 animate-spin" /> Agents Debating...</>
              : <><Zap className="h-5 w-5" /> Ask AI Captain</>}
          </button>
        </div>
        {error && <p className="text-red-400 mt-4 text-sm font-medium relative z-10">{error}</p>}
      </motion.div>

      <AnimatePresence>
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            {/* Final Decision Hero Card */}
            <div className="bg-gradient-to-br from-yellow-950 to-black rounded-3xl p-8 border border-yellow-500/30 relative overflow-hidden">
              <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,rgba(234,179,8,0.12),transparent_70%)]" />
              <div className="relative z-10 space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-yellow-400 text-xs uppercase font-black tracking-widest">⚡ Captain's Committed Call</span>
                  <span className={`text-xs font-bold px-3 py-1 rounded-full ${
                    result.finalDecision.verdict?.includes('REVISED')
                      ? 'bg-orange-500/20 text-orange-400 border border-orange-500/30'
                      : 'bg-green-500/20 text-green-400 border border-green-500/30'
                  }`}>
                    {result.finalDecision.verdict?.includes('REVISED') ? '🔄 Decision Revised' : '✅ Standing Firm'}
                  </span>
                </div>

                <p className="text-white text-2xl md:text-3xl font-black leading-tight">
                  {result.finalDecision.finalCall || result.finalDecision.initialDecision}
                </p>

                {result.finalDecision.verdict && (
                  <p className="text-yellow-400/70 text-sm italic">{result.finalDecision.verdict}</p>
                )}

                {/* Dissent */}
                <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-2xl">
                  <p className="text-red-400 text-xs uppercase font-bold tracking-wider mb-1">
                    <Shield className="inline h-3 w-3 mr-1" /> Devil's Counter-Proposal
                  </p>
                  <p className="text-gray-300 text-sm">{result.finalDecision.dissentingView}</p>
                </div>

                {/* Win Probability */}
                {result.finalDecision.winProbability && (
                  <div className="p-4 bg-purple-500/10 border border-purple-500/20 rounded-2xl">
                    <p className="text-purple-400 text-xs uppercase font-bold tracking-wider mb-2">
                      <BarChart2 className="inline h-3 w-3 mr-1" /> Win Probability & Counterfactual
                    </p>
                    <p className="text-gray-200 text-sm leading-relaxed whitespace-pre-line">
                      {result.finalDecision.winProbability}
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Commentator Card with Voice */}
            <div className="bg-emerald-950/30 rounded-3xl p-6 border border-emerald-500/20">
              <div className="flex justify-between items-center mb-3">
                <p className="text-emerald-400 text-xs uppercase font-black tracking-widest flex items-center gap-2">
                  <MessageSquare className="h-4 w-4" /> Star Sports Commentary
                </p>
                <button
                  onClick={handleVoice}
                  className={`flex items-center gap-2 text-xs px-3 py-1.5 rounded-xl font-semibold transition-all ${
                    isSpeaking
                      ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                      : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 hover:bg-emerald-500/20'
                  }`}
                >
                  {isSpeaking ? <><VolumeX className="h-3 w-3" /> Stop</> : <><Volume2 className="h-3 w-3" /> Listen</>}
                </button>
              </div>
              <p className="text-gray-200 leading-relaxed whitespace-pre-line text-sm">
                {result.finalDecision.commentatorVerdict}
              </p>
            </div>

            {/* Agent Debate Timeline */}
            <div>
              <h3 className="text-gray-500 text-xs uppercase font-black tracking-widest mb-4 flex items-center gap-2">
                Multi-Turn Agent Debate — {result.agentDebate.length} steps
              </h3>
              <div className="space-y-3">
                {result.agentDebate.map((agent, i) => {
                  const meta = getAgentMeta(agent.agent);
                  return (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.05 }}
                      className={`rounded-2xl border p-5 ${meta.border} cursor-pointer`}
                      onClick={() => setExpandedAgent(expandedAgent === i ? null : i)}
                    >
                      <div className="flex justify-between items-center">
                        <div className="flex items-center gap-3">
                          <span className={`${meta.color}`}>{meta.icon}</span>
                          <div>
                            <p className="text-white font-bold text-sm">{agent.agent}</p>
                            <p className="text-gray-500 text-xs">{agent.role}</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          {/* Show tool call badge */}
                          {agent.toolCall && (
                            <span className="hidden md:flex items-center gap-1 text-[10px] bg-blue-500/10 border border-blue-500/20 text-blue-400 px-2 py-0.5 rounded-full font-mono">
                              <Wrench className="h-3 w-3" /> {agent.toolCall.slice(0, 30)}...
                            </span>
                          )}
                          <span className="text-gray-600 text-xs font-bold">
                            {STEP_LABELS[agent.step] || `Step ${agent.step}`}
                          </span>
                          {expandedAgent === i
                            ? <ChevronUp className="h-4 w-4 text-gray-500" />
                            : <ChevronDown className="h-4 w-4 text-gray-500" />}
                        </div>
                      </div>
                      <AnimatePresence>
                        {expandedAgent === i && (
                          <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: 'auto', opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            className="overflow-hidden"
                          >
                            {/* Show tool call explicitly if present */}
                            {agent.toolCall && (
                              <div className="mt-4 p-3 bg-blue-500/10 border border-blue-500/20 rounded-xl font-mono text-xs text-blue-300 flex items-center gap-2">
                                <Wrench className="h-4 w-4 flex-shrink-0" />
                                🔧 Tool Call: <span className="font-bold">{agent.toolCall}</span>
                              </div>
                            )}
                            <p className="text-gray-300 text-sm mt-4 leading-relaxed whitespace-pre-line border-t border-white/5 pt-4">
                              {agent.output}
                            </p>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </motion.div>
                  );
                })}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
