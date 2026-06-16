import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Mail, Lock, User as UserIcon, Loader2, AlertCircle } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import useScrollReveal from '../../hooks/useScrollReveal';

const Auth = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({ email: '', password: '', full_name: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const { login, register } = useAuth();

  useScrollReveal();

  const handleToggle = () => {
    setIsLogin(!isLogin);
    setError(null);
    setFormData({ email: '', password: '', full_name: '' });
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (isLogin) {
        await login(formData.email, formData.password);
      } else {
        await register({
          email: formData.email,
          password: formData.password,
          full_name: formData.full_name,
        });
      }
      navigate('/chat');
    } catch (err) {
      console.error('Auth error:', err);
      setError(
        err.response?.data?.detail || 
        "Une erreur est survenue. Vérifiez vos identifiants ou l'état du serveur."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page" style={{ 
      minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '6rem 1.5rem 2rem' 
    }}>
      <div className="card-premium reveal-scale" style={{ width: '100%', maxWidth: '420px', padding: '2.5rem' }}>
        <h2 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '0.5rem', textAlign: 'center' }}>
          {isLogin ? 'Bon retour !' : 'Créez votre compte'}
        </h2>
        <p style={{ color: 'var(--text-secondary)', textAlign: 'center', marginBottom: '2rem', fontSize: '0.9rem' }}>
          {isLogin 
            ? 'Connectez-vous pour retrouver vos recommandations.' 
            : 'Rejoignez EduBot pour orienter votre avenir.'}
        </p>

        {error && (
          <div style={{
            display: 'flex', alignItems: 'center', gap: '0.5rem',
            padding: '1rem', marginBottom: '1.5rem',
            background: 'rgba(253, 121, 168, 0.1)', borderRadius: 'var(--radius-md)',
            border: '1px solid rgba(253, 121, 168, 0.2)', color: '#fd79a8', fontSize: '0.85rem'
          }}>
            <AlertCircle size={16} style={{ flexShrink: 0 }} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {!isLogin && (
            <div style={{ position: 'relative' }}>
              <UserIcon size={18} color="var(--text-muted)" style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)' }} />
              <input
                type="text"
                name="full_name"
                placeholder="Nom complet"
                value={formData.full_name}
                onChange={handleChange}
                required={!isLogin}
                style={{
                  width: '100%', padding: '0.85rem 1rem 0.85rem 2.75rem',
                  borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)',
                  background: 'var(--bg-primary)', color: 'var(--text-primary)', outline: 'none'
                }}
              />
            </div>
          )}

          <div style={{ position: 'relative' }}>
            <Mail size={18} color="var(--text-muted)" style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)' }} />
            <input
              type="email"
              name="email"
              placeholder="Adresse email"
              value={formData.email}
              onChange={handleChange}
              required
              style={{
                width: '100%', padding: '0.85rem 1rem 0.85rem 2.75rem',
                borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)',
                background: 'var(--bg-primary)', color: 'var(--text-primary)', outline: 'none'
              }}
            />
          </div>

          <div style={{ position: 'relative' }}>
            <Lock size={18} color="var(--text-muted)" style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)' }} />
            <input
              type="password"
              name="password"
              placeholder="Mot de passe"
              value={formData.password}
              onChange={handleChange}
              required
              style={{
                width: '100%', padding: '0.85rem 1rem 0.85rem 2.75rem',
                borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)',
                background: 'var(--bg-primary)', color: 'var(--text-primary)', outline: 'none'
              }}
            />
          </div>

          <button 
            type="submit" 
            className="btn btn-primary" 
            disabled={loading}
            style={{ width: '100%', marginTop: '0.5rem', padding: '0.85rem' }}
          >
            {loading ? <Loader2 size={18} className="spinner" /> : (isLogin ? 'Se connecter' : "S'inscrire")}
          </button>
        </form>

        <div style={{ marginTop: '2rem', textAlign: 'center', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
          {isLogin ? "Vous n'avez pas de compte ?" : "Vous avez déjà un compte ?"}
          <button 
            onClick={handleToggle}
            style={{ 
              background: 'none', border: 'none', color: 'var(--accent-2)', 
              fontWeight: 600, marginLeft: '0.5rem', cursor: 'pointer' 
            }}
          >
            {isLogin ? "S'inscrire" : 'Se connecter'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Auth;
