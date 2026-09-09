import { useState } from 'react';
import { Card, Table, Button, Space, Tag, Modal, Form, Input, InputNumber, Select, message } from 'antd';
import { PlusOutlined, FolderOpenOutlined, DeleteOutlined } from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { projectApi } from '@services/api/project';
import { useProjectStore } from '@stores/projectStore';
import { useNavigate } from 'react-router-dom';
import type { Project } from '../../types/project';
import './ProjectList.css';
import { EDUCATION_LEVELS, MAJORS, PAPER_TYPES } from '../../constants/academic';

const ProjectList = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { setActiveProject } = useProjectStore();
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [form] = Form.useForm();

  // 获取项目列表
  const { data: projectsData, isLoading } = useQuery({
    queryKey: ['projects'],
    queryFn: () => projectApi.getProjects(),
  });

  // 创建项目
  const createMutation = useMutation({
    mutationFn: projectApi.createProject,
    onSuccess: (res: any) => {
      // Backend returns project object directly
      message.success('项目创建成功');
      setCreateModalVisible(false);
      form.resetFields();
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      navigate(`/projects/${res.id}`);
    },
    onError: () => {
      message.error('创建项目失败');
    },
  });

  // 删除项目
  const deleteMutation = useMutation({
    mutationFn: projectApi.deleteProject,
    onSuccess: () => {
      message.success('项目已删除');
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
    onError: () => {
      message.error('删除项目失败');
    },
  });

  const handleCreate = (values: any) => {
    createMutation.mutate(values);
  };

  const handleDelete = (id: string) => {
    Modal.confirm({
      title: '确认删除',
      content: '删除项目后无法恢复，确定要删除吗？',
      onOk: () => deleteMutation.mutate(id),
    });
  };

  const handleOpen = (project: Project) => {
    setActiveProject(project.id);
    navigate(`/projects/${project.id}`);
  };

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

  const columns = [
    {
      title: '项目名称',
      dataIndex: 'title',
      key: 'title',
      width: '30%',
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
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: '10%',
      render: (status: string) => getStatusTag(status),
    },
    {
      title: '字数',
      dataIndex: 'word_count',
      key: 'word_count',
      width: '10%',
      render: (count: number) => count ? `${count.toLocaleString()} 字` : '-',
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: '15%',
      render: (date: string) => new Date(date).toLocaleDateString(),
    },
    {
      title: '操作',
      key: 'action',
      width: '10%',
      render: (_: any, record: Project) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<FolderOpenOutlined />}
            onClick={() => handleOpen(record)}
          >
            打开
          </Button>
          <Button
            type="link"
            size="small"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record.id)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];

  const projects = (projectsData as any)?.items || [];

  return (
    <div className="project-list">
      <Card
        title="我的项目"
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setCreateModalVisible(true)}
          >
            新建项目
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={projects}
          rowKey="id"
          loading={isLoading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Modal
        title="新建项目"
        open={createModalVisible}
        onCancel={() => {
          setCreateModalVisible(false);
          form.resetFields();
        }}
        footer={null}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreate}
          initialValues={{ word_count: 10000 }}
        >
          <Form.Item
            name="title"
            label="项目名称"
            rules={[{ required: true, message: '请输入项目名称' }]}
          >
            <Input placeholder="请输入项目名称" />
          </Form.Item>

          <Form.Item name="major" label="专业" rules={[{ required: true, message: '请选择专业' }]}>
            <Select showSearch placeholder="请选择专业" optionFilterProp="label" options={MAJORS.map((major) => ({ value: major, label: major }))} />
          </Form.Item>

          <Form.Item name="education_level" label="学历" rules={[{ required: true, message: '请选择学历' }]}>
            <Select placeholder="请选择学历" options={EDUCATION_LEVELS.map((level) => ({ value: level, label: level }))} />
          </Form.Item>

          <Form.Item name="paper_type" label="论文类型" rules={[{ required: true, message: '请选择论文类型' }]}>
            <Select placeholder="请选择论文类型" optionLabelProp="label">
              {PAPER_TYPES.map((type) => (
                <Select.Option key={type.value} value={type.value} label={type.value}>
                  <div>{type.value}<div style={{ fontSize: 12, color: '#999' }}>{type.help}</div></div>
                </Select.Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="word_count"
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
              <Button type="primary" htmlType="submit" loading={createMutation.isPending}>
                创建
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default ProjectList;
