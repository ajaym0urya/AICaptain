'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Trophy, Zap, Brain, MessageSquare, Shield, Loader2, ChevronDown, ChevronUp } from 'lucide-react';

interface AgentOutput {
  agent: string;
  role: string;
  output: string;
}

interface CaptainResponse {
  agentDebate: AgentOutput[];
  finalDecision: {
    decision: string;
    fullProposal: string;
    dissentingView: string;
    commentatorVerdict: string;
  };
}

const AGENT_ICONS: Record<string, React.ReactNode> = {
  'Stats Analyst':     <Brain className="h-5 w-5 text-blue-400" />,
  'The Strategist':    <Trophy className="h-5 w-5 text-yellow-400" />,
  "Devil's Advocate":  <Shield className="h-5 w-5 text-red-400" />,
  'Match Commentator': <MessageSquare className="h-5 w-5 text-emerald-400" />,
};

const AGENT_COLORS: Record<string, string> = {
  'Stats Analyst':     'border-blue-500/40 bg-blue-500/5',
  'The Strategist':    'border-yellow-500/40 bg-yellow-500/5',
  "Devil's Advocate":  'border-red-500/40 bg-red-500/5',
  'Match Commentator': 'border-emerald-500/40 bg-emerald-500/5',
};

interface Props {
  matchUrl: string;
}

export default function CaptainCorner({ matchUrl }: Props) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<CaptainResponse | null>(null);
  const [error, setError] = useState('');
  const [expandedAgent, setExpandedAgent] = useState<number | null>(null);

  const handleAskCaptain = async () => {
    setLoading(true);
    setError('');
    setResult(null);
    setExpandedAgent(null);

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
      setExpandedAgent(3); // Auto-expand commentator (final verdict)
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="lg:col-span-3 space-y-6">
      {/* Captain Trigger Button */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-yellow-900/30 to-amber-900/20 rounded-3xl p-6 border border-yellow-500/20"
      >
        <div className="flex flex-col md:flex-row justify-between items-center gap-4">
          <div>
            <h2 className="text-2xl font-black text-white flex items-center gap-3">
              <Trophy className="h-7 w-7 text-yellow-400" />
              Captain Cool AI
            </h2>
            <p className="text-gray-400 mt-1 text-sm">
              4 Gemini agents debate the next tactical move — live, from this match
            </p>
          </div>
          <button
            onClick={handleAskCaptain}
            disabled={loading || !matchUrl}
            className="flex items-center gap-3 bg-gradient-to-r from-yellow-500 to-amber-500 hover:from-yellow-400 hover:to-amber-400 text-black font-black px-8 py-4 rounded-2xl shadow-lg shadow-yellow-500/25 hover:shadow-yellow-500/40 transition-all disabled:opacity-50 disabled:cursor-not-allowed text-sm uppercase tracking-wider"
          >
            {loading ? (
              <><Loader2 className="h-5 w-5 animate-spin" /> Agents Thinking...</>
            ) : (
              <><Zap className="h-5 w-5" /> Ask AI Captain</>
            )}
          </button>
        </div>
        {error && <p className="text-red-400 mt-4 text-sm font-medium">{error}</p>}
      </motion.div>

      {/* Final Decision — prominent card */}
      <AnimatePresence>
        {result && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="space-y-6"
          >
            {/* The Big Call */}
            <div className="bg-gradient-to-br from-yellow-950 to-black rounded-3xl p-8 border border-yellow-500/30 relative overflow-hidden">
              <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,rgba(234,179,8,0.1),transparent_70%)]" />
              <div className="relative z-10">
                <span className="text-yellow-400 text-xs uppercase font-black tracking-widest">⚡ Captain's Final Call</span>
                <p className="text-white text-2xl md:text-3xl font-black mt-3 leading-tight">
                  {result.finalDecision.decision}
                </p>
                <div className="mt-6 p-4 bg-red-500/10 border border-red-500/20 rounded-2xl">
                  <p className="text-red-400 text-xs uppercase font-bold tracking-wider mb-1">Dissenting View</p>
                  <p className="text-gray-300 text-sm">{result.finalDecision.dissentingView}</p>
                </div>
              </div>
            </div>

            {/* Commentator Verdict */}
            <div className="bg-emerald-950/30 rounded-3xl p-6 border border-emerald-500/20">
              <p className="text-emerald-400 text-xs uppercase font-black tracking-widest mb-3 flex items-center gap-2">
                <MessageSquare className="h-4 w-4" /> Star Sports Commentary
              </p>
              <p className="text-gray-200 leading-relaxed whitespace-pre-line text-sm">
                {result.finalDecision.commentatorVerdict}
              </p>
            </div>

            {/* Agent Debate Timeline */}
            <div>
              <h3 className="text-gray-400 text-xs uppercase font-black tracking-widest mb-4">
                Agent Debate Timeline
              </h3>
              <div className="space-y-3">
                {result.agentDebate.map((agent, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.1 }}
                    className={`rounded-2xl border p-5 ${AGENT_COLORS[agent.agent] || 'border-white/10 bg-white/5'} cursor-pointer`}
                    onClick={() => setExpandedAgent(expandedAgent === i ? null : i)}
                  >
                    <div className="flex justify-between items-center">
                      <div className="flex items-center gap-3">
                        {AGENT_ICONS[agent.agent] || <Brain className="h-5 w-5 text-gray-400" />}
                        <div>
                          <p className="text-white font-bold">{agent.agent}</p>
                          <p className="text-gray-500 text-xs">{agent.role}</p>
                        </div>
                      </div>
                      {expandedAgent === i
                        ? <ChevronUp className="h-4 w-4 text-gray-400" />
                        : <ChevronDown className="h-4 w-4 text-gray-400" />
                      }
                    </div>
                    <AnimatePresence>
                      {expandedAgent === i && (
                        <motion.div
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: 'auto', opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }}
                          className="overflow-hidden"
                        >
                          <p className="text-gray-300 text-sm mt-4 leading-relaxed whitespace-pre-line border-t border-white/5 pt-4">
                            {agent.output}
                          </p>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
