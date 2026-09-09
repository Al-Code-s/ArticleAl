import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Card,
  Tabs,
  Button,
  Space,
  Spin,
  message,
  Tag,
  Descriptions,
  Empty,
  Table,
  Modal,
} from 'antd';
import {
  RocketOutlined,
  StopOutlined,
  FileTextOutlined,
  BookOutlined,
  EditOutlined,
} from '@ant-design/icons';
import { useQuery, useMutation } from '@tanstack/react-query';
import { projectApi } from '@services/api/project';
import { agentApi } from '@services/api/agent';
import { useProjectStore } from '@stores/projectStore';
import { ChatPanel } from '@components/ChatPanel';
import './ProjectWorkspace.css';

const ProjectWorkspace = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const { projects, setActiveProject, updateProject } = useProjectStore();
  const [activeTab, setActiveTab] = useState('chat');
  const [outlineModalVisible, setOutlineModalVisible] = useState(false);

  const currentProject = projects.find((p) => p.id === projectId);

  // 获取项目详情
  const { data: projectData, isLoading: projectLoading } = useQuery({
    queryKey: ['project', projectId],
    queryFn: () => projectApi.getProject(projectId!),
    enabled: !!projectId && !currentProject,
  });

  // 获取大纲
  const { data: outlineData, refetch: refetchOutline } = useQuery({
    queryKey: ['outline', projectId],
    queryFn: () => projectApi.getOutline(projectId!),
    enabled: !!projectId && activeTab === 'outline',
  });

  // 获取参考文献
  const { data: referencesData } = useQuery({
    queryKey: ['references', projectId],
    queryFn: () => projectApi.getReferences(projectId!),
    enabled: !!projectId && activeTab === 'references',
  });

  // 启动智能体
  const startAgentMutation = useMutation({
    mutationFn: (projectId: string) => agentApi.startAgent(projectId),
    onSuccess: () => {
      message.success('智能体已启动');
      if (projectId) {
        updateProject(projectId, { agent_status: 'running' });
      }
    },
    onError: () => {
      message.error('启动智能体失败');
    },
  });

  // 停止智能体
  const stopAgentMutation = useMutation({
    mutationFn: (projectId: string) => agentApi.stopAgent(projectId),
    onSuccess: () => {
      message.success('智能体已停止');
      if (projectId) {
        updateProject(projectId, { agent_status: 'stopped' });
      }
    },
    onError: () => {
      message.error('停止智能体失败');
    },
  });

  // 生成大纲
  const generateOutlineMutation = useMutation({
    mutationFn: ({ projectId, title }: { projectId: string; title: string }) =>
      projectApi.generateOutline(projectId, title),
    onSuccess: () => {
      message.success('大纲生成成功');
      refetchOutline();
      setOutlineModalVisible(false);
    },
    onError: () => {
      message.error('生成大纲失败');
    },
  });

  useEffect(() => {
    if (projectId) {
      setActiveProject(projectId);
    }
  }, [projectId]);

  if (!projectId) {
    return (
      <div className="project-workspace">
        <Card>
          <Empty description="请选择一个项目" />
        </Card>
      </div>
    );
  }

  const project = currentProject || (projectData as any);

  if (projectLoading || !project) {
    return (
      <div className="project-workspace">
        <Spin size="large" />
      </div>
    );
  }

  const getStatusTag = (status: string) => {
    const statusMap: Record<string, { color: string; text: string }> = {
      created: { color: 'default', text: '已创建' },
      in_progress: { color: 'processing', text: '进行中' },
      completed: { color: 'success', text: '已完成' },
      archived: { color: 'default', text: '已归档' },
    };
    const config = statusMap[status] || statusMap.created;
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  const getAgentStatusTag = (status: string) => {
    const statusMap: Record<string, { color: string; text: string }> = {
      idle: { color: 'default', text: '待启动' },
      running: { color: 'processing', text: '运行中' },
      stopped: { color: 'warning', text: '已停止' },
      error: { color: 'error', text: '错误' },
    };
    const config = statusMap[status] || statusMap.idle;
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  const referenceColumns = [
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      width: '40%',
    },
    {
      title: '作者',
      dataIndex: 'authors',
      key: 'authors',
      width: '20%',
      render: (authors: string[]) => authors?.join(', ') || '-',
    },
    {
      title: '期刊',
      dataIndex: 'journal',
      key: 'journal',
      width: '20%',
    },
    {
      title: '年份',
      dataIndex: 'year',
      key: 'year',
      width: '10%',
    },
    {
      title: '状态',
      dataIndex: 'is_selected',
      key: 'is_selected',
      width: '10%',
      render: (selected: boolean) => (
        <Tag color={selected ? 'green' : 'default'}>{selected ? '已选择' : '待选'}</Tag>
      ),
    },
  ];

  return (
    <div className="project-workspace">
      <Card
        title={
          <Space>
            <FileTextOutlined />
            <span>{project.title}</span>
            {getStatusTag(project.status)}
            {getAgentStatusTag(project.agent_status)}
          </Space>
        }
        extra={
          <Space>
            {project.agent_status === 'running' ? (
              <Button
                icon={<StopOutlined />}
                onClick={() => stopAgentMutation.mutate(projectId)}
                loading={stopAgentMutation.isPending}
              >
                停止智能体
              </Button>
            ) : (
              <Button
                type="primary"
                icon={<RocketOutlined />}
                onClick={() => startAgentMutation.mutate(projectId)}
                loading={startAgentMutation.isPending}
              >
                启动智能体
              </Button>
            )}
          </Space>
        }
      >
        <Descriptions column={4} size="small">
          <Descriptions.Item label="专业">{project.major || '-'}</Descriptions.Item>
          <Descriptions.Item label="学历">{project.education_level || '-'}</Descriptions.Item>
          <Descriptions.Item label="类型">{project.paper_type || '-'}</Descriptions.Item>
          <Descriptions.Item label="目标字数">{project.word_count}</Descriptions.Item>
        </Descriptions>
      </Card>

      <Card style={{ marginTop: 16 }}>
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={[
            {
              key: 'chat',
              label: (
                <span>
                  <RocketOutlined />
                  智能体对话
                </span>
              ),
              children: (
                <div style={{ padding: '16px 0' }}>
                  <ChatPanel projectId={parseInt(projectId)} />
                </div>
              ),
            },
            {
              key: 'outline',
              label: (
                <span>
                  <FileTextOutlined />
                  论文大纲
                </span>
              ),
              children: (
                <div>
                  {(outlineData as any)?.items?.[0] ? (
                    <div>
                      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
                        <span>版本: {(outlineData as any).items[0].version}</span>
                        <Button
                          icon={<EditOutlined />}
                          onClick={() => setOutlineModalVisible(true)}
                        >
                          重新生成
                        </Button>
                      </div>
                      <Card>
                        <pre style={{ whiteSpace: 'pre-wrap', margin: 0 }}>
                          {JSON.stringify((outlineData as any).items[0].content, null, 2)}
                        </pre>
                      </Card>
                    </div>
                  ) : (
                    <Empty
                      description="暂无大纲"
                      image={Empty.PRESENTED_IMAGE_SIMPLE}
                    >
                      <Button
                        type="primary"
                        onClick={() => setOutlineModalVisible(true)}
                      >
                        生成大纲
                      </Button>
                    </Empty>
                  )}
                </div>
              ),
            },
            {
              key: 'references',
              label: (
                <span>
                  <BookOutlined />
                  参考文献
                </span>
              ),
              children: (
                <div>
                  {(referencesData as any)?.items && (referencesData as any).items.length > 0 ? (
                    <Table
                      columns={referenceColumns}
                      dataSource={(referencesData as any).items}
                      rowKey="id"
                      pagination={{ pageSize: 10 }}
                    />
                  ) : (
                    <Empty
                      description="暂无参考文献"
                      image={Empty.PRESENTED_IMAGE_SIMPLE}
                    >
                      <p>使用智能体对话搜索文献，例如："帮我搜索相关文献"</p>
                    </Empty>
                  )}
                </div>
              ),
            },
          ]}
        />
      </Card>

      <Modal
        title="生成大纲"
        open={outlineModalVisible}
        onCancel={() => setOutlineModalVisible(false)}
        footer={null}
      >
        <Space direction="vertical" style={{ width: '100%' }}>
          <p>选择生成方式：</p>
          <Button
            block
            type="primary"
            onClick={() =>
              generateOutlineMutation.mutate({ projectId, title: project?.title || '论文' })
            }
            loading={generateOutlineMutation.isPending}
          >
            生成大纲
          </Button>
        </Space>
      </Modal>
    </div>
  );
};

export default ProjectWorkspace;
