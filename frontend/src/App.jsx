import React, { useEffect, useState, useRef } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation, useNavigate } from 'react-router-dom';
import {
  Bot, GraduationCap, LayoutDashboard, ChevronRight,
  Upload, Sparkles, MessageSquare, FileText, Users, BookOpen, Award,
  Stethoscope, Terminal, Scale, Leaf, Pickaxe, TrendingUp, Microscope, Building, Globe, Book, Calculator,
  LogOut, User as UserIcon, Settings, ChevronDown, Sun, Moon
} from 'lucide-react';
import useScrollReveal from './hooks/useScrollReveal';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ThemeProvider, useTheme } from './context/ThemeContext';
import ChatInterface from './components/chat/ChatInterface';
import FilieresCatalog from './components/filieres/FilieresCatalog';
import Auth from './components/auth/Auth';
import StudentDashboard from './components/dashboard/StudentDashboard';
import AdminDashboard from './components/dashboard/AdminDashboard';
import './index.css';

// ─── Background Orbs ─────────────────────────────────────────────
const BackgroundOrbs = () => (
  <div className="bg-orbs">
    <div className="bg-orb bg-orb-1" />
    <div className="bg-orb bg-orb-2" />
    <div className="bg-orb bg-orb-3" />
  </div>
);

// ─── Noise Overlay ───────────────────────────────────────────────
const NoiseOverlay = () => <div className="noise-overlay" />;

