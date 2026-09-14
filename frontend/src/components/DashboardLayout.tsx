'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import {
  TrendingUp,
  Truck,
  Globe,
  ShieldCheck,
  Video,
  MessageSquare,
  DollarSign,
  LogOut,
  User,
  Sparkles,
  Menu,
  X
} from 'lucide-react';
import api from '@/lib/api';

const navItems = [
  { href: '/products', label: '1. Repérage Produits', icon: TrendingUp },
  { href: '/suppliers', label: '2. Fournisseurs Fiables', icon: Truck },
  { href: '/landing-builder', label: '3. MVB & Landing Page', icon: Globe },
  { href: '/compliance', label: '4. Conformité UE', icon: ShieldCheck },
  { href: '/marketing', label: '5. Marketing IA', icon: Video },
  { href: '/sav', label: '6. SAV Automatique', icon: MessageSquare },
  { href: '/financials', label: '7. Dashboard Financier', icon: DollarSign },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    if (pathname.startsWith('/p/') || pathname === '/login' || pathname === '/register') {
      return;
    }

    const token = localStorage.getItem('mvb_token');
    if (!token) {
      router.push('/login');
      return;
    }

    api.get('/api/auth/me')
      .then((res) => setCurrentUser(res.data))
      .catch(() => {
        localStorage.removeItem('mvb_token');
        router.push('/login');
      });
  }, [pathname, router]);

  const handleLogout = () => {
    localStorage.removeItem('mvb_token');
    router.push('/login');
  };

  if (pathname.startsWith('/p/') || pathname === '/login' || pathname === '/register') {
    return <>{children}</>;
  }

  return (
    <div className="min-h-screen flex bg-slate-50 text-slate-800">
      {/* Sidebar Desktop */}
      <aside className="hidden md:flex flex-col w-72 bg-slate-900 text-slate-200 border-r border-slate-800">
        <div className="p-6 border-b border-slate-800 flex items-center space-x-3">
          <div className="p-2 bg-emerald-500 rounded-xl text-slate-900 font-extrabold">
            <Sparkles className="w-6 h-6 text-slate-950" />
          </div>
          <div>
            <h1 className="font-bold text-lg text-white leading-none">MVB Platform</h1>
            <p className="text-xs text-emerald-400 mt-1 font-medium">Mini-Market Validation</p>
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-1.5 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center space-x-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-900/30 font-semibold'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
                }`}
              >
                <Icon className={`w-5 h-5 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        {currentUser && (
          <div className="p-4 border-t border-slate-800 bg-slate-950/50">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-9 h-9 rounded-full bg-emerald-600/20 text-emerald-400 flex items-center justify-center font-bold text-sm border border-emerald-500/30">
                  <User className="w-4 h-4" />
                </div>
                <div className="overflow-hidden">
                  <p className="text-sm font-semibold text-white truncate">{currentUser.full_name || 'Utilisateur'}</p>
                  <p className="text-xs text-slate-400 truncate">{currentUser.email}</p>
                </div>
              </div>
              <button
                onClick={handleLogout}
                title="Déconnexion"
                className="p-2 text-slate-400 hover:text-red-400 hover:bg-slate-800 rounded-lg transition"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </aside>

      {/* Main Container */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Header Mobile */}
        <header className="md:hidden flex items-center justify-between p-4 bg-slate-900 text-white border-b border-slate-800">
          <div className="flex items-center space-x-2">
            <Sparkles className="w-6 h-6 text-emerald-400" />
            <span className="font-bold text-lg">MVB Platform</span>
          </div>
          <button onClick={() => setMobileMenuOpen(!mobileMenuOpen)} className="p-2 text-slate-300">
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </header>

        {/* Mobile Navigation Drawer */}
        {mobileMenuOpen && (
          <div className="md:hidden bg-slate-900 border-b border-slate-800 p-4 space-y-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className="flex items-center space-x-3 px-4 py-3 rounded-lg text-slate-300 hover:bg-slate-800 text-sm"
                >
                  <Icon className="w-5 h-5 text-emerald-400" />
                  <span>{item.label}</span>
                </Link>
              );
            })}
            <button
              onClick={handleLogout}
              className="w-full flex items-center space-x-3 px-4 py-3 text-red-400 hover:bg-slate-800 rounded-lg text-sm text-left"
            >
              <LogOut className="w-5 h-5" />
              <span>Se déconnecter</span>
            </button>
          </div>
        )}

        {/* Page Content */}
        <main className="flex-1 p-6 md:p-8 overflow-y-auto max-w-7xl mx-auto w-full">
          {children}
        </main>
      </div>
    </div>
  );
}
