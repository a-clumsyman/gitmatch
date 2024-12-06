import { Card } from "@/components/ui/card";
import { Star, GitFork, Eye } from "lucide-react";

interface RepositoryStatsProps {
  repoImpact: string;
}

export default function RepositoryStats({ repoImpact }: RepositoryStatsProps) {
  // Mock data - in a real app this would come from the API
  const stats = {
    stars: 128,
    forks: 45,
    watchers: 67
  };

  return (
    <Card className="p-6 backdrop-blur-lg bg-background/80 shadow-xl transition-all duration-300 border-primary/10">
      <h4 className="text-lg font-semibold mb-4">Repository Impact</h4>
      
      <div className="grid grid-cols-3 gap-4">
        <div className="text-center">
          <div className="flex justify-center mb-2">
            <Star className="text-yellow-400" />
          </div>
          <div className="font-bold">{stats.stars}</div>
          <div className="text-xs text-muted-foreground">Stars</div>
        </div>
        
        <div className="text-center">
          <div className="flex justify-center mb-2">
            <GitFork className="text-primary" />
          </div>
          <div className="font-bold">{stats.forks}</div>
          <div className="text-xs text-muted-foreground">Forks</div>
        </div>
        
        <div className="text-center">
          <div className="flex justify-center mb-2">
            <Eye className="text-green-500" />
          </div>
          <div className="font-bold">{stats.watchers}</div>
          <div className="text-xs text-muted-foreground">Watchers</div>
        </div>
      </div>

      <p className="text-sm text-muted-foreground mt-4">
        {repoImpact}
      </p>
    </Card>
  );
}
