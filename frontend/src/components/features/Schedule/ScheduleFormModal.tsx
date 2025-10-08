import { useState, FormEvent, useEffect } from "react";
import { scheduleApi } from "@/api/schedule";
import { channelsApi } from "@/api/channels";
import type { ScheduleCreateInput } from "@/types/schedule";
import type { Channel } from "@/types/channel";
import { XMarkIcon } from "@heroicons/react/24/outline";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  initialDate?: string;
}

export default function ScheduleFormModal({
  isOpen,
  onClose,
  onSuccess,
}: Props) {
  const [channels, setChannels] = useState<Channel[]>([]);
  const [formData, setFormData] = useState<ScheduleCreateInput>({
    name: "",
    cron_expression: "0 9 * * *", // 9am daily
    target_channel_ids: [],
    is_active: true,
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadChannels();
      // Reset form when opening
      setFormData({
        name: "",
        cron_expression: "0 9 * * *",
        target_channel_ids: [],
        is_active: true,
      });
    }
  }, [isOpen]);

  const loadChannels = async () => {
    try {
      const data = await channelsApi.list({ only_active: true });
      setChannels(data);
    } catch (error) {
      console.error("Failed to load channels:", error);
      alert("Không thể tải danh sách kênh");
    }
  };

  if (!isOpen) return null;

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    // Validation
    if (!formData.name.trim()) {
      alert("Vui lòng nhập tên lịch");
      return;
    }

    if (formData.target_channel_ids.length === 0) {
      alert("Vui lòng chọn ít nhất 1 kênh");
      return;
    }

    if (!formData.cron_expression.trim()) {
      alert("Vui lòng nhập cron expression");
      return;
    }

    setLoading(true);
    try {
      await scheduleApi.create(formData);
      onSuccess();
    } catch (error: any) {
      alert(error.response?.data?.detail || "Tạo lịch thất bại");
    } finally {
      setLoading(false);
    }
  };

  const cronPresets = [
    { label: "Hàng ngày 9h sáng", value: "0 9 * * *" },
    { label: "Hàng ngày 6h chiều", value: "0 18 * * *" },
    { label: "Thứ 2-6 lúc 9h", value: "0 9 * * 1-5" },
    { label: "Cuối tuần 10h", value: "0 10 * * 0,6" },
    { label: "Mỗi giờ", value: "0 * * * *" },
    { label: "Mỗi 30 phút", value: "*/30 * * * *" },
    { label: "Tùy chỉnh", value: "" },
  ];

  const toggleChannel = (channelId: number) => {
    setFormData((prev) => ({
      ...prev,
      target_channel_ids: prev.target_channel_ids.includes(channelId)
        ? prev.target_channel_ids.filter((id) => id !== channelId)
        : [...prev.target_channel_ids, channelId],
    }));
  };

  const selectAllChannels = () => {
    setFormData((prev) => ({
      ...prev,
      target_channel_ids: channels.map((c) => c.id),
    }));
  };

  const deselectAllChannels = () => {
    setFormData((prev) => ({
      ...prev,
      target_channel_ids: [],
    }));
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center p-6 border-b sticky top-0 bg-white z-10">
          <h2 className="text-xl font-bold text-gray-900">Tạo lịch đăng mới</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <XMarkIcon className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          {/* Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tên lịch <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) =>
                setFormData({ ...formData, name: e.target.value })
              }
              placeholder="Ví dụ: Đăng bài hàng ngày lúc 9h"
              className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

          {/* Cron Expression */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Thời gian đăng <span className="text-red-500">*</span>
            </label>

            {/* Presets */}
            <select
              value={formData.cron_expression}
              onChange={(e) =>
                setFormData({ ...formData, cron_expression: e.target.value })
              }
              className="w-full border border-gray-300 rounded-lg px-4 py-2 mb-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {cronPresets.map((preset) => (
                <option key={preset.value} value={preset.value}>
                  {preset.label}
                  {preset.value && ` (${preset.value})`}
                </option>
              ))}
            </select>

            {/* Custom Input */}
            <input
              type="text"
              value={formData.cron_expression}
              onChange={(e) =>
                setFormData({ ...formData, cron_expression: e.target.value })
              }
              placeholder="0 9 * * * (phút giờ ngày tháng thứ)"
              className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />

            <div className="mt-2 bg-blue-50 border border-blue-200 rounded-lg p-3">
              <p className="text-xs text-blue-900 font-medium mb-1">
                ℹ️ Format: phút giờ ngày tháng thứ
              </p>
              <ul className="text-xs text-blue-700 space-y-0.5">
                <li>• 0 9 * * * = 9h sáng hàng ngày</li>
                <li>• 0 18 * * 1-5 = 6h chiều thứ 2-6</li>
                <li>• */30 * * * * = Mỗi 30 phút</li>
              </ul>
            </div>
          </div>

          {/* Channels */}
          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="block text-sm font-medium text-gray-700">
                Chọn kênh <span className="text-red-500">*</span>
              </label>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={selectAllChannels}
                  className="text-xs text-blue-600 hover:text-blue-800"
                >
                  Chọn tất cả
                </button>
                <span className="text-gray-300">|</span>
                <button
                  type="button"
                  onClick={deselectAllChannels}
                  className="text-xs text-gray-600 hover:text-gray-800"
                >
                  Bỏ chọn
                </button>
              </div>
            </div>

            {channels.length === 0 ? (
              <div className="border border-gray-200 rounded-lg p-4 text-center text-gray-500">
                <p className="text-sm">Chưa có kênh nào được kết nối</p>
                <p className="text-xs mt-1">
                  Vui lòng kết nối kênh trước khi tạo lịch
                </p>
              </div>
            ) : (
              <div className="space-y-2 max-h-64 overflow-y-auto border border-gray-200 rounded-lg p-3">
                {channels.map((channel) => (
                  <label
                    key={channel.id}
                    className="flex items-center gap-3 p-2 hover:bg-gray-50 rounded cursor-pointer transition-colors"
                  >
                    <input
                      type="checkbox"
                      checked={formData.target_channel_ids.includes(channel.id)}
                      onChange={() => toggleChannel(channel.id)}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <div className="flex-1">
                      <div className="text-sm font-medium text-gray-900">
                        {channel.name}
                      </div>
                      <div className="text-xs text-gray-500">
                        {channel.platform.toUpperCase()}
                      </div>
                    </div>
                  </label>
                ))}
              </div>
            )}

            <p className="text-xs text-gray-500 mt-2">
              Đã chọn: {formData.target_channel_ids.length} / {channels.length}{" "}
              kênh
            </p>
          </div>

          {/* Active Toggle */}
          <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-lg">
            <input
              type="checkbox"
              id="is_active"
              checked={formData.is_active}
              onChange={(e) =>
                setFormData({ ...formData, is_active: e.target.checked })
              }
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <label htmlFor="is_active" className="text-sm text-gray-700">
              Kích hoạt lịch ngay sau khi tạo
            </label>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
            >
              Hủy
            </button>
            <button
              type="submit"
              disabled={loading || channels.length === 0}
              className="flex-1 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium transition-colors"
            >
              {loading ? "Đang tạo..." : "Tạo lịch"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
