import KeepAliveOutlet from './KeepAliveOutlet';
import { Layout, Menu, Avatar, Dropdown } from 'antd';
import type { MenuProps } from 'antd';
import {
  BulbOutlined,
  ProjectOutlined,
  SettingOutlined,
  BookOutlined,
  UserOutlined,
  LogoutOutlined,
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import { useUserStore } from '@stores/userStore';
import './MainLayout.css';

const { Header, Sider, Content } = Layout;

const MainLayout = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useUserStore();

  const menuItems = [
    {
      key: '/skills',
      icon: <BookOutlined />,
      label: '我的 Skills',
    },
    {
      key: '/topics',
      icon: <BulbOutlined />,
      label: '选题大厅',
    },
    {
      key: '/projects',
      icon: <ProjectOutlined />,
      label: '我的项目',
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: '系统设置',
    },
  ];

  const userMenuItems: MenuProps['items'] = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人信息',
    },
    {
      type: 'divider' as const,
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: () => {
        logout();
        navigate('/login');
      },
    },
  ];

  return (
    <Layout className="main-layout">
      <Header className="main-header">
        <div className="logo">
          <BulbOutlined style={{ fontSize: 24, marginRight: 8 }} />
          <span>ArticleAI</span>
        </div>
        <div className="user-info">
          <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
            <div className="user-avatar">
              <Avatar icon={<UserOutlined />} />
              <span className="username">{user?.username}</span>
            </div>
          </Dropdown>
        </div>
      </Header>
      <Layout>
        <Sider width={200} theme="light" className="main-sider">
          <Menu
            mode="inline"
            selectedKeys={[location.pathname]}
            items={menuItems}
            onClick={({ key }) => navigate(key)}
          />
        </Sider>
        <Content className="main-content">
          <KeepAliveOutlet />
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout;
