import { useEffect, useState } from "react";
import { templatesApi, Template } from "@/api/templates";
import {
  DocumentTextIcon,
  PencilIcon,
  TrashIcon,
  EyeIcon,
} from "@heroicons/react/24/outline";
import TemplateFormModal from "@/components/features/Templates/TemplateFormModal";
import TemplatePreviewModal from "@/components/features/Templates/TemplatePreviewModal";

export default function TemplatesList() {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);
  const [showFormModal, setShowFormModal] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<Template | null>(null);
  const [previewingTemplate, setPreviewingTemplate] = useState<Template | null>(
    null
  );

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    setLoading(true);
    try {
      const data = await templatesApi.list();
      setTemplates(data);
    } catch (error) {
      console.error("Failed to load templates:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Xóa template này?")) return;

    try {
      await templatesApi.delete(id);
      loadTemplates();
    } catch (error) {
      alert("Xóa thất bại");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Templates</h1>
          <p className="text-gray-600 mt-1">
            Quản lý mẫu nội dung có thể tái sử dụng
          </p>
        </div>
        <button
          onClick={() => setShowFormModal(true)}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
        >
          + Tạo Template
        </button>
      </div>

      {templates.length === 0 ? (
        <div className="text-center py-12">
          <DocumentTextIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500 text-lg">Chưa có template nào</p>
          <button
            onClick={() => setShowFormModal(true)}
            className="mt-4 text-blue-600 hover:text-blue-700 font-medium"
          >
            Tạo template đầu tiên →
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {templates.map((template) => (
            <div
              key={template.id}
              className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6"
            >
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {template.name}
              </h3>

              <div className="bg-gray-50 rounded p-3 mb-4 max-h-32 overflow-y-auto">
                <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                  {template.content}
                </pre>
              </div>

              <p className="text-xs text-gray-500 mb-4">
                Tạo: {new Date(template.created_at).toLocaleDateString("vi-VN")}
              </p>

              <div className="flex gap-2">
                <button
                  onClick={() => setPreviewingTemplate(template)}
                  className="flex-1 px-3 py-2 bg-green-100 text-green-700 rounded hover:bg-green-200 transition-colors text-sm font-medium flex items-center justify-center gap-1"
                >
                  <EyeIcon className="w-4 h-4" />
                  Preview
                </button>
                <button
                  onClick={() => setEditingTemplate(template)}
                  className="px-3 py-2 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors"
                >
                  <PencilIcon className="w-4 h-4" />
                </button>
                <button
                  onClick={() => handleDelete(template.id)}
                  className="px-3 py-2 bg-red-100 text-red-700 rounded hover:bg-red-200 transition-colors"
                >
                  <TrashIcon className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <TemplateFormModal
        isOpen={showFormModal || !!editingTemplate}
        onClose={() => {
          setShowFormModal(false);
          setEditingTemplate(null);
        }}
        onSuccess={() => {
          setShowFormModal(false);
          setEditingTemplate(null);
          loadTemplates();
        }}
        template={editingTemplate}
      />

      {previewingTemplate && (
        <TemplatePreviewModal
          template={previewingTemplate}
          isOpen={!!previewingTemplate}
          onClose={() => setPreviewingTemplate(null)}
        />
      )}
    </div>
  );
}
