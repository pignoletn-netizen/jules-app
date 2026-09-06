"use client";

import Link from "next/link";
import { Trophy, Compass, Ticket } from "lucide-react";

export default function HeaderNav() {
  return (
    <header className="bg-slate-900 border-b border-slate-800 text-white sticky top-0 z-50 shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2 font-bold text-xl text-amber-400 hover:text-amber-300 transition">
          <Trophy className="h-6 w-6 text-amber-400" />
          <span>Turf<span className="text-emerald-400">Prono</span> PMU</span>
        </Link>

        <nav className="flex items-center space-x-2 sm:space-x-4">
          <Link
            href="/"
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium hover:bg-slate-800 text-slate-200 hover:text-white transition"
          >
            <Compass className="h-4 w-4 text-emerald-400" />
            <span>Courses du jour</span>
          </Link>
          <Link
            href="/pmu-recap"
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium bg-emerald-600 hover:bg-emerald-500 text-white shadow-sm transition"
          >
            <Ticket className="h-4 w-4" />
            <span>Récap Mises PMU.fr</span>
          </Link>
        </nav>
      </div>
    </header>
  );
}
