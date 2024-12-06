import { Card } from "@/components/ui/card";
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from "recharts";

interface FollowerNetworkProps {
  followerEngagement: string;
}

export default function FollowerNetwork({ followerEngagement }: FollowerNetworkProps) {
  // Mock data - in a real app this would come from the API
  const data = [
    { name: "Shared", value: 30 },
    { name: "User 1", value: 45 },
    { name: "User 2", value: 25 }
  ];

  const COLORS = ["hsl(250 95% 60%)", "hsl(250 70% 80%)", "hsl(250 50% 90%)"];

  return (
    <Card className="p-6 backdrop-blur-lg bg-background/80 shadow-xl transition-all duration-300 border-primary/10">
      <h4 className="text-lg font-semibold mb-4">Follower Network</h4>
      
      <div className="h-[200px]">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={80}
              paddingAngle={5}
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <p className="text-sm text-muted-foreground mt-4">
        {followerEngagement}
      </p>
    </Card>
  );
}
