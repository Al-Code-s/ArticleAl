export interface Topic {
  id: string;
  user_id: string;
  title: string;
  major?: string;
  education_level?: string;
  paper_type?: string;
  description?: string;
  feasibility_score?: number;
  keywords?: string[];
  is_used: boolean;
  created_at: string;
}

export interface GenerateTopicDto {
  major: string;
  educationLevel: string;
  paperType: string;
  count?: number;
}
