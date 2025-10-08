import { apiClient } from "./client";
import type {
  Template,
  TemplateCreateInput,
  TemplateUpdateInput,
} from "@/types/template";

export const templatesApi = {
  list: async (params?: { category?: string }): Promise<Template[]> => {
    const response = await apiClient.get<Template[]>("/templates", {
      params,
    });
    return response.data;
  },

  getById: async (id: number): Promise<Template> => {
    const response = await apiClient.get<Template>(`/templates/${id}`);
    return response.data;
  },

  create: async (data: TemplateCreateInput): Promise<Template> => {
    const response = await apiClient.post<Template>("/templates", data);
    return response.data;
  },

  update: async (id: number, data: TemplateUpdateInput): Promise<Template> => {
    const response = await apiClient.patch<Template>(`/templates/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/templates/${id}`);
  },

  preview: async (
    id: number,
    variables: Record<string, any>
  ): Promise<{ rendered: string }> => {
    const response = await apiClient.post<{ rendered: string }>(
      `/templates/${id}/preview`,
      variables
    );
    return response.data;
  },
};
