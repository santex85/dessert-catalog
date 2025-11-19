import { useState, useEffect } from 'react';
import { Routes, Route, useNavigate, Navigate } from 'react-router-dom';
import Catalog from './components/Catalog';
import AdminPanel from './components/AdminPanel';
import Login from './components/Login';
import Register from './components/Register';
import { Dessert } from './types';
import { dessertsApi } from './services/api';
import { useAuth } from './contexts/AuthContext';

function ProtectedRoute({ children, requireAdmin = false }: { children: React.ReactNode; requireAdmin?: boolean }) {
  const { isAuthenticated, isAdmin, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl text-gray-600">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (requireAdmin && !isAdmin) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
}

function App() {
  const [isAdmin, setIsAdmin] = useState(false);
  const [desserts, setDesserts] = useState<Dessert[]>([]);
  const [loading, setLoading] = useState(true);
  const { isAuthenticated, isAdmin: userIsAdmin, logout, user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    loadDesserts();
  }, []);

  const loadDesserts = async () => {
    try {
      setLoading(true);
      const data = await dessertsApi.getAll({ is_active: true });
      setDesserts(data);
    } catch (error) {
      console.error('Error loading desserts:', error);
    } finally {
      setLoading(false);
    }
  };

  // Показываем загрузку только если действительно загружаем данные
  // AuthContext уже обработал проверку токена
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl text-gray-600">Loading catalog...</div>
      </div>
    );
  }

  return (
    <Routes>
      <Route
        path="/"
        element={
          <div className="min-h-screen bg-gray-50">
            <header className="bg-white shadow-sm">
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                <div className="flex justify-between items-center">
                  <h1 className="text-3xl font-bold text-gray-900">Dessert Catalog</h1>
                  <div className="flex gap-3 items-center">
                    {isAuthenticated ? (
                      <>
                        {user && (
                          <span className="text-sm text-gray-600">
                            {user.username} {user.is_admin && '(Admin)'}
                          </span>
                        )}
                        {userIsAdmin && (
                          <button
                            onClick={() => {
                              setIsAdmin(!isAdmin);
                              navigate(isAdmin ? '/' : '/admin');
                            }}
                            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                          >
                            {isAdmin ? 'Back to Catalog' : 'Admin Panel'}
                          </button>
                        )}
                        <button
                          onClick={() => {
                            logout();
                            navigate('/');
                          }}
                          className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                        >
                          Logout
                        </button>
                      </>
                    ) : (
                      <>
                        <button
                          onClick={() => navigate('/login')}
                          className="px-4 py-2 text-blue-600 hover:text-blue-800"
                        >
                          Login
                        </button>
                        <button
                          onClick={() => navigate('/register')}
                          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                        >
                          Register
                        </button>
                      </>
                    )}
                  </div>
                </div>
              </div>
            </header>

            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
              {isAdmin ? (
                <ProtectedRoute requireAdmin>
                  <AdminPanel onUpdate={loadDesserts} />
                </ProtectedRoute>
              ) : (
                <Catalog desserts={desserts} />
              )}
            </main>
          </div>
        }
      />
      <Route
        path="/admin"
        element={
          <ProtectedRoute requireAdmin>
            <div className="min-h-screen bg-gray-50">
              <header className="bg-white shadow-sm">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                  <div className="flex justify-between items-center">
                    <h1 className="text-3xl font-bold text-gray-900">Admin Panel</h1>
                    <button
                      onClick={() => {
                        setIsAdmin(false);
                        navigate('/');
                      }}
                      className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                    >
                      Back to Catalog
                    </button>
                  </div>
                </div>
              </header>
              <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <AdminPanel onUpdate={loadDesserts} />
              </main>
            </div>
          </ProtectedRoute>
        }
      />
      <Route
        path="/login"
        element={isAuthenticated ? <Navigate to="/" replace /> : <Login />}
      />
      <Route
        path="/register"
        element={isAuthenticated ? <Navigate to="/" replace /> : <Register />}
      />
    </Routes>
  );
}

export default App;

