"use client";

import React, { useState } from "react";
import { Search, MapPin, Tag, BookOpen, Bug, ShieldCheck, Loader2 } from "lucide-react";

interface Taxonomy {
  kingdom: string;
  phylum: string;
  class: string;
  order: string;
  family: string;
  genus: string;
  species: string;
}

interface Ecology {
  general_ecology: string;
  habitat_type: string;
  lifestyle: string;
}

interface Distribution {
  total_france_occurrences: number;
  auvergne_rhone_alpes_occurrences: number;
  departments_breakdown: Record<string, number>;
}

interface SpeciesData {
  query: string;
  cd_nom: string;
  scientific_name: string;
  canonical_name: string;
  authorship: string;
  taxonomy: Taxonomy;
  vernacular_names: string[];
  ecology: Ecology;
  distribution: Distribution;
  summary_text: string;
}

const EXAMPLES = [
  "Textrix denticulata",
  "Agelena labyrinthica",
  "Pardosa amentata",
  "Araneus diadematus",
  "Salticus scenicus",
  "Xysticus cristatus",
];

export default function SpeciesSearch() {
  const [searchTerm, setSearchTerm] = useState("Textrix denticulata");
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<SpeciesData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (termToSearch?: string) => {
    const query = termToSearch || searchTerm;
    if (!query.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`/api/species/search?name=${encodeURIComponent(query)}`);
      if (!res.ok) {
        throw new Error(`Erreur HTTP: ${res.status}`);
      }
      const json: SpeciesData = await res.json();
      setData(json);
    } catch (err: any) {
      setError(err.message || "Impossible de récupérer les informations de l'espèce.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Search Header */}
      <div className="bg-white rounded-2xl shadow-sm border border-emerald-100 p-6">
        <h2 className="text-xl font-bold text-slate-800 mb-2 flex items-center gap-2">
          <Bug className="w-6 h-6 text-emerald-600" />
          Recherche d'une Espèce (Fiche Écologie & Taxref / INPN)
        </h2>
        <p className="text-slate-600 text-sm mb-4">
          Entrez le nom scientifique d'une espèce d'araignée pour consulter son identifiant Taxref (CDnom), sa position taxonomique, son écologie et sa répartition géographique en France et Auvergne-Rhône-Alpes.
        </p>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSearch();
          }}
          className="flex flex-col sm:flex-row gap-3"
        >
          <div className="relative flex-1">
            <Search className="absolute left-3.5 top-3.5 w-5 h-5 text-slate-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="ex: Textrix denticulata, Pardosa amentata..."
              className="w-full pl-11 pr-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent text-slate-800 text-sm"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-medium rounded-xl text-sm transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : "Rechercher"}
          </button>
        </form>

        {/* Suggestions */}
        <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-slate-500">
          <span className="font-medium">Exemples :</span>
          {EXAMPLES.map((ex) => (
            <button
              key={ex}
              type="button"
              onClick={() => {
                setSearchTerm(ex);
                handleSearch(ex);
              }}
              className="px-2.5 py-1 bg-slate-100 hover:bg-emerald-50 text-slate-700 hover:text-emerald-700 rounded-lg transition-colors"
            >
              {ex}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl text-sm">
          {error}
        </div>
      )}

      {data && (
        <div className="space-y-6">
          {/* Species Banner */}
          <div className="bg-gradient-to-r from-emerald-800 to-teal-900 text-white rounded-2xl p-6 shadow-md">
            <div className="flex flex-wrap justify-between items-start gap-4">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="px-3 py-1 bg-emerald-700/80 text-emerald-100 text-xs font-semibold rounded-full uppercase tracking-wider">
                    {data.taxonomy.family}
                  </span>
                  <span className="px-3 py-1 bg-emerald-500/30 text-emerald-200 text-xs font-semibold rounded-full flex items-center gap-1">
                    <ShieldCheck className="w-3.5 h-3.5 text-emerald-300" />
                    CDnom INPN: {data.cd_nom}
                  </span>
                </div>
                <h1 className="text-3xl font-extrabold italic tracking-tight">
                  {data.canonical_name}
                </h1>
                <p className="text-emerald-200 text-sm mt-1">{data.authorship}</p>
              </div>

              {data.vernacular_names.length > 0 && (
                <div className="bg-white/10 backdrop-blur-md rounded-xl p-3 text-right max-w-xs">
                  <span className="text-xs text-emerald-200 font-medium block mb-1">
                    Noms vernaculaires :
                  </span>
                  <p className="text-xs font-semibold text-white">
                    {data.vernacular_names.join(", ")}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Grid Layout: Taxonomy & Ecology */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Taxonomy Card */}
            <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6 space-y-4">
              <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2 border-b border-slate-100 pb-3">
                <Tag className="w-5 h-5 text-emerald-600" />
                Taxonomie & Classification
              </h3>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="bg-slate-50 p-3 rounded-xl">
                  <span className="text-xs text-slate-400 font-medium block">Règne</span>
                  <span className="font-semibold text-slate-700">{data.taxonomy.kingdom}</span>
                </div>
                <div className="bg-slate-50 p-3 rounded-xl">
                  <span className="text-xs text-slate-400 font-medium block">Embranchement</span>
                  <span className="font-semibold text-slate-700">{data.taxonomy.phylum}</span>
                </div>
                <div className="bg-slate-50 p-3 rounded-xl">
                  <span className="text-xs text-slate-400 font-medium block">Classe</span>
                  <span className="font-semibold text-slate-700">{data.taxonomy.class}</span>
                </div>
                <div className="bg-slate-50 p-3 rounded-xl">
                  <span className="text-xs text-slate-400 font-medium block">Ordre</span>
                  <span className="font-semibold text-slate-700">{data.taxonomy.order}</span>
                </div>
                <div className="bg-emerald-50 p-3 rounded-xl border border-emerald-100">
                  <span className="text-xs text-emerald-600 font-medium block">Famille</span>
                  <span className="font-bold text-emerald-900">{data.taxonomy.family}</span>
                </div>
                <div className="bg-emerald-50 p-3 rounded-xl border border-emerald-100">
                  <span className="text-xs text-emerald-600 font-medium block">Genre</span>
                  <span className="font-bold italic text-emerald-900">{data.taxonomy.genus}</span>
                </div>
              </div>
            </div>

            {/* Ecology & Habitat Card */}
            <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6 space-y-4">
              <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2 border-b border-slate-100 pb-3">
                <BookOpen className="w-5 h-5 text-emerald-600" />
                Écologie & Habitat
              </h3>
              <div className="space-y-3 text-sm">
                <div>
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                    Écologie générale
                  </span>
                  <p className="text-slate-700 bg-slate-50 p-3 rounded-xl leading-relaxed">
                    {data.ecology.general_ecology}
                  </p>
                </div>
                <div>
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                    Habitat de prédilection
                  </span>
                  <p className="text-slate-700 bg-slate-50 p-3 rounded-xl">
                    {data.ecology.habitat_type}
                  </p>
                </div>
                <div>
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                    Mode de vie & Prédation
                  </span>
                  <p className="text-slate-700 bg-slate-50 p-3 rounded-xl">
                    {data.ecology.lifestyle}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Geographic Distribution Card */}
          <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6 space-y-4">
            <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2 border-b border-slate-100 pb-3">
              <MapPin className="w-5 h-5 text-emerald-600" />
              Répartition Géographique (INPN / GBIF)
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="bg-gradient-to-br from-emerald-50 to-teal-50 border border-emerald-100 p-4 rounded-xl flex items-center gap-4">
                <div className="w-12 h-12 bg-emerald-600 text-white rounded-xl flex items-center justify-center font-bold text-xl shadow-sm">
                  {data.distribution.total_france_occurrences}
                </div>
                <div>
                  <span className="text-xs text-emerald-700 font-semibold block uppercase">
                    France métropolitaine
                  </span>
                  <span className="text-sm text-slate-600">Occurrences enregistrées</span>
                </div>
              </div>

              <div className="bg-gradient-to-br from-teal-50 to-cyan-50 border border-teal-100 p-4 rounded-xl flex items-center gap-4">
                <div className="w-12 h-12 bg-teal-600 text-white rounded-xl flex items-center justify-center font-bold text-xl shadow-sm">
                  {data.distribution.auvergne_rhone_alpes_occurrences}
                </div>
                <div>
                  <span className="text-xs text-teal-700 font-semibold block uppercase">
                    Auvergne-Rhône-Alpes
                  </span>
                  <span className="text-sm text-slate-600">Occurrences répertoriées</span>
                </div>
              </div>
            </div>

            {Object.keys(data.distribution.departments_breakdown).length > 0 ? (
              <div>
                <span className="text-xs font-semibold text-slate-500 block mb-2">
                  Détail par département / secteur (Auvergne-Rhône-Alpes) :
                </span>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(data.distribution.departments_breakdown).map(([dep, count]) => (
                    <span
                      key={dep}
                      className="px-3 py-1.5 bg-slate-100 text-slate-700 rounded-lg text-xs font-medium border border-slate-200"
                    >
                      {dep} : <strong className="text-emerald-700">{count}</strong> obs.
                    </span>
                  ))}
                </div>
              </div>
            ) : (
              <p className="text-xs text-slate-500 italic bg-slate-50 p-3 rounded-xl">
                Presence attestée en Auvergne-Rhône-Alpes. Les données détaillées par département sont issues des relevés récents GBIF/INPN.
              </p>
            )}
          </div>

          {/* Clean Synthetic Summary */}
          <div className="bg-slate-900 text-slate-100 rounded-2xl p-6 shadow-md space-y-3">
            <h4 className="text-md font-bold text-emerald-400 flex items-center gap-2">
              <BookOpen className="w-5 h-5" />
              Résumé Synthétique d'Écologie
            </h4>
            <div className="text-sm leading-relaxed text-slate-300 space-y-2 whitespace-pre-line">
              {data.summary_text}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
