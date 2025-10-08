import { useEffect, useState } from "react";
import { channelsApi, Channels } from "@/api/channels";
import { Platform } from "@/types/channel";
import { TrashIcon, PencilIcon } from "@heroicons/react/24/outline";
import ConnectChannelModal from "@/components/features/channels/ConnectChannelModal";

export default function ChannelsList() {
  const [channels, setChannels] = useState<Channel[]>([]);
  const [loading, setLoading] = useState(true);
  const [showConnectModal, setShowConnectModal] = useState(false);
  const [filter, setFilter] = useState<Platform | "all">("all");

  useEffect(() => {
    loadChannels();
  }, [filter]);

  const loadChannels = async () => {
    setLoading(true);
    try {
      const data = await channelsApi.list({
        platform: filter === "all" ? undefined : filter,
        only_active: true,
      });
      setChannels(data);
    } catch (error) {
      console.error("Failed to load channels:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Bạn có chắc muốn xóa kênh này?")) return;

    try {
      await channelsApi.delete(id);
      loadChannels();
    } catch (error) {
      alert("Xóa kênh thất bại");
    }
  };

  const handleToggleActive = async (channel: Channel) => {
    try {
      await channelsApi.update(channel.id, {
        is_active: !channel.is_active,
      });
      loadChannels();
    } catch (error) {
      alert("Cập nhật thất bại");
    }
  };

  const platformConfig = {
    facebook: { icon: "📘", color: "bg-blue-500", name: "Facebook" },
    instagram: { icon: "📷", color: "bg-pink-500", name: "Instagram" },
    tiktok: { icon: "🎵", color: "bg-black", name: "TikTok" },
    youtube: { icon: "📺", color: "bg-red-500", name: "YouTube" },
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
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Kênh kết nối</h1>
          <p className="text-gray-600 mt-1">Quản lý các kênh social media</p>
        </div>
        <button
          onClick={() => setShowConnectModal(true)}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
        >
          + Kết nối kênh mới
        </button>
      </div>

      {/* Filter */}
      <div className="flex gap-2 mb-6 flex-wrap">
        <button
          onClick={() => setFilter("all")}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            filter === "all"
              ? "bg-blue-600 text-white"
              : "bg-gray-200 text-gray-700 hover:bg-gray-300"
          }`}
        >
          Tất cả ({channels.length})
        </button>
        {Object.entries(platformConfig).map(([key, config]) => (
          <button
            key={key}
            onClick={() => setFilter(key as Platform)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filter === key
                ? "bg-blue-600 text-white"
                : "bg-gray-200 text-gray-700 hover:bg-gray-300"
            }`}
          >
            {config.icon} {config.name}
          </button>
        ))}
      </div>

      {/* Channels Grid */}
      {channels.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">Chưa có kênh nào được kết nối</p>
          <button
            onClick={() => setShowConnectModal(true)}
            className="mt-4 text-blue-600 hover:text-blue-700 font-medium"
          >
            Kết nối kênh đầu tiên →
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {channels.map((channel) => {
            const config = platformConfig[channel.platform];
            return (
              <div
                key={channel.id}
                className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow p-6"
              >
                {/* Platform Badge */}
                <div
                  className={`${config.color} w-12 h-12 rounded-full flex items-center justify-center text-2xl mb-4`}
                >
                  {config.icon}
                </div>

                {/* Channel Info */}
                <h3 className="text-lg font-semibold text-gray-900 mb-1">
                  {channel.name}
                </h3>
                <p className="text-sm text-gray-600 mb-4">
                  @{channel.username || "N/A"}
                </p>

                {/* Status */}
                <div className="flex items-center mb-4">
                  <div
                    className={`w-2 h-2 rounded-full mr-2 ${
                      channel.is_active ? "bg-green-500" : "bg-gray-400"
                    }`}
                  ></div>
                  <span className="text-sm text-gray-600">
                    {channel.is_active ? "Hoạt động" : "Không hoạt động"}
                  </span>
                </div>

                {/* Actions */}
                <div className="flex gap-2">
                  <button
                    onClick={() => handleToggleActive(channel)}
                    className={`flex-1 px-3 py-2 rounded text-sm font-medium transition-colors ${
                      channel.is_active
                        ? "bg-yellow-100 text-yellow-700 hover:bg-yellow-200"
                        : "bg-green-100 text-green-700 hover:bg-green-200"
                    }`}
                  >
                    {channel.is_active ? "Tắt" : "Bật"}
                  </button>
                  <button
                    onClick={() => handleDelete(channel.id)}
                    className="px-3 py-2 bg-red-100 text-red-700 rounded hover:bg-red-200 transition-colors"
                  >
                    <TrashIcon className="w-4 h-4" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Connect Modal */}
      <ConnectChannelModal
        isOpen={showConnectModal}
        onClose={() => setShowConnectModal(false)}
        onSuccess={() => {
          setShowConnectModal(false);
          loadChannels();
        }}
      />
    </div>
  );
}
