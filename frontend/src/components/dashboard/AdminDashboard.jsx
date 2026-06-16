import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import {
  Users, BookOpen, MessageSquare, TrendingUp, Plus, Trash2, Edit3,
  Search, Download, ChevronDown, ChevronUp, Shield, UserCheck, X,
  GraduationCap, MapPin, Clock, Loader2, AlertCircle, Check, RefreshCw
} from 'lucide-react';
import api from '../../services/api';
import useScrollReveal from '../../hooks/useScrollReveal';

// ─── KPI Card ────────────────────────────────────────────────────
const KpiCard = ({ icon: Icon, label, value, color, delay }) => (
  <div className="card-premium reveal-up" style={{ padding: '1.5rem', display: 'flex', alignItems: 'center', gap: '1.25rem', animationDelay: delay }}>
    <div style={{ width: '48px', height: '48px', borderRadius: '12px', background: `${color}15`, color: color, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
      <Icon size={24} />
    </div>
    <div>
      <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '0.25rem' }}>{label}</div>
      <div style={{ fontSize: '1.75rem', fontWeight: 700 }}>{value}</div>
    </div>
  </div>
);

// ─── Tab Button ──────────────────────────────────────────────────
const TabBtn = ({ active, onClick, icon: Icon, label }) => (
  <button
    onClick={onClick}
    style={{
      display: 'flex', alignItems: 'center', gap: '0.5rem',
      padding: '0.65rem 1.25rem', borderRadius: 'var(--radius-full)',
      fontSize: '0.9rem', fontWeight: 600, cursor: 'pointer',
      transition: 'all 0.2s', border: 'none',
      background: active ? 'var(--gradient-primary)' : 'var(--bg-tertiary)',
      color: active ? 'white' : 'var(--text-secondary)',
    }}
  >
    <Icon size={16} /> {label}
  </button>
);

