export default function HomePage() {
  return (
    <main className="min-h-screen bg-slate-950 p-8 text-slate-100">
      <div className="mx-auto flex max-w-5xl flex-col gap-6 rounded-2xl border border-slate-800 bg-slate-900/70 p-8 shadow-2xl">
        <div>
          <p className="text-sm uppercase tracking-[0.35em] text-cyan-400">Video Clipper AI</p>
          <h1 className="mt-3 text-4xl font-semibold">Automated short-form video clipping engine</h1>
          <p className="mt-3 max-w-3xl text-lg text-slate-400">
            Built for high-performance clip generation with virality scoring, subtitle rendering, and multi-platform optimization.
          </p>
        </div>
        <div className="grid gap-4 md:grid-cols-2">
          <div className="rounded-xl border border-slate-800 bg-slate-950/70 p-5">
            <h2 className="text-xl font-semibold">Backend API</h2>
            <p className="mt-2 text-sm text-slate-400">POST /api/clip to create a processed clip from a video source.</p>
          </div>
          <div className="rounded-xl border border-slate-800 bg-slate-950/70 p-5">
            <h2 className="text-xl font-semibold">Next steps</h2>
            <p className="mt-2 text-sm text-slate-400">Connect uploads, transcription, queue workers, and a polished dashboard.</p>
          </div>
        </div>
      </div>
    </main>
  );
}
