"use client";

interface PredictionBadgeProps {
  confidence?: string;
  probVictoire?: number;
  probPlace?: number;
}

export default function PredictionBadge({ confidence, probVictoire, probPlace }: PredictionBadgeProps) {
  if (confidence) {
    const config = {
      TRES_ELEVE: { label: "Confiance Très Élevée", bg: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30" },
      ELEVE: { label: "Confiance Élevée", bg: "bg-green-500/20 text-green-400 border-green-500/30" },
      MOYEN: { label: "Confiance Moyenne", bg: "bg-amber-500/20 text-amber-400 border-amber-500/30" },
      FAIBLE: { label: "Course Indécise", bg: "bg-rose-500/20 text-rose-400 border-rose-500/30" },
    }[confidence] || { label: "Analyse", bg: "bg-slate-700 text-slate-300 border-slate-600" };

    return (
      <span className={`px-2.5 py-1 text-xs font-semibold rounded-full border ${config.bg}`}>
        {config.label}
      </span>
    );
  }

  if (probVictoire !== undefined) {
    let colorClass = "text-slate-300 bg-slate-800";
    if (probVictoire >= 20) colorClass = "text-emerald-400 bg-emerald-950/50 border border-emerald-800";
    else if (probVictoire >= 12) colorClass = "text-amber-400 bg-amber-950/50 border border-amber-800";
    else colorClass = "text-slate-400 bg-slate-900";

    return (
      <div className={`px-2 py-1 rounded text-center font-bold text-xs ${colorClass}`}>
        <div>{probVictoire}% Victoire</div>
        {probPlace !== undefined && (
          <div className="text-[10px] text-slate-400 font-normal">({probPlace}% Placé)</div>
        )}
      </div>
    );
  }

  return null;
}
