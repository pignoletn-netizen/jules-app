'use client';

import React, { useState, useEffect } from 'react';
import {
  Video,
  Sparkles,
  FileText,
  CheckSquare,
  Copy,
  Check,
  Share2,
  Tv,
  Megaphone,
  X
} from 'lucide-react';
import api from '@/lib/api';
import LoadingSpinner, { SkeletonCard } from '@/components/LoadingSpinner';

export default function MarketingPage() {
  const [products, setProducts] = useState<any[]>([]);
  const [selectedProductId, setSelectedProductId] = useState<number>(0);
  const [angle, setAngle] = useState('');
  const [loading, setLoading] = useState(false);
  const [content, setContent] = useState<any>(null);
  const [copiedField, setCopiedField] = useState<string | null>(null);

  const [guideItems, setGuideItems] = useState<any[]>([]);

  useEffect(() => {
    api.get('/api/products').then((res) => {
      setProducts(res.data);
      if (res.data.length > 0) {
        setSelectedProductId(res.data[0].id);
      }
    });

    api.get('/api/marketing/guide').then((res) => {
      setGuideItems(res.data);
    });
  }, []);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedProductId) return;
    setLoading(true);
    try {
      const res = await api.post('/api/marketing/generate', {
        product_id: selectedProductId,
        custom_angle: angle,
      });
      setContent(res.data);
    } catch (err: any) {
      console.error('Marketing generation error:', err);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string, fieldName: string) => {
    navigator.clipboard.writeText(text);
    setCopiedField(fieldName);
    setTimeout(() => setCopiedField(null), 2000);
  };

  const toggleGuideStep = (id: string) => {
    setGuideItems((prev) =>
      prev.map((item) => (item.id === id ? { ...item, is_completed: !item.is_completed } : item))
    );
  };

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center space-x-2 text-emerald-600 font-semibold text-sm mb-1">
            <Video className="w-4 h-4" />
            <span>Module 5 • Marketing Studio & Media-Buying</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-900">Scripts Vidéo, Ad Copies & Guide Media-Buying</h1>
          <p className="text-sm text-slate-500 mt-1">
            Générez des scripts TikTok/Reels en 4 temps (Hook, Problème, Solution, CTA) et gérez votre checklist Pixel.
          </p>
        </div>

        {/* Product selector */}
        <div className="flex items-center space-x-2">
          <label className="text-xs font-semibold text-slate-600 whitespace-nowrap">Produit :</label>
          <select
            value={selectedProductId}
            onChange={(e) => setSelectedProductId(parseInt(e.target.value))}
            className="px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-emerald-500"
          >
            {products.map((p) => (
              <option key={p.id} value={p.id}>
                {p.title}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Form & Content */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
            <h2 className="text-lg font-bold text-slate-900 flex items-center space-x-2">
              <Sparkles className="w-5 h-5 text-emerald-600" />
              <span>Générateur IA Créatives & Copywriting</span>
            </h2>

            <form onSubmit={handleGenerate} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Angle ou Axe de Vente Spécifique (Optionnel)
                </label>
                <input
                  type="text"
                  value={angle}
                  onChange={(e) => setAngle(e.target.value)}
                  placeholder="Ex: Anti-douleur immédiat, Écologie, Idée cadeau originale..."
                  className="w-full px-4 py-2.5 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl text-sm transition shadow flex items-center justify-center space-x-2"
              >
                {loading ? (
                  <span>Génération des créatives en cours...</span>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    <span>Générer Scripts & Textes Pubs</span>
                  </>
                )}
              </button>
            </form>
          </div>

          {/* Generated Result View */}
          {loading ? (
            <SkeletonCard />
          ) : content ? (
            <div className="space-y-6">
              {/* 4-Part Video Script */}
              <div className="bg-slate-900 text-white rounded-2xl p-6 shadow-xl space-y-6">
                <div className="flex justify-between items-center border-b border-slate-800 pb-4">
                  <h3 className="font-bold text-lg text-emerald-400 flex items-center space-x-2">
                    <Video className="w-5 h-5" />
                    <span>Script Vidéo TikTok / Reels / Shorts (4 Parties)</span>
                  </h3>
                  <button
                    onClick={() =>
                      copyToClipboard(
                        `HOOK: ${content.video_script.hook}\n\nPROBLÈME: ${content.video_script.problem}\n\nSOLUTION: ${content.video_script.solution}\n\nCTA: ${content.video_script.cta}`,
                        'script'
                      )
                    }
                    className="flex items-center space-x-1 text-xs text-slate-300 hover:text-white px-3 py-1.5 bg-slate-800 rounded-lg"
                  >
                    {copiedField === 'script' ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>{copiedField === 'script' ? 'Copié !' : 'Copier Script'}</span>
                  </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-slate-800/80 p-4 rounded-xl border border-slate-700/60">
                    <span className="text-xs font-bold text-amber-400 uppercase tracking-wider block mb-1">
                      1. Hook (3 premières secondes)
                    </span>
                    <p className="text-sm text-slate-200">{content.video_script.hook}</p>
                  </div>

                  <div className="bg-slate-800/80 p-4 rounded-xl border border-slate-700/60">
                    <span className="text-xs font-bold text-rose-400 uppercase tracking-wider block mb-1">
                      2. Le Problème Client
                    </span>
                    <p className="text-sm text-slate-200">{content.video_script.problem}</p>
                  </div>

                  <div className="bg-slate-800/80 p-4 rounded-xl border border-slate-700/60">
                    <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider block mb-1">
                      3. La Solution Produit
                    </span>
                    <p className="text-sm text-slate-200">{content.video_script.solution}</p>
                  </div>

                  <div className="bg-slate-800/80 p-4 rounded-xl border border-slate-700/60">
                    <span className="text-xs font-bold text-sky-400 uppercase tracking-wider block mb-1">
                      4. CTA (Appel à l'Action)
                    </span>
                    <p className="text-sm text-slate-200">{content.video_script.cta}</p>
                  </div>
                </div>
              </div>

              {/* Ad Copies */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white rounded-2xl p-6 border border-slate-200 space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-xs font-extrabold text-blue-600 bg-blue-50 px-2.5 py-1 rounded-lg">
                      Meta Ads Copy
                    </span>
                    <button
                      onClick={() => copyToClipboard(content.ad_copies.meta, 'meta')}
                      className="p-1.5 text-slate-400 hover:text-slate-600"
                    >
                      {copiedField === 'meta' ? <Check className="w-4 h-4 text-emerald-600" /> : <Copy className="w-4 h-4" />}
                    </button>
                  </div>
                  <p className="text-xs text-slate-700 whitespace-pre-line leading-relaxed">
                    {content.ad_copies.meta}
                  </p>
                </div>

                <div className="bg-white rounded-2xl p-6 border border-slate-200 space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-xs font-extrabold text-slate-900 bg-slate-100 px-2.5 py-1 rounded-lg">
                      TikTok Ads Copy
                    </span>
                    <button
                      onClick={() => copyToClipboard(content.ad_copies.tiktok, 'tiktok')}
                      className="p-1.5 text-slate-400 hover:text-slate-600"
                    >
                      {copiedField === 'tiktok' ? <Check className="w-4 h-4 text-emerald-600" /> : <Copy className="w-4 h-4" />}
                    </button>
                  </div>
                  <p className="text-xs text-slate-700 whitespace-pre-line leading-relaxed">
                    {content.ad_copies.tiktok}
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-slate-100 border border-slate-200 rounded-2xl p-8 text-center text-slate-500 text-sm">
              Sélectionnez un produit et cliquez sur "Générer" pour obtenir vos scripts et textes publicitaires.
            </div>
          )}
        </div>

        {/* Right Interactive Guide Media Buying */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm h-fit space-y-6">
          <div className="border-b pb-4">
            <h2 className="text-lg font-bold text-slate-900 flex items-center space-x-2">
              <Megaphone className="w-5 h-5 text-emerald-600" />
              <span>Guide Media-Buying Pas-à-Pas</span>
            </h2>
            <p className="text-xs text-slate-500 mt-1">
              Checklist interactive de configuration des Pixels & Business Manager.
            </p>
          </div>

          <div className="space-y-4">
            {guideItems.map((item) => (
              <div
                key={item.id}
                onClick={() => toggleGuideStep(item.id)}
                className={`p-4 rounded-xl border cursor-pointer transition ${
                  item.is_completed
                    ? 'bg-emerald-50/60 border-emerald-300 text-slate-800'
                    : 'bg-slate-50 border-slate-200 text-slate-700 hover:border-slate-300'
                }`}
              >
                <div className="flex items-start space-x-3">
                  <input
                    type="checkbox"
                    checked={item.is_completed}
                    onChange={() => {}}
                    className="mt-1 rounded text-emerald-600 focus:ring-emerald-500 w-4 h-4"
                  />
                  <div>
                    <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-600 block">
                      {item.step}
                    </span>
                    <h4 className="text-sm font-bold text-slate-900">{item.title}</h4>
                    <p className="text-xs text-slate-500 mt-1 leading-relaxed">{item.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