// ─── Navbar ──────────────────────────────────────────────────────
const Navbar = () => {
  const [scrolled, setScrolled] = useState(false);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { user, isAuthenticated, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const isActive = (path) => location.pathname === path;

  const getInitials = () => {
    if (!user?.full_name) return user?.email?.charAt(0)?.toUpperCase() || 'U';
    return user.full_name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  };

  const handleLogout = () => {
    logout();
    setDropdownOpen(false);
    navigate('/');
  };

  return (
    <nav className={`navbar ${scrolled ? 'scrolled' : ''}`}>
      <div className="container navbar-inner">
        <Link to="/" className="navbar-logo">
          Edu<span className="gradient-text">Bot</span>
        </Link>
        <div className="navbar-links">
          <button className="theme-toggle" onClick={toggleTheme} title={theme === 'dark' ? 'Mode clair' : 'Mode sombre'}>
            {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
          </button>
          <Link to="/chat" className={`navbar-link ${isActive('/chat') ? 'active' : ''}`}>
            Chat IA
          </Link>
          <Link to="/filieres" className={`navbar-link ${isActive('/filieres') ? 'active' : ''}`}>
            Filières
          </Link>

          {isAuthenticated ? (
            <div className="navbar-user" ref={dropdownRef}>
              <button
                className="navbar-avatar-btn"
                onClick={() => setDropdownOpen(!dropdownOpen)}
              >
                <div className="navbar-avatar">{getInitials()}</div>
                <ChevronDown size={14} style={{ color: 'var(--text-secondary)', transition: 'transform 0.2s', transform: dropdownOpen ? 'rotate(180deg)' : 'none' }} />
              </button>
              {dropdownOpen && (
                <div className="navbar-dropdown">
                  <div className="navbar-dropdown-header">
                    <div className="navbar-avatar" style={{ width: '36px', height: '36px', fontSize: '0.85rem' }}>{getInitials()}</div>
                    <div>
                      <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{user.full_name || 'Utilisateur'}</div>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{user.email}</div>
                    </div>
                  </div>
                  <div className="navbar-dropdown-divider" />
                  <Link to="/dashboard" className="navbar-dropdown-item" onClick={() => setDropdownOpen(false)}>
                    <LayoutDashboard size={16} /> Mon espace
                  </Link>
                  <Link to="/chat" className="navbar-dropdown-item" onClick={() => setDropdownOpen(false)}>
                    <MessageSquare size={16} /> Chat IA
                  </Link>
                  <div className="navbar-dropdown-divider" />
                  <button className="navbar-dropdown-item logout" onClick={handleLogout}>
                    <LogOut size={16} /> Déconnexion
                  </button>
                </div>
              )}
            </div>
          ) : (
            <>
              <Link to="/auth" className={`navbar-link ${isActive('/auth') ? 'active' : ''}`}>
                Connexion
              </Link>
              <Link to="/chat" className="btn btn-primary" style={{ padding: '0.5rem 1.25rem', fontSize: '0.85rem' }}>
                <Sparkles size={14} /> Commencer
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
};

// ─── Animated Modules Showcase (infinite scroll) ─────────────────
const univData = [
  { icon: Stethoscope, name: 'Médecine Générale', university: 'UGANC - Conakry' },
  { icon: Terminal, name: 'Génie Informatique', university: 'UGLCS - Sonfonia' },
  { icon: Scale, name: 'Droit des Affaires', university: 'Univ. de Sonfonia' },
  { icon: Leaf, name: 'Agronomie', university: 'ISAF - Faranah' },
  { icon: Pickaxe, name: 'Mines et Géologie', university: 'ISMGB - Boké' },
  { icon: TrendingUp, name: 'Sciences Économiques', university: 'UGLCS - Sonfonia' },
  { icon: Building, name: 'Génie Civil', university: 'UGANC - Conakry' },
  { icon: Users, name: 'Sociologie', university: 'Univ. de Sonfonia' },
  { icon: Book, name: 'Lettres Modernes', university: 'UGANC - Conakry' },
];

const ModulesShowcase = () => (
  <section className="modules-showcase">
    <div className="container" style={{ marginBottom: '3rem' }}>
      <h2 className="features-section-title reveal-up">
        Explorez nos <span className="gradient-text">Formations</span>
      </h2>
      <p className="features-section-subtitle reveal-up delay-100">
        Des filières variées à travers les meilleures universités de Guinée
      </p>
    </div>

    {/* Univ Track */}
    <div style={{ overflow: 'hidden' }}>
      <div className="modules-track" style={{ animationDuration: '40s' }}>
        {[...univData, ...univData].map((mod, i) => {
          const Icon = mod.icon;
          return (
            <div className="module-card" key={`univ-${i}`}>
              <div className="module-emoji"><Icon size={40} color="var(--accent-1)" /></div>
              <div className="module-name">{mod.name}</div>
              <div className="module-university">{mod.university}</div>
            </div>
          );
        })}
      </div>
    </div>
  </section>
);

// ─── Stats Section ───────────────────────────────────────────────
const StatsSection = () => (
  <section className="stats-section container">
    <div className="stats-grid">
      <div className="stat-item reveal-up">
        <div className="stat-number gradient-text">12+</div>
        <div className="stat-label">Universités partenaires</div>
      </div>
      <div className="stat-item reveal-up delay-100">
        <div className="stat-number gradient-text">150+</div>
        <div className="stat-label">Filières disponibles</div>
      </div>
      <div className="stat-item reveal-up delay-200">
        <div className="stat-number gradient-text">98%</div>
        <div className="stat-label">Satisfaction étudiante</div>
      </div>
      <div className="stat-item reveal-up delay-300">
        <div className="stat-number gradient-text">24/7</div>
        <div className="stat-label">Disponibilité IA</div>
      </div>
    </div>
  </section>
);

// ─── Home Page ───────────────────────────────────────────────────
const Home = () => (
  <>
    {/* Hero */}
    <section className="hero-section">
      <div className="hero-badge reveal-up">
        <div className="hero-badge-dot" />
        Intelligence Artificielle d'Orientation
      </div>

      <h1 className="hero-title reveal-up delay-100">
        L'orientation intelligente{' '}
        <span className="gradient-text">réinventée.</span>
      </h1>

      <p className="hero-subtitle reveal-up delay-200">
        Découvrez votre voie idéale grâce à notre IA d'orientation avancée.
        Analysez vos notes, explorez les filières, et trouvez votre avenir.
      </p>

      <div className="hero-actions reveal-up delay-300">
        <Link to="/chat" className="btn btn-primary">
          Commencer maintenant <ChevronRight size={18} />
        </Link>
        <Link to="/filieres" className="btn btn-secondary">
          Explorer les filières
        </Link>
      </div>
    </section>

    {/* Features */}
    <section className="features-section container">
      <h2 className="features-section-title reveal-up">
        Pourquoi choisir <span className="gradient-text">EduBot</span> ?
      </h2>
      <p className="features-section-subtitle reveal-up delay-100">
        Une plateforme complète pour guider votre parcours académique en Guinée.
      </p>

      <div className="features-grid">
        <div className="card-premium reveal-up delay-200">
          <div className="feature-icon-wrap violet">
            <MessageSquare size={28} color="var(--accent-1)" />
          </div>
          <h3 className="feature-title">Assistant IA Intelligent</h3>
          <p className="feature-description">
            Discutez avec notre chatbot intelligent. Il analyse votre profil et vos intérêts pour des recommandations personnalisées.
          </p>
        </div>

        <div className="card-premium reveal-up delay-300">
          <div className="feature-icon-wrap teal">
            <GraduationCap size={28} color="var(--accent-2)" />
          </div>
          <h3 className="feature-title">Catalogue Complet</h3>
          <p className="feature-description">
            Parcourez des centaines de filières avec des fiches détaillées, les débouchés professionnels et les taux d'insertion.
          </p>
        </div>

        <div className="card-premium reveal-up delay-400">
          <div className="feature-icon-wrap pink">
            <FileText size={28} color="var(--accent-3)" />
          </div>
          <h3 className="feature-title">Analyse de Notes</h3>
          <p className="feature-description">
            Importez votre relevé de notes en PDF. Notre IA extrait vos résultats et identifie vos points forts automatiquement.
          </p>
        </div>
      </div>
    </section>

    {/* Animated Modules */}
    <ModulesShowcase />

    {/* Stats */}
    <StatsSection />

    {/* CTA */}
    <section className="container reveal-up" style={{ textAlign: 'center', padding: '4rem 0 6rem' }}>
      <h2 style={{ fontSize: 'clamp(1.8rem, 3vw, 2.5rem)', fontWeight: 800, marginBottom: '1rem' }}>
        Prêt à trouver votre <span className="gradient-text">voie</span> ?
      </h2>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem', maxWidth: '450px', margin: '0 auto 2rem' }}>
        Commencez gratuitement et laissez l'IA vous guider vers la filière parfaite.
      </p>
      <Link to="/chat" className="btn btn-primary" style={{ fontSize: '1.05rem', padding: '1rem 2.5rem' }}>
        <Sparkles size={18} /> Démarrer le Chat IA
      </Link>
    </section>

    {/* Footer */}
    <footer className="footer">
      <div className="container">
        <p>© 2026 EduBot — Plateforme d'Orientation Académique en Guinée</p>
      </div>
    </footer>
  </>
);

// ─── Dashboard Router ──────────────────────────────────────────────
const DashboardRouter = () => {
  const { user, isAuthenticated, isLoading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      navigate('/auth');
    }
  }, [isLoading, isAuthenticated, navigate]);

  if (isLoading || !isAuthenticated) return null;

  return user.role === 'admin' ? <AdminDashboard /> : <StudentDashboard />;
};

// ─── App Content (Router) ────────────────────────────────────────
const AppContent = () => {
  useScrollReveal();
  const location = useLocation();

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [location.pathname]);

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <BackgroundOrbs />
      <NoiseOverlay />
      <Navbar />
      <div style={{ flex: 1 }}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/chat" element={<ChatInterface />} />
          <Route path="/filieres" element={<FilieresCatalog />} />
          <Route path="/auth" element={<Auth />} />
          <Route path="/dashboard" element={<DashboardRouter />} />
        </Routes>
      </div>
    </div>
  );
};

// ─── App Root ────────────────────────────────────────────────────────
const App = () => (
  <Router>
    <ThemeProvider>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </ThemeProvider>
  </Router>
);

export default App;
