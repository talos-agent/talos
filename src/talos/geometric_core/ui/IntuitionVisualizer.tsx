import React, { useEffect, useRef, useState } from 'react';

/**
 * FractalMind: Intuition Visualizer component.
 * Visualizes the 11D geometric intuition manifold and coherence states.
 */
const IntuitionVisualizer: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [coherence, setCoherence] = useState<number>(0.0);
  const [phi, setPhi] = useState<number>(0.0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;

    const render = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Draw background (Ghost Interior)
      ctx.fillStyle = 'rgba(10, 10, 20, 0.1)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Draw typicality shell (Reality)
      const time = Date.now() * 0.001;
      const centerX = canvas.width / 2;
      const centerY = canvas.height / 2;
      const radius = 150 + Math.sin(time) * 10;

      ctx.beginPath();
      ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
      ctx.strokeStyle = 'rgba(0, 255, 128, 0.5)';
      ctx.lineWidth = 2;
      ctx.stroke();

      // Visualize 11D projections as orbital harmonics
      for (let i = 0; i < 11; i++) {
        const angle = time + (i * Math.PI * 2) / 11;
        const orbitRadius = radius + Math.cos(time * (i + 1)) * 20;
        const x = centerX + Math.cos(angle) * orbitRadius;
        const y = centerY + Math.sin(angle) * orbitRadius;

        ctx.beginPath();
        ctx.arc(x, y, 4, 0, 2 * Math.PI);
        ctx.fillStyle = `hsla(${i * 33}, 70%, 60%, 0.8)`;
        ctx.fill();

        // Draw connections (Geodesic Attention)
        ctx.beginPath();
        ctx.moveTo(centerX, centerY);
        ctx.lineTo(x, y);
        ctx.strokeStyle = `hsla(${i * 33}, 70%, 60%, 0.2)`;
        ctx.stroke();
      }

      // Update metrics
      setCoherence(0.8 + Math.sin(time * 0.5) * 0.1);
      setPhi(0.75 + Math.cos(time * 0.3) * 0.05);

      animationFrameId = window.requestAnimationFrame(render);
    };

    render();

    return () => {
      window.cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <div className="p-6 bg-slate-900 rounded-xl shadow-2xl border border-emerald-500/30">
      <h2 className="text-2xl font-bold text-emerald-400 mb-4">FractalMind: 11D Intuition Visualizer</h2>
      <div className="flex flex-col md:flex-row gap-8">
        <div className="relative">
          <canvas
            ref={canvasRef}
            width={400}
            height={400}
            className="rounded-lg bg-black/50 border border-emerald-500/20"
          />
          <div className="absolute top-4 left-4 bg-black/60 p-2 rounded border border-emerald-500/20">
            <p className="text-xs text-emerald-300">Phase Transition: <span className="font-mono">ULTRA-STRONG</span></p>
          </div>
        </div>

        <div className="flex-1 space-y-4">
          <div className="bg-slate-800 p-4 rounded-lg border border-emerald-500/10">
            <h3 className="text-sm font-semibold text-emerald-300 uppercase tracking-wider">Φ Coherence (Fênix)</h3>
            <div className="text-3xl font-mono text-emerald-400">{phi.toFixed(4)}</div>
            <div className="w-full bg-slate-700 h-2 rounded-full mt-2">
              <div className="bg-emerald-500 h-full rounded-full" style={{ width: `${phi * 100}%` }}></div>
            </div>
          </div>

          <div className="bg-slate-800 p-4 rounded-lg border border-emerald-500/10">
            <h3 className="text-sm font-semibold text-emerald-300 uppercase tracking-wider">Intuition Gain</h3>
            <div className="text-3xl font-mono text-cyan-400">33.0x</div>
          </div>

          <div className="bg-slate-800 p-4 rounded-lg border border-emerald-500/10">
            <h3 className="text-sm font-semibold text-emerald-300 uppercase tracking-wider">Geometric State</h3>
            <ul className="text-xs text-slate-400 font-mono mt-2 space-y-1">
              <li>Dimension: 11</li>
              <li>Manifold: Calabi-Yau 3-fold</li>
              <li>Curvature: Riemannian</li>
              <li>Status: Resonant</li>
            </ul>
          </div>
        </div>
      </div>
      <div className="mt-6 text-sm text-slate-500 italic">
        "The interior is ghost; the shell is reality." — Prometheus Architecture
      </div>
    </div>
  );
};

export default IntuitionVisualizer;
