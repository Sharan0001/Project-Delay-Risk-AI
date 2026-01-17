/**
 * App Component - Dark Theme
 * 
 * Root component with:
 * - Dark themed navigation layout
 * - Route definitions
 * - Lazy loading with Suspense
 */

import { lazy, Suspense } from 'react';
import { Routes, Route, NavLink } from 'react-router-dom';
import {
    LayoutDashboard,
    BarChart2,
    History,
    Brain,
    GitBranch
} from 'lucide-react';
import { RouteLoadingFallback } from './components/common';
import { APP_CONFIG } from './config';

// Lazy load pages for route-level code splitting
const Dashboard = lazy(() => import('./pages/Dashboard').then(m => ({ default: m.Dashboard })));
const Analysis = lazy(() => import('./pages/Analysis').then(m => ({ default: m.Analysis })));
const HistoryPage = lazy(() => import('./pages/History').then(m => ({ default: m.History })));

export default function App() {
    return (
        <div className="min-h-screen bg-dark-bg flex flex-col">
            {/* Top Navigation Bar */}
            <nav className="bg-dark-100 border-b border-dark-400/50 sticky top-0 z-50 backdrop-blur-sm">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between h-16">
                        {/* Logo */}
                        <div className="flex items-center gap-3">
                            <div className="w-9 h-9 bg-gradient-to-br from-primary-500 to-primary-700 rounded-xl flex items-center justify-center shadow-glow-sm">
                                <Brain className="w-5 h-5 text-white" />
                            </div>
                            <div>
                                <span className="font-bold text-light-100">{APP_CONFIG.name}</span>
                                <span className="text-xs text-light-400 ml-2">v{APP_CONFIG.version}</span>
                            </div>
                        </div>

                        {/* Navigation Links */}
                        <div className="flex items-center gap-1">
                            <NavItem to="/" icon={LayoutDashboard} label="Dashboard" />
                            <NavItem to="/analysis" icon={BarChart2} label="Analysis" />
                            <NavItem to="/history" icon={History} label="History" />
                        </div>

                        {/* GitHub Link */}
                        <a
                            href="https://github.com"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="p-2 text-light-400 hover:text-light-200 hover:bg-dark-300 rounded-lg transition-all"
                        >
                            <GitBranch className="w-5 h-5" />
                        </a>
                    </div>
                </div>
            </nav>

            {/* Main Content with Suspense for route transitions */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 w-full">
                <Suspense fallback={<RouteLoadingFallback />}>
                    <Routes>
                        <Route path="/" element={<Dashboard />} />
                        <Route path="/analysis" element={<Analysis />} />
                        <Route path="/history" element={<HistoryPage />} />
                    </Routes>
                </Suspense>
            </main>

            {/* Footer */}
            <footer className="border-t border-dark-400/30">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                    <p className="text-center text-sm text-light-400">
                        Project Delay Risk AI — Decision Intelligence System
                    </p>
                </div>
            </footer>
        </div>
    );
}

// Navigation item component
function NavItem({
    to,
    icon: Icon,
    label
}: {
    to: string;
    icon: typeof LayoutDashboard;
    label: string;
}) {
    return (
        <NavLink
            to={to}
            className={({ isActive }) =>
                `flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${isActive
                    ? 'bg-primary-500/15 text-primary-400 shadow-glow-sm'
                    : 'text-light-300 hover:bg-dark-300 hover:text-light-100'
                }`
            }
        >
            <Icon className="w-4 h-4" />
            {label}
        </NavLink>
    );
}
