import { useState, FormEvent, useEffect } from "react";
import { templatesApi } from "@/api/templates";
import type { Template, TemplateCreateInput } from "@/types/template";
import { XMarkIcon } from "@heroicons/react/24/outline";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  template?: Template | null;
}

export default function TemplateFormModal({
  isOpen,
  onClose,
  onSuccess,
  template,
}: Props) {
  const [formData, setFormData] = useState<TemplateCreateInput>({
    name: "",
    content: "",
    metadata: {},
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      if (template) {
        setFormData({
          name: template.name,
          content: template.content,
          metadata: template.metadata || {},
        });
      } else {
        setFormData({
          name: "",
          content: "",
          metadata: {},
        });
      }
    }
  }, [isOpen, template]);

  if (!isOpen) return null;

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    if (!formData.name.trim() || !formData.content.trim()) {
      alert("Vui lòng nhập đầy đủ thông tin");
      return;
    }

    setLoading(true);
    try {
      if (template) {
        await templatesApi.update(template.id, formData);
      } else {
        await templatesApi.create(formData);
      }
      onSuccess();
    } catch (error: any) {
      alert(error.response?.data?.detail || "Lưu template thất bại");
    } finally {
      setLoading(false);
    }
  };

  const variables = [
    { key: "{{title}}", label: "Tiêu đề" },
    { key: "{{content}}", label: "Nội dung" },
    { key: "{{date}}", label: "Ngày tháng" },
    { key: "{{author}}", label: "Tác giả" },
    { key: "{{url}}", label: "Đường dẫn" },
    { key: "{{price}}", label: "Giá" },
    { key: "{{discount}}", label: "Giảm giá" },
  ];

  const insertVariable = (variable: string) => {
    const textarea = document.querySelector(
      'textarea[name="content"]'
    ) as HTMLTextAreaElement;
    if (textarea) {
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const text = formData.content;
      const before = text.substring(0, start);
      const after = text.substring(end);

      setFormData({
        ...formData,
        content: before + variable + after,
      });

      // Set cursor position
      setTimeout(() => {
        textarea.focus();
        textarea.selectionStart = textarea.selectionEnd =
          start + variable.length;
      }, 0);
    } else {
      setFormData({
        ...formData,
        content: formData.content + ` ${variable}`,
      });
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center p-6 border-b sticky top-0 bg-white z-10">
          <h2 className="text-xl font-bold text-gray-900">
            {template ? "Chỉnh sửa Template" : "Tạo Template Mới"}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <XMarkIcon className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tên Template <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) =>
                setFormData({ ...formData, name: e.target.value })
              }
              placeholder="Ví dụ: Bài đăng khuyến mãi"
              className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nội dung Template <span className="text-red-500">*</span>
            </label>
            <textarea
              name="content"
              value={formData.content}
              onChange={(e) =>
                setFormData({ ...formData, content: e.target.value })
              }
              placeholder="Nhập nội dung với biến động..."
              rows={12}
              className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
              required
            />
            <p className="text-xs text-gray-500 mt-1">
              Click vào biến bên dưới để chèn vào nội dung
            </p>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-sm font-medium text-blue-900 mb-3">
              📌 Biến động có sẵn:
            </p>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              {variables.map((variable) => (
                <button
                  key={variable.key}
                  type="button"
                  onClick={() => insertVariable(variable.key)}
                  className="bg-white border border-blue-300 text-blue-700 px-3 py-2 rounded text-sm hover:bg-blue-100 transition-colors text-left"
                  title={`Chèn ${variable.label}`}
                >
                  <div className="font-mono text-xs">{variable.key}</div>
                  <div className="text-xs text-gray-600">{variable.label}</div>
                </button>
              ))}
            </div>
          </div>

          <div className="flex gap-4 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
            >
              Hủy
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium transition-colors"
            >
              {loading ? "Đang lưu..." : template ? "Cập nhật" : "Tạo mới"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
