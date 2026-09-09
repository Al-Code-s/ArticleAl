-- ArticleAI Database Initialization Script
-- PostgreSQL 16+

-- 启用UUID扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ==================== 用户表 ====================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);

-- ==================== AI配置表 ====================
CREATE TABLE ai_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    config_name VARCHAR(50) NOT NULL,
    provider VARCHAR(20) NOT NULL CHECK (provider IN ('claude', 'openai', 'custom')),
    api_key VARCHAR(255) NOT NULL,
    model_name VARCHAR(50) NOT NULL,
    base_url VARCHAR(255),
    max_tokens INTEGER DEFAULT 4096,
    temperature DECIMAL(3,2) DEFAULT 0.7 CHECK (temperature >= 0 AND temperature <= 2),
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, config_name)
);

CREATE INDEX idx_ai_configs_user_id ON ai_configs(user_id);
CREATE INDEX idx_ai_configs_default ON ai_configs(user_id, is_default) WHERE is_default = TRUE;

-- ==================== 选题表 ====================
CREATE TABLE topics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    major VARCHAR(100),
    education_level VARCHAR(50),
    paper_type VARCHAR(50),
    description TEXT,
    feasibility_score INTEGER CHECK (feasibility_score >= 0 AND feasibility_score <= 100),
    keywords TEXT[],
    is_used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_topics_user_id ON topics(user_id);
CREATE INDEX idx_topics_unused ON topics(user_id, is_used) WHERE is_used = FALSE;

-- ==================== 项目表 ====================
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    topic_id UUID REFERENCES topics(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    major VARCHAR(100),
    education_level VARCHAR(50),
    paper_type VARCHAR(50),
    word_count INTEGER DEFAULT 10000 CHECK (word_count > 0),
    status VARCHAR(20) DEFAULT 'created' CHECK (status IN ('created', 'in_progress', 'completed', 'archived')),
    current_stage VARCHAR(50),
    agent_session_id UUID,
    agent_status VARCHAR(20) DEFAULT 'idle' CHECK (agent_status IN ('idle', 'running', 'stopped', 'error')),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_projects_status ON projects(user_id, status);
CREATE INDEX idx_projects_updated ON projects(user_id, updated_at DESC);

-- ==================== 智能体会话表 ====================
CREATE TABLE agent_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    session_name VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'stopped', 'error')),
    ai_config_id UUID REFERENCES ai_configs(id) ON DELETE SET NULL,
    context JSONB DEFAULT '{}',
    total_tokens_used INTEGER DEFAULT 0,
    message_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    ended_at TIMESTAMP,
    error_message TEXT
);

CREATE INDEX idx_agent_sessions_project_id ON agent_sessions(project_id);
CREATE INDEX idx_agent_sessions_status ON agent_sessions(status) WHERE status = 'active';

-- ==================== 智能体消息表 ====================
CREATE TABLE agent_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES agent_sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    tokens_used INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_agent_messages_session_id ON agent_messages(session_id, created_at);

-- ==================== 大纲表 ====================
CREATE TABLE outlines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    content JSONB NOT NULL,
    version INTEGER DEFAULT 1,
    is_current BOOLEAN DEFAULT TRUE,
    generated_by VARCHAR(20) CHECK (generated_by IN ('ai', 'manual', 'agent')),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_outlines_project_id ON outlines(project_id);
CREATE INDEX idx_outlines_current ON outlines(project_id, is_current) WHERE is_current = TRUE;

-- ==================== 参考文献表 ====================
CREATE TABLE references (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    authors TEXT[],
    journal VARCHAR(255),
    year INTEGER,
    doi VARCHAR(100),
    cnki_url TEXT,
    abstract TEXT,
    keywords TEXT[],
    citation_format TEXT,
    is_selected BOOLEAN DEFAULT FALSE,
    selection_order INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_references_project_id ON references(project_id);
CREATE INDEX idx_references_selected ON references(project_id, is_selected, selection_order) WHERE is_selected = TRUE;

-- ==================== 文档表 ====================
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    doc_type VARCHAR(50) NOT NULL CHECK (doc_type IN ('task_book', 'proposal', 'literature_review')),
    content TEXT,
    structured_content JSONB DEFAULT '{}',
    version INTEGER DEFAULT 1,
    is_current BOOLEAN DEFAULT TRUE,
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'completed', 'exported')),
    word_count INTEGER DEFAULT 0,
    generated_by VARCHAR(20) CHECK (generated_by IN ('ai', 'manual', 'agent')),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_documents_project_id ON documents(project_id);
