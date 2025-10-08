import { useEffect, useState, FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { postsApi } from "@/api/posts";
import type { PostCreateInput } from "@/types/post";
import { channelsApi } from "@/api/channels";
import type { Channel } from "@/types/channel";
import { mediaApi } from "@/api/media";
import type { MediaAsset } from "@/types/media";

export default function PostCreate() {
  const navigate = useNavigate();
  const [channels, setChannels] = useState<Channel[]>([]);
  const [mediaLibrary, setMediaLibrary] = useState<MediaAsset[]>([]);

  const [formData, setFormData] = useState<PostCreateInput>({
    content: "",
    target_channel_ids: [],
    media_ids: [],
  });
  const [scheduledTime, setScheduledTime] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [channelsData, mediaData] = await Promise.all([
        channelsApi.list({ only_active: true }),
        mediaApi.list({ limit: 20 }),
      ]);
      setChannels(channelsData.items || channelsData);
      setMediaLibrary(mediaData.items);
    } catch (error) {
      console.error("Failed to load data:", error);
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!formData.content) {
      alert("Vui lòng nhập nội dung");
      return;
    }
    if (formData.target_channel_ids.length === 0) {
      alert("Vui lòng chọn ít nhất một kênh");
      return;
    }

    setLoading(true);
    try {
      const payload: PostCreateInput = {
        ...formData,
        scheduled_time: scheduledTime || undefined,
      };

      const created = await postsApi.create(payload);

      // ✅ Không có lịch -> đăng ngay
      if (!scheduledTime) {
        try {
          await postsApi.publishNow(created.id);
        } catch (e: any) {
          console.error("Publish after create error:", e);
          alert(e?.response?.data?.detail || "Đăng ngay sau khi tạo thất bại");
        }
      }

      alert("Tạo bài đăng thành công!");
      navigate("/posts");
    } catch (error: any) {
      console.error("Create post error:", error);
      alert(error.response?.data?.detail || "Tạo bài thất bại");
    } finally {
      setLoading(false);
    }
  };

  const toggleChannel = (id: number) => {
    setFormData((prev) => ({
      ...prev,
      target_channel_ids: prev.target_channel_ids.includes(id)
        ? prev.target_channel_ids.filter((cid) => cid !== id)
        : [...prev.target_channel_ids, id],
    }));
  };

  const toggleMedia = (id: number) => {
    setFormData((prev) => ({
      ...prev,
      media_ids: prev.media_ids?.includes(id)
        ? prev.media_ids.filter((mid) => mid !== id)
        : [...(prev.media_ids || []), id],
    }));
  };

  const platformConfig: Record<string, { icon: string; color: string }> = {
    facebook: { icon: "📘", color: "bg-blue-500" },
    instagram: { icon: "📷", color: "bg-pink-500" },
    tiktok: { icon: "🎵", color: "bg-black" },
    youtube: { icon: "📺", color: "bg-red-500" },
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Tạo bài đăng mới</h1>
        <p className="text-gray-600 mt-1">
          Đăng nội dung lên nhiều nền tảng cùng lúc
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Content */}
        <div className="bg-white rounded-lg shadow p-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Nội dung <span className="text-red-500">*</span>
          </label>
          <textarea
            value={formData.content}
            onChange={(e) =>
              setFormData({ ...formData, content: e.target.value })
            }
            placeholder="Nhập nội dung bài đăng..."
            rows={6}
            className="w-full border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          />
        </div>

        {/* Channels */}
        <div className="bg-white rounded-lg shadow p-6">
          <label className="block text-sm font-medium text-gray-700 mb-4">
            Chọn kênh đăng <span className="text-red-500">*</span>
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {channels.map((channel) => {
              const config = platformConfig[channel.platform] || {
                icon: "📱",
                color: "bg-gray-500",
              };
              const isSelected = formData.target_channel_ids.includes(
                channel.id
              );
              return (
                <button
                  key={channel.id}
                  type="button"
                  onClick={() => toggleChannel(channel.id)}
                  className={`p-4 rounded-lg border-2 transition-all text-left ${
                    isSelected
                      ? "border-blue-600 bg-blue-50"
                      : "border-gray-200 hover:border-gray-300"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div
                      className={`${config.color} w-10 h-10 rounded-full flex items-center justify-center text-xl text-white`}
                    >
                      {config.icon}
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">
                        {channel.name}
                      </p>
                      <p className="text-sm text-gray-600">
                        @{channel.username || "N/A"}
                      </p>
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
          {channels.length === 0 && (
            <p className="text-gray-500 text-center py-4">
              Chưa có kênh nào.{" "}
              <a href="/channels" className="text-blue-600 hover:underline">
                Kết nối ngay
              </a>
            </p>
          )}
        </div>

        {/* Media */}
        <div className="bg-white rounded-lg shadow p-6">
          <label className="block text-sm font-medium text-gray-700 mb-4">
            Chọn media (tùy chọn)
          </label>
          <div className="grid grid-cols-3 md:grid-cols-5 gap-4">
            {mediaLibrary.map((media) => {
              const isSelected = formData.media_ids?.includes(media.id);
              return (
                <button
                  key={media.id}
                  type="button"
                  onClick={() => toggleMedia(media.id)}
                  className={`relative aspect-square rounded-lg overflow-hidden border-2 transition-all ${
                    isSelected
                      ? "border-blue-600"
                      : "border-gray-200 hover:border-gray-300"
                  }`}
                >
                  <img
                    src={media.url}
                    alt={media.title}
                    className="w-full h-full object-cover"
                  />
                  {isSelected && (
                    <div className="absolute inset-0 bg-blue-600 bg-opacity-30 flex items-center justify-center">
                      <span className="text-white text-2xl">✓</span>
                    </div>
                  )}
                </button>
              );
            })}
          </div>
        </div>

        {/* Schedule */}
        <div className="bg-white rounded-lg shadow p-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Lên lịch đăng (tùy chọn)
          </label>
          <input
            type="datetime-local"
            value={scheduledTime}
            onChange={(e) => setScheduledTime(e.target.value)}
            className="border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <p className="text-sm text-gray-500 mt-2">
            Để trống để đăng ngay lập tức
          </p>
        </div>

        {/* Actions */}
        <div className="flex gap-4">
          <button
            type="button"
            onClick={() => navigate("/posts")}
            className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
          >
            Hủy
          </button>
          <button
            type="submit"
            disabled={loading}
            className="flex-1 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium transition-colors"
          >
            {loading
              ? "Đang tạo..."
              : scheduledTime
              ? "Tạo & Lên lịch"
              : "Tạo & Đăng ngay"}
          </button>
        </div>
      </form>
    </div>
  );
}
