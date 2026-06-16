import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  GraduationCap, MapPin, ArrowRight, Search, Loader2, AlertCircle, 
  Clock, TrendingUp, Filter, X, Briefcase,
  Stethoscope, Terminal, Scale, Pickaxe, Building, Cpu, Leaf, Users, 
  BookOpen, Calculator, Globe, Microscope
} from 'lucide-react';
import { getFilieres } from '../../services/api';

const DOMAIN_CONFIG = {
  'Sante': { icon: <Stethoscope size={24} />, gradient: 'linear-gradient(135deg, #fd79a8, #e84393)', color: '#fd79a8', bgAlpha: 'rgba(253, 121, 168, 0.12)' },
  'Technologie': { icon: <Terminal size={24} />, gradient: 'linear-gradient(135deg, #6c5ce7, #a29bfe)', color: '#6c5ce7', bgAlpha: 'rgba(108, 92, 231, 0.12)' },
  'Droit': { icon: <Scale size={24} />, gradient: 'linear-gradient(135deg, #ffeaa7, #fdcb6e)', color: '#fdcb6e', bgAlpha: 'rgba(253, 203, 110, 0.12)' },
  'Ingenierie': { icon: <Pickaxe size={24} />, gradient: 'linear-gradient(135deg, #00cec9, #81ecec)', color: '#00cec9', bgAlpha: 'rgba(0, 206, 201, 0.12)' },
  'Economie': { icon: <TrendingUp size={24} />, gradient: 'linear-gradient(135deg, #0984e3, #74b9ff)', color: '#74b9ff', bgAlpha: 'rgba(116, 185, 255, 0.12)' },
  'Agriculture': { icon: <Leaf size={24} />, gradient: 'linear-gradient(135deg, #55efc4, #00b894)', color: '#55efc4', bgAlpha: 'rgba(85, 239, 196, 0.12)' },
  'Sciences Humaines': { icon: <Users size={24} />, gradient: 'linear-gradient(135deg, #e17055, #fab1a0)', color: '#fab1a0', bgAlpha: 'rgba(250, 177, 160, 0.12)' },
  'Sciences Exactes': { icon: <Calculator size={24} />, gradient: 'linear-gradient(135deg, #e056fd, #be2edd)', color: '#e056fd', bgAlpha: 'rgba(224, 86, 253, 0.12)' },
  'Finance': { icon: <Briefcase size={24} />, gradient: 'linear-gradient(135deg, #f0932b, #ffbe76)', color: '#f0932b', bgAlpha: 'rgba(240, 147, 43, 0.12)' },
  'Lettres et Communication': { icon: <Globe size={24} />, gradient: 'linear-gradient(135deg, #7ed6df, #22a6b3)', color: '#22a6b3', bgAlpha: 'rgba(126, 214, 223, 0.12)' },
  'Sante Animale': { icon: <Microscope size={24} />, gradient: 'linear-gradient(135deg, #ff7979, #eb4d4b)', color: '#eb4d4b', bgAlpha: 'rgba(255, 121, 121, 0.12)' },
  'Design et Environnement': { icon: <Building size={24} />, gradient: 'linear-gradient(135deg, #badc58, #6ab04c)', color: '#6ab04c', bgAlpha: 'rgba(186, 220, 88, 0.12)' }
};

const getConfig = (domaine) => DOMAIN_CONFIG[domaine] || { icon: <GraduationCap size={24} />, gradient: 'linear-gradient(135deg, #6c5ce7, #a29bfe)', color: '#a29bfe', bgAlpha: 'rgba(108, 92, 231, 0.12)' };

