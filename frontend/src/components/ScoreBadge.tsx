import { Badge } from "@/components/ui/badge";

interface ScoreBadgeProps {
  score: number;
}

export function ScoreBadge({ score }: ScoreBadgeProps) {
  const getScoreColor = (score: number) => {
    if (score >= 70) return "bg-green-500 hover:bg-green-600";
    if (score >= 40) return "bg-yellow-500 hover:bg-yellow-600";
    return "bg-red-500 hover:bg-red-600";
  };

  const getScoreLabel = (score: number) => {
    if (score >= 70) return "High";
    if (score >= 40) return "Medium";
    return "Low";
  };

  return (
    <Badge className={`${getScoreColor(score)} text-white font-semibold`}>
      {score.toFixed(1)} - {getScoreLabel(score)}
    </Badge>
  );
}
