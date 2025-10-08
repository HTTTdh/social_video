import { useState } from "react";
import { Platform } from "@/types/channel";
import { useOAuth } from "@/hooks/useOAuth";
import { channelsApi } from "@/api/channels";
import { XMarkIcon } from "@heroicons/react/24/outline";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export default function ConnectChannelModal({
  isOpen,
  onClose,
  onSuccess,
}: Props) {
  const [mode, setMode] = useState<"oauth" | "manual">("oauth");
  const [platform, setPlatform] = useState<Platform>(Platform.FACEBOOK);
  const [manualToken, setManualToken] = useState("");
  const [manualName, setManualName] = useState("");
  const [manualLoading, setManualLoading] = useState(false);
  const { connect, loading, error } = useOAuth();

  if (!isOpen) return null;

  const handleOAuth = async () => {
    const success = await connect(platform);
    if (success) {
      onSuccess();
      onClose();
    }
  };

  const handleManual = async () => {
    // Validation
    if (!manualName.trim()) {
      alert("Vui lòng nhập tên kênh");
      return;
    }

    if (!manualToken.trim()) {
      alert("Vui lòng nhập access token");
      return;
    }

    setManualLoading(true);
    try {
      // Tạo channel mới
      const channel = await channelsApi.create({
        platform,
        name: manualName.trim(),
        external_id: `manual-${Date.now()}`,
        username: manualName
          .toLowerCase()
          .replace(/\s+/g, "_")
          .replace(/[^a-z0-9_]/g, ""),
        is_active: true,
      });

      // Set token
      await channelsApi.setManualToken(channel.id, {
        platform,
        access_token: manualToken.trim(),
      });

      alert("Kết nối kênh thành công!");
      onSuccess();
      onClose();
    } catch (error: any) {
      alert(error.response?.data?.detail || "Kết nối thất bại");
    } finally {
      setManualLoading(false);
    }
  };

  const platformOptions = [
    { value: Platform.FACEBOOK, label: "Facebook", icon: "📘", color: "blue" },
    {
      value: Platform.INSTAGRAM,
      label: "Instagram",
      icon: "📷",
      color: "pink",
    },
    { value: Platform.TIKTOK, label: "TikTok", icon: "🎵", color: "gray" },
    { value: Platform.YOUTUBE, label: "YouTube", icon: "📺", color: "red" },
  ];

  const currentPlatform = platformOptions.find((p) => p.value === platform);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b">
          <h2 className="text-xl font-bold text-gray-900">Kết nối kênh mới</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
            disabled={loading || manualLoading}
          >
            <XMarkIcon className="w-6 h-6" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-5">
          {/* Mode Toggle */}
          <div className="flex gap-2 bg-gray-100 p-1 rounded-lg">
            <button
              type="button"
              onClick={() => setMode("oauth")}
              className={`flex-1 py-2.5 px-4 rounded-md font-medium transition-all ${
                mode === "oauth"
                  ? "bg-white text-blue-600 shadow-sm"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              OAuth (Khuyến nghị)
            </button>
            <button
              type="button"
              onClick={() => setMode("manual")}
              className={`flex-1 py-2.5 px-4 rounded-md font-medium transition-all ${
                mode === "manual"
                  ? "bg-white text-blue-600 shadow-sm"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              Thủ công
            </button>
          </div>

          {/* Platform Select */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Chọn nền tảng <span className="text-red-500">*</span>
            </label>
            <div className="grid grid-cols-2 gap-3">
              {platformOptions.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => setPlatform(option.value)}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    platform === option.value
                      ? "border-blue-600 bg-blue-50 shadow-sm"
                      : "border-gray-200 hover:border-gray-300 hover:bg-gray-50"
                  }`}
                >
                  <span className="text-3xl mb-2 block">{option.icon}</span>
                  <span className="text-sm font-medium block">
                    {option.label}
                  </span>
                </button>
              ))}
            </div>
          </div>

          {/* OAuth Mode */}
          {mode === "oauth" && (
            <div className="space-y-4">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm text-blue-900">
                  ✨ Phương thức OAuth đảm bảo an toàn và dễ dàng hơn. Bạn sẽ
                  được chuyển đến trang {currentPlatform?.label} để đăng nhập và
                  cấp quyền.
                </p>
              </div>

              <button
                type="button"
                onClick={handleOAuth}
                disabled={loading}
                className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium transition-colors flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <svg
                      className="animate-spin h-5 w-5"
                      viewBox="0 0 24 24"
                      fill="none"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      />
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      />
                    </svg>
                    <span>Đang kết nối...</span>
                  </>
                ) : (
                  <>
                    <span>Kết nối với {currentPlatform?.label}</span>
                    <span>→</span>
                  </>
                )}
              </button>
            </div>
          )}

          {/* Manual Mode */}
          {mode === "manual" && (
            <div className="space-y-4">
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <p className="text-sm text-yellow-900">
                  ⚠️ Phương thức thủ công yêu cầu bạn tự lấy access token từ{" "}
                  {currentPlatform?.label}. Chỉ dùng nếu bạn am hiểu kỹ thuật.
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tên kênh <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={manualName}
                  onChange={(e) => setManualName(e.target.value)}
                  placeholder={`Ví dụ: My ${currentPlatform?.label} Page`}
                  className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  disabled={manualLoading}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Access Token <span className="text-red-500">*</span>
                </label>
                <textarea
                  value={manualToken}
                  onChange={(e) => setManualToken(e.target.value)}
                  placeholder="Dán access token từ platform vào đây..."
                  rows={4}
                  className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-xs"
                  disabled={manualLoading}
                />
              </div>

              <button
                type="button"
                onClick={handleManual}
                disabled={
                  !manualToken.trim() || !manualName.trim() || manualLoading
                }
                className="w-full bg-green-600 text-white py-3 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium transition-colors"
              >
                {manualLoading ? "Đang kết nối..." : "Kết nối thủ công"}
              </button>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3">
              <p className="text-sm text-red-700">❌ {error}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
