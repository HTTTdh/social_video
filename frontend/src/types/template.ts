export interface Template {
  id: number;
  name: string;
  category: string;
  content: string;
  variables: string[];
  created_at: string;
  updated_at: string;
}

export interface TemplateCreateInput {
  name: string;
  category: string;
  content: string;
}

export interface TemplateUpdateInput {
  name?: string;
  category?: string;
  content?: string;
}
