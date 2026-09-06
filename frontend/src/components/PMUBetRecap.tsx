"use client";

import { useState } from "react";
import { PMUBets } from "@/services/api";
import { Ticket, Star, Zap, CheckCircle2, ShieldAlert, Copy, Check } from "lucide-react";

interface PMUBetRecapProps {
  bets: PMUBets;
  raceTitle?: string;
}

export default function PMUBetRecap({ bets, raceTitle = "Course PMU" }: PMUBetRecapProps) {
  const [copied, setCopied] = useState(false);

  if (!bets) return null;

  const generateFormattedText = () => {
    return `🏇 *PRONOSTIC PMU.fr - ${raceTitle}* 🏇\n\n` +
      `📌 *Simple Gagnant:* ${bets.simple_gagnant?.favori || "N/A"}\n` +
      `🔥 *Value Bet / Outsider:* ${bets.simple_gagnant?.value_bet || "N/A"}\n` +
      `🤝 *Couplé Gagnant:* ${bets.couple?.couple_gagnant || "N/A"}\n` +
      `🎯 *Trio Base:* ${bets.trio?.base || "N/A"} avec X = [${bets.trio?.associes?.join(", ")}]\n` +
      `🏆 *Quinté+ (8 Chevaux):* [${bets.quinte?.pronostic_8_chevaux?.join(" - ")}]\n` +
      `⚡ *Multi en 4:* [${bets.multi?.multi_en_4?.join(" - ")}]\n\n` +
      `💡 _Généré par Turf Predictor Pro_`;
  };

  const handleCopy = () => {
    const text = generateFormattedText();
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6">
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4 pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <Ticket className="w-5 h-5 text-emerald-400" />
            <h2 className="text-lg font-bold text-white">Récapitulatif des Mises Conseillées PMU.fr</h2>
          </div>
          <button
            onClick={handleCopy}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-emerald-600/20 text-emerald-400 hover:bg-emerald-600/30 border border-emerald-500/30 rounded-lg text-xs font-semibold transition cursor-pointer"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-300" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copied ? "Copié pour Telegram / WhatsApp !" : "Copier pour Telegram / WhatsApp"}</span>
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-slate-800/80 border border-slate-700/80 rounded-lg p-4 space-y-3">
            <div className="flex items-center gap-2 text-amber-400 font-bold text-sm">
              <Star className="w-4 h-4" />
              <span>Simple Gagnant & Placé</span>
            </div>
            <div className="text-xs space-y-1 text-slate-300">
              <p><strong className="text-emerald-400">Favori Principal:</strong> {bets.simple_gagnant?.favori}</p>
              <p><strong className="text-amber-400">Value Bet / Outsider:</strong> {bets.simple_gagnant?.value_bet}</p>
              <p className="text-slate-400 italic pt-1">{bets.simple_gagnant?.conseil}</p>
            </div>
          </div>

          <div className="bg-slate-800/80 border border-slate-700/80 rounded-lg p-4 space-y-3">
            <div className="flex items-center gap-2 text-emerald-400 font-bold text-sm">
              <Zap className="w-4 h-4" />
              <span>Couplé (Gagnant / Placé / Ordre)</span>
            </div>
            <div className="text-xs space-y-1 text-slate-300">
              <p><strong className="text-slate-200">Couplé Gagnant:</strong> {bets.couple?.couple_gagnant}</p>
              <p><strong className="text-slate-200">Couplé Placé:</strong> {bets.couple?.couple_place}</p>
              <p><strong className="text-slate-200">Couplé Ordre:</strong> {bets.couple?.couple_ordre}</p>
              <p><strong className="text-emerald-400">Combinaison Élargie:</strong> Chevaux [{bets.couple?.combinaison_elargie?.join(" - ")}]</p>
            </div>
          </div>

          <div className="bg-slate-800/80 border border-slate-700/80 rounded-lg p-4 space-y-3">
            <div className="flex items-center gap-2 text-sky-400 font-bold text-sm">
              <CheckCircle2 className="w-4 h-4" />
              <span>2 sur 4</span>
            </div>
            <div className="text-xs space-y-1 text-slate-300">
              <p><strong className="text-slate-200">Sélection 4 Chevaux:</strong> N°{bets.deux_sur_quatre?.selections?.join(" - N°")}</p>
              <p className="text-slate-400 italic pt-1">{bets.deux_sur_quatre?.conseil}</p>
            </div>
          </div>

          <div className="bg-slate-800/80 border border-slate-700/80 rounded-lg p-4 space-y-3">
            <div className="flex items-center gap-2 text-indigo-400 font-bold text-sm">
              <Ticket className="w-4 h-4" />
              <span>Trio & Tiercé</span>
            </div>
            <div className="text-xs space-y-1 text-slate-300">
              <p><strong className="text-slate-200">Base Trio:</strong> {bets.trio?.base}</p>
              <p><strong className="text-slate-200">Champ Réduit Trio:</strong> {bets.trio?.ticket_champ_reduit}</p>
              <p><strong className="text-indigo-300">Tiercé Ordre Probable:</strong> {bets.tierce?.ordre_probable}</p>
            </div>
          </div>

          <div className="bg-slate-800/80 border border-slate-700/80 rounded-lg p-4 space-y-3 md:col-span-2">
            <div className="flex items-center gap-2 text-amber-500 font-bold text-sm">
              <ShieldAlert className="w-4 h-4" />
              <span>Quarté+ & Quinté+ (Pronostic 8 Chevaux)</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs text-slate-300">
              <div>
                <p><strong className="text-amber-400">Pronostic Quinté+ (8 chevaux):</strong></p>
                <div className="flex gap-1.5 mt-1.5 flex-wrap">
                  {bets.quinte?.pronostic_8_chevaux?.map((num, idx) => (
                    <span key={num} className={`px-2 py-1 rounded font-bold text-xs ${idx < 3 ? "bg-amber-500 text-slate-950" : "bg-slate-700 text-slate-200"}`}>
                      N°{num}
                    </span>
                  ))}
                </div>
              </div>
              <div className="space-y-1">
                <p><strong className="text-slate-200">Base Solide Quinté:</strong> {bets.quinte?.base_quinte}</p>
                <p><strong className="text-slate-200">Complémentaires:</strong> N°{bets.quinte?.complementaires?.join(" - N°")}</p>
              </div>
            </div>
          </div>

          <div className="bg-slate-800/80 border border-slate-700/80 rounded-lg p-4 space-y-3 md:col-span-2">
            <div className="flex items-center gap-2 text-purple-400 font-bold text-sm">
              <Ticket className="w-4 h-4" />
              <span>Multi (PMU.fr)</span>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
              <div className="bg-slate-900/60 p-2 rounded border border-slate-700">
                <span className="text-purple-400 font-semibold block">Multi en 4</span>
                <span className="text-slate-200 font-mono">N°{bets.multi?.multi_en_4?.join(" - N°")}</span>
              </div>
              <div className="bg-slate-900/60 p-2 rounded border border-slate-700">
                <span className="text-purple-400 font-semibold block">Multi en 5</span>
                <span className="text-slate-200 font-mono">N°{bets.multi?.multi_en_5?.join(" - N°")}</span>
              </div>
              <div className="bg-slate-900/60 p-2 rounded border border-slate-700">
                <span className="text-purple-400 font-semibold block">Multi en 6</span>
                <span className="text-slate-200 font-mono">N°{bets.multi?.multi_en_6?.join(" - N°")}</span>
              </div>
              <div className="bg-slate-900/60 p-2 rounded border border-slate-700">
                <span className="text-purple-400 font-semibold block">Multi en 7</span>
                <span className="text-slate-200 font-mono">N°{bets.multi?.multi_en_7?.join(" - N°")}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
