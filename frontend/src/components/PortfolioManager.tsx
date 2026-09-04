"use client";

import React, { useState } from "react";
import { Account, toggleAccountSyncMode, uploadCsvPositions } from "@/lib/api";
import { Upload, RefreshCw, Layers, CheckCircle2, AlertTriangle, FileText, ArrowRight } from "lucide-react";

interface PortfolioManagerProps {
  accounts: Account[];
  onRefresh: () => void;
}

export default function PortfolioManager({ accounts, onRefresh }: PortfolioManagerProps) {
  const [selectedAccId, setSelectedAccId] = useState<string>(accounts[0]?.id || "pea");
  const [uploading, setUploading] = useState<boolean>(false);
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);

  const activeAccount = accounts.find((a) => a.id === selectedAccId) || accounts[0];

  const handleToggleSync = async (mode: string) => {
    try {
      await toggleAccountSyncMode(selectedAccId, mode);
      onRefresh();
    } catch (err) {
      console.error(err);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setUploadStatus("Importation en cours...");

    try {
      const res = await uploadCsvPositions(selectedAccId, file);
      setUploadStatus(`✅ ${res.message}`);
      onRefresh();
    } catch (err: any) {
      setUploadStatus(`❌ Erreur: ${err.message || "Échec de l'importation"}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Broker Tabs */}
      <div className="flex flex-wrap gap-3 border-b border-slate-800 pb-4">
        {accounts.map((acc) => (
          <button
            key={acc.id}
            onClick={() => {
              setSelectedAccId(acc.id);
              setUploadStatus(null);
            }}
            className={`px-4 py-2.5 rounded-lg text-sm font-semibold transition flex items-center space-x-2 ${
              selectedAccId === acc.id
                ? "bg-blue-600 text-white shadow-md shadow-blue-900/30"
                : "bg-slate-900 text-slate-400 hover:text-slate-200 hover:bg-slate-800 border border-slate-800"
            }`}
          >
            <span>{acc.name}</span>
            <span
              className={`text-[10px] px-2 py-0.5 rounded ${
                acc.is_active_for_deposits
                  ? "bg-emerald-950 text-emerald-400 border border-emerald-800/40"
                  : "bg-slate-800 text-slate-400"
              }`}
            >
              {acc.broker}
            </span>
          </button>
        ))}
      </div>

      {/* Selected Account Overview Header */}
      {activeAccount && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="flex items-center space-x-3">
                <h2 className="text-xl font-bold text-white">{activeAccount.name}</h2>
                <span className="text-xs px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 font-medium">
                  {activeAccount.account_type}
                </span>
              </div>
              <p className="text-sm text-slate-400 mt-1">
                {activeAccount.is_active_for_deposits
                  ? "Compte principal de versement (Reçoit 100% des versements mensuels)"
                  : "Compte inactif en nouveaux versements (Gestion du capital déjà présent)"}
              </p>
            </div>

            {/* Sync Mode Toggle & CSV Upload Actions */}
            <div className="flex flex-wrap items-center gap-3">
              <div className="flex items-center bg-slate-950 p-1 rounded-lg border border-slate-800">
                <button
                  onClick={() => handleToggleSync("CONNECTED")}
                  className={`px-3 py-1.5 rounded-md text-xs font-medium transition flex items-center ${
                    activeAccount.api_sync_status.includes("CONNECTED")
                      ? "bg-blue-600 text-white font-bold"
                      : "text-slate-400 hover:text-white"
                  }`}
                >
                  <RefreshCw className="w-3 h-3 mr-1" /> API En Direct
                </button>
                <button
                  onClick={() => handleToggleSync("MANUAL")}
                  className={`px-3 py-1.5 rounded-md text-xs font-medium transition flex items-center ${
                    activeAccount.api_sync_status.includes("MANUAL")
                      ? "bg-amber-600 text-white font-bold"
                      : "text-slate-400 hover:text-white"
                  }`}
                >
                  Saisie Manuelle
                </button>
              </div>

              {/* CSV Upload Button */}
              <label className="cursor-pointer px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition">
                <Upload className="w-3.5 h-3.5 text-blue-400" />
                <span>Import CSV / Relevé</span>
                <input
                  type="file"
                  accept=".csv,.txt"
                  className="hidden"
                  onChange={handleFileUpload}
                  disabled={uploading}
                />
              </label>
            </div>
          </div>

          {uploadStatus && (
            <div className="text-xs font-medium p-2.5 bg-slate-950 border border-slate-800 rounded-lg text-slate-300">
              {uploadStatus}
            </div>
          )}

          {/* Key Metrics of Account */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-slate-800/80">
            <div>
              <span className="text-xs text-slate-400">Solde Total</span>
              <p className="text-lg font-bold text-white">{activeAccount.total_value.toLocaleString("fr-FR")} €</p>
            </div>
            <div>
              <span className="text-xs text-slate-400">Solde Liquide</span>
              <p className="text-lg font-bold text-emerald-400">{activeAccount.cash_balance.toLocaleString("fr-FR")} €</p>
            </div>
            <div>
              <span className="text-xs text-slate-400">Statut Synchro</span>
              <p className="text-sm font-semibold text-blue-400">{activeAccount.api_sync_status}</p>
            </div>
            <div>
              <span className="text-xs text-slate-400">Dernière MàJ</span>
              <p className="text-sm font-medium text-slate-300">{activeAccount.last_synced}</p>
            </div>
          </div>
        </div>
      )}

      {/* Structured Product Special Card if Goliaths */}
      {activeAccount?.structured_product && (
        <div className="bg-slate-900 border border-amber-900/40 rounded-xl p-6 space-y-4">
          <div className="flex justify-between items-start">
            <div className="flex items-center space-x-2">
              <AlertTriangle className="w-5 h-5 text-amber-400" />
              <h3 className="text-md font-bold text-white">{activeAccount.structured_product.name}</h3>
            </div>
            <span className="text-xs font-bold px-2.5 py-1 rounded bg-amber-950 text-amber-300 border border-amber-800/50">
              Échéance : 15 Mars 2030
            </span>
          </div>

          <p className="text-xs text-slate-300 bg-amber-950/30 p-3 rounded-lg border border-amber-900/30">
            {activeAccount.structured_product.alert_message}
          </p>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
            <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
              <span className="text-slate-400">Montant Investi</span>
              <p className="text-sm font-bold text-white mt-0.5">{activeAccount.structured_product.invested_amount} €</p>
            </div>
            <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
              <span className="text-slate-400">Valeur Courante Est.</span>
              <p className="text-sm font-bold text-emerald-400 mt-0.5">{activeAccount.structured_product.current_value.toFixed(2)} €</p>
            </div>
            <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
              <span className="text-slate-400">Barrière de Protection</span>
              <p className="text-sm font-bold text-amber-400 mt-0.5">-40 % du cours initial</p>
            </div>
            <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
              <span className="text-slate-400">Pire Sous-Jacent</span>
              <p className="text-sm font-bold text-slate-200 mt-0.5">{activeAccount.structured_product.worst_underlying_pct}%</p>
            </div>
          </div>
        </div>
      )}

      {/* Positions Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        <div className="p-5 border-b border-slate-800 flex justify-between items-center">
          <h3 className="text-md font-bold text-white flex items-center">
            <Layers className="w-4 h-4 mr-2 text-blue-400" /> Positions Détallées ({activeAccount?.positions.length || 0})
          </h3>
        </div>

        {activeAccount?.positions.length === 0 ? (
          <div className="p-8 text-center text-slate-400 text-sm">
            <p>Aucune position en portefeuille pour ce compte.</p>
            <p className="text-xs text-slate-500 mt-1">
              {activeAccount.id === "pea"
                ? "Utilisez le widget DCA pour exécuter votre versement mensuel de 100 à 200 € sur l'ETF MSCI World PEA."
                : "Vous pouvez importer vos positions via le bouton 'Import CSV'."}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider border-b border-slate-800">
                <tr>
                  <th className="px-5 py-3.5">Actif</th>
                  <th className="px-5 py-3.5">Type / Secteur</th>
                  <th className="px-5 py-3.5">Quantité</th>
                  <th className="px-5 py-3.5">Prix d'Achat</th>
                  <th className="px-5 py-3.5">Cours Actuel</th>
                  <th className="px-5 py-3.5">Valeur Totale</th>
                  <th className="px-5 py-3.5">Plus / Moins Value</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-200">
                {activeAccount?.positions.map((pos, idx) => (
                  <tr key={`${pos.ticker}-${idx}`} className="hover:bg-slate-800/40 transition">
                    <td className="px-5 py-4 font-semibold text-white">
                      <div>{pos.name}</div>
                      <div className="text-[10px] text-blue-400 font-mono">{pos.ticker}</div>
                    </td>
                    <td className="px-5 py-4">
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-medium">
                        {pos.asset_type}
                      </span>
                      <div className="text-[10px] text-slate-400 mt-0.5">{pos.sector}</div>
                    </td>
                    <td className="px-5 py-4 font-medium">{pos.units}</td>
                    <td className="px-5 py-4">{pos.buy_price.toFixed(2)} €</td>
                    <td className="px-5 py-4 font-bold text-slate-100">{pos.current_price.toFixed(2)} €</td>
                    <td className="px-5 py-4 font-bold text-white">{pos.total_value.toFixed(2)} €</td>
                    <td className="px-5 py-4 font-bold">
                      <span className={pos.gain_loss >= 0 ? "text-emerald-400" : "text-rose-400"}>
                        {pos.gain_loss >= 0 ? "+" : ""}{pos.gain_loss.toFixed(2)} € ({pos.gain_loss_percent >= 0 ? "+" : ""}{pos.gain_loss_percent}%)
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
