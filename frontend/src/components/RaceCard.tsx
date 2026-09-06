"use client";

import Link from "next/link";
import { RaceSummary } from "@/services/api";
import { ChevronRight, Users, Clock } from "lucide-react";

interface RaceCardProps {
  race: RaceSummary;
  dateStr: string;
  reunionNum: number;
}

export default function RaceCard({ race, dateStr, reunionNum }: RaceCardProps) {
  const timeFormatted = race.heureDepart
    ? new Date(race.heureDepart).toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" })
    : "";

  return (
    <Link
      href={`/race/${dateStr}/${reunionNum}/${race.num}`}
      className="block bg-slate-800/80 hover:bg-slate-800 border border-slate-700/60 rounded-xl p-4 transition shadow-sm hover:shadow-md hover:border-emerald-500/50 group"
    >
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-bold px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800/60">
          R{reunionNum} C{race.num}
        </span>
        {timeFormatted && (
          <div className="flex items-center text-xs text-amber-400 font-medium">
            <Clock className="w-3.5 h-3.5 mr-1" />
            {timeFormatted}
          </div>
        )}
      </div>

      <h3 className="font-semibold text-slate-100 group-hover:text-emerald-400 text-sm mb-2 line-clamp-1">
        {race.libelle}
      </h3>

      <div className="flex items-center justify-between text-xs text-slate-400 pt-2 border-t border-slate-700/40">
        <span className="font-medium text-slate-300">{race.discipline} • {race.distance}m</span>
        <div className="flex items-center gap-1 text-slate-400">
          <Users className="w-3.5 h-3.5" />
          <span>{race.nombrePartants} partants</span>
        </div>
      </div>

      <div className="mt-3 flex items-center justify-end text-xs font-medium text-emerald-400 group-hover:translate-x-1 transition-transform">
        <span>Analyse & Pronostic</span>
        <ChevronRight className="w-4 h-4 ml-0.5" />
      </div>
    </Link>
  );
}
