"use client";

import React, { useState, useEffect } from "react";
import { PortfolioSummary, fetchPortfolioSummary } from "@/lib/api";
import Dashboard from "@/components/Dashboard";
import PortfolioManager from "@/components/PortfolioManager";
import AdvisoryCenter from "@/components/AdvisoryCenter";
import MarketAcademy from "@/components/MarketAcademy";
import {
  PieChart,
  Wallet,
  Sparkles,
  BookOpen,
  RefreshCw,
  Bell,
  ShieldCheck,
  TrendingUp,
  Clock,
} from "lucide-react";

export default function Home() {
  const [activeTab, setActiveTab] = useState<"dashboard" | "portfolio" | "advisory" | "academy">("dashboard");
  const [summary, setSummary] = useState<PortfolioSummary | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchPortfolioSummary();
      setSummary(data);
    } catch (err: any) {
      console.error("Failed to fetch portfolio summary:", err);
      setError("Impossible de contacter le serveur backend. Veuillez vérifier la connexion.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans antialiased selection:bg-blue-600 selection:text-white">
      {/* Header Bar */}
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-600 rounded-xl text-white shadow-lg shadow-blue-600/30">
              <TrendingUp className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-white tracking-tight">Horizon Invest 15-20 Ans</h1>
              <p className="text-xs text-slate-400">Gestion & Conseil Patrimonial Orienté Débutant</p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={loadData}
              className="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-slate-300 transition"
              title="Rafraîchir les cours en direct"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
            </button>
            <div className="hidden sm:flex items-center text-xs font-semibold px-3 py-1.5 rounded-full bg-emerald-950/80 text-emerald-400 border border-emerald-800/50">
              <ShieldCheck className="w-3.5 h-3.5 mr-1.5" /> PEA Fortuneo Actif
            </div>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {/* Monthly Connection Reminder Banner */}
        <div className="bg-gradient-to-r from-blue-900/40 via-indigo-900/30 to-slate-900 border border-blue-800/50 rounded-xl p-4 flex items-center justify-between text-xs">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-500/20 rounded-lg text-blue-400">
              <Clock className="w-4 h-4" />
            </div>
            <div>
              <span className="font-bold text-white">Rappel Conseil Débutant :</span>{" "}
              <span className="text-slate-300">
                Fréquence idéale de connexion = <strong>1 fois par mois</strong> (1er du mois) pour passer l'ordre DCA sur PEA Fortuneo. Évitez de regarder les cours tous les jours.
              </span>
            </div>
          </div>
        </div>

        {/* Primary Navigation Tabs */}
        <div className="flex space-x-2 border-b border-slate-800 pb-2 overflow-x-auto">
          <button
            onClick={() => setActiveTab("dashboard")}
            className={`px-4 py-2.5 rounded-lg text-xs font-bold transition flex items-center space-x-2 shrink-0 ${
              activeTab === "dashboard"
                ? "bg-blue-600 text-white shadow-md shadow-blue-900/40"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-900"
            }`}
          >
            <PieChart className="w-4 h-4" />
            <span>Vue Globale / Dashboard</span>
          </button>

          <button
            onClick={() => setActiveTab("portfolio")}
            className={`px-4 py-2.5 rounded-lg text-xs font-bold transition flex items-center space-x-2 shrink-0 ${
              activeTab === "portfolio"
                ? "bg-blue-600 text-white shadow-md shadow-blue-900/40"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-900"
            }`}
          >
            <Wallet className="w-4 h-4" />
            <span>Gestion des 3 Comptes</span>
          </button>

          <button
            onClick={() => setActiveTab("advisory")}
            className={`px-4 py-2.5 rounded-lg text-xs font-bold transition flex items-center space-x-2 shrink-0 ${
              activeTab === "advisory"
                ? "bg-blue-600 text-white shadow-md shadow-blue-900/40"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-900"
            }`}
          >
            <Sparkles className="w-4 h-4" />
            <span>Moteur de Conseils & Remaniement</span>
          </button>

          <button
            onClick={() => setActiveTab("academy")}
            className={`px-4 py-2.5 rounded-lg text-xs font-bold transition flex items-center space-x-2 shrink-0 ${
              activeTab === "academy"
                ? "bg-blue-600 text-white shadow-md shadow-blue-900/40"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-900"
            }`}
          >
            <BookOpen className="w-4 h-4" />
            <span>Marchés & Académie</span>
          </button>
        </div>

        {/* Content Body */}
        {loading && !summary ? (
          <div className="py-20 text-center text-slate-400 text-sm flex flex-col items-center justify-center space-y-3">
            <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
            <p>Chargement des données du portefeuille et des cours en direct...</p>
          </div>
        ) : error ? (
          <div className="p-6 bg-rose-950/40 border border-rose-800 rounded-xl text-rose-300 text-sm text-center">
            {error}
          </div>
        ) : (
          <div>
            {activeTab === "dashboard" && summary && <Dashboard summary={summary} />}
            {activeTab === "portfolio" && summary && (
              <PortfolioManager accounts={summary.accounts} onRefresh={loadData} />
            )}
            {activeTab === "advisory" && <AdvisoryCenter />}
            {activeTab === "academy" && <MarketAcademy />}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 py-8 text-center text-xs text-slate-500 mt-12">
        <p>Horizon Invest 15-20 Ans • Stratégie DCA PEA Fortuneo & Gestion Capital CTO • Fait pour investisseur débutant</p>
      </footer>
    </div>
  );
}
