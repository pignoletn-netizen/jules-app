'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  Globe,
  Sparkles,
  MousePointerClick,
  Mail,
  ExternalLink,
  Plus,
  BarChart3,
  CheckCircle2,
  HelpCircle,
  X
} from 'lucide-react';
import api from '@/lib/api';
import LoadingSpinner, { SkeletonCard } from '@/components/LoadingSpinner';

export default function LandingBuilderPage() {
  const [landings, setLandings] = useState<any[]>([]);
  const [products, setProducts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [showModal, setShowModal] = useState(false);

  const [productId, setProductId] = useState<number>(0);
  const [slug, setSlug] = useState('');
  const [instructions, setInstructions] = useState('');

  const fetchData = async () => {
    setLoading(true);
    try {
      const [prodRes, landRes] = await Promise.all([
        api.get('/api/products'),
        api.get('/api/landing-pages'),
      ]);
      setProducts(prodRes.data);
      setLandings(landRes.data);
      if (prodRes.data.length > 0 && productId === 0) {
        setProductId(prodRes.data[0].id);
        setSlug(prodRes.data[0].title.toLowerCase().replace(/[^a-z0-9]+/g, '-'));
      }
    } catch (err) {
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleGenerateLanding = async (e: React.FormEvent) => {
    e.preventDefault();
    setGenerating(true);
    try {
      await api.post('/api/landing-pages/generate', {
        product_id: productId,
        slug: slug,
        custom_instructions: instructions,
      });
      setShowModal(false);
      setInstructions('');
      fetchData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Erreur lors de la génération AI.');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center space-x-2 text-emerald-600 font-semibold text-sm mb-1">
            <Globe className="w-4 h-4" />
            <span>Module 3 • MVB Validation Core</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-900">Générateur Landing Page & Compteur d'Intention</h1>
          <p className="text-sm text-slate-500 mt-1">
            Générez une landing page de test via IA et mesurez l'intention d'achat réelle (clics & e-mails récoltés) avant d'acheter du stock.
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center justify-center space-x-2 px-5 py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded-xl shadow-lg shadow-emerald-900/20 transition"
        >
          <Sparkles className="w-5 h-5" />
          <span>Générer Landing Page IA</span>
        </button>
      </div>

      {/* Landing List */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <SkeletonCard />
          <SkeletonCard />
        </div>
      ) : landings.length === 0 ? (
        <div className="bg-white rounded-2xl p-12 text-center border border-slate-200">
          <Globe className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <h3 className="text-lg font-bold text-slate-800">Aucune Landing Page générée</h3>
          <p className="text-sm text-slate-500 mt-1">
            Créez votre première structure de page grâce à l'IA pour valider votre marché.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {landings.map((l) => {
            const conversionRate =
              l.click_count > 0 ? ((l.email_count / l.click_count) * 100).toFixed(1) : '0.0';
            return (
              <div
                key={l.id}
                className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm hover:shadow-md transition space-y-5"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <span className="text-xs font-semibold px-2.5 py-1 bg-emerald-50 text-emerald-700 rounded-lg border border-emerald-200">
                      /{l.slug}
                    </span>
                    <h3 className="text-lg font-bold text-slate-900 mt-2">{l.title}</h3>
                  </div>
                  <Link
                    href={`/p/${l.slug}`}
                    target="_blank"
                    className="inline-flex items-center space-x-1 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold transition"
                  >
                    <span>Voir la Page Public</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </Link>
                </div>

                <div className="bg-slate-900 text-white p-4 rounded-xl space-y-2">
                  <p className="text-xs text-emerald-400 font-semibold uppercase tracking-wider">Accroche IA</p>
                  <p className="font-bold text-base">{l.main_headline}</p>
                  <p className="text-xs text-slate-300">{l.subheadline}</p>
                </div>

                {/* Intent Stats Dashboard */}
                <div className="grid grid-cols-3 gap-3 bg-slate-50 p-4 rounded-xl text-center">
                  <div>
                    <div className="flex items-center justify-center space-x-1 text-slate-500 text-xs mb-1">
                      <MousePointerClick className="w-3.5 h-3.5" />
                      <span>Clics CTA</span>
                    </div>
                    <span className="text-xl font-extrabold text-slate-900">{l.click_count}</span>
                  </div>

                  <div>
                    <div className="flex items-center justify-center space-x-1 text-slate-500 text-xs mb-1">
                      <Mail className="w-3.5 h-3.5" />
                      <span>E-mails Recueillis</span>
                    </div>
                    <span className="text-xl font-extrabold text-emerald-600">{l.email_count}</span>
                  </div>

                  <div>
                    <div className="flex items-center justify-center space-x-1 text-slate-500 text-xs mb-1">
                      <BarChart3 className="w-3.5 h-3.5" />
                      <span>Taux Intention</span>
                    </div>
                    <span className="text-xl font-extrabold text-slate-900">{conversionRate}%</span>
                  </div>
                </div>

                {/* Selling points preview */}
                <div>
                  <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                    Arguments de vente (Selling Points)
                  </h4>
                  <ul className="space-y-1 text-xs text-slate-600">
                    {l.selling_points?.map((sp: string, idx: number) => (
                      <li key={idx} className="flex items-start space-x-2">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 flex-shrink-0 mt-0.5" />
                        <span>{sp}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Generator Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 md:p-8 shadow-2xl space-y-6">
            <div className="flex justify-between items-center border-b pb-4">
              <h2 className="text-xl font-bold text-slate-900 flex items-center space-x-2">
                <Sparkles className="w-5 h-5 text-emerald-600" />
                <span>Générer une Landing Page IA</span>
              </h2>
              <button
                onClick={() => setShowModal(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleGenerateLanding} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Sélectionner le Produit</label>
                <select
                  value={productId}
                  onChange={(e) => {
                    const id = parseInt(e.target.value);
                    setProductId(id);
                    const selP = products.find((p) => p.id === id);
                    if (selP) {
                      setSlug(selP.title.toLowerCase().replace(/[^a-z0-9]+/g, '-'));
                    }
                  }}
                  className="w-full px-3 py-2 border rounded-lg text-sm"
                >
                  {products.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.title} ({p.category})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Slug / URL de la landing
                </label>
                <input
                  type="text"
                  required
                  value={slug}
                  onChange={(e) => setSlug(e.target.value)}
                  placeholder="mon-produit-test"
                  className="w-full px-3 py-2 border rounded-lg text-sm font-mono"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Instructions Marketing Spécifiques (Optionnel)
                </label>
                <textarea
                  rows={3}
                  value={instructions}
                  onChange={(e) => setInstructions(e.target.value)}
                  placeholder="Ex: Insister sur la livraison offerte et la garantie de 30 jours."
                  className="w-full px-3 py-2 border rounded-lg text-sm"
                />
              </div>

              <div className="flex justify-end space-x-3 pt-4 border-t">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 border rounded-lg text-slate-600 text-sm font-medium"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  disabled={generating}
                  className="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-sm font-semibold shadow flex items-center space-x-2"
                >
                  {generating ? (
                    <span>Génération par l'IA...</span>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4" />
                      <span>Lancer la Génération</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
