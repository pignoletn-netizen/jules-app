"use client";

import React, { useState, useEffect } from "react";
import {
  MarketNewsItem,
  AnalystConsensus,
  AcademyConcept,
  fetchMarketNews,
  fetchAnalystConsensus,
  fetchAcademyConcepts,
} from "@/lib/api";
import {
  Newspaper,
  BookOpen,
  Target,
  Calendar,
  Search,
  ExternalLink,
  ShieldCheck,
  Globe,
  Award,
} from "lucide-react";

export default function MarketAcademy() {
  const [news, setNews] = useState<MarketNewsItem[]>([]);
  const [consensus, setConsensus] = useState<AnalystConsensus[]>([]);
  const [academy, setAcademy] = useState<AcademyConcept[]>([]);
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [selectedCategory, setSelectedCategory] = useState<string>("TOUS");

  useEffect(() => {
    async function loadData() {
      try {
        const [newsRes, consRes, acadRes] = await Promise.all([
          fetchMarketNews(),
          fetchAnalystConsensus(),
          fetchAcademyConcepts(),
        ]);
        setNews(newsRes);
        setConsensus(consRes);
        setAcademy(acadRes);
      } catch (err) {
        console.error("Error loading market academy data", err);
      }
    }
    loadData();
  }, []);

  const categories = ["TOUS", "Stratégie", "Produits", "Fiscalité", "Risques"];

  const filteredAcademy = academy.filter((item) => {
    const matchesSearch =
      item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.short_definition.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCat =
      selectedCategory === "TOUS" || item.category.toLowerCase() === selectedCategory.toLowerCase();
    return matchesSearch && matchesCat;
  });

  return (
    <div className="space-y-8">
      {/* 1. FREQUENCY PLANNER BANNER */}
      <div className="bg-gradient-to-r from-blue-950 via-slate-900 to-slate-900 border border-blue-800/60 rounded-xl p-6 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <Calendar className="w-5 h-5 text-blue-400" />
            <h2 className="text-lg font-bold text-white">Planification & Fréquence de Connexion Optimale</h2>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed max-w-3xl">
            Pour réussir un investissement boursier orienté long terme (15-20 ans) et éviter le stress ainsi que le sur-trading (over-trading) néfaste,{" "}
            <strong className="text-emerald-400">connectez-vous 1 seule fois par mois</strong> (par exemple chaque 1er du mois) pour exécuter votre versement DCA PEA.
          </p>
        </div>

        <div className="px-4 py-3 bg-blue-900/40 rounded-xl border border-blue-700/50 text-center shrink-0">
          <span className="text-[10px] text-blue-300 uppercase tracking-wider font-semibold block">Prochain Rendez-vous</span>
          <span className="text-base font-extrabold text-white">1er du mois prochain</span>
        </div>
      </div>

      {/* 2. REAL-TIME MARKET NEWS & GEOPOLITICAL IMPACT */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm space-y-6">
        <div className="flex items-center space-x-2 border-b border-slate-800 pb-4">
          <Newspaper className="w-5 h-5 text-blue-400" />
          <div>
            <h2 className="text-lg font-bold text-white">Flux d'Analyses & Impact Géopolitique</h2>
            <p className="text-xs text-slate-400">
              Événements macroéconomiques, géopolitiques et tendances sectorielles d'avenir.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {news.map((item) => (
            <div key={item.id} className="bg-slate-950 p-5 rounded-xl border border-slate-800 flex flex-col justify-between space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between items-center text-[10px]">
                  <span className="text-blue-400 font-semibold">{item.source}</span>
                  <span className="text-slate-500">{item.published_at}</span>
                </div>
                <h3 className="text-sm font-bold text-white leading-snug">{item.title}</h3>
                <p className="text-xs text-slate-400 leading-relaxed">{item.summary}</p>
              </div>

              <div className="pt-3 border-t border-slate-800/80 space-y-2">
                <div className="bg-slate-900 p-2.5 rounded-lg border border-slate-800 text-[11px] text-slate-300">
                  <span className="font-bold text-amber-400 block mb-0.5">Impact Boursier & Géopolitique :</span>
                  {item.geopolitical_impact}
                </div>

                <div className="flex flex-wrap gap-1">
                  {item.relevant_tickers.map((t) => (
                    <span key={t} className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
                      {t}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 3. ANALYST CONSENSUS & PRICE TARGETS */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm space-y-6">
        <div className="flex items-center space-x-2 border-b border-slate-800 pb-4">
          <Target className="w-5 h-5 text-emerald-400" />
          <div>
            <h2 className="text-lg font-bold text-white">Consensus des Analystes Wall Street / Europe</h2>
            <p className="text-xs text-slate-400">
              Objectifs de cours moyens et potentiel de hausse estimé sur vos actifs en portefeuille.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {consensus.map((c) => (
            <div key={c.ticker} className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-3">
              <div className="flex justify-between items-start">
                <div>
                  <h4 className="font-bold text-white text-sm">{c.company_name}</h4>
                  <span className="text-[10px] font-mono text-blue-400">{c.ticker}</span>
                </div>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800/40">
                  {c.recommendation}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs pt-1">
                <div>
                  <span className="text-slate-400 text-[10px]">Cours Actuel</span>
                  <p className="font-bold text-white">{c.current_price.toFixed(2)} €/$</p>
                </div>
                <div>
                  <span className="text-slate-400 text-[10px]">Cible Moyenne</span>
                  <p className="font-bold text-emerald-400">{c.target_price_avg.toFixed(2)} €/$</p>
                </div>
              </div>

              <div className="pt-2 border-t border-slate-800 flex justify-between items-center text-[11px]">
                <span className="text-slate-400">Potentiel Estimé :</span>
                <span className="font-bold text-emerald-400">+{c.upside_potential_pct} %</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 4. FINANCIAL ACADEMY (ACADÉMIE DE L'INVESTISSEUR) */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-4">
          <div className="flex items-center space-x-2">
            <BookOpen className="w-5 h-5 text-indigo-400" />
            <div>
              <h2 className="text-lg font-bold text-white">Académie de l'Investisseur Débutant</h2>
              <p className="text-xs text-slate-400">
                Guide pédagogique pour maîtriser les concepts clés de la bourse et de la gestion de patrimoine.
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-3 py-1 rounded-lg text-xs font-semibold transition ${
                  selectedCategory === cat
                    ? "bg-indigo-600 text-white"
                    : "bg-slate-950 text-slate-400 hover:text-white border border-slate-800"
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        {/* Search bar */}
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3 top-3 text-slate-500" />
          <input
            type="text"
            placeholder="Rechercher un concept (ex: DCA, ETF, Flat Tax, Drawdown...)..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-4 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
        </div>

        {/* Concept Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {filteredAcademy.map((concept) => (
            <div key={concept.id} className="bg-slate-950 p-6 rounded-xl border border-slate-800 space-y-4 hover:border-slate-700 transition">
              <div className="flex justify-between items-start">
                <h3 className="text-base font-bold text-white">{concept.title}</h3>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-800/50">
                  {concept.category}
                </span>
              </div>

              <p className="text-xs font-medium text-slate-300 bg-slate-900/60 p-3 rounded-lg border border-slate-800">
                {concept.short_definition}
              </p>

              <p className="text-xs text-slate-400 leading-relaxed">{concept.detailed_explanation}</p>

              <div className="bg-blue-950/30 p-3 rounded-lg border border-blue-900/30 text-xs text-blue-200">
                <strong className="text-blue-400 block mb-1">Exemple Concret :</strong>
                {concept.concrete_example}
              </div>

              <div className="pt-3 border-t border-slate-800 text-xs font-bold text-emerald-400 flex items-center">
                <Award className="w-4 h-4 mr-1.5 shrink-0" />
                <span>À retenir : {concept.key_takeaway}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
