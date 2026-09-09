export interface Project {
  id: string;
  user_id: string;
  topic_id?: string;
  title: string;
  major?: string;
  education_level?: string;
  paper_type?: string;
  word_count: number;
  status: 'created' | 'in_progress' | 'completed' | 'archived';
  current_stage?: string;
  agent_session_id?: string;
  agent_status: 'idle' | 'running' | 'stopped' | 'error';
  created_at: string;
  updated_at: string;
}

export interface CreateProjectDto {
  title: string;
  major?: string;
  education_level?: string;
  paper_type?: string;
  word_count?: number;
}

export interface UpdateProjectDto {
  title?: string;
  word_count?: number;
  status?: string;
}

export interface Outline {
  id: string;
  project_id: string;
  content: any;
  version: number;
  is_current: boolean;
  generated_by?: 'ai' | 'manual' | 'agent';
  created_at: string;
}

export interface Reference {
  id: string;
  project_id: string;
  title: string;
  authors?: string[];
  journal?: string;
  year?: number;
  doi?: string;
  cnki_url?: string;
  abstract?: string;
  keywords?: string[];
  citation_format?: string;
  is_selected: boolean;
  selection_order?: number;
  created_at: string;
}
