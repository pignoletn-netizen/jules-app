"use client";

import { useEffect, useState } from "react";
import HeaderNav from "@/components/HeaderNav";
import RaceCard from "@/components/RaceCard";
import FilterBar from "@/components/FilterBar";
import { fetchDailyProgramme, DailyProgramme } from "@/services/api";
import { RefreshCw, Sparkles, MapPin } from "lucide-react";

export default function Home() {
  const [programme, setProgramme] = useState<DailyProgramme | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedDiscipline, setSelectedDiscipline] = useState("TOUS");
  const [searchQuery, setSearchQuery] = useState("");

  const loadData = async () => {
    setLoading(true);
    try {
      const data = await fetchDailyProgramme();
      setProgramme(data);
    } catch (err) {
      console.error("Error loading daily programme:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const allDisciplines = Array.from(
    new Set(
      programme?.reunions?.flatMap((r) => r.courses.map((c) => c.discipline)) || []
    )
  ).filter(Boolean);

  const filteredReunions = programme?.reunions?.map((r) => {
    const matchingCourses = r.courses.filter((c) => {
      const matchesDisc =
        selectedDiscipline === "TOUS" || c.discipline === selectedDiscipline;
      const matchesQuery =
        !searchQuery ||
        r.hippodrome.toLowerCase().includes(searchQuery.toLowerCase()) ||
        c.libelle.toLowerCase().includes(searchQuery.toLowerCase());
      return matchesDisc && matchesQuery;
    });

    return { ...r, courses: matchingCourses };
  }).filter((r) => r.courses.length > 0) || [];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <HeaderNav />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-gradient-to-r from-slate-900 via-emerald-950/40 to-slate-900 border border-emerald-900/50 rounded-2xl p-6 mb-8 shadow-xl relative overflow-hidden">
          <div className="max-w-3xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-400 text-xs font-semibold mb-3 border border-emerald-500/30">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Pronostics Hippiques IA Multi-Critères & Value Bets</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-black text-white mb-2 tracking-tight">
              Programme & Pronostics des Courses du Jour
            </h1>
            <p className="text-slate-300 text-sm leading-relaxed">
              Analyse automatique basée sur la musique des chevaux, le terrain, le déferrage (D4/DA), les œillères, les cotes en direct et la détection de Value Bets.
            </p>
          </div>

          <button
            onClick={loadData}
            disabled={loading}
            className="mt-4 sm:mt-0 sm:absolute sm:right-6 sm:top-6 inline-flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium rounded-lg border border-slate-700 transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
            <span>Actualiser</span>
          </button>
        </div>

        <FilterBar
          selectedDiscipline={selectedDiscipline}
          onSelectDiscipline={setSelectedDiscipline}
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          disciplines={allDisciplines}
        />

        {loading ? (
          <div className="text-center py-20 space-y-3">
            <RefreshCw className="w-8 h-8 text-emerald-400 animate-spin mx-auto" />
            <p className="text-slate-400 text-sm">Chargement du programme PMU du jour...</p>
          </div>
        ) : filteredReunions.length === 0 ? (
          <div className="text-center py-16 bg-slate-900 border border-slate-800 rounded-xl p-8">
            <p className="text-slate-400 text-base">Aucune course trouvée pour ces critères.</p>
          </div>
        ) : (
          <div className="space-y-10">
            {filteredReunions.map((reunion) => (
              <section key={reunion.num} className="space-y-4">
                <div className="flex items-center gap-2 pb-2 border-b border-slate-800">
                  <span className="px-3 py-1 bg-amber-500 text-slate-950 font-black text-xs rounded-md shadow-sm">
                    Réunion {reunion.num}
                  </span>
                  <h2 className="text-lg font-bold text-white flex items-center gap-1.5">
                    <MapPin className="w-4 h-4 text-emerald-400" />
                    <span>{reunion.hippodrome}</span>
                  </h2>
                  <span className="text-xs text-slate-400 ml-auto font-medium">
                    {reunion.courses.length} course{reunion.courses.length > 1 ? "s" : ""}
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                  {reunion.courses.map((course) => (
                    <RaceCard
                      key={course.num}
                      race={course}
                      dateStr={programme?.date || ""}
                      reunionNum={reunion.num}
                    />
                  ))}
                </div>
              </section>
            ))}
          </div>
        )}
      </main>

      <footer className="border-t border-slate-800 bg-slate-900 py-6 text-center text-xs text-slate-500">
        <p>Turf Predictor & PMU Bet Advisor • Données officielles PMU.fr en temps réel</p>
      </footer>
    </div>
  );
}