// ─── Admin Dashboard ─────────────────────────────────────────────
const AdminDashboard = () => {
  const { user } = useAuth();
  useScrollReveal();

  const [activeTab, setActiveTab] = useState('users');
  const [stats, setStats] = useState({ total_users: 0, total_filieres: 0, active_users: 0, admins: 0, students: 0 });
  const [users, setUsers] = useState([]);
  const [filieres, setFilieres] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [showAddFiliere, setShowAddFiliere] = useState(false);
  const [editingFiliere, setEditingFiliere] = useState(null);
  const [toast, setToast] = useState(null);

  // Toast helper
  const showToast = (message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  };

  // Fetch stats
  const fetchStats = async () => {
    try {
      const res = await api.get('/admin/stats');
      setStats(res.data.data);
    } catch (err) {
      console.error('Stats error:', err);
    }
  };

  // Fetch users
  const fetchUsers = async () => {
    try {
      const res = await api.get('/admin/users?limit=100');
      setUsers(res.data.data || []);
    } catch (err) {
      console.error('Users error:', err);
      setError("Impossible de charger les utilisateurs.");
    }
  };

  // Fetch filieres
  const fetchFilieres = async () => {
    try {
      const res = await api.get('/filieres?limit=100');
      setFilieres(res.data.data || []);
    } catch (err) {
      console.error('Filieres error:', err);
    }
  };

  useEffect(() => {
    const init = async () => {
      setLoading(true);
      await Promise.all([fetchStats(), fetchUsers(), fetchFilieres()]);
      setLoading(false);
    };
    init();
  }, []);

  // ─── User Actions ────────────────────────────────────────────
  const handleChangeRole = async (userId, newRole) => {
    try {
      await api.put(`/admin/users/${userId}/role`, { role: newRole });
      showToast(`Rôle mis à jour vers "${newRole}"`);
      fetchUsers();
      fetchStats();
    } catch (err) {
      showToast(err.response?.data?.detail || 'Erreur', 'error');
    }
  };

  const handleDeleteUser = async (userId, email) => {
    if (!confirm(`Supprimer l'utilisateur "${email}" ? Cette action est irréversible.`)) return;
    try {
      await api.delete(`/admin/users/${userId}`);
      showToast('Utilisateur supprimé');
      fetchUsers();
      fetchStats();
    } catch (err) {
      showToast(err.response?.data?.detail || 'Erreur', 'error');
    }
  };

  // ─── Filiere Actions ─────────────────────────────────────────
  const handleDeleteFiliere = async (id, nom) => {
    if (!confirm(`Supprimer la filière "${nom}" ? Cette action est irréversible.`)) return;
    try {
      await api.delete(`/admin/filieres/${id}`);
      showToast('Filière supprimée');
      fetchFilieres();
      fetchStats();
    } catch (err) {
      showToast(err.response?.data?.detail || 'Erreur', 'error');
    }
  };

  const handleExport = async () => {
    try {
      const res = await api.get('/admin/export/filieres');
      const blob = new Blob([JSON.stringify(res.data.data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'edubot_filieres_export.json';
      a.click();
      URL.revokeObjectURL(url);
      showToast('Export téléchargé avec succès');
    } catch (err) {
      showToast('Erreur lors de l\'export', 'error');
    }
  };

  // Filter
  const filteredUsers = users.filter(u =>
    u.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    u.full_name?.toLowerCase().includes(searchTerm.toLowerCase())
  );
  const filteredFilieres = filieres.filter(f =>
    f.nom?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    f.domaine?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <Loader2 size={40} className="spinner" color="var(--accent-1)" />
      </div>
    );
  }

  return (
    <div className="container" style={{ padding: '6rem 1.5rem 4rem', minHeight: '100vh' }}>
      {/* Toast */}
      {toast && (
        <div style={{
          position: 'fixed', top: '5rem', right: '1.5rem', zIndex: 600,
          padding: '0.85rem 1.5rem', borderRadius: 'var(--radius-md)',
          background: toast.type === 'error' ? 'rgba(253,121,168,0.15)' : 'rgba(0,206,201,0.15)',
          border: `1px solid ${toast.type === 'error' ? 'rgba(253,121,168,0.3)' : 'rgba(0,206,201,0.3)'}`,
          color: toast.type === 'error' ? '#fd79a8' : '#00cec9',
          fontSize: '0.9rem', fontWeight: 500, display: 'flex', alignItems: 'center', gap: '0.5rem',
          animation: 'slideUp 0.3s var(--ease-out-expo)',
        }}>
          {toast.type === 'error' ? <AlertCircle size={16} /> : <Check size={16} />}
          {toast.message}
        </div>
      )}

      {/* Header */}
      <div className="reveal-up" style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
          <Shield size={28} color="var(--accent-1)" />
          <h1 style={{ fontSize: '2.25rem', fontWeight: 800 }}>
            Espace <span className="gradient-text">Administrateur</span>
          </h1>
        </div>
        <p style={{ color: 'var(--text-secondary)' }}>
          Bienvenue, {user?.full_name}. Gérez les utilisateurs, les filières et les données de la plateforme.
        </p>
      </div>

      {/* KPI Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2.5rem' }}>
        <KpiCard icon={Users} label="Utilisateurs" value={stats.total_users} color="#6c5ce7" delay="0ms" />
        <KpiCard icon={BookOpen} label="Filières" value={stats.total_filieres} color="#00cec9" delay="50ms" />
        <KpiCard icon={UserCheck} label="Étudiants" value={stats.students} color="#fd79a8" delay="100ms" />
        <KpiCard icon={Shield} label="Admins" value={stats.admins} color="#f39c12" delay="150ms" />
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
        <TabBtn active={activeTab === 'users'} onClick={() => { setActiveTab('users'); setSearchTerm(''); }} icon={Users} label="Utilisateurs" />
        <TabBtn active={activeTab === 'filieres'} onClick={() => { setActiveTab('filieres'); setSearchTerm(''); }} icon={GraduationCap} label="Filières" />
      </div>

      {/* Search + Actions bar */}
      <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.5rem', flexWrap: 'wrap', alignItems: 'center' }}>
        <div style={{ flex: 1, minWidth: '250px', position: 'relative' }}>
          <Search size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input
            type="text"
            placeholder={activeTab === 'users' ? 'Rechercher un utilisateur...' : 'Rechercher une filière...'}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{
              width: '100%', padding: '0.75rem 1rem 0.75rem 2.75rem',
              borderRadius: 'var(--radius-full)', border: '1px solid var(--border-subtle)',
              background: 'var(--bg-secondary)', fontSize: '0.9rem', outline: 'none',
              color: 'var(--text-primary)', transition: 'border-color 0.2s',
            }}
          />
        </div>
        <button className="btn btn-secondary" onClick={() => { fetchUsers(); fetchFilieres(); fetchStats(); }} style={{ gap: '0.5rem' }}>
          <RefreshCw size={16} /> Actualiser
        </button>
        {activeTab === 'filieres' && (
          <>
            <button className="btn btn-primary" onClick={() => setShowAddFiliere(true)} style={{ gap: '0.5rem' }}>
              <Plus size={16} /> Ajouter
            </button>
            <button className="btn btn-secondary" onClick={handleExport} style={{ gap: '0.5rem' }}>
              <Download size={16} /> Exporter JSON
            </button>
          </>
        )}
      </div>

      {/* ─── Users Tab ─────────────────────────────────────────── */}
      {activeTab === 'users' && (
        <div className="card-premium" style={{ overflow: 'hidden' }}>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                  <th style={thStyle}>Utilisateur</th>
                  <th style={thStyle}>Email</th>
                  <th style={thStyle}>Rôle</th>
                  <th style={thStyle}>Statut</th>
                  <th style={thStyle}>Inscrit le</th>
                  <th style={thStyle}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredUsers.map((u) => (
                  <tr key={u.id} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                    <td style={tdStyle}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <div style={{
                          width: '32px', height: '32px', borderRadius: '50%', flexShrink: 0,
                          background: u.role === 'admin' ? 'linear-gradient(135deg, #f39c12, #e67e22)' : 'var(--gradient-primary)',
                          display: 'flex', alignItems: 'center', justifyContent: 'center',
                          color: 'white', fontSize: '0.75rem', fontWeight: 700
                        }}>
                          {u.full_name ? u.full_name[0].toUpperCase() : 'U'}
                        </div>
                        <span style={{ fontWeight: 600 }}>{u.full_name || '—'}</span>
                      </div>
                    </td>
                    <td style={tdStyle}>{u.email}</td>
                    <td style={tdStyle}>
                      <span style={{
                        padding: '0.25rem 0.75rem', borderRadius: 'var(--radius-full)',
                        fontSize: '0.8rem', fontWeight: 600,
                        background: u.role === 'admin' ? 'rgba(243,156,18,0.12)' : 'rgba(108,92,231,0.12)',
                        color: u.role === 'admin' ? '#f39c12' : '#6c5ce7'
                      }}>
                        {u.role === 'admin' ? 'Admin' : 'Étudiant'}
                      </span>
                    </td>
                    <td style={tdStyle}>
                      <span style={{
                        width: '8px', height: '8px', borderRadius: '50%', display: 'inline-block',
                        background: u.is_active ? '#00cec9' : '#636e72', marginRight: '0.5rem'
                      }} />
                      {u.is_active ? 'Actif' : 'Inactif'}
                    </td>
                    <td style={tdStyle}>
                      {u.created_at ? new Date(u.created_at).toLocaleDateString('fr-FR') : '—'}
                    </td>
                    <td style={tdStyle}>
                      <div style={{ display: 'flex', gap: '0.5rem' }}>
                        <button
                          onClick={() => handleChangeRole(u.id, u.role === 'admin' ? 'student' : 'admin')}
                          title={u.role === 'admin' ? 'Rétrograder en étudiant' : 'Promouvoir en admin'}
                          style={actionBtnStyle}
                        >
                          <Shield size={14} />
                        </button>
                        <button
                          onClick={() => handleDeleteUser(u.id, u.email)}
                          title="Supprimer"
                          style={{ ...actionBtnStyle, color: '#fd79a8' }}
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
                {filteredUsers.length === 0 && (
                  <tr>
                    <td colSpan="6" style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
                      Aucun utilisateur trouvé
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ─── Filieres Tab ──────────────────────────────────────── */}
      {activeTab === 'filieres' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '1.25rem' }}>
          {filteredFilieres.map((f) => (
            <div key={f.id} className="card-premium" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                <div>
                  <h3 style={{ fontSize: '1.05rem', fontWeight: 700, marginBottom: '0.25rem' }}>{f.nom}</h3>
                  <span style={{
                    padding: '0.2rem 0.6rem', borderRadius: 'var(--radius-full)',
                    fontSize: '0.75rem', fontWeight: 600,
                    background: 'rgba(0,206,201,0.1)', color: '#00cec9'
                  }}>{f.domaine}</span>
                </div>
                <div style={{ display: 'flex', gap: '0.35rem' }}>
                  <button onClick={() => setEditingFiliere(f)} style={actionBtnStyle} title="Modifier">
                    <Edit3 size={14} />
                  </button>
                  <button onClick={() => handleDeleteFiliere(f.id, f.nom)} style={{ ...actionBtnStyle, color: '#fd79a8' }} title="Supprimer">
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.75rem', lineHeight: 1.5, flex: 1 }}>
                {f.description?.slice(0, 120)}{f.description?.length > 120 ? '...' : ''}
              </p>
              <div style={{ display: 'flex', gap: '1rem', fontSize: '0.8rem', color: 'var(--text-muted)', flexWrap: 'wrap' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                  <Clock size={13} /> {f.duree_annees} ans
                </span>
                <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                  <MapPin size={13} /> {f.etablissements?.[0]?.nom || '—'}
                </span>
                <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                  <TrendingUp size={13} /> {f.taux_insertion}%
                </span>
              </div>
            </div>
          ))}
          {filteredFilieres.length === 0 && (
            <div style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
              Aucune filière trouvée
            </div>
          )}
        </div>
      )}

      {/* ─── Add / Edit Filiere Modal ──────────────────────────── */}
      {(showAddFiliere || editingFiliere) && (
        <FiliereFormModal
          filiere={editingFiliere}
          onClose={() => { setShowAddFiliere(false); setEditingFiliere(null); }}
          onSaved={() => { fetchFilieres(); fetchStats(); showToast(editingFiliere ? 'Filière modifiée' : 'Filière ajoutée'); }}
        />
      )}

    </div>
  );
};

// ─── Filiere Form Modal ──────────────────────────────────────────
const FiliereFormModal = ({ filiere, onClose, onSaved }) => {
  const isEditing = !!filiere;
  const [form, setForm] = useState({
    nom: filiere?.nom || '',
    domaine: filiere?.domaine || '',
    description: filiere?.description || '',
    duree_annees: filiere?.duree_annees || 3,
    niveau_entree: filiere?.niveau_entree || 'Bac',
    taux_insertion: filiere?.taux_insertion || 0,
    salaire_moyen_sortie: filiere?.salaire_moyen_sortie || 0,
    cout_annuel_moyen: filiere?.cout_annuel_moyen || 0,
    etablissement_nom: filiere?.etablissements?.[0]?.nom || '',
    etablissement_ville: filiere?.etablissements?.[0]?.ville || 'Conakry',
    etablissement_type: filiere?.etablissements?.[0]?.type || 'Public',
    debouches_text: Array.isArray(filiere?.debouches) ? filiere.debouches.join(', ') : '',
    matieres_text: Array.isArray(filiere?.matieres_cles) ? filiere.matieres_cles.join(', ') : '',
    serie_bac: filiere?.prerequis_academiques?.serie_bac || '',
    mention_min: filiere?.prerequis_academiques?.mention_min || 'Passable',
    note_seuil: filiere?.prerequis_academiques?.note_seuil || 10,
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (field, value) => setForm(prev => ({ ...prev, [field]: value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.nom || !form.domaine) {
      setError('Le nom et le domaine sont requis');
      return;
    }
    setSaving(true);
    setError(null);

    const payload = {
      nom: form.nom,
      domaine: form.domaine,
      description: form.description,
      duree_annees: parseInt(form.duree_annees),
      niveau_entree: form.niveau_entree,
      taux_insertion: parseFloat(form.taux_insertion),
      salaire_moyen_sortie: parseFloat(form.salaire_moyen_sortie),
      cout_annuel_moyen: parseFloat(form.cout_annuel_moyen),
      etablissements: [{ nom: form.etablissement_nom, ville: form.etablissement_ville, type: form.etablissement_type }],
      debouches: form.debouches_text.split(',').map(s => s.trim()).filter(Boolean),
      matieres_cles: form.matieres_text.split(',').map(s => s.trim()).filter(Boolean),
      prerequis_academiques: { serie_bac: form.serie_bac, mention_min: form.mention_min, note_seuil: parseInt(form.note_seuil) },
    };

    try {
      if (isEditing) {
        await api.put(`/admin/filieres/${filiere.id}`, payload);
      } else {
        await api.post('/admin/filieres', payload);
      }
      onSaved();
      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors de la sauvegarde');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="auth-gate-overlay" onClick={onClose}>
      <div
        className="auth-gate-modal"
        onClick={(e) => e.stopPropagation()}
        style={{ maxWidth: '600px', textAlign: 'left', maxHeight: '85vh', overflowY: 'auto' }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700 }}>
            {isEditing ? 'Modifier la filière' : 'Ajouter une filière'}
          </h3>
          <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}>
            <X size={20} />
          </button>
        </div>

        {error && (
          <div style={{ padding: '0.75rem 1rem', borderRadius: 'var(--radius-md)', background: 'rgba(253,121,168,0.1)', border: '1px solid rgba(253,121,168,0.2)', color: '#fd79a8', fontSize: '0.85rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <AlertCircle size={16} /> {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <FormField label="Nom de la filière *" value={form.nom} onChange={v => handleChange('nom', v)} span={2} />
            <FormField label="Domaine *" value={form.domaine} onChange={v => handleChange('domaine', v)} />
            <FormField label="Durée (années)" value={form.duree_annees} onChange={v => handleChange('duree_annees', v)} type="number" />
            <FormField label="Établissement" value={form.etablissement_nom} onChange={v => handleChange('etablissement_nom', v)} />
            <FormField label="Ville" value={form.etablissement_ville} onChange={v => handleChange('etablissement_ville', v)} />
            <FormField label="Type (Public/Privé)" value={form.etablissement_type} onChange={v => handleChange('etablissement_type', v)} />
            <FormField label="Niveau d'entrée" value={form.niveau_entree} onChange={v => handleChange('niveau_entree', v)} />
            <FormField label="Taux d'insertion (%)" value={form.taux_insertion} onChange={v => handleChange('taux_insertion', v)} type="number" />
            <FormField label="Salaire moyen (GNF)" value={form.salaire_moyen_sortie} onChange={v => handleChange('salaire_moyen_sortie', v)} type="number" />
            <FormField label="Coût annuel (GNF)" value={form.cout_annuel_moyen} onChange={v => handleChange('cout_annuel_moyen', v)} type="number" />
            <FormField label="Série Bac requise" value={form.serie_bac} onChange={v => handleChange('serie_bac', v)} placeholder="SM, SE, SS..." />
            <FormField label="Mention minimum" value={form.mention_min} onChange={v => handleChange('mention_min', v)} />
            <FormField label="Note seuil (/20)" value={form.note_seuil} onChange={v => handleChange('note_seuil', v)} type="number" />
          </div>
          <div style={{ marginTop: '1rem' }}>
            <FormField label="Description" value={form.description} onChange={v => handleChange('description', v)} textarea span={2} />
            <FormField label="Débouchés (séparés par des virgules)" value={form.debouches_text} onChange={v => handleChange('debouches_text', v)} placeholder="Médecin, Spécialiste, Chercheur..." span={2} />
            <FormField label="Matières clés (séparées par des virgules)" value={form.matieres_text} onChange={v => handleChange('matieres_text', v)} placeholder="Biologie, Chimie, Physique..." span={2} />
          </div>
          <div style={{ display: 'flex', gap: '0.75rem', marginTop: '1.5rem' }}>
            <button type="submit" className="btn btn-primary" style={{ flex: 1 }} disabled={saving}>
              {saving ? <Loader2 size={16} className="spinner" /> : <Check size={16} />}
              {isEditing ? 'Enregistrer' : 'Créer la filière'}
            </button>
            <button type="button" className="btn btn-secondary" onClick={onClose} style={{ flex: 0.5 }}>
              Annuler
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// ─── Form Field helper ───────────────────────────────────────────
const FormField = ({ label, value, onChange, type = 'text', placeholder, textarea, span }) => (
  <div style={{ gridColumn: span === 2 ? '1 / -1' : undefined, marginBottom: '0.5rem' }}>
    <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>{label}</label>
    {textarea ? (
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        rows={3}
        placeholder={placeholder}
        style={inputStyle}
      />
    ) : (
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        style={inputStyle}
      />
    )}
  </div>
);

// ─── Styles ──────────────────────────────────────────────────────
const thStyle = {
  padding: '0.85rem 1rem', textAlign: 'left', fontWeight: 600, fontSize: '0.85rem',
  color: 'var(--text-secondary)', whiteSpace: 'nowrap'
};

const tdStyle = {
  padding: '0.85rem 1rem', color: 'var(--text-primary)', fontSize: '0.9rem'
};

const actionBtnStyle = {
  width: '32px', height: '32px', borderRadius: '8px', display: 'flex',
  alignItems: 'center', justifyContent: 'center', cursor: 'pointer',
  background: 'var(--bg-tertiary)', border: '1px solid var(--border-subtle)',
  color: 'var(--text-secondary)', transition: 'all 0.15s'
};

const inputStyle = {
  width: '100%', padding: '0.65rem 0.85rem', borderRadius: 'var(--radius-md)',
  border: '1px solid var(--border-subtle)', background: 'var(--bg-primary)',
  fontSize: '0.9rem', color: 'var(--text-primary)', outline: 'none',
  resize: 'vertical', transition: 'border-color 0.2s',
};

export default AdminDashboard;
