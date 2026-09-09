import { Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from '@components/layouts/MainLayout';
import ProtectedRoute from '@components/ProtectedRoute';
import TopicHall from '@pages/TopicHall';
import ProjectList from '@pages/ProjectList';
import ProjectWorkspace from '@pages/ProjectWorkspace';
import Settings from '@pages/Settings';
import Login from '@pages/Login';
import Register from '@pages/Register';

function App() {
  return (
    <Routes>
      {/* 公开路由 */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* 受保护的路由 */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/topics" replace />} />
        <Route path="topics" element={<TopicHall />} />
        <Route path="projects" element={<ProjectList />} />
        <Route path="projects/:projectId" element={<ProjectWorkspace />} />
        <Route path="settings" element={<Settings />} />
      </Route>

      {/* 404 */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
