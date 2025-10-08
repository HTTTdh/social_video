import { useEffect, useState } from "react";
import { videosApi } from "@/api/videos";
import { Video, VideoStatus } from "@/types/video";
import {
  VideoCameraIcon,
  TrashIcon,
  ArrowDownTrayIcon,
  PencilIcon,
  PlayIcon,
} from "@heroicons/react/24/outline";
import VideoUploadModal from "@/components/features/videos/VideoUploadModal";
import VideoEditModal from "@/components/features/videos/VideoEditModal";

export default function VideosList() {
  const [videos, setVideos] = useState<Video[]>([]); // Khởi tạo là mảng rỗng
  const [loading, setLoading] = useState(true); // Thêm state loading
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [editingVideo, setEditingVideo] = useState<Video | null>(null);

  useEffect(() => {
    loadVideos();
  }, []);

  const loadVideos = async () => {
    setLoading(true);
    try {
      const data = await videosApi.list();
      // Đảm bảo data là array hoặc sử dụng mảng rỗng
      setVideos(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error("Failed to load videos:", error);
      setVideos([]); // Reset về mảng rỗng khi có lỗi
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Xóa video này?")) return;

    try {
      await videosApi.delete(id);
      alert("Xóa thành công!");
      loadVideos();
    } catch (error) {
      console.error("Delete error:", error);
      alert("Xóa thất bại");
    }
  };

  const handleDownload = async (video: Video) => {
    try {
      const blob = await videosApi.download(video.id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${video.title}.${video.format || "mp4"}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error("Download error:", error);
      alert("Download thất bại");
    }
  };

  const statusConfig: Record<VideoStatus, { label: string; color: string }> = {
    [VideoStatus.UPLOADING]: {
      label: "Đang tải lên",
      color: "bg-gray-100 text-gray-700",
    },
    [VideoStatus.PROCESSING]: {
      label: "Đang xử lý",
      color: "bg-blue-100 text-blue-700",
    },
    [VideoStatus.READY]: {
      label: "Sẵn sàng",
      color: "bg-green-100 text-green-700",
    },
    [VideoStatus.FAILED]: {
      label: "Thất bại",
      color: "bg-red-100 text-red-700",
    },
  };

  const formatDuration = (seconds?: number) => {
    if (!seconds) return "N/A";
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return "N/A";
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    if (bytes < 1024 * 1024 * 1024)
      return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`;
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
          <h1 className="text-3xl font-bold text-gray-900">Quản lý Video</h1>
          <p className="text-gray-600 mt-1">
            Upload, chỉnh sửa và quản lý video
          </p>
        </div>
        <button
          onClick={() => setShowUploadModal(true)}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium flex items-center gap-2"
        >
          <VideoCameraIcon className="w-5 h-5" />
          <span>Upload Video</span>
        </button>
      </div>

      {/* Videos Grid */}
      {loading ? (
        <div className="text-center py-10">Loading...</div>
      ) : (
        <>
          {videos && videos.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {videos.map((video) => {
                const config = statusConfig[video.status];
                return (
                  <div
                    key={video.id}
                    className="bg-white rounded-lg shadow hover:shadow-xl transition-shadow overflow-hidden border border-gray-200"
                  >
                    {/* Thumbnail */}
                    <div className="relative aspect-video bg-gray-900">
                      {video.thumbnail_path ? (
                        <img
                          src={video.thumbnail_path}
                          alt={video.title}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-gray-800 to-gray-900">
                          <VideoCameraIcon className="w-16 h-16 text-gray-600" />
                        </div>
                      )}

                      {/* Duration Badge */}
                      {video.duration && (
                        <div className="absolute bottom-2 right-2 bg-black bg-opacity-75 text-white text-xs px-2 py-1 rounded backdrop-blur-sm">
                          {formatDuration(video.duration)}
                        </div>
                      )}

                      {/* Play Button Overlay */}
                      <button
                        className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-0 hover:bg-opacity-30 transition-all group"
                        disabled={video.status !== VideoStatus.READY}
                      >
                        <PlayIcon className="w-16 h-16 text-white opacity-0 group-hover:opacity-100 transition-opacity drop-shadow-lg" />
                      </button>
                    </div>

                    {/* Info */}
                    <div className="p-4">
                      <h3
                        className="font-semibold text-gray-900 mb-2 truncate"
                        title={video.title}
                      >
                        {video.title}
                      </h3>

                      {video.description && (
                        <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                          {video.description}
                        </p>
                      )}

                      {/* Status Badge */}
                      <div className="mb-3">
                        <span
                          className={`${config.color} px-2.5 py-1 rounded-full text-xs font-medium inline-block`}
                        >
                          {config.label}
                        </span>
                      </div>

                      {/* Metadata */}
                      <div className="text-xs text-gray-500 space-y-1 mb-4 bg-gray-50 p-2 rounded">
                        <div className="flex justify-between">
                          <span>Kích thước:</span>
                          <span className="font-medium">
                            {formatFileSize(video.file_size)}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span>Độ phân giải:</span>
                          <span className="font-medium">
                            {video.resolution || "N/A"}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span>Format:</span>
                          <span className="font-medium">
                            {video.format?.toUpperCase() || "MP4"}
                          </span>
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="flex gap-2">
                        <button
                          onClick={() => setEditingVideo(video)}
                          className="flex-1 px-3 py-2 bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 transition-colors text-sm font-medium border border-blue-200"
                          title="Chỉnh sửa video"
                        >
                          <PencilIcon className="w-4 h-4 inline mr-1" />
                          <span>Sửa</span>
                        </button>
                        <button
                          onClick={() => handleDownload(video)}
                          className="px-3 py-2 bg-green-50 text-green-700 rounded-lg hover:bg-green-100 transition-colors border border-green-200 disabled:opacity-50 disabled:cursor-not-allowed"
                          disabled={video.status !== VideoStatus.READY}
                          title="Tải xuống video"
                        >
                          <ArrowDownTrayIcon className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(video.id)}
                          className="px-3 py-2 bg-red-50 text-red-700 rounded-lg hover:bg-red-100 transition-colors border border-red-200"
                          title="Xóa video"
                        >
                          <TrashIcon className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
              <VideoCameraIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500 text-lg font-medium mb-2">
                Chưa có video nào
              </p>
              <p className="text-gray-400 text-sm mb-4">
                Bắt đầu bằng cách upload video đầu tiên của bạn
              </p>
              <button
                onClick={() => setShowUploadModal(true)}
                className="text-blue-600 hover:text-blue-700 font-medium inline-flex items-center gap-1"
              >
                <span>Upload video đầu tiên</span>
                <span>→</span>
              </button>
            </div>
          )}
        </>
      )}

      {/* Upload Modal */}
      <VideoUploadModal
        isOpen={showUploadModal}
        onClose={() => setShowUploadModal(false)}
        onSuccess={() => {
          setShowUploadModal(false);
          loadVideos();
        }}
      />

      {/* Edit Modal */}
      {editingVideo && (
        <VideoEditModal
          video={editingVideo}
          isOpen={!!editingVideo}
          onClose={() => setEditingVideo(null)}
          onSuccess={() => {
            setEditingVideo(null);
            loadVideos();
          }}
        />
      )}
    </div>
  );
}
