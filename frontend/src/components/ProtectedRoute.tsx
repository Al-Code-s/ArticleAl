import { Navigate, useLocation } from 'react-router-dom';
import { useUserStore } from '../stores/userStore';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  const { isAuthenticated } = useUserStore();
  const location = useLocation();

  if (!isAuthenticated()) {
    // 未登录，重定向到登录页面，并保存当前路径
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;
