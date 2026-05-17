import CricbuzzLive from '@/components/CricbuzzLive';

export default function Home() {
  return (
    <main className="min-h-screen bg-[#0f172a] bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(120,119,198,0.3),rgba(255,255,255,0))] selection:bg-blue-500/30 font-sans">
      <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 brightness-100 contrast-150 mix-blend-overlay pointer-events-none"></div>
      
      <div className="relative z-10 py-16 px-4">
        <header className="text-center mb-16">
          <h1 className="text-5xl md:text-7xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400 mb-4 tracking-tight">
            AI CricTracker
          </h1>
          <p className="text-gray-400 text-lg md:text-xl max-w-2xl mx-auto">
            Real-time, AI-powered ball-by-ball extraction directly from Cricbuzz. No API limits, no page reloads.
          </p>
        </header>

        <CricbuzzLive />
      </div>
    </main>
  );
}
