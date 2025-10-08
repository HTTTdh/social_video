import { useEffect, useState } from "react";
import {
  analyticsApi,
  AnalyticsOverview,
  PlatformStats,
} from "@/api/analytics";
import { Link } from "react-router-dom";
import {
  ChartBarIcon,
  UserGroupIcon,
  DocumentTextIcon,
  CalendarIcon,
  ExclamationCircleIcon,
  CheckCircleIcon,
} from "@heroicons/react/24/outline";

export default function Dashboard() {
  const [overview, setOverview] = useState<AnalyticsOverview | null>(null);
  const [platformStats, setPlatformStats] = useState<PlatformStats[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [overviewData, platformData] = await Promise.all([
        analyticsApi.getOverview(),
        analyticsApi.getByPlatform(),
      ]);
      setOverview(overviewData);
      setPlatformStats(platformData);
    } catch (error) {
      console.error("Failed to load dashboard data:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const stats = [
    {
      name: "Tổng bài đăng",
      value: overview?.total_posts || 0,
      icon: DocumentTextIcon,
      color: "bg-blue-500",
      link: "/posts",
    },
    {
      name: "Kênh kết nối",
      value: overview?.total_channels || 0,
      icon: UserGroupIcon,
      color: "bg-green-500",
      link: "/channels",
    },
    {
      name: "Đã đăng hôm nay",
      value: overview?.published_today || 0,
      icon: CheckCircleIcon,
      color: "bg-purple-500",
    },
    {
      name: "Bài đã lên lịch",
      value: overview?.scheduled_posts || 0,
      icon: CalendarIcon,
      color: "bg-yellow-500",
      link: "/schedule",
    },
    {
      name: "Thất bại",
      value: overview?.failed_posts || 0,
      icon: ExclamationCircleIcon,
      color: "bg-red-500",
    },
  ];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">
          Tổng quan hệ thống quản lý đa nền tảng
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon;
          const content = (
            <div className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
              <div className="flex items-center">
                <div className={`${stat.color} p-3 rounded-lg`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">
                    {stat.name}
                  </p>
                  <p className="text-2xl font-bold text-gray-900">
                    {stat.value}
                  </p>
                </div>
              </div>
            </div>
          );

          return stat.link ? (
            <Link key={stat.name} to={stat.link}>
              {content}
            </Link>
          ) : (
            <div key={stat.name}>{content}</div>
          );
        })}
      </div>

      {/* Platform Stats */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Thống kê theo nền tảng</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead>
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Nền tảng
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tổng bài đăng
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Thành công
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Thất bại
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tỷ lệ thành công
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {platformStats.map((stat) => (
                <tr key={stat.platform}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <span className="text-sm font-medium text-gray-900 capitalize">
                        {stat.platform}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {stat.total_posts}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600">
                    {stat.successful_posts}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-red-600">
                    {stat.failed_posts}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="w-full bg-gray-200 rounded-full h-2 mr-2">
                        <div
                          className="bg-green-500 h-2 rounded-full"
                          style={{ width: `${stat.success_rate}%` }}
                        ></div>
                      </div>
                      <span className="text-sm text-gray-700">
                        {stat.success_rate.toFixed(1)}%
                      </span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link
          to="/posts/create"
          className="bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg p-6 hover:from-blue-600 hover:to-blue-700 transition-all"
        >
          <h3 className="text-lg font-semibold mb-2">Tạo bài đăng mới</h3>
          <p className="text-blue-100">
            Đăng nội dung lên nhiều nền tảng cùng lúc
          </p>
        </Link>

        <Link
          to="/channels"
          className="bg-gradient-to-r from-green-500 to-green-600 text-white rounded-lg p-6 hover:from-green-600 hover:to-green-700 transition-all"
        >
          <h3 className="text-lg font-semibold mb-2">Kết nối kênh</h3>
          <p className="text-green-100">
            Thêm Facebook, Instagram, TikTok, YouTube
          </p>
        </Link>

        <Link
          to="/schedule"
          className="bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-lg p-6 hover:from-purple-600 hover:to-purple-700 transition-all"
        >
          <h3 className="text-lg font-semibold mb-2">Lịch đăng bài</h3>
          <p className="text-purple-100">
            Xem và quản lý lịch đăng bài tự động
          </p>
        </Link>
      </div>
    </div>
  );
}
