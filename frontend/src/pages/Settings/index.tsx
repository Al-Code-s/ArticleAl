import { useState } from 'react';
import {
  Card,
  Form,
  Input,
  Button,
  Space,
  message,
  Divider,
  Select,
  InputNumber,
  Switch,
  Tabs,
  Tag,
  Alert,
} from 'antd';
import {
  UserOutlined,
  LockOutlined,
  ApiOutlined,
  SaveOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useUserStore } from '@stores/userStore';
import apiClient from '@services/api/client';
import './Settings.css';

const PROVIDERS = [
  { value: 'anthropic', label: 'Anthropic (Claude)', baseUrl: 'https://api.anthropic.com' },
  { value: 'openai', label: 'OpenAI (GPT)', baseUrl: 'https://api.openai.com/v1' },
  { value: 'deepseek', label: 'DeepSeek', baseUrl: 'https://api.deepseek.com/v1' },
  { value: 'qwen', label: '阿里千问 (Qwen)', baseUrl: 'https://dashscope.aliyuncs.com/compatible-mode/v1' },
  { value: 'chatglm', label: '智谱 ChatGLM', baseUrl: 'https://open.bigmodel.cn/api/paas/v4' },
  { value: 'moonshot', label: '月之暗面 Moonshot', baseUrl: 'https://api.moonshot.cn/v1' },
  { value: 'custom', label: '自定义 OpenAI 兼容 API', baseUrl: '' },
];

const setProviderBaseUrl = (form: any, provider: string) => {
  const item = PROVIDERS.find((candidate) => candidate.value === provider);
  form.setFieldValue('baseUrl', item?.baseUrl || '');
};

