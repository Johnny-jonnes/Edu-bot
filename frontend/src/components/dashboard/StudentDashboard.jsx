import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
  BookOpen, Target, Settings, User, MessageSquare, GraduationCap,
  MapPin, Clock, Sparkles, ArrowRight, FileText, TrendingUp, Loader2
} from 'lucide-react';
import { getFilieres } from '../../services/api';
import useScrollReveal from '../../hooks/useScrollReveal';

const StudentDashboard = () => {
  const { user } = useAuth();
  useScrollReveal();

  const [topFilieres, setTopFilieres] = useState([]);
  const [loadingFilieres, setLoadingFilieres] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await getFilieres({ limit: 4 });
        setTopFilieres(data.data || []);
      } catch (e) { console.error(e); }
      finally { setLoadingFilieres(false); }
    };
    load();
  }, []);

  if (!user) return null;

  const initials = user.full_name
    ? user.full_name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
    : user.email?.charAt(0)?.toUpperCase() || 'U';

  return (
    <div className="container" style={{ padding: '6rem 1.5rem 4rem', minHeight: '100vh' }}>
      {/* Header */}
      <div className="reveal-up" style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2.25rem', fontWeight: 800, marginBottom: '0.5rem' }}>
          Espace <span className="gradient-text">Étudiant</span>
        </h1>
        <p style={{ color: 'var(--text-secondary)' }}>
          Bienvenue, {user.full_name || user.email}. Voici votre tableau de bord personnalisé.
        </p>
      </div>

      {/* ─── Top Row: Profile + Quick Actions ─────────────────── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem', marginBottom: '2.5rem' }}>
        
        {/* Profile Card */}
        <div className="card-premium reveal-up delay-100" style={{ padding: '2rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
            <div style={{
              width: '60px', height: '60px', borderRadius: '50%',
              background: 'var(--gradient-primary)', display: 'flex',
              alignItems: 'center', justifyContent: 'center',
              color: 'white', fontSize: '1.5rem', fontWeight: 700, flexShrink: 0
            }}>
              {initials}
            </div>
            <div>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 700 }}>{user.full_name || 'Profil Incomplet'}</h3>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>{user.email}</div>
            </div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <InfoRow icon={User} label="Rôle" value="Étudiant" />
            <InfoRow icon={Clock} label="Membre depuis" value={user.created_at ? new Date(user.created_at).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' }) : '—'} />
          </div>
        </div>

        {/* Quick Actions */}
        <div className="card-premium reveal-up delay-200" style={{ padding: '2rem', display: 'flex', flexDirection: 'column' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '1.25rem' }}>Actions Rapides</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', flex: 1 }}>
            <QuickAction
              icon={Sparkles}
              color="#6c5ce7"
              title="Parler à EduBot"
              desc="Obtenez des recommandations de l'IA"
              to="/chat"
            />
            <QuickAction
              icon={GraduationCap}
              color="#00cec9"
              title="Explorer les Filières"
              desc="Parcourez le catalogue complet"
              to="/filieres"
            />
            <QuickAction
              icon={FileText}
              color="#fd79a8"
              title="Importer un relevé"
              desc="Analysez vos notes automatiquement"
              to="/chat"
            />
          </div>
        </div>
      </div>

      {/* ─── Recommendations Section ──────────────────────────── */}
      <div className="reveal-up delay-300" style={{ marginBottom: '2.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 700 }}>Mes Recommandations</h2>
        </div>
        <div className="card-premium" style={{ padding: '2.5rem', textAlign: 'center', border: '1px dashed var(--border-subtle)' }}>
          <Target size={48} color="var(--accent-2)" style={{ margin: '0 auto 1rem', opacity: 0.6 }} />
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '0.5rem' }}>Aucune recommandation sauvegardée</h3>
          <p style={{ color: 'var(--text-secondary)', maxWidth: '400px', margin: '0 auto 1.5rem', lineHeight: 1.6 }}>
            Discutez avec EduBot en lui donnant vos notes ou votre série de Bac pour recevoir des recommandations personnalisées.
          </p>
          <Link to="/chat" className="btn btn-primary" style={{ display: 'inline-flex' }}>
            <Sparkles size={16} /> Démarrer une analyse
          </Link>
        </div>
      </div>

      {/* ─── Top Filières Section ─────────────────────────────── */}
      <div className="reveal-up delay-400">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 700 }}>Filières Populaires</h2>
          <Link to="/filieres" style={{ color: 'var(--accent-1)', fontSize: '0.9rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
            Voir tout <ArrowRight size={14} />
          </Link>
        </div>

        {loadingFilieres ? (
          <div style={{ display: 'flex', justifyContent: 'center', padding: '3rem' }}>
            <Loader2 size={32} className="spinner" color="var(--accent-1)" />
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: '1rem' }}>
            {topFilieres.map(f => (
              <div key={f.id} className="card-premium" style={{ padding: '1.25rem' }}>
                <h4 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: '0.35rem' }}>{f.nom}</h4>
                <div style={{ display: 'flex', gap: '0.75rem', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.5rem', flexWrap: 'wrap' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    <MapPin size={12} /> {f.etablissements?.[0]?.nom || '—'}
                  </span>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    <Clock size={12} /> {f.duree_annees} ans
                  </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{
                    padding: '0.2rem 0.6rem', borderRadius: 'var(--radius-full)',
                    fontSize: '0.75rem', fontWeight: 600,
                    background: 'rgba(0,206,201,0.1)', color: '#00cec9'
                  }}>{f.domaine}</span>
                  <span style={{ fontSize: '0.8rem', color: 'var(--accent-2)', fontWeight: 600 }}>
                    <TrendingUp size={12} style={{ marginRight: '0.25rem' }} />{f.taux_insertion}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

// ─── Helpers ─────────────────────────────────────────────────────
const InfoRow = ({ icon: Icon, label, value }) => (
  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '0.9rem' }}>
    <Icon size={16} color="var(--text-muted)" />
    <span style={{ color: 'var(--text-secondary)' }}>{label} :</span>
    <span style={{ fontWeight: 600 }}>{value}</span>
  </div>
);

const QuickAction = ({ icon: Icon, color, title, desc, to }) => (
  <Link to={to} style={{
    display: 'flex', alignItems: 'center', gap: '1rem',
    padding: '0.85rem 1rem', borderRadius: 'var(--radius-md)',
    background: 'var(--bg-tertiary)', border: '1px solid var(--border-subtle)',
    transition: 'all 0.2s', textDecoration: 'none', color: 'inherit'
  }}>
    <div style={{
      width: '40px', height: '40px', borderRadius: '10px', flexShrink: 0,
      background: `${color}15`, color: color,
      display: 'flex', alignItems: 'center', justifyContent: 'center'
    }}>
      <Icon size={20} />
    </div>
    <div>
      <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{title}</div>
      <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>{desc}</div>
    </div>
    <ArrowRight size={16} color="var(--text-muted)" style={{ marginLeft: 'auto' }} />
  </Link>
);

export default StudentDashboard;
