interface BadgeProps {
  status: string;
  className?: string;
}

export const Badge = ({ status, className = "" }: BadgeProps) => {
  const statusColors: Record<string, string> = {
    draft: "bg-gray-100 text-gray-700",
    scheduled: "bg-blue-100 text-blue-700",
    published: "bg-green-100 text-green-700",
    failed: "bg-red-100 text-red-700",
    pending: "bg-yellow-100 text-yellow-700",
    active: "bg-green-100 text-green-700",
    inactive: "bg-gray-100 text-gray-700",
  };

  return (
    <span
      className={`px-2 py-1 text-xs rounded-full ${
        statusColors[status] || statusColors.draft
      } ${className}`}
    >
      {status}
    </span>
  );
};
