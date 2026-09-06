"use client";

import { useEffect, useState } from "react";
import HeaderNav from "@/components/HeaderNav";
import { fetchDailyPMUSummary, fetchBacktestData, DailySummary, BacktestResponse } from "@/services/api";
import { Ticket, RefreshCw, Trophy, ChevronRight, Star, MapPin, Flame, LineChart, TrendingUp, Percent, DollarSign, Award } from "lucide-react";
import Link from "next/link";

export default function PMURecapPage() {
  const [activeTab, setActiveTab] = useState<"daily" | "backtest">("daily");
  const [summaryData, setSummaryData] = useState<DailySummary | null>(null);
  const [backtestData, setBacktestData] = useState<BacktestResponse | null>(null);
  const [loadingSummary, setLoadingSummary] = useState(true);
  const [loadingBacktest, setLoadingBacktest] = useState(false);
  const [backtestDays, setBacktestDays] = useState(30);

  const loadSummary = async () => {
    setLoadingSummary(true);
    try {
      const data = await fetchDailyPMUSummary();
      setSummaryData(data);
    } catch (err) {
      console.error("Erreur lors du chargement du récapitulatif:", err);
    } finally {
      setLoadingSummary(false);
    }
  };

  const loadBacktest = async (days: number) => {
    setLoadingBacktest(true);
    try {
      const data = await fetchBacktestData(days);
      setBacktestData(data);
    } catch (err) {
      console.error("Erreur lors du chargement du backtest:", err);
    } finally {
      setLoadingBacktest(false);
    }
  };

  useEffect(() => {
    loadSummary();
  }, []);

  useEffect(() => {
    if (activeTab === "backtest" && !backtestData) {
      loadBacktest(backtestDays);
    }
  }, [activeTab]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <HeaderNav />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Banner Header */}
        <div className="bg-gradient-to-r from-emerald-950 via-slate-900 to-slate-900 border border-emerald-800/60 rounded-2xl p-6 shadow-xl relative overflow-hidden">
          <div className="max-w-3xl space-y-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-400 text-xs font-semibold border border-emerald-500/30">
              <Ticket className="w-3.5 h-3.5" />
              <span>Synthèse PMU.fr & Performance Backtesting</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
              Récapitulatif des Paris & Historique de Rentabilité (ROI)
            </h1>
            <p className="text-slate-300 text-sm leading-relaxed">
              Analyse synthétique des paris du jour et suivi rigoureux de l'historique des pronostics (Taux de réussite, Rendement ROI %, Gains nets).
            </p>
          </div>
        </div>

        {/* Tab Selection */}
        <div className="flex border-b border-slate-800 gap-4">
          <button
            onClick={() => setActiveTab("daily")}
            className={`pb-3 px-2 text-sm font-bold flex items-center gap-2 border-b-2 transition ${
              activeTab === "daily"
                ? "border-emerald-400 text-emerald-400"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            <Ticket className="w-4 h-4" />
            <span>Récapitulatif Mises du Jour</span>
          </button>
          <button
            onClick={() => setActiveTab("backtest")}
            className={`pb-3 px-2 text-sm font-bold flex items-center gap-2 border-b-2 transition ${
              activeTab === "backtest"
                ? "border-emerald-400 text-emerald-400"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            <LineChart className="w-4 h-4" />
            <span>Performance & Backtesting (ROI)</span>
          </button>
        </div>

        {/* TAB 1: Daily Summary */}
        {activeTab === "daily" && (
          <div>
            <div className="flex justify-end mb-4">
              <button
                onClick={loadSummary}
                disabled={loadingSummary}
                className="inline-flex items-center gap-2 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium rounded-lg border border-slate-700 transition"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${loadingSummary ? "animate-spin" : ""}`} />
                <span>Actualiser</span>
              </button>
            </div>

            {loadingSummary ? (
              <div className="text-center py-20 space-y-3">
                <RefreshCw className="w-8 h-8 text-emerald-400 animate-spin mx-auto" />
                <p className="text-slate-400 text-sm">Génération du récapitulatif des différentes mises PMU...</p>
              </div>
            ) : !summaryData || !summaryData.summary || summaryData.summary.length === 0 ? (
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-8 text-center text-slate-400 text-sm">
                Aucun récapitulatif disponible pour le moment.
              </div>
            ) : (
              <div className="space-y-6">
                {summaryData.summary.map((item) => (
                  <div
                    key={`${item.reunion}-${item.course}`}
                    className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-md hover:border-slate-700 transition space-y-4"
                  >
                    <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-slate-800">
                      <div className="flex items-center gap-2">
                        <span className="px-2.5 py-1 bg-amber-500 text-slate-950 font-black text-xs rounded">
                          R{item.reunion} C{item.course}
                        </span>
                        <div className="flex items-center gap-1 text-slate-200 font-bold text-sm">
                          <MapPin className="w-4 h-4 text-emerald-400" />
                          <span>{item.hippodrome}</span>
                        </div>
                        <span className="text-xs text-slate-400 font-medium">
                          ({item.discipline} - {item.distance}m)
                        </span>
                        {item.has_value_bets && (
                          <span className="px-2 py-0.5 bg-amber-500/20 text-amber-400 font-bold text-[10px] rounded border border-amber-500/40 flex items-center gap-1">
                            <Flame className="w-3 h-3 text-amber-400" />
                            Value Bet détectée
                          </span>
                        )}
                      </div>

                      <Link
                        href={`/race/${summaryData.date}/${item.reunion}/${item.course}`}
                        className="inline-flex items-center gap-1 text-xs font-semibold text-emerald-400 hover:text-emerald-300 transition"
                      >
                        <span>Fiche complète & Tickets</span>
                        <ChevronRight className="w-4 h-4" />
                      </Link>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-xs">
                      <div className="bg-slate-800/60 p-3 rounded-lg border border-slate-700/60 space-y-2">
                        <div className="flex items-center gap-1.5 font-bold text-amber-400">
                          <Trophy className="w-3.5 h-3.5" />
                          <span>Top 3 Favoris Pronostiqués</span>
                        </div>
                        <div className="space-y-1 text-slate-200">
                          {item.top_runners.map((r) => (
                            <div key={r.num} className="flex items-center justify-between">
                              <span>
                                <strong className="text-amber-400">N°{r.num}</strong> {r.nom}
                              </span>
                              <span className="text-emerald-400 font-mono font-bold">
                                {r.prob_victoire}%
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>

                      <div className="bg-slate-800/60 p-3 rounded-lg border border-slate-700/60 space-y-2">
                        <div className="flex items-center gap-1.5 font-bold text-emerald-400">
                          <Star className="w-3.5 h-3.5" />
                          <span>Simple Gagnant & Value Bet</span>
                        </div>
                        <div className="space-y-1 text-slate-300">
                          <p><strong className="text-emerald-400">Favori:</strong> {item.bets_preview.simple_favori}</p>
                          <p><strong className="text-amber-400">Outsider / Value:</strong> {item.bets_preview.simple_outsider}</p>
                        </div>
                      </div>

                      <div className="bg-slate-800/60 p-3 rounded-lg border border-slate-700/60 space-y-2 md:col-span-2 lg:col-span-1">
                        <div className="flex items-center gap-1.5 font-bold text-sky-400">
                          <Ticket className="w-3.5 h-3.5" />
                          <span>Bases PMU.fr (Trio, Quinté+, Multi)</span>
                        </div>
                        <div className="space-y-1 text-slate-300">
                          <p><strong className="text-slate-200">Base Trio:</strong> {item.bets_preview.trio_base}</p>
                          <p><strong className="text-slate-200">Base Quinté:</strong> {item.bets_preview.quinte_base}</p>
                          <p><strong className="text-purple-400">Multi 4:</strong> N°{item.bets_preview.multi_4?.join(" - N°")}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* TAB 2: Backtest & ROI Performance */}
        {activeTab === "backtest" && (
          <div className="space-y-6">
            <div className="flex items-center justify-between bg-slate-900 p-4 rounded-xl border border-slate-800">
              <div className="flex items-center gap-3">
                <span className="text-xs font-semibold text-slate-300">Période d'Analyse:</span>
                <div className="flex gap-2">
                  {[15, 30, 60, 90].map((d) => (
                    <button
                      key={d}
                      onClick={() => {
                        setBacktestDays(d);
                        loadBacktest(d);
                      }}
                      className={`px-3 py-1 rounded-lg text-xs font-bold transition ${
                        backtestDays === d
                          ? "bg-emerald-500 text-slate-950"
                          : "bg-slate-800 text-slate-300 hover:bg-slate-700"
                      }`}
                    >
                      {d} Jours
                    </button>
                  ))}
                </div>
              </div>

              <button
                onClick={() => loadBacktest(backtestDays)}
                disabled={loadingBacktest}
                className="inline-flex items-center gap-2 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium rounded-lg border border-slate-700 transition"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${loadingBacktest ? "animate-spin" : ""}`} />
                <span>Actualiser</span>
              </button>
            </div>

            {loadingBacktest ? (
              <div className="text-center py-20 space-y-3">
                <RefreshCw className="w-8 h-8 text-emerald-400 animate-spin mx-auto" />
                <p className="text-slate-400 text-sm">Calcul du backtest et calcul des rendements ROI...</p>
              </div>
            ) : !backtestData ? (
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-8 text-center text-slate-400 text-sm">
                Aucune donnée de backtest disponible.
              </div>
            ) : (
              <div className="space-y-6">
                {/* Metrics Cards */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                  <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-1">
                    <div className="flex items-center justify-between text-slate-400 text-xs">
                      <span>Rendement ROI Global</span>
                      <TrendingUp className="w-4 h-4 text-emerald-400" />
                    </div>
                    <p className={`text-2xl font-black ${backtestData.metrics.roi_pct >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                      {backtestData.metrics.roi_pct > 0 ? `+${backtestData.metrics.roi_pct}%` : `${backtestData.metrics.roi_pct}%`}
                    </p>
                    <p className="text-[11px] text-slate-500">Mise plate 10€ / course</p>
                  </div>

                  <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-1">
                    <div className="flex items-center justify-between text-slate-400 text-xs">
                      <span>Taux Gagnant (1er)</span>
                      <Award className="w-4 h-4 text-amber-400" />
                    </div>
                    <p className="text-2xl font-black text-amber-400">
                      {backtestData.metrics.win_rate_pct}%
                    </p>
                    <p className="text-[11px] text-slate-500">Placé (Top 3): {backtestData.metrics.placed_rate_pct}%</p>
                  </div>

                  <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-1">
                    <div className="flex items-center justify-between text-slate-400 text-xs">
                      <span>Profit Net Modélisé</span>
                      <DollarSign className="w-4 h-4 text-emerald-400" />
                    </div>
                    <p className={`text-2xl font-black ${backtestData.metrics.net_profit >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                      {backtestData.metrics.net_profit > 0 ? `+${backtestData.metrics.net_profit}€` : `${backtestData.metrics.net_profit}€`}
                    </p>
                    <p className="text-[11px] text-slate-500">Total Engagé: {backtestData.metrics.total_staked}€</p>
                  </div>

                  <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-1">
                    <div className="flex items-center justify-between text-slate-400 text-xs">
                      <span>ROI Stratégie Value Bet</span>
                      <Flame className="w-4 h-4 text-amber-500" />
                    </div>
                    <p className={`text-2xl font-black ${backtestData.metrics.value_bet_roi_pct >= 0 ? "text-amber-400" : "text-rose-400"}`}>
                      {backtestData.metrics.value_bet_roi_pct > 0 ? `+${backtestData.metrics.value_bet_roi_pct}%` : `${backtestData.metrics.value_bet_roi_pct}%`}
                    </p>
                    <p className="text-[11px] text-slate-500">Pondération Kelly Criterion</p>
                  </div>
                </div>

                {/* History Table */}
                <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <LineChart className="w-4 h-4 text-emerald-400" />
                    <span>Dernières Courses du Backtest ({backtestData.metrics.total_races} courses analysées)</span>
                  </h3>

                  <div className="overflow-x-auto">
                    <table className="w-full text-xs text-left text-slate-300">
                      <thead className="bg-slate-800/80 text-slate-400 font-semibold border-b border-slate-700">
                        <tr>
                          <th className="py-2.5 px-3">Course</th>
                          <th className="py-2.5 px-3">Date</th>
                          <th className="py-2.5 px-3">N° Pronostiqué</th>
                          <th className="py-2.5 px-3">Gagnant Réel</th>
                          <th className="py-2.5 px-3 text-right">Mise</th>
                          <th className="py-2.5 px-3 text-right">Gains</th>
                          <th className="py-2.5 px-3 text-center">Résultat</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800">
                        {backtestData.metrics.breakdown.map((row, idx) => (
                          <tr key={idx} className="hover:bg-slate-800/40">
                            <td className="py-2 px-3 font-mono text-amber-400 font-bold">{row.race_id}</td>
                            <td className="py-2 px-3 text-slate-400">{row.date}</td>
                            <td className="py-2 px-3 font-bold text-slate-200">N°{row.top_predicted}</td>
                            <td className="py-2 px-3 font-bold text-emerald-400">N°{row.winner}</td>
                            <td className="py-2 px-3 text-right font-mono">{row.staked}€</td>
                            <td className="py-2 px-3 text-right font-mono font-bold text-slate-100">{row.payout}€</td>
                            <td className="py-2 px-3 text-center">
                              {row.is_win ? (
                                <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-bold text-[10px] border border-emerald-500/30">
                                  GAGNÉ
                                </span>
                              ) : (
                                <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-400 text-[10px]">
                                  PERDU
                                </span>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      <footer className="border-t border-slate-800 bg-slate-900 py-6 text-center text-xs text-slate-500">
        <p>Turf Predictor & PMU Bet Advisor • Récapitulatif et Backtesting</p>
      </footer>
    </div>
  );
}
