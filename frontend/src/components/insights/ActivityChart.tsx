import { Line } from "recharts";
import { Card } from "@/components/ui/card";
import {
  LineChart,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from "recharts";

interface ActivityChartProps {
  activityTrend: string;
}

export default function ActivityChart({ activityTrend }: ActivityChartProps) {
  // Mock data - in a real app this would come from the API
  const data = [
    { month: "Jan", commits: 30 },
    { month: "Feb", commits: 45 },
    { month: "Mar", commits: 35 },
    { month: "Apr", commits: 50 },
    { month: "May", commits: 40 },
    { month: "Jun", commits: 60 }
  ];

  return (
    <Card className="p-6 backdrop-blur-lg bg-background/80 shadow-xl transition-all duration-300 border-primary/10">
      <h4 className="text-xl font-semibold mb-6 bg-gradient-to-r from-primary to-primary/80 bg-clip-text text-transparent">
        Activity Trends
      </h4>
      <div className="h-[200px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--primary) / 0.1)" />
            <XAxis 
              dataKey="month"
              stroke="hsl(var(--primary))"
              tick={{ fill: "hsl(var(--muted-foreground))" }}
            />
            <YAxis
              stroke="hsl(var(--primary))"
              tick={{ fill: "hsl(var(--muted-foreground))" }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(var(--background))",
                border: "1px solid hsl(var(--primary) / 0.2)",
                borderRadius: "8px",
              }}
            />
            <Line 
              type="monotone" 
              dataKey="commits" 
              stroke="hsl(var(--primary))"
              strokeWidth={2}
              dot={{ stroke: "hsl(var(--primary))", strokeWidth: 2, fill: "hsl(var(--background))" }}
              activeDot={{ r: 6, stroke: "hsl(var(--primary))", strokeWidth: 2, fill: "hsl(var(--background))" }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <p className="text-sm text-muted-foreground mt-4 leading-relaxed">
        {activityTrend}
      </p>
    </Card>
  );
}
