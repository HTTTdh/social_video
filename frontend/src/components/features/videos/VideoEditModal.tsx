import { useState, FormEvent, useEffect } from "react";
import { videosApi } from "@/api/videos";
import type { Video } from "@/types/video";
import {
  XMarkIcon,
  ScissorsIcon,
  PhotoIcon as WatermarkIcon,
} from "@heroicons/react/24/outline";

interface Props {
  video: Video;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export default function VideoEditModal({
  video,
  isOpen,
  onClose,
  onSuccess,
}: Props) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [saving, setSaving] = useState(false);
  const [activeTab, setActiveTab] = useState<"info" | "trim" | "watermark">(
    "info"
  );

  // Trim state
  const [startTime, setStartTime] = useState(0);
  const [endTime, setEndTime] = useState(0);
  const [trimming, setTrimming] = useState(false);

  // Watermark state
  const [watermarkFile, setWatermarkFile] = useState<File | null>(null);
  const [watermarkPosition, setWatermarkPosition] = useState<
    "top-left" | "top-right" | "bottom-left" | "bottom-right" | "center"
  >("bottom-right");
  const [watermarkOpacity, setWatermarkOpacity] = useState(0.8);
  const [addingWatermark, setAddingWatermark] = useState(false);

  useEffect(() => {
    if (isOpen && video) {
      setTitle(video.title);
      setDescription(video.description || "");
      setEndTime(video.duration || 0);
    }
  }, [isOpen, video]);

  if (!isOpen) return null;

  const handleUpdateInfo = async (e: FormEvent) => {
    e.preventDefault();

    setSaving(true);
    try {
      await videosApi.update(video.id, {
        title: title.trim(),
        description: description.trim(),
      });

      alert("Cập nhật thông tin thành công!");
      onSuccess();
    } catch (error: any) {
      console.error("Update error:", error);
      alert(error.response?.data?.detail || "Cập nhật thất bại");
    } finally {
      setSaving(false);
    }
  };

  const handleTrim = async () => {
    if (startTime >= endTime) {
      alert("Thời gian bắt đầu phải nhỏ hơn thời gian kết thúc");
      return;
    }

    if (startTime === 0 && endTime === video.duration) {
      alert("Vui lòng chọn khoảng thời gian cần cắt");
      return;
    }

    setTrimming(true);
    try {
      await videosApi.trim({
        video_id: video.id,
        start: startTime, // ✅ đổi tên field
        end: endTime, // ✅ đổi tên field
      });

      alert("Cắt video thành công!");
      onSuccess();
    } catch (error: any) {
      console.error("Trim error:", error);
      alert(error.response?.data?.detail || "Cắt video thất bại");
    } finally {
      setTrimming(false);
    }
  };

  const positionToXY = (pos: typeof watermarkPosition, margin = 20) => {
    // giá trị tương đối; backend nên hiểu theo pixel hoặc tỉ lệ tùy định nghĩa
    switch (pos) {
      case "top-left":
        return { x: margin, y: margin };
      case "top-right":
        return { x: 1920 - margin, y: margin }; // giả định FullHD, điều chỉnh nếu backend dùng tỉ lệ
      case "bottom-left":
        return { x: margin, y: 1080 - margin };
      case "bottom-right":
        return { x: 1920 - margin, y: 1080 - margin };
      case "center":
        return { x: 960, y: 540 };
    }
  };

