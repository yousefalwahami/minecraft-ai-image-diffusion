"use client";

import { useState, useEffect, useRef } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { initScene, renderVoxels } from './threeScene';

export default function Home() {
  const [voxels, setVoxels] = useState<{ x: number; y: number; z: number }[]>([]);
  const [loading, setLoading] = useState(false);
  const [prompt, setPrompt] = useState("");

  const mountRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const meshRef = useRef<THREE.InstancedMesh | null>(null);
  const controlsRef = useRef<OrbitControls | null>(null);
  const edgesRef = useRef<THREE.LineSegments | null>(null);

  useEffect(() => {
    if (!mountRef.current) return;
    const cleanup = initScene(mountRef.current, sceneRef, controlsRef);
    return cleanup;
  }, []);

  // ── API call ────────────────────────────────────────────────────────────────
  const startBuild = async () => {
    
    if (!prompt) return;
    setLoading(true);

    try {
      
      const response = await fetch('/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt }),
      });

      const data = await response.json();
      const voxelList: { x: number; y: number; z: number }[] = data.voxels ?? [];
      setVoxels(voxelList);
      console.log("Received voxel data:", data);

      // Render into the live Three.js scene
      if (sceneRef.current) {
        renderVoxels(voxelList, sceneRef.current, meshRef, controlsRef, edgesRef);
      }

    } catch (error) {
      console.error("Connection failed!", error);
    } finally {
      setLoading(false);
    }
  };

  // ── UI ──────────────────────────────────────────────────────────────────────
  return (
    <main className="relative h-screen w-full bg-slate-900 overflow-hidden">
      {/* THREE.JS CANVAS */}
      <div ref={mountRef} className="absolute inset-0 z-0" />

      {/* UI OVERLAY */}
      <div className="absolute top-0 left-0 w-full p-6 z-10 pointer-events-none">
        <div className="max-w-md bg-black/60 backdrop-blur-md border-2 border-slate-700 p-6 rounded-none pointer-events-auto shadow-[0_0_20px_rgba(0,0,0,0.5)]">

          <h1 className="text-2xl font-bold text-white mb-1 tracking-tighter uppercase italic">
            Minecraft<span className="text-green-500 underline">AI</span>
          </h1>
          <p className="text-slate-400 text-xs mb-6 uppercase tracking-widest">Hackathon Build System v1.0</p>

          <div className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase mb-1">Input Prompt</label>
              <input
                type="text"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Ex: A small stone castle..."
                className="w-full bg-slate-900 border border-slate-700 p-3 text-white focus:outline-none focus:border-green-500 transition-colors font-mono text-sm"
              />
            </div>

            <button
              onClick={startBuild}
              disabled={loading || !prompt}
              className={`w-full py-3 px-4 flex items-center justify-center gap-2 font-bold uppercase tracking-wider transition-all
                ${loading
                  ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                  : 'bg-green-600 hover:bg-green-500 text-white active:scale-95 shadow-[4px_4px_0px_#052e16]'
                }`}
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-slate-400 border-t-transparent rounded-full animate-spin" />
                  Generating...
                </>
              ) : 'Initialize Build'}
            </button>
          </div>

          {voxels.length > 0 && (
            <div className="mt-6 pt-4 border-t border-slate-800">
              <div className="flex justify-between text-[10px] text-slate-500 uppercase font-bold">
                <span>Structures: 1</span>
                <span>Voxel Count: {voxels.length}</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* FOOTER STATS */}
      <div className="absolute bottom-4 right-6 text-slate-500 font-mono text-[10px] uppercase tracking-widest">
        Latency: 14ms | GPU: Active
      </div>
    </main>
  );
}