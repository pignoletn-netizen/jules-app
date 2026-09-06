"use client";

import { useEffect, useState, use } from "react";
import HeaderNav from "@/components/HeaderNav";
import RunnerTable from "@/components/RunnerTable";
import PMUBetRecap from "@/components/PMUBetRecap";
import PredictionBadge from "@/components/PredictionBadge";
import { fetchRaceAnalysis, RaceAnalysis } from "@/services/api";
import { ArrowLeft, MapPin, ShieldCheck, RefreshCw } from "lucide-react";
import Link from "next/link";

interface PageProps {
  params: Promise<{
    date: string;
    reunion: string;
    course: string;
  }>;
}

export default function RaceDetailPage({ params }: PageProps) {
  const { date, reunion, course } = use(params);
  const [analysis, setAnalysis] = useState<RaceAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadRaceData = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchRaceAnalysis(date, parseInt(reunion), parseInt(course));
      setAnalysis(data);
    } catch (err: any) {
      setError(err.message || "Erreur de chargement de la course");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRaceData();
  }, [date, reunion, course]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <HeaderNav />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        <div>
          <Link
            href="/"
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-400 hover:text-white transition"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Retour aux courses du jour</span>
          </Link>
        </div>

        {loading ? (
          <div className="text-center py-20 space-y-3">
            <RefreshCw className="w-8 h-8 text-emerald-400 animate-spin mx-auto" />
            <p className="text-slate-400 text-sm">Calcul du pronostic et analyse multi-critères en cours...</p>
          </div>
        ) : error || !analysis ? (
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-8 text-center space-y-4">
            <p className="text-rose-400 text-sm font-semibold">{error || "Course non disponible"}</p>
            <button
              onClick={loadRaceData}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs rounded-lg font-medium"
            >
              Réessayer
            </button>
          </div>
        ) : (
          <>
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
              <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-slate-800">
                <div className="flex items-center gap-2">
                  <span className="px-3 py-1 bg-amber-500 text-slate-950 font-black text-sm rounded-md">
                    R{analysis.race_info.reunion} C{analysis.race_info.course}
                  </span>
                  <div className="flex items-center gap-1 text-slate-300 font-semibold text-sm">
                    <MapPin className="w-4 h-4 text-emerald-400" />
                    <span>{analysis.race_info.hippodrome}</span>
                  </div>
                </div>

                <PredictionBadge confidence={analysis.race_info.confidence} />
              </div>

              <div>
                <h1 className="text-2xl font-black text-white tracking-tight">
                  {analysis.race_info.libelle}
                </h1>
                <p className="text-xs text-slate-400 mt-1">
                  Discipline: <strong className="text-slate-200">{analysis.race_info.discipline}</strong> • Distance: <strong className="text-slate-200">{analysis.race_info.distance} m</strong> • Terrain: <strong className="text-slate-200">{analysis.race_info.terrain || "SYNTHETIQUE/HERBE"}</strong> • Partants: <strong className="text-slate-200">{analysis.race_info.nombrePartants}</strong>
                </p>
                {analysis.race_info.conditions && (
                  <p className="text-xs text-slate-500 mt-2 bg-slate-950 p-3 rounded-lg border border-slate-800/80 italic">
                    {analysis.race_info.conditions}
                  </p>
                )}
              </div>
            </div>

            <PMUBetRecap bets={analysis.pmu_bets} />

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-bold text-white flex items-center gap-2">
                  <ShieldCheck className="w-5 h-5 text-emerald-400" />
                  <span>Classement des Chevaux par Probabilité de Victoire & Value Bets</span>
                </h2>
                <span className="text-xs text-slate-400">
                  Total: {analysis.ranked_runners.length} partants
                </span>
              </div>

              <RunnerTable runners={analysis.ranked_runners} />
            </div>
          </>
        )}
      </main>

      <footer className="border-t border-slate-800 bg-slate-900 py-6 text-center text-xs text-slate-500">
        <p>Turf Predictor & PMU Bet Advisor • Analyse multi-critères & Value Bets</p>
      </footer>
    </div>
  );
}
