'use client';

import React, { useState, useEffect } from 'react';
import {
  TrendingUp,
  Plus,
  Search,
  Filter,
  ShieldAlert,
  Star,
  DollarSign,
  ChevronRight,
  AlertTriangle,
  X
} from 'lucide-react';
import api from '@/lib/api';
import LoadingSpinner, { SkeletonCard } from '@/components/LoadingSpinner';

export default function ProductsPage() {
  const [products, setProducts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [filterCategory, setFilterCategory] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  // Form state
  const [formData, setFormData] = useState({
    title: '',
    category: 'Santé & Bien-être',
    description: '',
    selling_price: 39.99,
    estimated_cogs: 8.5,
    estimated_shipping: 3.5,
    estimated_cac: 10.0,
    search_volume: 12000,
    competition_level: 'Medium',
    complexity_score: 1,
    fragility_score: 1,
    customer_rating: 4.8,
  });

  const fetchProducts = async () => {
    setLoading(true);
    try {
      let url = '/api/products';
      if (filterCategory) {
        url += `?category=${encodeURIComponent(filterCategory)}`;
      }
      const res = await api.get(url);
      setProducts(res.data);
    } catch (err) {
      console.error('Error fetching products:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, [filterCategory]);

  const handleCreateProduct = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/api/products', formData);
      setShowModal(false);
      fetchProducts();
    } catch (err) {
      console.error('Error creating product:', err);
    }
  };

  const getScoreBadge = (score: number) => {
    if (score >= 70) {
      return 'bg-emerald-500/10 text-emerald-600 border-emerald-500/30';
    } else if (score >= 50) {
      return 'bg-amber-500/10 text-amber-600 border-amber-500/30';
    } else {
      return 'bg-rose-500/10 text-rose-600 border-rose-500/30';
    }
  };

  const filteredProducts = products.filter((p) =>
    p.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    p.category.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center space-x-2 text-emerald-600 font-semibold text-sm mb-1">
            <TrendingUp className="w-4 h-4" />
            <span>Module 1 • Product Hunting</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-900">Repérage Produits & Filtres Qualité</h1>
          <p className="text-sm text-slate-500 mt-1">
            Évaluez la viabilité automatique (0-100) et filtrez les risques avant d'investir du stock.
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center justify-center space-x-2 px-5 py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded-xl shadow-lg shadow-emerald-900/20 transition"
        >
          <Plus className="w-5 h-5" />
          <span>Nouveau Produit</span>
        </button>
      </div>

      {/* Filters & Search */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="w-5 h-5 absolute left-3.5 top-3.5 text-slate-400" />
          <input
            type="text"
            placeholder="Rechercher un produit ou une catégorie..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-11 pr-4 py-3 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
          />
        </div>
        <div className="flex items-center space-x-2">
          <Filter className="w-4 h-4 text-slate-400" />
          <select
            value={filterCategory}
            onChange={(e) => setFilterCategory(e.target.value)}
            className="px-4 py-3 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
          >
            <option value="">Toutes les catégories</option>
            <option value="Santé & Bien-être">Santé & Bien-être</option>
            <option value="Cuisine & Sport">Cuisine & Sport</option>
            <option value="Électronique & Animalerie">Électronique & Animalerie</option>
          </select>
        </div>
      </div>

      {/* Products Grid / Table */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
        </div>
      ) : filteredProducts.length === 0 ? (
        <div className="bg-white rounded-2xl p-12 text-center border border-slate-200">
          <AlertTriangle className="w-12 h-12 text-amber-500 mx-auto mb-3" />
          <h3 className="text-lg font-bold text-slate-800">Aucun produit trouvé</h3>
          <p className="text-sm text-slate-500 mt-1">
            Commencez par ajouter un produit ou réinitialisez les filtres.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProducts.map((p) => {
            const marginEuro = (p.selling_price - (p.estimated_cogs + p.estimated_shipping)).toFixed(2);
            return (
              <div
                key={p.id}
                className="bg-white rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition p-6 flex flex-col justify-between space-y-5"
              >
                <div>
                  <div className="flex justify-between items-start gap-2 mb-3">
                    <span className="text-xs font-semibold px-2.5 py-1 bg-slate-100 text-slate-600 rounded-lg">
                      {p.category}
                    </span>
                    <div
                      className={`px-3 py-1 rounded-full text-xs font-extrabold border ${getScoreBadge(
                        p.viability_score
                      )}`}
                    >
                      Score Viabilité : {p.viability_score}/100
                    </div>
                  </div>

                  <h3 className="text-lg font-bold text-slate-900 leading-snug">{p.title}</h3>
                  <p className="text-xs text-slate-500 line-clamp-2 mt-1">{p.description}</p>
                </div>

                {/* Financial Overview */}
                <div className="bg-slate-50 p-4 rounded-xl grid grid-cols-2 gap-3 text-xs">
                  <div>
                    <span className="text-slate-400 block">Prix Vente</span>
                    <span className="font-bold text-slate-800 text-sm">{p.selling_price} €</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block">Marge Est.</span>
                    <span className="font-bold text-emerald-600 text-sm">+{marginEuro} €</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block">Volume Rech.</span>
                    <span className="font-medium text-slate-700">{p.search_volume} / mois</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block">Concurrence</span>
                    <span className="font-medium text-slate-700">{p.competition_level}</span>
                  </div>
                </div>

                {/* Risk Indicators */}
                <div className="flex items-center justify-between text-xs pt-2 border-t border-slate-100">
                  <div className="flex items-center space-x-1 text-slate-600">
                    <ShieldAlert className="w-4 h-4 text-amber-500" />
                    <span>
                      Complexité: <strong>{p.complexity_score}/5</strong>
                    </span>
                  </div>
                  <div className="flex items-center space-x-1 text-slate-600">
                    <span>
                      Fragilité: <strong>{p.fragility_score}/5</strong>
                    </span>
                  </div>
                  <div className="flex items-center space-x-1 text-amber-500 font-semibold">
                    <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-400" />
                    <span>{p.customer_rating}</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Creation Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6 md:p-8 shadow-2xl space-y-6">
            <div className="flex justify-between items-center border-b pb-4">
              <h2 className="text-xl font-bold text-slate-900">Ajouter un Produit à Évaluer</h2>
              <button
                onClick={() => setShowModal(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateProduct} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Titre Produit</label>
                  <input
                    type="text"
                    required
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Catégorie</label>
                  <input
                    type="text"
                    required
                    value={formData.category}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg text-sm"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Description</label>
                <textarea
                  rows={2}
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg text-sm"
                />
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Prix Vente (€)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.selling_price}
                    onChange={(e) => setFormData({ ...formData, selling_price: parseFloat(e.target.value) || 0 })}
                    className="w-full px-3 py-2 border rounded-lg text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">COGS / Achat (€)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.estimated_cogs}
                    onChange={(e) => setFormData({ ...formData, estimated_cogs: parseFloat(e.target.value) || 0 })}
                    className="w-full px-3 py-2 border rounded-lg text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Frais Port Est. (€)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.estimated_shipping}
                    onChange={(e) =>
                      setFormData({ ...formData, estimated_shipping: parseFloat(e.target.value) || 0 })
                    }
                    className="w-full px-3 py-2 border rounded-lg text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">CAC Pub Est. (€)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.estimated_cac}
                    onChange={(e) => setFormData({ ...formData, estimated_cac: parseFloat(e.target.value) || 0 })}
                    className="w-full px-3 py-2 border rounded-lg text-sm"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Vol. Recherche / mois</label>
                  <input
                    type="number"
                    value={formData.search_volume}
                    onChange={(e) => setFormData({ ...formData, search_volume: parseInt(e.target.value) || 0 })}
                    className="w-full px-3 py-2 border rounded-lg text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Niveau Concurrence</label>
                  <select
                    value={formData.competition_level}
                    onChange={(e) => setFormData({ ...formData, competition_level: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg text-sm"
                  >
                    <option value="Low">Faible (Low)</option>
                    <option value="Medium">Moyenne (Medium)</option>
                    <option value="High">Élevée (High)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Note Client Moyenne</label>
                  <input
                    type="number"
                    step="0.1"
                    max="5.0"
                    min="1.0"
                    value={formData.customer_rating}
                    onChange={(e) => setFormData({ ...formData, customer_rating: parseFloat(e.target.value) || 4.5 })}
                    className="w-full px-3 py-2 border rounded-lg text-sm"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Complexité (1 à 5)</label>
                  <input
                    type="number"
                    min="1"
                    max="5"
                    value={formData.complexity_score}
                    onChange={(e) => setFormData({ ...formData, complexity_score: parseInt(e.target.value) || 1 })}
                    className="w-full px-3 py-2 border rounded-lg text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Fragilité (1 à 5)</label>
                  <input
                    type="number"
                    min="1"
                    max="5"
                    value={formData.fragility_score}
                    onChange={(e) => setFormData({ ...formData, fragility_score: parseInt(e.target.value) || 1 })}
                    className="w-full px-3 py-2 border rounded-lg text-sm"
                  />
                </div>
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
                  className="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-sm font-semibold shadow"
                >
                  Calculer Viabilité & Enregistrer
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
