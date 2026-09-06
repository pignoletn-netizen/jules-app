"use client";

import { Runner } from "@/services/api";
import PredictionBadge from "./PredictionBadge";
import { Flame } from "lucide-react";

interface RunnerTableProps {
  runners: Runner[];
}

export default function RunnerTable({ runners }: RunnerTableProps) {
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-700 bg-slate-900 shadow-md">
      <table className="w-full text-left text-sm text-slate-200 min-w-[700px]">
        <thead className="bg-slate-800 text-xs uppercase text-slate-400 border-b border-slate-700">
          <tr>
            <th className="px-3 py-3 text-center">Rang</th>
            <th className="px-3 py-3 text-center">N°</th>
            <th className="px-4 py-3">Cheval & Équipement</th>
            <th className="px-3 py-3">Âge/Sexe</th>
            <th className="px-3 py-3">Musique</th>
            <th className="px-4 py-3">Driver / Entraîneur</th>
            <th className="px-3 py-3 text-center">Cote Live</th>
            <th className="px-4 py-3 text-center">Score & Value Bet</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800">
          {runners.map((r) => {
            const isTop3 = r.predicted_rank <= 3;
            const isD4 = r.deferre && (r.deferre.includes("ANTERIEURS_POSTERIEURS") || r.deferre.includes("D4"));
            const isDP = r.deferre && (r.deferre.includes("ANTERIEURS") || r.deferre.includes("POSTERIEURS"));

            return (
              <tr
                key={r.num}
                className={`hover:bg-slate-800/50 transition ${
                  r.is_value_bet
                    ? "bg-amber-950/20 border-l-4 border-l-amber-500"
                    : isTop3
                    ? "bg-emerald-950/10"
                    : ""
                }`}
              >
                <td className="px-3 py-3 text-center font-bold">
                  <span
                    className={`inline-flex items-center justify-center w-6 h-6 rounded-full text-xs ${
                      r.predicted_rank === 1
                        ? "bg-amber-400 text-slate-950 font-black"
                        : r.predicted_rank === 2
                        ? "bg-slate-300 text-slate-950 font-bold"
                        : r.predicted_rank === 3
                        ? "bg-amber-700 text-white font-bold"
                        : "text-slate-400"
                    }`}
                  >
                    {r.predicted_rank}
                  </span>
                </td>

                <td className="px-3 py-3 text-center font-bold text-amber-400">
                  N°{r.num}
                </td>

                <td className="px-4 py-3 font-semibold text-slate-100">
                  <div className="flex items-center gap-1.5 flex-wrap">
                    <span>{r.nom}</span>
                    {isD4 && (
                      <span className="px-1.5 py-0.5 bg-emerald-900/80 text-emerald-300 font-bold text-[10px] rounded border border-emerald-700 shrink-0">
                        D4
                      </span>
                    )}
                    {isDP && !isD4 && (
                      <span className="px-1.5 py-0.5 bg-sky-900/80 text-sky-300 font-bold text-[10px] rounded border border-sky-700 shrink-0">
                        DA/DP
                      </span>
                    )}
                    {r.oeilleres && r.oeilleres !== "SANS_OEILLERES" && (
                      <span className="px-1.5 py-0.5 bg-purple-900/80 text-purple-300 font-bold text-[10px] rounded border border-purple-700 shrink-0">
                        👁️ Oeill.
                      </span>
                    )}
                  </div>
                </td>

                <td className="px-3 py-3 text-slate-400 text-xs">
                  {r.age} ans ({r.sexe})
                </td>

                <td className="px-3 py-3 font-mono text-xs text-amber-300">
                  {r.musique || "Inconnue"}
                </td>

                <td className="px-4 py-3 text-xs text-slate-300">
                  <div className="font-medium text-slate-200">{r.driver || "-"}</div>
                  <div className="text-slate-500 text-[11px]">{r.entraineur || "-"}</div>
                </td>

                <td className="px-3 py-3 text-center whitespace-nowrap">
                  {r.cote ? (
                    <span className="font-bold text-emerald-400 bg-emerald-950/80 px-2 py-1 rounded text-xs border border-emerald-800/80">
                      {r.cote.toFixed(1)}
                    </span>
                  ) : (
                    <span className="text-slate-500 text-xs italic">Cote non dispo</span>
                  )}
                </td>

                <td className="px-4 py-3 text-center">
                  <div className="flex flex-col items-center gap-1">
                    <PredictionBadge probVictoire={r.prob_victoire} probPlace={r.prob_place} />
                    {r.is_value_bet && (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-500 text-slate-950 font-black text-[10px] animate-pulse whitespace-nowrap">
                        <Flame className="w-3 h-3 fill-slate-950" />
                        <span>VALUE BET ({r.kelly_stake_pct}% Kelly)</span>
                      </span>
                    )}
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
