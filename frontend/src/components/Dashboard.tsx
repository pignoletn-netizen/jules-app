"use client";

import React from "react";
import { PortfolioSummary } from "@/lib/api";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from "recharts";
import { Wallet, TrendingUp, ShieldCheck, ArrowUpRight, DollarSign, PieChart as PieIcon } from "lucide-react";

interface DashboardProps {
  summary: PortfolioSummary;
}

const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#8b5cf6", "#ec4899", "#06b6d4", "#64748b"];

export default function Dashboard({ summary }: DashboardProps) {
  const accountPieData = summary.accounts.map((acc) => ({
    name: acc.name,
    value: acc.total_value,
  }));

  const sectorPieData = Object.entries(summary.sector_allocation).map(([key, val]) => ({
    name: key,
    value: val,
  }));

  const geoPieData = Object.entries(summary.geo_allocation).map(([key, val]) => ({
    name: key,
    value: val,
  }));

  return (
    <div className="space-y-6">
      {/* Wealth Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex items-center justify-between shadow-sm">
          <div>
            <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Patrimoine Global</p>
            <h3 className="text-2xl font-bold text-white mt-1">{summary.total_wealth.toLocaleString("fr-FR")} €</h3>
            <span className="inline-flex items-center text-xs font-semibold text-emerald-400 mt-2 bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-800/40">
              <TrendingUp className="w-3 h-3 mr-1" /> Horizon 15-20 ans
            </span>
          </div>
          <div className="p-3 bg-blue-600/20 rounded-xl text-blue-400 border border-blue-500/20">
            <Wallet className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex items-center justify-between shadow-sm">
          <div>
            <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Capital Investi</p>
            <h3 className="text-2xl font-bold text-slate-100 mt-1">{summary.invested_total.toLocaleString("fr-FR")} €</h3>
            <p className="text-xs text-slate-400 mt-2">
              Liquidités: <span className="text-emerald-400 font-medium">{summary.cash_total.toLocaleString("fr-FR")} €</span>
            </p>
          </div>
          <div className="p-3 bg-emerald-600/20 rounded-xl text-emerald-400 border border-emerald-500/20">
            <DollarSign className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex items-center justify-between shadow-sm">
          <div>
            <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Gains / Pertes Latents</p>
            <h3 className={`text-2xl font-bold mt-1 ${summary.total_gain_loss >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
              {summary.total_gain_loss >= 0 ? "+" : ""}{summary.total_gain_loss.toLocaleString("fr-FR")} €
            </h3>
            <span className={`inline-flex items-center text-xs font-bold mt-2 ${summary.total_gain_loss_percent >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
              {summary.total_gain_loss_percent >= 0 ? "+" : ""}{summary.total_gain_loss_percent} % global
            </span>
          </div>
          <div className="p-3 bg-indigo-600/20 rounded-xl text-indigo-400 border border-indigo-500/20">
            <ArrowUpRight className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex items-center justify-between shadow-sm">
          <div>
            <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Objectif DCA PEA</p>
            <h3 className="text-2xl font-bold text-slate-100 mt-1">100 - 200 € / mois</h3>
            <span className="inline-flex items-center text-xs text-blue-400 mt-2 bg-blue-950/60 px-2 py-0.5 rounded border border-blue-800/40">
              <ShieldCheck className="w-3 h-3 mr-1" /> Fortuneo Starter (0 € frais)
            </span>
          </div>
          <div className="p-3 bg-amber-600/20 rounded-xl text-amber-400 border border-amber-500/20">
            <PieIcon className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Broker Accounts Summary Grid */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm">
        <h3 className="text-lg font-bold text-white mb-4 flex items-center">
          <Wallet className="w-5 h-5 mr-2 text-blue-400" /> Répartition par Courtier & Statut des Apports
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {summary.accounts.map((acc) => (
            <div key={acc.id} className="p-4 rounded-lg bg-slate-950/70 border border-slate-800 hover:border-slate-700 transition">
              <div className="flex justify-between items-start mb-2">
                <div>
                  <h4 className="font-semibold text-slate-200">{acc.name}</h4>
                  <p className="text-xs text-slate-400">{acc.broker} • {acc.account_type}</p>
                </div>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${acc.is_active_for_deposits ? "bg-emerald-950 text-emerald-400 border border-emerald-800/50" : "bg-slate-800 text-slate-400 border border-slate-700"}`}>
                  {acc.is_active_for_deposits ? "ACTIF (DCA)" : "INACTIF (GÉRÉ)"}
                </span>
              </div>

              <div className="my-3">
                <span className="text-xs text-slate-400">Solde Total :</span>
                <p className="text-xl font-bold text-white">{acc.total_value.toLocaleString("fr-FR")} €</p>
              </div>

              <div className="pt-2 border-t border-slate-800/80 text-xs flex justify-between items-center text-slate-400">
                <span>Sync : <span className="text-slate-200 font-medium">{acc.api_sync_status}</span></span>
                <span>{acc.positions.length} position(s)</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Visual Allocations: Sector & Geographic Pie Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Sector Allocation */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm">
          <h3 className="text-md font-bold text-white mb-4">Allocation Sectorielle</h3>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={sectorPieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label={(e) => `${e.name}: ${e.value.toFixed(0)}€`}>
                  {sectorPieData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value: any) => [`${Number(value).toFixed(2)} €`, "Valeur"]} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Geographic Allocation */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm">
          <h3 className="text-md font-bold text-white mb-4">Allocation Géographique</h3>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={geoPieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label={(e) => `${e.name}: ${e.value.toFixed(0)}€`}>
                  {geoPieData.map((_, index) => (
                    <Cell key={`cell-geo-${index}`} fill={COLORS[(index + 2) % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value: any) => [`${Number(value).toFixed(2)} €`, "Valeur"]} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
