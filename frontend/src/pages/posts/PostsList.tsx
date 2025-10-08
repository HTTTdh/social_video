import { useEffect, useState } from "react";
// ✅ ĐÚNG: Tách riêng API và Types
import { postsApi } from "@/api/posts";
import type { Post, PostStatus } from "@/types/post";
import {
  RocketLaunchIcon,
  PencilIcon,
  TrashIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
} from "@heroicons/react/24/outline";
import PostCreateModal from "@/components/features/posts/PostCreateModal";

export default function PostsList() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<PostStatus | "all">("all");
  const [showCreateModal, setShowCreateModal] = useState(false);

  useEffect(() => {
    loadPosts();
  }, [filter]);

  const loadPosts = async () => {
    setLoading(true);
    try {
      const data = await postsApi.list({
        status: filter === "all" ? undefined : filter,
        limit: 100,
      });
      setPosts(data.items || []); // Đảm bảo luôn có array
    } catch (error) {
      console.error("Failed to load posts:", error);
      alert("Không thể tải danh sách bài đăng");
      setPosts([]); // Reset posts về array rỗng khi lỗi
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Xóa bài đăng này?")) return;

    try {
      await postsApi.delete(id);
      alert("Xóa thành công!");
      loadPosts();
    } catch (error) {
      console.error("Delete error:", error);
      alert("Xóa thất bại");
    }
  };

  const handlePublish = async (id: number) => {
    if (!confirm("Đăng bài ngay bây giờ?")) return;

    try {
      await postsApi.publishNow(id); // Sửa tên method đúng
      alert("Đăng bài thành công!");
      loadPosts();
    } catch (error: any) {
      console.error("Publish error:", error);
      alert(error.response?.data?.detail || "Đăng bài thất bại");
    }
  };

  const statusConfig: Record<
    PostStatus,
    { label: string; color: string; icon: any }
  > = {
    ready: {
      label: "Sẵn sàng",
      color: "bg-gray-100 text-gray-700",
      icon: PencilIcon,
    },
    scheduled: {
      label: "Đã lên lịch",
      color: "bg-blue-100 text-blue-700",
      icon: ClockIcon,
    },
    posted: {
      label: "Đã đăng",
      color: "bg-green-100 text-green-700",
      icon: CheckCircleIcon,
    },
    failed: {
      label: "Thất bại",
      color: "bg-red-100 text-red-700",
      icon: XCircleIcon,
    },
    cancelled: {
      label: "Đã hủy",
      color: "bg-gray-200 text-gray-700",
      icon: XCircleIcon,
    },
  };

  const filterOptions = [
    { value: "all", label: "Tất cả" },
    { value: "ready", label: "Sẵn sàng" },
    { value: "scheduled", label: "Đã lên lịch" },
    { value: "posted", label: "Đã đăng" },
    { value: "failed", label: "Thất bại" },
    { value: "cancelled", label: "Đã hủy" },
  ];

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
          <h1 className="text-3xl font-bold text-gray-900">Quản lý Bài đăng</h1>
          <p className="text-gray-600 mt-1">
            Tạo và quản lý bài đăng trên các nền tảng
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium flex items-center gap-2"
        >
          <RocketLaunchIcon className="w-5 h-5" />
          <span>Tạo bài đăng</span>
        </button>
      </div>

      {/* Filter */}
      <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
        <div className="flex gap-2 overflow-x-auto">
          {filterOptions.map((option) => (
            <button
              key={option.value}
              onClick={() => setFilter(option.value as any)}
              className={`px-4 py-2 rounded-lg font-medium transition-all whitespace-nowrap ${
                filter === option.value
                  ? "bg-blue-600 text-white"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      {/* Posts List */}
      {posts?.length > 0 ? (
        <div className="grid gap-4">
          {posts.map((post) => {
            const config =
              statusConfig[post.status as PostStatus] || statusConfig.ready;
            const StatusIcon = config.icon;
            return (
              <div
                key={post.id}
                className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow p-6 border border-gray-200"
              >
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      {post.content.substring(0, 100)}
                      {post.content.length > 100 ? "..." : ""}
                    </h3>
                    <div className="flex items-center gap-4 text-sm text-gray-600">
                      <span
                        className={`${config.color} px-3 py-1 rounded-full font-medium inline-flex items-center gap-1`}
                      >
                        <StatusIcon className="w-4 h-4" />
                        {config.label}
                      </span>
                      {post.scheduled_time && (
                        <span className="flex items-center gap-1">
                          <ClockIcon className="w-4 h-4" />
                          {new Date(post.scheduled_time).toLocaleString(
                            "vi-VN"
                          )}
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="flex gap-2">
                    {post.status === "ready" && (
                      <button
                        onClick={() => handlePublish(post.id)}
                        className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm font-medium"
                      >
                        Đăng ngay
                      </button>
                    )}
                    <button
                      onClick={() => handleDelete(post.id)}
                      className="px-3 py-2 bg-red-50 text-red-700 rounded-lg hover:bg-red-100 transition-colors"
                    >
                      <TrashIcon className="w-5 h-5" />
                    </button>
                  </div>
                </div>

                {/* Channels */}
                {post.channels && post.channels.length > 0 && (
                  <div className="flex gap-2 flex-wrap">
                    {post.channels.map((channel: any) => (
                      <span
                        key={channel.id}
                        className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-xs font-medium"
                      >
                        {channel.platform}: {channel.name}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      ) : (
        <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
          <RocketLaunchIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500 text-lg font-medium mb-2">
            Chưa có bài đăng nào
          </p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="text-blue-600 hover:text-blue-700 font-medium"
          >
            Tạo bài đăng đầu tiên →
          </button>
        </div>
      )}

      {/* Create Modal */}
      <PostCreateModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onSuccess={() => {
          setShowCreateModal(false);
          loadPosts();
        }}
      />
    </div>
  );
}
