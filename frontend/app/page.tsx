"use client";

import React, { useState } from "react";
import SpeciesSearch from "@/components/SpeciesSearch";
import InventoryAnalysis from "@/components/InventoryAnalysis";
import { Bug, BarChart3, Info } from "lucide-react";

export default function Home() {
  const [activeTab, setActiveTab] = useState<"species" | "analysis">("species");

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900 pb-12">
      {/* Top Navbar Header */}
      <header className="bg-slate-900 border-b border-slate-800 text-white sticky top-0 z-50 shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-emerald-600 text-white rounded-xl flex items-center justify-center font-bold shadow-sm">
              <Bug className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-lg font-bold tracking-tight leading-tight">
                ArachnoData <span className="text-emerald-400 font-normal text-xs ml-1">v1.0</span>
              </h1>
              <p className="text-xs text-slate-400">
                Fiches Écologiques INPN/Taxref & Analyse d'Inventaires d'Araignées (R)
              </p>
            </div>
          </div>

          <div className="hidden sm:flex items-center gap-2 text-xs text-slate-400 bg-slate-800/80 px-3 py-1.5 rounded-xl border border-slate-700">
            <Info className="w-3.5 h-3.5 text-emerald-400" />
            <span>Moteur R (FactoMineR, vegan, openxlsx) & API Taxref</span>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-6 space-y-6">
        {/* Main Tab Switcher */}
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-1.5 flex gap-1">
          <button
            onClick={() => setActiveTab("species")}
            className={`flex-1 py-3 px-4 rounded-xl text-sm font-bold flex items-center justify-center gap-2 transition-all ${
              activeTab === "species"
                ? "bg-emerald-600 text-white shadow-sm"
                : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
            }`}
          >
            <Bug className="w-4 h-4" />
            Onglet 1 : Recherche d'Espèce (Fiche INPN / Taxref)
          </button>

          <button
            onClick={() => setActiveTab("analysis")}
            className={`flex-1 py-3 px-4 rounded-xl text-sm font-bold flex items-center justify-center gap-2 transition-all ${
              activeTab === "analysis"
                ? "bg-emerald-600 text-white shadow-sm"
                : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
            }`}
          >
            <BarChart3 className="w-4 h-4" />
            Onglet 2 : Analyse d'Inventaire & Exports Excel
          </button>
        </div>

        {/* Tab Contents */}
        {activeTab === "species" ? <SpeciesSearch /> : <InventoryAnalysis />}
      </div>
    </main>
  );
}
