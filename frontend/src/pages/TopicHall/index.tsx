import { useState } from 'react';
import {
  Card,
  Button,
  Form,
  Select,
  AutoComplete,
  InputNumber,
  Table,
  Tag,
  Space,
  message,
  Modal,
  Spin,
} from 'antd';
import { PlusOutlined, RocketOutlined } from '@ant-design/icons';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { topicApi } from '@services/api/topic';
import { projectApi } from '@services/api/project';
import { useProjectStore } from '@stores/projectStore';
import { useNavigate } from 'react-router-dom';
import type { Topic } from '../../types/topic';
import './TopicHall.css';
import { EDUCATION_LEVELS, MAJORS, PAPER_TYPES } from '../../constants/academic';


const TopicHall = () => {
  const [form] = Form.useForm();
  const navigate = useNavigate();
  const { addProject, setActiveProject } = useProjectStore();
  const queryClient = useQueryClient();
  const [topics, setTopics] = useState<Topic[]>([]);
  const [selectedTopic, setSelectedTopic] = useState<Topic | null>(null);
  const [createModalVisible, setCreateModalVisible] = useState(false);

  // 生成题目
  const generateMutation = useMutation({
    mutationFn: topicApi.generateTopics,
    onSuccess: (res: any) => {
      // Backend returns array directly, axios interceptor already unwrapped response.data
      const newTopics = Array.isArray(res) ? res : (res?.items || []);
      setTopics(newTopics);
      message.success(`成功生成 ${newTopics.length} 个题目`);
    },
    onError: (error: any) => {
      const detail = error?.response?.data?.detail;
      message.error(detail || '生成题目失败，请检查后端日志或 AI 配置');
    },
  });

  // 创建项目
  const createProjectMutation = useMutation({
    mutationFn: ({ topic, wordCount }: { topic: Topic; wordCount: number }) =>
      projectApi.createProject({
        title: topic.title,
        major: topic.major,
        education_level: topic.education_level,
        paper_type: topic.paper_type,
        word_count: wordCount,
      }),
    onSuccess: (res: any) => {
      // Backend returns project object directly
      addProject(res);
      // ProjectList is kept alive, so explicitly refresh its cached query after
      // creating a project from the topic hall.
      queryClient.setQueryData(['projects'], (current: any) => {
        const items = current?.items || [];
        return {
          ...(current || {}),
          items: [res, ...items.filter((item: any) => item.id !== res.id)],
          total: Math.max(current?.total || 0, items.length + 1),
        };
      });
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      setActiveProject(res.id);
      message.success('项目创建成功！');
      setCreateModalVisible(false);
      navigate(`/projects/${res.id}`);
    },
    onError: () => {
      message.error('创建项目失败');
    },
  });

  const handleGenerate = (values: any) => {
    generateMutation.mutate({
      major: values.major,
      educationLevel: values.educationLevel,
      paperType: values.paperType,
      count: values.count || 5,
    });
  };

  const handleCreateProject = (topic: Topic) => {
    setSelectedTopic(topic);
    setCreateModalVisible(true);
  };

  const handleConfirmCreate = (values: any) => {
    if (!selectedTopic) return;
    createProjectMutation.mutate({
      topic: selectedTopic,
      wordCount: values.wordCount || 10000,
    });
  };

  const columns = [
    {
      title: '题目',
      dataIndex: 'title',
      key: 'title',
      width: '40%',
    },
    {
      title: '专业',
      dataIndex: 'major',
      key: 'major',
      width: '15%',
    },
    {
      title: '学历',
      dataIndex: 'education_level',
      key: 'education_level',
      width: '10%',
      render: (level: string) => {
        const colorMap: Record<string, string> = {
          专科: 'orange',
          本科: 'blue',
          硕士: 'green',
        };
        return <Tag color={colorMap[level] || 'default'}>{level}</Tag>;
      },
    },
    {
      title: '类型',
      dataIndex: 'paper_type',
      key: 'paper_type',
      width: '10%',
    },
    {
      title: '可行性',
      dataIndex: 'feasibility_score',
      key: 'feasibility_score',
      width: '10%',
      render: (score: number) => (
        <span style={{ color: score >= 80 ? '#52c41a' : score >= 60 ? '#faad14' : '#ff4d4f' }}>
          {score}%
        </span>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: '15%',
      render: (_: any, record: Topic) => (
        <Button
          type="primary"
          size="small"
          icon={<RocketOutlined />}
          onClick={() => handleCreateProject(record)}
          disabled={record.is_used}
        >
          {record.is_used ? '已使用' : '创建项目'}
        </Button>
      ),
    },
  ];

  return (
    <div className="topic-hall">
      <Card title="AI 选题生成" style={{ marginBottom: 16 }}>
        <Form
          form={form}
          layout="inline"
          onFinish={handleGenerate}
          initialValues={{ count: 5, educationLevel: '本科', paperType: '研究性论文' }}
        >
          <Form.Item
            name="major"
            label="专业"
            rules={[{ required: true, message: '请输入专业' }]}
          >
            <AutoComplete
              style={{ width: 200 }}
              placeholder="请选择或输入专业"
              options={MAJORS.map((major) => ({ value: major, label: major }))}
              filterOption={(input, option) => String(option?.label || '').toLowerCase().includes(input.toLowerCase())}
            />
          </Form.Item>

          <Form.Item name="educationLevel" label="学历">
            <Select style={{ width: 120 }}>
              {EDUCATION_LEVELS.map((level) => (
                <Select.Option key={level} value={level}>{level}</Select.Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item name="paperType" label="论文类型">
            <Select style={{ width: 180 }}>
              {PAPER_TYPES.map((type) => (
                <Select.Option key={type.value} value={type.value}>
                  <div>{type.value}<div style={{ fontSize: 12, color: '#999' }}>{type.help}</div></div>
                </Select.Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item name="count" label="生成数量">
            <InputNumber min={1} max={10} style={{ width: 80 }} />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              icon={<PlusOutlined />}
              loading={generateMutation.isPending}
            >
              生成题目
            </Button>
          </Form.Item>
        </Form>
      </Card>

      <Card title={`候选题目 (${topics.length})`}>
        {generateMutation.isPending ? (
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <Spin size="large" tip="AI 正在生成题目..." />
          </div>
        ) : topics.length > 0 ? (
          <Table
            columns={columns}
            dataSource={topics}
            rowKey="id"
            pagination={{ pageSize: 10 }}
          />
        ) : (
          <div style={{ textAlign: 'center', padding: '40px 0', color: '#999' }}>
            请先生成题目
          </div>
        )}
      </Card>

      <Modal
        title="创建项目"
        open={createModalVisible}
        onCancel={() => setCreateModalVisible(false)}
        footer={null}
      >
        <div style={{ marginBottom: 16 }}>
          <strong>选题：</strong>
          <div style={{ marginTop: 8 }}>{selectedTopic?.title}</div>
        </div>
        <Form onFinish={handleConfirmCreate} initialValues={{ wordCount: 10000 }}>
          <Form.Item
            name="wordCount"
            label="目标字数"
            rules={[{ required: true, message: '请输入目标字数' }]}
          >
            <InputNumber
              min={3000}
              max={50000}
              step={1000}
              style={{ width: '100%' }}
              addonAfter="字"
            />
          </Form.Item>
          <Form.Item>
            <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
              <Button onClick={() => setCreateModalVisible(false)}>取消</Button>
              <Button type="primary" htmlType="submit" loading={createProjectMutation.isPending}>
                确认创建
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default TopicHall;