  const handleAddWatermark = async () => {
    if (!watermarkFile) {
      alert("Vui lòng chọn ảnh watermark");
      return;
    }

    setAddingWatermark(true);
    try {
      // Upload watermark first
      const formData = new FormData();
      formData.append("file", watermarkFile);

      // This is simplified - you may need a separate endpoint
      // For now, assume watermark is already uploaded
      const watermarkPath = "/path/to/watermark.png";

      const { x, y } = positionToXY(watermarkPosition);
      await videosApi.addWatermark({
        video_id: video.id,
        watermark_path: watermarkPath,
        x, // ✅ backend mong x,y
        y, // ✅ backend mong x,y
        opacity: watermarkOpacity,
      });

      alert("Thêm watermark thành công!");
      onSuccess();
    } catch (error: any) {
      console.error("Watermark error:", error);
      alert(error.response?.data?.detail || "Thêm watermark thất bại");
    } finally {
      setAddingWatermark(false);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const tabs = [
    { id: "info", label: "Thông tin", icon: "📝" },
    { id: "trim", label: "Cắt video", icon: "✂️" },
    { id: "watermark", label: "Watermark", icon: "🏷️" },
  ];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b sticky top-0 bg-white z-10">
          <div>
            <h2 className="text-xl font-bold text-gray-900">Chỉnh sửa Video</h2>
            <p className="text-sm text-gray-600 mt-1">{video.title}</p>
          </div>
          <button
            onClick={onClose}
            disabled={saving || trimming || addingWatermark}
            className="text-gray-400 hover:text-gray-600 transition-colors disabled:opacity-50"
          >
            <XMarkIcon className="w-6 h-6" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b px-6">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-4 py-3 font-medium text-sm transition-colors relative ${
                activeTab === tab.id
                  ? "text-blue-600 border-b-2 border-blue-600"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="p-6">
          {/* Info Tab */}
          {activeTab === "info" && (
            <form onSubmit={handleUpdateInfo} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tiêu đề <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                  disabled={saving}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Mô tả
                </label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={5}
                  className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  disabled={saving}
                />
              </div>

              <button
                type="submit"
                disabled={saving}
                className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium transition-colors"
              >
                {saving ? "Đang lưu..." : "Lưu thay đổi"}
              </button>
            </form>
          )}

          {/* Trim Tab */}
          {activeTab === "trim" && (
            <div className="space-y-4">
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <p className="text-sm text-yellow-900">
                  ⚠️ Cắt video sẽ tạo ra một video mới. Video gốc vẫn được giữ
                  nguyên.
                </p>
              </div>

              {video.duration && (
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600 mb-2">
                    Độ dài video: <strong>{formatTime(video.duration)}</strong>
                  </p>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Thời gian bắt đầu: {formatTime(startTime)}
                </label>
                <input
                  type="range"
                  min={0}
                  max={video.duration || 100}
                  step={1}
                  value={startTime}
                  onChange={(e) => setStartTime(Number(e.target.value))}
                  className="w-full"
                  disabled={trimming}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Thời gian kết thúc: {formatTime(endTime)}
                </label>
                <input
                  type="range"
                  min={0}
                  max={video.duration || 100}
                  step={1}
                  value={endTime}
                  onChange={(e) => setEndTime(Number(e.target.value))}
                  className="w-full"
                  disabled={trimming}
                />
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm text-blue-900">
                  📹 Đoạn video mới: <strong>{formatTime(startTime)}</strong> →{" "}
                  <strong>{formatTime(endTime)}</strong> (
                  {formatTime(endTime - startTime)})
                </p>
              </div>

              <button
                onClick={handleTrim}
                disabled={trimming || startTime >= endTime}
                className="w-full bg-green-600 text-white py-3 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium transition-colors flex items-center justify-center gap-2"
              >
                <ScissorsIcon className="w-5 h-5" />
                {trimming ? "Đang xử lý..." : "Cắt video"}
              </button>
            </div>
          )}

          {/* Watermark Tab */}
          {activeTab === "watermark" && (
            <div className="space-y-4">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm text-blue-900">
                  💡 Thêm logo hoặc văn bản watermark vào video của bạn
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Chọn ảnh watermark (PNG)
                </label>
                <input
                  type="file"
                  accept="image/png"
                  onChange={(e) =>
                    setWatermarkFile(e.target.files?.[0] || null)
                  }
                  className="w-full border border-gray-300 rounded-lg px-4 py-2"
                  disabled={addingWatermark}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Vị trí
                </label>
                <select
                  value={watermarkPosition}
                  onChange={(e) => setWatermarkPosition(e.target.value as any)}
                  className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  disabled={addingWatermark}
                >
                  <option value="top-left">Trên - Trái</option>
                  <option value="top-right">Trên - Phải</option>
                  <option value="bottom-left">Dưới - Trái</option>
                  <option value="bottom-right">Dưới - Phải</option>
                  <option value="center">Giữa</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Độ mờ: {Math.round(watermarkOpacity * 100)}%
                </label>
                <input
                  type="range"
                  min={0}
                  max={1}
                  step={0.1}
                  value={watermarkOpacity}
                  onChange={(e) => setWatermarkOpacity(Number(e.target.value))}
                  className="w-full"
                  disabled={addingWatermark}
                />
              </div>

              <button
                onClick={handleAddWatermark}
                disabled={!watermarkFile || addingWatermark}
                className="w-full bg-purple-600 text-white py-3 rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium transition-colors flex items-center justify-center gap-2"
              >
                <WatermarkIcon className="w-5 h-5" />
                {addingWatermark ? "Đang xử lý..." : "Thêm Watermark"}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