const Settings = () => {
  const [form] = Form.useForm();
  const [passwordForm] = Form.useForm();
  const [contentAiForm] = Form.useForm();
  const [agentAiForm] = Form.useForm();
  const { user, setUser } = useUserStore();
  const [activeTab, setActiveTab] = useState('profile');

  // 内容生成AI配置的状态
  const [contentModels, setContentModels] = useState<any[]>([]);
  const [contentLoadingModels, setContentLoadingModels] = useState(false);

  // 智能体AI配置的状态
  const [agentModels, setAgentModels] = useState<any[]>([]);
  const [agentLoadingModels, setAgentLoadingModels] = useState(false);

  // 获取用户信息
  useQuery({
    queryKey: ['user', 'me'],
    queryFn: () => apiClient.get('/auth/me'),
  });

  // 获取AI配置
  const { data: aiConfigData, refetch: refetchAiConfig } = useQuery({
    queryKey: ['aiConfig'],
    queryFn: () => apiClient.get('/ai-configs'),
    enabled: activeTab === 'ai',
  });

  // 更新用户信息
  const updateProfileMutation = useMutation({
    mutationFn: (data: any) => apiClient.put('/users/profile', data),
    onSuccess: (res: any) => {
      message.success('个人信息更新成功');
      setUser(res);
    },
    onError: (error: any) => {
      message.error(error?.response?.data?.detail || '更新失败');
    },
  });

  // 修改密码
  const changePasswordMutation = useMutation({
    mutationFn: (data: { old_password: string; new_password: string }) =>
      apiClient.post('/users/change-password', data),
    onSuccess: () => {
      message.success('密码修改成功，请重新登录');
      passwordForm.resetFields();
    },
    onError: (error: any) => {
      message.error(error?.response?.data?.detail || '修改密码失败');
    },
  });

  // 保存AI配置
  const saveAiConfigMutation = useMutation({
    mutationFn: (data: any) => apiClient.post('/ai-configs', data),
    onSuccess: () => {
      message.success('AI配置保存成功');
      refetchAiConfig();
    },
    onError: (error: any) => {
      message.error(error?.response?.data?.detail || '保存失败');
    },
  });

  // 获取模型列表
  const fetchModelsMutation = useMutation({
    mutationFn: (data: { provider: string; apiKey: string; baseUrl?: string }) =>
      apiClient.post('/ai-configs/actions/fetch-models', data),
    onSuccess: (res: any) => {
      if (res.warning) {
        message.warning(res.warning);
      } else {
        message.success(`已从${res.source === 'provider' ? '供应商' : '内置目录'}获取模型`);
      }
      return res.models;
    },
    onError: (error: any) => {
      message.error(error?.response?.data?.detail || '获取模型列表失败');
    },
  });

  // 获取内容生成AI的模型列表
  const handleFetchContentModels = async () => {
    const provider = contentAiForm.getFieldValue('provider');
    const apiKey = contentAiForm.getFieldValue('apiKey');
    const baseUrl = contentAiForm.getFieldValue('baseUrl');

    console.log('========== Fetch Content Models ==========');
    console.log('Provider:', provider);
    console.log('Base URL:', baseUrl);
    console.log('Request URL:', '/ai-configs/actions/fetch-models');
    console.log('==========================================');

    if (!provider || !apiKey) {
      message.warning('请先选择提供商并输入API Key');
      return;
    }

    setContentLoadingModels(true);
    try {
      const res: any = await fetchModelsMutation.mutateAsync({ provider, apiKey, baseUrl });
      console.log('✅ Models fetched successfully:', res);
      setContentModels(res.models || []);
    } catch (error) {
      console.error('❌ Fetch models failed:', error);
    } finally {
      setContentLoadingModels(false);
    }
  };

  // 获取智能体AI的模型列表
  const handleFetchAgentModels = async () => {
    const provider = agentAiForm.getFieldValue('provider');
    const apiKey = agentAiForm.getFieldValue('apiKey');
    const baseUrl = agentAiForm.getFieldValue('baseUrl');

    if (!provider || !apiKey) {
      message.warning('请先选择提供商并输入API Key');
      return;
    }

    setAgentLoadingModels(true);
    try {
      const res: any = await fetchModelsMutation.mutateAsync({ provider, apiKey, baseUrl });
      setAgentModels(res.models || []);
    } finally {
      setAgentLoadingModels(false);
    }
  };

  const handleProfileSubmit = (values: any) => {
    updateProfileMutation.mutate(values);
  };

  const handlePasswordSubmit = (values: any) => {
    if (values.newPassword !== values.confirmPassword) {
      message.error('两次输入的密码不一致');
      return;
    }
    changePasswordMutation.mutate({
      old_password: values.oldPassword,
      new_password: values.newPassword,
    });
  };

  const handleAiConfigSubmit = (values: any, configType: string) => {
    saveAiConfigMutation.mutate({
      ...values,
      config_type: configType,
    });
  };

  return (
    <div className="settings">
      <Card title="系统设置">
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={[
            {
              key: 'profile',
              label: (
                <span>
                  <UserOutlined />
                  个人信息
                </span>
              ),
              children: (
                <div style={{ maxWidth: 600 }}>
                  <Form
                    form={form}
                    layout="vertical"
                    onFinish={handleProfileSubmit}
                    initialValues={{
                      username: user?.username,
                      email: user?.email,
                    }}
                  >
                    <Form.Item
                      name="username"
                      label="用户名"
                      rules={[{ required: true, message: '请输入用户名' }]}
                    >
                      <Input prefix={<UserOutlined />} placeholder="用户名" />
                    </Form.Item>

                    <Form.Item
                      name="email"
                      label="邮箱"
                      rules={[
                        { required: true, message: '请输入邮箱' },
                        { type: 'email', message: '请输入有效的邮箱地址' },
                      ]}
                    >
                      <Input prefix={<UserOutlined />} placeholder="邮箱" />
                    </Form.Item>

                    <Form.Item>
                      <Button
                        type="primary"
                        htmlType="submit"
                        icon={<SaveOutlined />}
                        loading={updateProfileMutation.isPending}
                      >
                        保存修改
                      </Button>
                    </Form.Item>
                  </Form>
                </div>
              ),
            },
            {
              key: 'password',
              label: (
                <span>
                  <LockOutlined />
                  修改密码
                </span>
              ),
              children: (
                <div style={{ maxWidth: 600 }}>
                  <Form
                    form={passwordForm}
                    layout="vertical"
                    onFinish={handlePasswordSubmit}
                  >
                    <Form.Item
                      name="oldPassword"
                      label="当前密码"
                      rules={[{ required: true, message: '请输入当前密码' }]}
                    >
                      <Input.Password prefix={<LockOutlined />} placeholder="当前密码" />
                    </Form.Item>

                    <Form.Item
                      name="newPassword"
                      label="新密码"
                      rules={[
                        { required: true, message: '请输入新密码' },
                        { min: 6, message: '密码至少6位' },
                      ]}
                    >
                      <Input.Password prefix={<LockOutlined />} placeholder="新密码" />
                    </Form.Item>

                    <Form.Item
                      name="confirmPassword"
                      label="确认密码"
                      rules={[{ required: true, message: '请再次输入新密码' }]}
                    >
                      <Input.Password prefix={<LockOutlined />} placeholder="确认新密码" />
                    </Form.Item>

                    <Form.Item>
                      <Button
                        type="primary"
                        htmlType="submit"
                        icon={<SaveOutlined />}
                        loading={changePasswordMutation.isPending}
                      >
                        修改密码
                      </Button>
                    </Form.Item>
                  </Form>
                </div>
              ),
            },
            {
              key: 'ai',
              label: (
                <span>
                  <ApiOutlined />
                  AI 配置
                </span>
              ),
              children: (
                <div style={{ maxWidth: 900 }}>
                  <Alert
                    message="配置说明"
                    description="需要配置两种AI：内容生成AI用于生成文章、大纲等；智能体AI用于MCP智能体对话功能。"
                    type="info"
                    showIcon
                    style={{ marginBottom: 24 }}
                  />

                  {/* 内容生成AI配置 */}
                  <Card
                    title="内容生成 AI 配置"
                    style={{ marginBottom: 24 }}
                    extra={<Tag color="blue">用于生成文章、大纲、文献等</Tag>}
                  >
                    <Form
                      form={contentAiForm}
                      layout="vertical"
                      onFinish={(values) => handleAiConfigSubmit(values, 'content_generation')}
                      initialValues={{
                        provider: 'anthropic',
                        temperature: 0.7,
                        maxTokens: 4096,
                        streamEnabled: true,
                      }}
                    >
                      <Form.Item
                        name="name"
                        label="配置名称"
                        rules={[{ required: true, message: '请输入配置名称' }]}
                      >
                        <Input placeholder="例如：内容生成配置" />
                      </Form.Item>

                      <Form.Item
                        name="provider"
                        label="AI 提供商"
                        rules={[{ required: true, message: '请选择AI提供商' }]}
                      >
                        <Select
                          onChange={(value) => {
                            setContentModels([]);
                            setProviderBaseUrl(contentAiForm, value);
                          }}
                          showSearch
                          placeholder="选择提供商"
                        >
                          {PROVIDERS.map((provider) => (
                            <Select.Option key={provider.value} value={provider.value}>
                              {provider.label}
                            </Select.Option>
                          ))}
                        </Select>
                      </Form.Item>

                      <Form.Item
                        name="apiKey"
                        label="API Key"
                        rules={[{ required: true, message: '请输入API Key' }]}
                      >
                        <Input.Password placeholder="sk-ant-..." />
                      </Form.Item>

                      <Form.Item name="baseUrl" label="API Base URL（可选）">
                        <Input placeholder="https://api.anthropic.com" />
                      </Form.Item>

                      <Form.Item
                        label="选择模型"
                        required
                      >
                        <Space.Compact style={{ width: '100%' }}>
                          <Button
                            icon={<ReloadOutlined />}
                            onClick={handleFetchContentModels}
                            loading={contentLoadingModels}
                          >
                            获取模型列表
                          </Button>
                        </Space.Compact>
                      </Form.Item>

                      {contentModels.length > 0 && (
                        <Form.Item
                          name="model"
                          rules={[{ required: true, message: '请选择模型' }]}
                        >
                          <Select placeholder="选择一个模型">
                            {contentModels.map((model: any) => (
                              <Select.Option key={model.id} value={model.id}>
                                <div>
                                  <div style={{ fontWeight: 500 }}>{model.name}</div>
                                  {model.description && (
                                    <div style={{ fontSize: 12, color: '#999' }}>
                                      {model.description}
                                    </div>
                                  )}
                                </div>
                              </Select.Option>
                            ))}
                          </Select>
                        </Form.Item>
                      )}

                      <Divider />

                      <Form.Item name="temperature" label="Temperature (创造性)">
                        <InputNumber
                          min={0}
                          max={2}
                          step={0.1}
                          style={{ width: '100%' }}
                        />
                      </Form.Item>

                      <Form.Item name="maxTokens" label="最大 Tokens">
                        <InputNumber min={256} max={8192} step={256} style={{ width: '100%' }} />
                      </Form.Item>

                      <Form.Item name="streamEnabled" label="启用流式输出" valuePropName="checked">
                        <Switch />
                      </Form.Item>

                      <Form.Item>
                        <Space>
                          <Button
                            type="primary"
                            htmlType="submit"
                            icon={<SaveOutlined />}
                            loading={saveAiConfigMutation.isPending}
                          >
                            保存配置
                          </Button>
                          <Button onClick={() => {
                            contentAiForm.resetFields();
                            setContentModels([]);
                          }}>
                            重置
                          </Button>
                        </Space>
                      </Form.Item>
                    </Form>
                  </Card>

                  {/* 智能体AI配置 */}
                  <Card
                    title="智能体 AI 配置"
                    extra={<Tag color="green">用于MCP智能体对话</Tag>}
                  >
                    <Form
                      form={agentAiForm}
                      layout="vertical"
                      onFinish={(values) => handleAiConfigSubmit(values, 'agent')}
                      initialValues={{
                        provider: 'anthropic',
                        temperature: 0.7,
                        maxTokens: 4096,
                        streamEnabled: true,
                      }}
                    >
                      <Form.Item
                        name="name"
                        label="配置名称"
                        rules={[{ required: true, message: '请输入配置名称' }]}
                      >
                        <Input placeholder="例如：智能体配置" />
                      </Form.Item>

                      <Form.Item
                        name="provider"
                        label="AI 提供商"
                        rules={[{ required: true, message: '请选择AI提供商' }]}
                      >
                        <Select
                          showSearch
                          onChange={(value) => {
                            setAgentModels([]);
                            setProviderBaseUrl(agentAiForm, value);
                          }}
                        >
                          {PROVIDERS.map((provider) => (
                            <Select.Option key={provider.value} value={provider.value}>
                              {provider.label}
                            </Select.Option>
                          ))}
                        </Select>
                      </Form.Item>

                      <Form.Item
                        name="apiKey"
                        label="API Key"
                        rules={[{ required: true, message: '请输入API Key' }]}
                      >
                        <Input.Password placeholder="sk-ant-..." />
                      </Form.Item>

                      <Form.Item name="baseUrl" label="API Base URL（可选）">
                        <Input placeholder="https://api.anthropic.com" />
                      </Form.Item>

                      <Form.Item
                        label="选择模型"
                        required
                      >
                        <Space.Compact style={{ width: '100%' }}>
                          <Button
                            icon={<ReloadOutlined />}
                            onClick={handleFetchAgentModels}
                            loading={agentLoadingModels}
                          >
                            获取模型列表
                          </Button>
                        </Space.Compact>
                      </Form.Item>

                      {agentModels.length > 0 && (
                        <Form.Item
                          name="model"
                          rules={[{ required: true, message: '请选择模型' }]}
                        >
                          <Select placeholder="选择一个模型">
                            {agentModels.map((model: any) => (
                              <Select.Option key={model.id} value={model.id}>
                                <div>
                                  <div style={{ fontWeight: 500 }}>{model.name}</div>
                                  {model.description && (
                                    <div style={{ fontSize: 12, color: '#999' }}>
                                      {model.description}
                                    </div>
                                  )}
                                </div>
                              </Select.Option>
                            ))}
                          </Select>
                        </Form.Item>
                      )}

                      <Divider />

                      <Form.Item name="temperature" label="Temperature (创造性)">
                        <InputNumber
                          min={0}
                          max={2}
                          step={0.1}
                          style={{ width: '100%' }}
                        />
                      </Form.Item>

                      <Form.Item name="maxTokens" label="最大 Tokens">
                        <InputNumber min={256} max={8192} step={256} style={{ width: '100%' }} />
                      </Form.Item>

                      <Form.Item name="streamEnabled" label="启用流式输出" valuePropName="checked">
                        <Switch />
                      </Form.Item>

                      <Form.Item>
                        <Space>
                          <Button
                            type="primary"
                            htmlType="submit"
                            icon={<SaveOutlined />}
                            loading={saveAiConfigMutation.isPending}
                          >
                            保存配置
                          </Button>
                          <Button onClick={() => {
                            agentAiForm.resetFields();
                            setAgentModels([]);
                          }}>
                            重置
                          </Button>
                        </Space>
                      </Form.Item>
                    </Form>
                  </Card>

                  {/* 已保存的配置列表 */}
                  {(aiConfigData as any)?.configs && (aiConfigData as any).configs.length > 0 && (
                    <>
                      <Divider />
                      <h3>已保存的配置</h3>
                      <div style={{ marginTop: 16 }}>
                        {(aiConfigData as any).configs.map((config: any) => (
                          <Card
                            key={config.id}
                            size="small"
                            style={{ marginBottom: 12 }}
                            title={config.name}
                            extra={
                              <Tag color={config.config_type === 'content_generation' ? 'blue' : 'green'}>
                                {config.config_type === 'content_generation' ? '内容生成' : '智能体'}
                              </Tag>
                            }
                          >
                            <Space direction="vertical" style={{ width: '100%' }}>
                              <div>提供商: {config.provider}</div>
                              <div>模型: {config.model}</div>
                              <div>
                                状态: {config.is_active ? (
                                  <Tag color="green">激活</Tag>
                                ) : (
                                  <Tag>未激活</Tag>
                                )}
                              </div>
                            </Space>
                          </Card>
                        ))}
                      </div>
                    </>
                  )}
                </div>
              ),
            },
          ]}
        />
      </Card>
    </div>
  );
};

export default Settings;
