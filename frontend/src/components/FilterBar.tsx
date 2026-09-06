"use client";

import { Filter, Search } from "lucide-react";

interface FilterBarProps {
  selectedDiscipline: string;
  onSelectDiscipline: (discipline: string) => void;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  disciplines: string[];
}

export default function FilterBar({
  selectedDiscipline,
  onSelectDiscipline,
  searchQuery,
  onSearchChange,
  disciplines
}: FilterBarProps) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 mb-6 flex flex-col sm:flex-row items-center justify-between gap-4">
      <div className="relative w-full sm:w-72">
        <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Rechercher hippo, course..."
          className="w-full pl-9 pr-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm text-slate-100 placeholder-slate-400 focus:outline-none focus:border-emerald-500"
        />
      </div>

      <div className="flex items-center gap-2 overflow-x-auto w-full sm:w-auto pb-1 sm:pb-0">
        <Filter className="h-4 w-4 text-slate-400 shrink-0 hidden sm:block" />
        <button
          onClick={() => onSelectDiscipline("TOUS")}
          className={`px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition ${
            selectedDiscipline === "TOUS"
              ? "bg-emerald-600 text-white"
              : "bg-slate-800 text-slate-300 hover:bg-slate-700"
          }`}
        >
          Toutes Disciplines
        </button>
        {disciplines.map((disc) => (
          <button
            key={disc}
            onClick={() => onSelectDiscipline(disc)}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition ${
              selectedDiscipline === disc
                ? "bg-emerald-600 text-white"
                : "bg-slate-800 text-slate-300 hover:bg-slate-700"
            }`}
          >
            {disc}
          </button>
        ))}
      </div>
    </div>
  );
}
