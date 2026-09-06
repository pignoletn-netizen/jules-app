"use client";

import React, { useState } from "react";
import {
  Upload,
  Download,
  FileSpreadsheet,
  BarChart3,
  Layers,
  Grid,
  TrendingUp,
  Loader2,
  CheckCircle2,
  AlertCircle
} from "lucide-react";

interface AnalysisResults {
  summary_table: any[];
  diversity_table: any[];
  jaccard_matrix: any[];
  species_clusters: any[];
  habitat_clusters: any[];
  barber_family_summary: any[];
  excel_file: string;
  plots: {
    afc_biplot: string;
    hcpc_species: string;
    hcpc_habitats: string;
    barber_species_pct: string;
    barber_individuals_pct: string;
  };
}

export default function InventoryAnalysis() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<AnalysisResults | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeSubTab, setActiveSubTab] = useState<"summary" | "diversity" | "jaccard" | "afc" | "barber">("summary");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Veuillez sélectionner un fichier Excel (.xls ou .xlsx).");
      return;
    }

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("/api/analysis/upload", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}));
        throw new Error(errJson.detail || `Erreur serveur: ${res.status}`);
      }

      const data: AnalysisResults = await res.json();
      setResults(data);
    } catch (err: any) {
      setError(err.message || "Échec de l'analyse du fichier Excel.");
    } finally {
      setLoading(false);
    }
  };

  const downloadSample = () => {
    window.open("/api/analysis/sample", "_blank");
  };

  const downloadExcelResult = () => {
    if (results?.excel_file) {
      window.open(`/api/analysis/download/${results.excel_file}`, "_blank");
    }
  };

  return (
    <div className="space-y-6">
      {/* Upload Box */}
      <div className="bg-white rounded-2xl shadow-sm border border-emerald-100 p-6 space-y-4">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
              <FileSpreadsheet className="w-6 h-6 text-emerald-600" />
              Traitement et Analyse des Données d'Inventaire
            </h2>
            <p className="text-slate-600 text-sm mt-1">
              Importez votre fichier d'inventaire (.xls, .xlsx) contenant les colonnes standard :{" "}
              <code className="bg-slate-100 text-emerald-800 px-1.5 py-0.5 rounded text-xs font-mono">
                Genresp, Famille, Date, Capture, Mâles, Fem, Juv, Ad, Tot ab, Station, ModeCapt
              </code>
            </p>
          </div>

          <button
            onClick={downloadSample}
            type="button"
            className="px-4 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-medium rounded-xl transition-colors flex items-center gap-2 whitespace-nowrap"
          >
            <Download className="w-4 h-4 text-slate-500" />
            Télécharger modèle Excel exemple
          </button>
        </div>

        {/* Drag and Drop Zone */}
        <div className="border-2 border-dashed border-slate-200 hover:border-emerald-500 rounded-2xl p-6 transition-colors text-center bg-slate-50/50">
          <input
            type="file"
            accept=".xlsx, .xls"
            onChange={handleFileChange}
            className="hidden"
            id="excel-upload"
          />
          <label htmlFor="excel-upload" className="cursor-pointer space-y-2 block">
            <Upload className="w-10 h-10 text-emerald-600 mx-auto" />
            <div className="text-sm font-medium text-slate-700">
              {file ? (
                <span className="text-emerald-700 font-bold flex items-center justify-center gap-1">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  {file.name}
                </span>
              ) : (
                "Cliquez ici ou déposez votre fichier Excel (.xlsx ou .xls)"
              )}
            </div>
            <p className="text-xs text-slate-400">Taille maximale recommandée : 10 Mo</p>
          </label>
        </div>

        <div className="flex justify-end gap-3">
          <button
            onClick={handleUpload}
            disabled={!file || loading}
            className="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-medium rounded-xl text-sm transition-colors flex items-center gap-2 disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Exécution des calculs R (FactoMineR / vegan)...
              </>
            ) : (
              "Lancer l'Analyse Statistique R"
            )}
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl text-sm flex items-center gap-2">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          {error}
        </div>
      )}

      {/* Results Section */}
      {results && (
        <div className="space-y-6">
          {/* Top Bar with Excel Export */}
          <div className="bg-emerald-900 text-white rounded-2xl p-5 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 shadow-md">
            <div>
              <h3 className="text-lg font-bold flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                Analyse terminée avec succès !
              </h3>
              <p className="text-xs text-emerald-200 mt-0.5">
                Tous les indices, matrices de similarité, axes factoriels et représentations graphiques ont été calculés.
              </p>
            </div>

            <button
              onClick={downloadExcelResult}
              className="px-5 py-2.5 bg-emerald-500 hover:bg-emerald-400 text-emerald-950 font-bold rounded-xl text-sm transition-colors flex items-center gap-2 shadow-sm"
            >
              <Download className="w-4 h-4" />
              Exporter Résultats (.xlsx Excel 2007)
            </button>
          </div>

          {/* Sub-Tabs Navigation */}
          <div className="flex border-b border-slate-200 overflow-x-auto space-x-1">
            {[
              { id: "summary", label: "1. Synthèse Habitats", icon: Layers },
              { id: "diversity", label: "2. Indices Diversité (H', J')", icon: TrendingUp },
              { id: "jaccard", label: "3. Similarité Jaccard", icon: Grid },
              { id: "afc", label: "4. AFC & HCPC (FactoMineR)", icon: BarChart3 },
              { id: "barber", label: "5. Pièges Barber (% Familles)", icon: BarChart3 },
            ].map((tab) => {
              const Icon = tab.icon;
              const isActive = activeSubTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveSubTab(tab.id as any)}
                  className={`px-4 py-3 text-sm font-semibold border-b-2 flex items-center gap-2 transition-colors whitespace-nowrap ${
                    isActive
                      ? "border-emerald-600 text-emerald-700 bg-emerald-50/50 rounded-t-xl"
                      : "border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300"
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                </button>
              );
            })}
          </div>

          {/* Tab 1: Summary Table */}
          {activeSubTab === "summary" && (
            <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6 space-y-4">
              <h3 className="text-md font-bold text-slate-800">
                1. Tableau de synthèse par Habitat / Station
              </h3>
              <p className="text-xs text-slate-500">
                Richesse spécifique, effectifs adultes, effectifs juvéniles et abondance relative (nombre d'individus par piège et par semaine).
              </p>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-slate-700 border-collapse">
                  <thead>
                    <tr className="bg-slate-100 border-b border-slate-200 text-slate-800 uppercase font-semibold">
                      {Object.keys(results.summary_table[0] || {}).map((col) => (
                        <th key={col} className="p-3">
                          {col}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {results.summary_table.map((row, idx) => (
                      <tr key={idx} className="border-b border-slate-100 hover:bg-slate-50">
                        {Object.values(row).map((val: any, cidx) => (
                          <td key={cidx} className="p-3 font-medium">
                            {val}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Tab 2: Diversity Indices */}
          {activeSubTab === "diversity" && (
            <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6 space-y-4">
              <h3 className="text-md font-bold text-slate-800">
                2. Indices de Diversité (Shannon H' & Équitabilité de Pielou J')
              </h3>
              <p className="text-xs text-slate-500">
                Calculés par habitat/station avec le package R <code className="text-emerald-700 font-mono">vegan</code>.
              </p>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-slate-700 border-collapse">
                  <thead>
                    <tr className="bg-slate-100 border-b border-slate-200 text-slate-800 uppercase font-semibold">
                      <th className="p-3">Habitat / Station</th>
                      <th className="p-3">Richesse Spécifique (S)</th>
                      <th className="p-3">Indice de Shannon (H')</th>
                      <th className="p-3">Équitabilité de Pielou (J')</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.diversity_table.map((row, idx) => (
                      <tr key={idx} className="border-b border-slate-100 hover:bg-slate-50">
                        <td className="p-3 font-bold text-slate-800">{row.Habitat_Station}</td>
                        <td className="p-3">{row.Richesse_Specifique}</td>
                        <td className="p-3 font-semibold text-emerald-700">{row.Shannon_H}</td>
                        <td className="p-3 font-semibold text-teal-700">{row.Pielou_J}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Tab 3: Jaccard Similarity */}
          {activeSubTab === "jaccard" && (
            <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6 space-y-4">
              <h3 className="text-md font-bold text-slate-800">
                3. Matrice de Similarité de Jaccard entre Habitats
              </h3>
              <p className="text-xs text-slate-500">
                Valeurs comprises entre 0 (aucune espèce en commun) et 1 (communautés identiques).
              </p>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-slate-700 border-collapse">
                  <thead>
                    <tr className="bg-slate-100 border-b border-slate-200 text-slate-800 uppercase font-semibold">
                      {Object.keys(results.jaccard_matrix[0] || {}).map((col) => (
                        <th key={col} className="p-3">
                          {col}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {results.jaccard_matrix.map((row, idx) => (
                      <tr key={idx} className="border-b border-slate-100 hover:bg-slate-50">
                        {Object.values(row).map((val: any, cidx) => {
                          const isNum = typeof val === "number";
                          const bgColor = isNum && val > 0.5 ? "bg-emerald-50 text-emerald-800 font-bold" : "";
                          return (
                            <td key={cidx} className={`p-3 ${bgColor}`}>
                              {val}
                            </td>
                          );
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Tab 4: AFC & HCPC Plots */}
          {activeSubTab === "afc" && (
            <div className="space-y-6">
              {/* AFC Biplot */}
              <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6 space-y-4">
                <h3 className="text-md font-bold text-slate-800">
                  4a. Analyse Factorielle des Correspondances (AFC)
                </h3>
                <p className="text-xs text-slate-500">
                  Biplot représentant la matrice Espèces x Habitats.
                </p>
                <div className="bg-slate-50 p-2 rounded-xl flex justify-center border border-slate-200">
                  <img
                    src={`/static/output/${results.plots.afc_biplot}?t=${Date.now()}`}
                    alt="Biplot AFC"
                    className="max-h-96 object-contain rounded-lg"
                  />
                </div>
              </div>

              {/* HCPC Plots Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* HCPC Species */}
                <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6 space-y-4">
                  <h3 className="text-md font-bold text-slate-800">
                    4b. Classification Hiérarchique (HCPC Espèces)
                  </h3>
                  <div className="bg-slate-50 p-2 rounded-xl flex justify-center border border-slate-200">
                    <img
                      src={`/static/output/${results.plots.hcpc_species}?t=${Date.now()}`}
                      alt="Dendrogramme Espèces"
                      className="max-h-80 object-contain rounded-lg"
                    />
                  </div>
                </div>

                {/* HCPC Habitats */}
                <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6 space-y-4">
                  <h3 className="text-md font-bold text-slate-800">
                    4c. Classification Hiérarchique (HCPC Habitats)
                  </h3>
                  <div className="bg-slate-50 p-2 rounded-xl flex justify-center border border-slate-200">
                    <img
                      src={`/static/output/${results.plots.hcpc_habitats}?t=${Date.now()}`}
                      alt="Dendrogramme Habitats"
                      className="max-h-80 object-contain rounded-lg"
                    />
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Tab 5: Barber Trap Charts */}
          {activeSubTab === "barber" && (
            <div className="space-y-6">
              <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6 space-y-4">
                <h3 className="text-md font-bold text-slate-800">
                  5. Représentation des familles (Pièges Barber)
                </h3>
                <p className="text-xs text-slate-500">
                  Graphiques synthétiques calculés sur le mode de capture "barber" (piégeage au sol).
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* % Species */}
                  <div className="bg-slate-50 p-3 rounded-xl border border-slate-200 text-center space-y-2">
                    <span className="text-xs font-bold text-slate-700 uppercase">
                      % Représentation en Nombre d'Espèces
                    </span>
                    <img
                      src={`/static/output/${results.plots.barber_species_pct}?t=${Date.now()}`}
                      alt="Barber % espèces"
                      className="max-h-80 mx-auto object-contain rounded-lg"
                    />
                  </div>

                  {/* % Individuals */}
                  <div className="bg-slate-50 p-3 rounded-xl border border-slate-200 text-center space-y-2">
                    <span className="text-xs font-bold text-slate-700 uppercase">
                      % Représentation en Nombre d'Individus
                    </span>
                    <img
                      src={`/static/output/${results.plots.barber_individuals_pct}?t=${Date.now()}`}
                      alt="Barber % individus"
                      className="max-h-80 mx-auto object-contain rounded-lg"
                    />
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
