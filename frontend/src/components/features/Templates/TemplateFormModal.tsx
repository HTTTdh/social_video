import { useState, FormEvent } from "react";
import { templatesApi } from "@/api/templates";
import type { Template } from "@/types/template";
import { XMarkIcon } from "@heroicons/react/24/outline";

interface Props {
  template: Template;
  isOpen: boolean;
  onClose: () => void;
}

export default function TemplatePreviewModal({
  template,
  isOpen,
  onClose,
}: Props) {
  const [variables, setVariables] = useState<Record<string, string>>({
    title: "Khuyến mãi mùa hè",
    content: "Giảm giá 50% tất cả sản phẩm",
    date: new Date().toLocaleDateString("vi-VN"),
    author: "Admin",
    url: "https://example.com",
  });
  const [preview, setPreview] = useState("");
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handlePreview = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const result = await templatesApi.preview(template.id, variables);
      setPreview(result.rendered);
    } catch (error: any) {
      alert(error.response?.data?.detail || "Preview thất bại");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center p-6 border-b sticky top-0 bg-white z-10">
          <h2 className="text-xl font-bold text-gray-900">
            Preview: {template.name}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <XMarkIcon className="w-6 h-6" />
          </button>
        </div>

        <div className="p-6 grid md:grid-cols-2 gap-6">
          {/* Left: Variables Input */}
          <div>
            <h3 className="text-lg font-semibold mb-4 text-gray-900">
              Nhập giá trị biến:
            </h3>
            <form onSubmit={handlePreview} className="space-y-3">
              {Object.keys(variables).map((key) => (
                <div key={key}>
                  <label className="block text-sm font-medium text-gray-700 mb-1 capitalize">
                    {key}
                  </label>
                  <input
                    type="text"
                    value={variables[key]}
                    onChange={(e) =>
                      setVariables({ ...variables, [key]: e.target.value })
                    }
                    className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              ))}

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium transition-colors"
              >
                {loading ? "Đang xử lý..." : "Xem Preview"}
              </button>
            </form>
          </div>

          {/* Right: Preview Output */}
          <div>
            <h3 className="text-lg font-semibold mb-4 text-gray-900">
              Kết quả:
            </h3>
            {preview ? (
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 min-h-[300px]">
                <div
                  className="prose prose-sm max-w-none"
                  dangerouslySetInnerHTML={{ __html: preview }}
                />
              </div>
            ) : (
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 h-[300px] flex items-center justify-center text-center text-gray-500">
                <div>
                  <svg
                    className="w-16 h-16 mx-auto mb-2 text-gray-400"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={1.5}
                      d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                    />
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={1.5}
                      d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                    />
                  </svg>
                  <p>Nhấn "Xem Preview" để xem kết quả</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}