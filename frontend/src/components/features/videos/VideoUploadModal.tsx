import { useState, FormEvent } from "react";
import { videosApi } from "@/api/videos";
import { XMarkIcon, ArrowUpTrayIcon } from "@heroicons/react/24/outline";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export default function VideoUploadModal({
  isOpen,
  onClose,
  onSuccess,
}: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [preview, setPreview] = useState<string>("");

  if (!isOpen) return null;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) return;

    // Validate video file
    if (!selectedFile.type.startsWith("video/")) {
      alert("Vui lòng chọn file video!");
      return;
    }

    // Check file size (max 500MB)
    const maxSize = 500 * 1024 * 1024; // 500MB
    if (selectedFile.size > maxSize) {
      alert("File quá lớn! Tối đa 500MB");
      return;
    }

    setFile(selectedFile);
    setTitle(selectedFile.name.replace(/\.[^/.]+$/, "")); // Remove extension

    // Generate video preview
    const videoUrl = URL.createObjectURL(selectedFile);
    setPreview(videoUrl);
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    if (!file) {
      alert("Vui lòng chọn video");
      return;
    }

    setUploading(true);
    setProgress(0);

    try {
      await videosApi.upload(
        file, // ✅ truyền 1 file, API tự bọc thành mảng
        {
          title: title.trim() || file.name,
          // description hiện backend không nhận -> bỏ cũng được
        },
        (p) => setProgress(p)
      );

      alert("Upload video thành công!");
      onSuccess();

      // Reset form
      setFile(null);
      setTitle("");
      setDescription("");
      setPreview("");
      if (preview) URL.revokeObjectURL(preview);
    } catch (error: any) {
      console.error("Upload error:", error);
      alert(error.response?.data?.detail || "Upload thất bại");
    } finally {
      setUploading(false);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    if (bytes < 1024 * 1024 * 1024)
      return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`;
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b sticky top-0 bg-white z-10">
          <h2 className="text-xl font-bold text-gray-900">Upload Video</h2>
          <button
            onClick={onClose}
            disabled={uploading}
            className="text-gray-400 hover:text-gray-600 transition-colors disabled:opacity-50"
          >
            <XMarkIcon className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          {/* File Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Chọn video <span className="text-red-500">*</span>
            </label>
            <div className="relative">
              <input
                type="file"
                onChange={handleFileChange}
                accept="video/*"
                className="hidden"
                id="video-upload"
                disabled={uploading}
              />
              <label
                htmlFor="video-upload"
                className={`flex flex-col items-center justify-center gap-3 w-full px-4 py-10 border-2 border-dashed rounded-lg transition-all ${
                  file
                    ? "border-blue-500 bg-blue-50"
                    : "border-gray-300 hover:border-blue-500 hover:bg-blue-50"
                } ${
                  uploading ? "cursor-not-allowed opacity-50" : "cursor-pointer"
                }`}
              >
                <ArrowUpTrayIcon className="w-12 h-12 text-gray-400" />
                <div className="text-center">
                  <span className="text-gray-600 font-medium block mb-1">
                    {file ? file.name : "Click để chọn video"}
                  </span>
                  {file && (
                    <span className="text-sm text-gray-500">
                      {formatFileSize(file.size)}
                    </span>
                  )}
                  {!file && (
                    <span className="text-xs text-gray-400 block mt-1">
                      Định dạng: MP4, MOV, AVI, MKV... (Tối đa 500MB)
                    </span>
                  )}
                </div>
              </label>
            </div>
          </div>

          {/* Video Preview */}
          {preview && (
            <div className="border border-gray-200 rounded-lg p-4 bg-gray-50">
              <p className="text-sm font-medium text-gray-700 mb-2">
                Preview video:
              </p>
              <video
                src={preview}
                controls
                className="w-full max-h-80 rounded-lg bg-black"
              />
            </div>
          )}

          {/* Title */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tiêu đề video <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Nhập tiêu đề cho video"
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={uploading}
              required
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Mô tả (tuỳ chọn)
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Nhập mô tả cho video..."
              rows={4}
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              disabled={uploading}
            />
          </div>

          {/* Upload Progress */}
          {uploading && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex justify-between text-sm text-blue-900 mb-2">
                <span className="font-medium">Đang upload video...</span>
                <span className="font-bold">{progress}%</span>
              </div>
              <div className="w-full bg-blue-200 rounded-full h-3 overflow-hidden">
                <div
                  className="bg-blue-600 h-3 rounded-full transition-all duration-300 ease-out"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <p className="text-xs text-blue-700 mt-2">
                Vui lòng không đóng cửa sổ này...
              </p>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3 pt-4 border-t">
            <button
              type="button"
              onClick={onClose}
              disabled={uploading}
              className="px-6 py-2.5 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Hủy
            </button>
            <button
              type="submit"
              disabled={!file || uploading}
              className="flex-1 bg-blue-600 text-white py-2.5 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium transition-colors"
            >
              {uploading ? `Đang upload... ${progress}%` : "Upload Video"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
