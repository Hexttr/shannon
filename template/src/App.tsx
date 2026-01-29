import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Layout from './components/Layout';
import Login from './pages/Login';
import Home from './pages/Home';
import Services from './pages/Services';
import Pentests from './pages/Pentests';
import Reports from './pages/Reports';
import Analytics from './pages/Analytics';
import About from './pages/About';
import './App.css';

// Компонент для защищенных маршрутов
function ProtectedRoute({ children }: { children: React.ReactElement }) {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  window.__DEBUG__?.log('[ProtectedRoute] isLoading:', isLoading, 'isAuthenticated:', isAuthenticated);

  if (isLoading) {
    window.__DEBUG__?.log('[ProtectedRoute] Показываем загрузку...');
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white">Загрузка...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    window.__DEBUG__?.log('[ProtectedRoute] Не авторизован, редирект на /');
    return <Navigate to="/" replace state={{ from: location }} />;
  }

  window.__DEBUG__?.log('[ProtectedRoute] Авторизован, показываем children');
  return children;
}

function AppRoutes() {
  // Базовый путь всегда / (изменено с /app на /)
  const basename = '/';
  
  window.__DEBUG__?.log('[App.tsx] basename:', basename);
  window.__DEBUG__?.log('[App.tsx] location:', window.location.href);
  
  return (
    <BrowserRouter basename={basename}>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route
          path="/home"
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Home />} />
          <Route path="services" element={<Services />} />
          <Route path="pentests" element={<Pentests />} />
          <Route path="reports" element={<Reports />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="about" element={<About />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

function App() {
  window.__DEBUG__?.log('[App.tsx] Рендеринг App компонента');
  
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  );
}

export default App;