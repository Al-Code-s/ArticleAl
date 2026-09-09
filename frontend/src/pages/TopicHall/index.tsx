import { useState } from 'react';
import {
  Card,
  Button,
  Form,
  Select,
  InputNumber,
  Table,
  Tag,
  Space,
  message,
  Modal,
  Spin,
} from 'antd';
import { PlusOutlined, RocketOutlined } from '@ant-design/icons';
import { useMutation } from '@tanstack/react-query';
import { topicApi } from '@services/api/topic';
import { useProjectStore } from '@stores/projectStore';
import { useNavigate } from 'react-router-dom';
import type { Topic } from '../../types/topic';
import './TopicHall.css';

const TopicHall = () => {
  const [form] = Form.useForm();
  const navigate = useNavigate();
  const { addProject, setActiveProject } = useProjectStore();
  const [topics, setTopics] = useState<Topic[]>([]);
  const [selectedTopic, setSelectedTopic] = useState<Topic | null>(null);
  const [createModalVisible, setCreateModalVisible] = useState(false);

  // 生成题目
  const generateMutation = useMutation({
    mutationFn: topicApi.generateTopics,
    onSuccess: (res: any) => {
      // Backend returns array directly, axios interceptor already unwrapped response.data
      const newTopics = Array.isArray(res) ? res : [];
      setTopics(newTopics);
      message.success(`成功生成 ${newTopics.length} 个题目`);
    },
    onError: () => {
      message.error('生成题目失败');
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
          initialValues={{ count: 5, educationLevel: '本科', paperType: '毕业论文' }}
        >
          <Form.Item
            name="major"
            label="专业"
            rules={[{ required: true, message: '请输入专业' }]}
          >
            <Select
              style={{ width: 200 }}
              placeholder="选择专业"
              showSearch
              filterOption={(input, option) => {
                const label = option?.label || option?.children;
                return String(label).toLowerCase().includes(input.toLowerCase());
              }}
            >
              <Select.Option value="计算机科学与技术">计算机科学与技术</Select.Option>
              <Select.Option value="软件工程">软件工程</Select.Option>
              <Select.Option value="人工智能">人工智能</Select.Option>
              <Select.Option value="大数据技术">大数据技术</Select.Option>
              <Select.Option value="网络工程">网络工程</Select.Option>
              <Select.Option value="信息安全">信息安全</Select.Option>
              <Select.Option value="物联网工程">物联网工程</Select.Option>
              <Select.Option value="数字媒体技术">数字媒体技术</Select.Option>
              <Select.Option value="电子信息工程">电子信息工程</Select.Option>
              <Select.Option value="通信工程">通信工程</Select.Option>
              <Select.Option value="自动化">自动化</Select.Option>
              <Select.Option value="电气工程">电气工程</Select.Option>
              <Select.Option value="机械工程">机械工程</Select.Option>
              <Select.Option value="土木工程">土木工程</Select.Option>
              <Select.Option value="建筑学">建筑学</Select.Option>
              <Select.Option value="化学工程">化学工程</Select.Option>
              <Select.Option value="材料科学与工程">材料科学与工程</Select.Option>
              <Select.Option value="生物工程">生物工程</Select.Option>
              <Select.Option value="环境工程">环境工程</Select.Option>
              <Select.Option value="工商管理">工商管理</Select.Option>
              <Select.Option value="市场营销">市场营销</Select.Option>
              <Select.Option value="会计学">会计学</Select.Option>
              <Select.Option value="财务管理">财务管理</Select.Option>
              <Select.Option value="人力资源管理">人力资源管理</Select.Option>
              <Select.Option value="金融学">金融学</Select.Option>
              <Select.Option value="国际经济与贸易">国际经济与贸易</Select.Option>
              <Select.Option value="经济学">经济学</Select.Option>
              <Select.Option value="法学">法学</Select.Option>
              <Select.Option value="社会学">社会学</Select.Option>
              <Select.Option value="心理学">心理学</Select.Option>
              <Select.Option value="教育学">教育学</Select.Option>
              <Select.Option value="学前教育">学前教育</Select.Option>
              <Select.Option value="汉语言文学">汉语言文学</Select.Option>
              <Select.Option value="英语">英语</Select.Option>
              <Select.Option value="新闻学">新闻学</Select.Option>
              <Select.Option value="广告学">广告学</Select.Option>
              <Select.Option value="历史学">历史学</Select.Option>
              <Select.Option value="哲学">哲学</Select.Option>
              <Select.Option value="数学与应用数学">数学与应用数学</Select.Option>
              <Select.Option value="物理学">物理学</Select.Option>
              <Select.Option value="化学">化学</Select.Option>
              <Select.Option value="生物科学">生物科学</Select.Option>
              <Select.Option value="地理科学">地理科学</Select.Option>
              <Select.Option value="临床医学">临床医学</Select.Option>
              <Select.Option value="护理学">护理学</Select.Option>
              <Select.Option value="药学">药学</Select.Option>
              <Select.Option value="中医学">中医学</Select.Option>
              <Select.Option value="口腔医学">口腔医学</Select.Option>
              <Select.Option value="公共事业管理">公共事业管理</Select.Option>
              <Select.Option value="行政管理">行政管理</Select.Option>
              <Select.Option value="旅游管理">旅游管理</Select.Option>
              <Select.Option value="酒店管理">酒店管理</Select.Option>
              <Select.Option value="农学">农学</Select.Option>
              <Select.Option value="园艺">园艺</Select.Option>
              <Select.Option value="动物医学">动物医学</Select.Option>
              <Select.Option value="林学">林学</Select.Option>
              <Select.Option value="艺术设计">艺术设计</Select.Option>
              <Select.Option value="音乐学">音乐学</Select.Option>
              <Select.Option value="美术学">美术学</Select.Option>
              <Select.Option value="舞蹈学">舞蹈学</Select.Option>
              <Select.Option value="体育教育">体育教育</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item name="educationLevel" label="学历">
            <Select style={{ width: 120 }}>
              <Select.Option value="专科">专科</Select.Option>
              <Select.Option value="本科">本科</Select.Option>
              <Select.Option value="硕士">硕士</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item name="paperType" label="类型">
            <Select style={{ width: 120 }}>
              <Select.Option value="毕业论文">毕业论文</Select.Option>
              <Select.Option value="学术论文">学术论文</Select.Option>
              <Select.Option value="研究报告">研究报告</Select.Option>
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