const FilieresCatalog = () => {
  const navigate = useNavigate();
  const [filieres, setFilieres] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [activeDomain, setActiveDomain] = useState('Tous');
  const [animateCards, setAnimateCards] = useState(false);

  const fetchFilieres = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getFilieres({ limit: 50 });
      const items = data?.data || data || [];
      setFilieres(Array.isArray(items) ? items : []);
    } catch (err) {
      console.error('Fetch filieres error:', err);
      setError("Impossible de charger les filieres. Verifiez que le serveur backend est en cours d'execution.");
      setFilieres([]);
    } finally {
      setLoading(false);
      setTimeout(() => setAnimateCards(true), 100);
    }
  };

  useEffect(() => {
    fetchFilieres();
  }, []);

  // Local filtering for instant results
  const filteredFilieres = useMemo(() => {
    let result = filieres;
    if (activeDomain !== 'Tous') {
      result = result.filter(f => f.domaine === activeDomain);
    }
    if (searchTerm.trim()) {
      const term = searchTerm.toLowerCase();
      result = result.filter(f =>
        (f.nom || '').toLowerCase().includes(term) ||
        (f.domaine || '').toLowerCase().includes(term) ||
        (f.description || '').toLowerCase().includes(term) ||
        (Array.isArray(f.debouches) ? f.debouches.join(' ') : (f.debouches || '')).toLowerCase().includes(term)
      );
    }
    return result;
  }, [filieres, searchTerm, activeDomain]);

  // Extract unique domains
  const domains = useMemo(() => {
    const d = [...new Set(filieres.map(f => f.domaine).filter(Boolean))];
    return ['Tous', ...d.sort()];
  }, [filieres]);

  return (
    <div className="filieres-page">
      {/* Hero Header */}
      <div className="catalog-hero">
        <div className="catalog-hero-glow" />
        <div className="catalog-hero-content">
          <div className="catalog-badge">
            <GraduationCap size={16} />
            <span>Catalogue Officiel</span>
          </div>
          <h1 className="catalog-title">
            Explorez les <span className="gradient-text">Filieres</span> de Guinee
          </h1>
          <p className="catalog-subtitle">
            Decouvrez toutes les formations universitaires disponibles, filtrez par domaine et trouvez la filiere qui vous correspond.
          </p>

          {/* Search Bar */}
          <div className="catalog-search-wrap">
            <Search size={20} className="catalog-search-icon" />
            <input
              type="text"
              placeholder="Rechercher par nom, domaine, debouches..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="catalog-search-input"
            />
            {searchTerm && (
              <button className="catalog-search-clear" onClick={() => setSearchTerm('')}>
                <X size={16} />
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Domain Filters */}
      <div className="catalog-filters">
        <div className="catalog-filters-inner">
          <Filter size={16} style={{ color: 'var(--text-muted)', flexShrink: 0 }} />
          {domains.map((domain) => (
            <button
              key={domain}
              className={`catalog-filter-chip ${activeDomain === domain ? 'active' : ''}`}
              onClick={() => { setActiveDomain(domain); setAnimateCards(false); setTimeout(() => setAnimateCards(true), 50); }}
            >
              {domain !== 'Tous' && <span style={{ marginRight: '0.25rem' }}>{getConfig(domain).icon}</span>}
              {domain}
            </button>
          ))}
        </div>
      </div>

      {/* Results Count */}
      {!loading && (
        <div className="catalog-results-info">
          <span className="catalog-results-count">{filteredFilieres.length}</span> filiere{filteredFilieres.length > 1 ? 's' : ''} trouvee{filteredFilieres.length > 1 ? 's' : ''}
          {searchTerm && <span> pour &laquo; {searchTerm} &raquo;</span>}
          {activeDomain !== 'Tous' && <span> en {activeDomain}</span>}
        </div>
      )}

      {/* Error Banner */}
      {error && (
        <div className="catalog-error">
          <AlertCircle size={18} />
          <span>{error}</span>
          <button onClick={fetchFilieres} className="catalog-retry-btn">Reessayer</button>
        </div>
      )}

      {/* Loading State */}
      {loading ? (
        <div className="catalog-loading">
          <div className="catalog-loading-spinner">
            <Loader2 size={36} className="spinner" />
          </div>
          <p>Chargement des filieres...</p>
        </div>
      ) : filteredFilieres.length === 0 ? (
        /* Empty State */
        <div className="catalog-empty">
          <div className="catalog-empty-icon">
            <Search size={48} />
          </div>
          <h3>Aucune filiere trouvee</h3>
          <p>
            {searchTerm
              ? <>Aucun resultat pour &laquo; {searchTerm} &raquo;. Essayez un autre terme.</>
              : 'Aucune filiere disponible pour ce filtre.'}
          </p>
          {(searchTerm || activeDomain !== 'Tous') && (
            <button className="catalog-reset-btn" onClick={() => { setSearchTerm(''); setActiveDomain('Tous'); }}>
              Reinitialiser les filtres
            </button>
          )}
        </div>
      ) : (
        /* Filières Grid */
        <div className="catalog-grid">
          {filteredFilieres.map((filiere, index) => {
            const config = getConfig(filiere.domaine);
            const delay = Math.min(index * 80, 600);
            return (
              <div
                key={filiere.id || index}
                className={`catalog-card ${animateCards ? 'visible' : ''}`}
                style={{ transitionDelay: `${delay}ms` }}
              >
                {/* Gradient top bar */}
                <div className="catalog-card-accent" style={{ background: config.gradient }} />

                {/* Card Header */}
                <div className="catalog-card-header">
                  <div className="catalog-card-icon" style={{ background: config.bgAlpha }}>
                    <span style={{ fontSize: '1.5rem' }}>{config.icon}</span>
                  </div>
                  <span className="catalog-card-domain" style={{ background: config.bgAlpha, color: config.color, borderColor: config.color + '33' }}>
                    {filiere.domaine || 'General'}
                  </span>
                </div>

                {/* Card Title */}
                <h3 className="catalog-card-title">{filiere.nom}</h3>

                {/* University */}
                <div className="catalog-card-uni">
                  <MapPin size={14} />
                  <span>{(filiere.etablissements && filiere.etablissements[0]?.nom) || 'Universite non precisee'}</span>
                </div>

                {/* Description */}
                <p className="catalog-card-desc">
                  {filiere.description ? filiere.description.substring(0, 120) + (filiere.description.length > 120 ? '...' : '') : 'Description non disponible.'}
                </p>

                <div className="catalog-card-divider" />

                {/* Info chips */}
                <div className="catalog-card-chips">
                  <div className="catalog-chip">
                    <Clock size={13} />
                    <span>{filiere.duree_annees || '?'} ans</span>
                  </div>
                  <div className="catalog-chip">
                    <Briefcase size={13} />
                    <span>{Array.isArray(filiere.debouches) ? filiere.debouches.length : 0} debouches</span>
                  </div>
                  {filiere.taux_insertion && (
                    <div className="catalog-chip insertion">
                      <TrendingUp size={13} />
                      <span>{filiere.taux_insertion}%</span>
                    </div>
                  )}
                </div>

                {/* Debouches preview */}
                {Array.isArray(filiere.debouches) && filiere.debouches.length > 0 && (
                  <div className="catalog-card-debouches">
                    {filiere.debouches.slice(0, 3).map((d, i) => (
                      <span key={i} className="catalog-debouche-tag">{d}</span>
                    ))}
                  </div>
                )}

                {/* Insertion bar */}
                {filiere.taux_insertion && (
                  <div className="catalog-card-insertion">
                    <div className="insertion-label">
                      <span>Taux d'insertion</span>
                      <span className="insertion-value" style={{ color: config.color }}>{filiere.taux_insertion}%</span>
                    </div>
                    <div className="insertion-bar-bg">
                      <div
                        className="insertion-bar-fill"
                        style={{
                          width: animateCards ? `${filiere.taux_insertion}%` : '0%',
                          background: config.gradient,
                          transitionDelay: `${delay + 300}ms`,
                        }}
                      />
                    </div>
                  </div>
                )}

                {/* CTA */}
                <button 
                  className="catalog-card-cta"
                  onClick={() => {
                    // Navigate to chat and open conversation with AI about this filière
                    navigate('/chat', { state: { initialQuery: `Je veux en savoir plus sur la filiere ${filiere.nom} (${filiere.domaine})` } });
                  }}
                >
                  <span>Poser une question a l'IA</span>
                  <ArrowRight size={16} />
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default FilieresCatalog;