CREATE INDEX idx_documents_type ON documents(project_id, doc_type, is_current) WHERE is_current = TRUE;

-- ==================== 论文章节表 ====================
CREATE TABLE paper_sections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    parent_id UUID REFERENCES paper_sections(id) ON DELETE CASCADE,
    section_number VARCHAR(20),
    section_title VARCHAR(255) NOT NULL,
    content TEXT,
    order_index INTEGER NOT NULL,
    level INTEGER DEFAULT 1 CHECK (level >= 1 AND level <= 5),
    word_count INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'in_progress', 'completed', 'reviewed')),
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_paper_sections_project_id ON paper_sections(project_id, order_index);
CREATE INDEX idx_paper_sections_parent ON paper_sections(parent_id);

-- ==================== 修改记录表 ====================
CREATE TABLE revisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    target_type VARCHAR(50) NOT NULL CHECK (target_type IN ('document', 'paper_section')),
    target_id UUID NOT NULL,
    original_content TEXT,
    revised_content TEXT,
    revision_comment TEXT,
    revised_by VARCHAR(20) CHECK (revised_by IN ('ai', 'user', 'agent')),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_revisions_project_id ON revisions(project_id, created_at DESC);
CREATE INDEX idx_revisions_target ON revisions(target_type, target_id);

-- ==================== 导出记录表 ====================
CREATE TABLE export_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    export_type VARCHAR(50) NOT NULL CHECK (export_type IN ('task_book', 'proposal', 'literature_review', 'paper')),
    file_format VARCHAR(10) NOT NULL CHECK (file_format IN ('docx', 'pdf')),
    file_path VARCHAR(500),
    file_size INTEGER,
    download_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);

CREATE INDEX idx_export_records_project_id ON export_records(project_id, created_at DESC);
CREATE INDEX idx_export_records_expires ON export_records(expires_at) WHERE expires_at IS NOT NULL;

-- ==================== 任务队列表 ====================
CREATE TABLE job_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    job_type VARCHAR(50) NOT NULL,
    job_data JSONB NOT NULL DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled')),
    priority INTEGER DEFAULT 5 CHECK (priority >= 1 AND priority <= 10),
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    error_message TEXT,
    result JSONB,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_job_queue_status ON job_queue(status, priority DESC, created_at) WHERE status IN ('pending', 'processing');
CREATE INDEX idx_job_queue_project_id ON job_queue(project_id, created_at DESC);

-- ==================== 触发器函数 ====================

-- 更新updated_at时间戳
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为需要的表添加触发器
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ai_configs_updated_at BEFORE UPDATE ON ai_configs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_paper_sections_updated_at BEFORE UPDATE ON paper_sections
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 创建项目时自动标记选题为已使用
CREATE OR REPLACE FUNCTION mark_topic_as_used()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.topic_id IS NOT NULL THEN
        UPDATE topics SET is_used = TRUE WHERE id = NEW.topic_id;
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER mark_topic_used AFTER INSERT ON projects
    FOR EACH ROW EXECUTE FUNCTION mark_topic_as_used();

-- 更新智能体会话统计
CREATE OR REPLACE FUNCTION update_session_stats()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE agent_sessions
    SET
        message_count = message_count + 1,
        total_tokens_used = total_tokens_used + COALESCE(NEW.tokens_used, 0)
    WHERE id = NEW.session_id;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_session_stats_on_message AFTER INSERT ON agent_messages
    FOR EACH ROW EXECUTE FUNCTION update_session_stats();

-- ==================== 初始数据 ====================

-- 创建演示用户（可选，生产环境应删除）
-- 密码: demo123456
INSERT INTO users (username, email, password_hash) VALUES
('demo', 'demo@articleai.com', '$2b$10$CwTycUXWue0Thq9StjUM0uJ8qKnUqKqKq0FJqFqQqKqKqKqKqKqKq');

-- 完成初始化
DO $$
BEGIN
    RAISE NOTICE '==============================================';
    RAISE NOTICE 'ArticleAI Database initialized successfully!';
    RAISE NOTICE '==============================================';
END $$;
