import CricbuzzLive from '@/components/CricbuzzLive';

export const metadata = {
  title: 'AI CricTracker — Captain Cool | Multi-Agent IPL Strategist',
  description: 'Real-time Cricbuzz scraper powered by 4 Gemini AI agents that debate and decide the next IPL tactical move.',
};

export default function Home() {
  return (
    <main className="min-h-screen bg-[#080d1a] bg-[radial-gradient(ellipse_80%_60%_at_50%_-10%,rgba(99,102,241,0.2),rgba(255,255,255,0))] font-sans selection:bg-indigo-500/30">
      {/* Subtle noise texture */}
      <div className="pointer-events-none fixed inset-0 opacity-[0.03] bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIzMDAiIGhlaWdodD0iMzAwIj48ZmlsdGVyIGlkPSJhIiB4PSIwIiB5PSIwIj48ZmVUdXJidWxlbmNlIHR5cGU9ImZyYWN0YWxOb2lzZSIgYmFzZUZyZXF1ZW5jeT0iLjc1IiBzdGl0Y2hUaWxlcz0ic3RpdGNoIi8+PGZlQ29sb3JNYXRyaXggdHlwZT0ic2F0dXJhdGUiIHZhbHVlcz0iMCIvPjwvZmlsdGVyPjxyZWN0IHdpZHRoPSIzMDAiIGhlaWdodD0iMzAwIiBmaWx0ZXI9InVybCgjYSkiIG9wYWNpdHk9IjEiLz48L3N2Zz4=')]"></div>

      <div className="relative z-10 py-16 px-4 max-w-6xl mx-auto">
        {/* Header */}
        <header className="text-center mb-16 space-y-4">
          <div className="inline-flex items-center gap-2 bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 px-4 py-2 rounded-full text-xs font-bold uppercase tracking-widest">
            ⚡ Powered by Google Gemini 2.5 Flash
          </div>
          <h1 className="text-5xl md:text-7xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white via-indigo-300 to-purple-400 tracking-tight">
            Captain Cool AI
          </h1>
          <p className="text-gray-400 text-lg md:text-xl max-w-2xl mx-auto leading-relaxed">
            Paste any live Cricbuzz URL. Get real-time scores <span className="text-white font-semibold">+</span> a 4-agent Gemini debate on the next tactical move.
          </p>
          <div className="flex flex-wrap justify-center gap-3 pt-2">
            {['Stats Analyst', 'Strategist (Dhoni Mode)', "Devil's Advocate", 'Commentator'].map((a) => (
              <span key={a} className="bg-white/5 border border-white/10 text-gray-300 text-xs px-3 py-1 rounded-full">{a}</span>
            ))}
          </div>
        </header>

        <CricbuzzLive />
      </div>
    </main>
  );
}
