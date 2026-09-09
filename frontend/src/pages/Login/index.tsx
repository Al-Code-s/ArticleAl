import { Form, Input, Button, Card, message } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useUserStore } from '@stores/userStore';
import { authApi } from '@services/api/auth';
import { useState } from 'react';
import './Login.css';

const Login = () => {
  const navigate = useNavigate();
  const { setUser, setToken } = useUserStore();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const onFinish = async (values: any) => {
    setLoading(true);
    try {
      // 调用登录API - apiClient已经返回response.data
      const loginResponse = await authApi.login({
        username: values.username,
        password: values.password,
      }) as any;

      console.log('Login response:', loginResponse);

      // 保存token
      const token = loginResponse.access_token;
      setToken(token);

      // 获取用户信息 - apiClient已经返回response.data
      const user = await authApi.me() as any;
      console.log('User response:', user);
      setUser(user);

      message.success('登录成功');
      navigate('/topics');
    } catch (error: any) {
      console.error('Login error:', error);
      if (error.response?.status === 401) {
        message.error('用户名或密码错误');
      } else if (error.detail) {
        message.error(error.detail);
      } else {
        message.error('登录失败，请稍后重试');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <Card className="login-card">
        <div className="login-header">
          <h1>ArticleAI</h1>
          <p>AI驱动的论文写作系统</p>
        </div>
        <Form form={form} onFinish={onFinish} size="large">
          <Form.Item
            name="username"
            rules={[{ required: true, message: '请输入用户名' }]}
          >
            <Input prefix={<UserOutlined />} placeholder="用户名" />
          </Form.Item>
          <Form.Item
            name="password"
            rules={[{ required: true, message: '请输入密码' }]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="密码" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" block loading={loading}>
              登录
            </Button>
          </Form.Item>
          <div className="login-footer">
            还没有账号？
            <Button type="link" onClick={() => navigate('/register')}>
              立即注册
            </Button>
          </div>
        </Form>
      </Card>
    </div>
  );
};

export default Login;
