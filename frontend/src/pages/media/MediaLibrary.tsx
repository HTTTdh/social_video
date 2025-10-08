import { useEffect, useState } from "react";
import { mediaApi } from "@/api/media";
import {
  PhotoIcon,
  TrashIcon,
  ArrowUpTrayIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
} from "@heroicons/react/24/outline";
import {
  PhotoIcon as PhotoIconSolid,
  VideoCameraIcon,
  MusicalNoteIcon,
} from "@heroicons/react/24/solid";
import MediaUploadModal from "@/components/features/media/MediaUploadModal";
import { MediaAsset } from "@/types/media"; // Đổi Media → MediaAsset

export default function MediaLibrary() {
  const [media, setMedia] = useState<MediaAsset[]>([]); // Đổi Media[] → MediaAsset[]
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [stats, setStats] = useState<{
    total: number;
    by_type: Record<string, number>;
    total_size: number;
  } | null>(null);

  useEffect(() => {
    loadData();
  }, [filter, searchQuery]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [mediaData, statsData] = await Promise.all([
        mediaApi.list({
          type: filter === "all" ? undefined : filter,
          q: searchQuery || undefined,
          limit: 100,
        }),
        mediaApi.getStats(),
      ]);

      setMedia(mediaData.items || []);
      setStats(statsData);
    } catch (error) {
      console.error("Failed to load data:", error);
      setMedia([]);
      setStats(null);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Xóa file này? Hành động này không thể hoàn tác.")) return;

    try {
      await mediaApi.delete(id);
      alert("Xóa thành công!");
      loadData();
    } catch (error) {
      console.error("Delete error:", error);
      alert("Xóa thất bại");
    }
  };

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return "N/A";
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    if (bytes < 1024 * 1024 * 1024)
      return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`;
  };

  const getMediaTypeIcon = (type: string) => {
    switch (type) {
      case "image":
        return <PhotoIconSolid className="w-8 h-8 text-blue-500" />;
      case "video":
        return <VideoCameraIcon className="w-8 h-8 text-purple-500" />;
      case "audio":
        return <MusicalNoteIcon className="w-8 h-8 text-green-500" />;
      default:
        return <PhotoIconSolid className="w-8 h-8 text-gray-500" />;
    }
  };

  const filterOptions = [
    { value: "all", label: "Tất cả", icon: FunnelIcon },
    { value: "image", label: "Ảnh", icon: PhotoIconSolid },
    { value: "video", label: "Video", icon: VideoCameraIcon },
    { value: "audio", label: "Audio", icon: MusicalNoteIcon },
  ];

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mb-4"></div>
        <p className="text-gray-600 font-medium">Đang tải media...</p>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4 mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Thư viện Media</h1>
          <div className="flex gap-4 text-sm text-gray-600 mt-2">
            {stats && (
              <>
                <span>Tổng: {stats.total} files</span>
                <span>Dung lượng: {formatFileSize(stats.total_size)}</span>
              </>
            )}
          </div>
        </div>
        <button
          onClick={() => setShowUploadModal(true)}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium flex items-center justify-center gap-2 shadow-lg hover:shadow-xl"
        >
          <ArrowUpTrayIcon className="w-5 h-5" />
          <span>Upload Media</span>
        </button>
      </div>

      <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <MagnifyingGlassIcon className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Tìm kiếm theo tên file, MIME type..."
              className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-shadow"
            />
          </div>

          <div className="flex gap-2 overflow-x-auto">
            {filterOptions.map((option) => {
              const Icon = option.icon;
              return (
                <button
                  key={option.value}
                  onClick={() => setFilter(option.value)}
                  className={`px-4 py-2.5 rounded-lg font-medium transition-all whitespace-nowrap flex items-center gap-2 ${
                    filter === option.value
                      ? "bg-blue-600 text-white shadow-md"
                      : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{option.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        {stats && (
          <div className="mt-4 flex items-center gap-4 text-sm text-gray-600">
            {Object.entries(stats.by_type).map(([type, count]) => (
              <span key={type} className="font-medium">
                {type}: <span className="text-blue-600">{count}</span>
              </span>
            ))}
          </div>
        )}
      </div>

      {!media || media.length === 0 ? (
        <div className="bg-white rounded-lg shadow-sm text-center py-16 border-2 border-dashed border-gray-300">
          <PhotoIcon className="w-20 h-20 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500 text-lg font-medium mb-2">
            {searchQuery || filter !== "all"
              ? "Không tìm thấy kết quả"
              : "Chưa có media nào"}
          </p>
          <p className="text-gray-400 text-sm mb-4">
            {searchQuery || filter !== "all"
              ? "Thử thay đổi bộ lọc hoặc từ khóa tìm kiếm"
              : "Upload file đầu tiên để bắt đầu"}
          </p>
          {!searchQuery && filter === "all" && (
            <button
              onClick={() => setShowUploadModal(true)}
              className="text-blue-600 hover:text-blue-700 font-medium inline-flex items-center gap-1"
            >
              <span>Upload ngay</span>
              <span>→</span>
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
          {media.map(
            (
              item: MediaAsset // Thêm type annotation nếu cần
            ) => (
              <div
                key={item.id}
                className="bg-white rounded-lg shadow-sm hover:shadow-xl transition-all overflow-hidden group border border-gray-200"
              >
                <div className="relative aspect-square bg-gradient-to-br from-gray-100 to-gray-200">
                  {item.type === "image" ? (
                    <img
                      src={item.url}
                      alt={item.title || item.alt_text || "Image"}
                      className="w-full h-full object-cover"
                      loading="lazy"
                    />
                  ) : item.type === "video" ? (
                    <video
                      src={item.url}
                      className="w-full h-full object-cover"
                      muted
                      onMouseEnter={(e) => e.currentTarget.play()}
                      onMouseLeave={(e) => {
                        e.currentTarget.pause();
                        e.currentTarget.currentTime = 0;
                      }}
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-green-50 to-blue-50">
                      {getMediaTypeIcon(item.type)}
                    </div>
                  )}

                  <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-60 transition-all flex items-center justify-center gap-2">
                    <a
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="opacity-0 group-hover:opacity-100 bg-white text-gray-900 p-2 rounded-full hover:bg-gray-100 transition-all transform scale-75 group-hover:scale-100"
                      title="Xem"
                    >
                      <MagnifyingGlassIcon className="w-5 h-5" />
                    </a>
                    <button
                      onClick={() => handleDelete(item.id)}
                      className="opacity-0 group-hover:opacity-100 bg-red-600 text-white p-2 rounded-full hover:bg-red-700 transition-all transform scale-75 group-hover:scale-100"
                      title="Xóa"
                    >
                      <TrashIcon className="w-5 h-5" />
                    </button>
                  </div>

                  <div className="absolute top-2 right-2 bg-black bg-opacity-75 text-white text-xs px-2 py-1 rounded-full backdrop-blur-sm">
                    {item.type.toUpperCase()}
                  </div>
                </div>

                <div className="p-3">
                  <p
                    className="text-sm font-medium text-gray-900 truncate mb-1"
                    title={item.title}
                  >
                    {item.title}
                  </p>
                  <div className="flex justify-between items-center text-xs text-gray-500">
                    <span className="truncate" title={item.mime_type}>
                      {item.mime_type?.split("/")[1]?.toUpperCase() ||
                        "UNKNOWN"}
                    </span>
                    <span className="font-medium">
                      {formatFileSize(item.size)}
                    </span>
                  </div>
                </div>
              </div>
            )
          )}
        </div>
      )}

      <MediaUploadModal
        isOpen={showUploadModal}
        onClose={() => setShowUploadModal(false)}
        onSuccess={() => {
          setShowUploadModal(false);
          loadData();
        }}
      />
    </div>
  );
}
