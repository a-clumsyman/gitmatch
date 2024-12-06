import { motion } from "framer-motion";
import type { CompareUsersResponse } from "@/lib/api";
import { Card } from "@/components/ui/card";
import ActivityChart from "./insights/ActivityChart";
import RepositoryStats from "./insights/RepositoryStats";
import FollowerNetwork from "./insights/FollowerNetwork";

interface ResultsDisplayProps {
  results: CompareUsersResponse;
}

export default function ResultsDisplay({ results }: ResultsDisplayProps) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.2, duration: 0.6 }}
      className="space-y-10 mt-12"
    >
      {/* Match Type & Summary */}
      <div className="text-center space-y-6">
        <motion.h2 
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-primary via-primary/90 to-primary bg-clip-text text-transparent"
        >
          {results.match_type}
        </motion.h2>
        <motion.p 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto"
        >
          {results.compatibility_summary}
        </motion.p>
      </div>

      {/* Strengths and Opportunities */}
      <motion.div
        whileHover={{ y: -5 }}
        transition={{ duration: 0.2 }}
      >
        <Card className="p-8 backdrop-blur-lg bg-background/80 shadow-xl hover:shadow-2xl transition-all duration-300 border-primary/10">
          <h3 className="text-2xl font-semibold mb-6 bg-gradient-to-r from-primary to-primary/80 bg-clip-text text-transparent">
            Strengths & Opportunities
          </h3>
          <p className="text-muted-foreground leading-relaxed">
            {results.strengths_and_opportunities}
          </p>
        </Card>
      </motion.div>

      {/* Collaboration Plan */}
      <motion.div
        whileHover={{ y: -5 }}
        transition={{ duration: 0.2 }}
      >
        <Card className="p-8 backdrop-blur-lg bg-background/80 shadow-xl hover:shadow-2xl transition-all duration-300 border-primary/10">
          <h3 className="text-2xl font-semibold mb-6 bg-gradient-to-r from-primary to-primary/80 bg-clip-text text-transparent">
            Collaboration Plan
          </h3>
          <p className="text-muted-foreground leading-relaxed">
            {results.collaboration_plan}
          </p>
        </Card>
      </motion.div>

      {/* Insights Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 md:gap-10">
        <motion.div whileHover={{ y: -5 }} transition={{ duration: 0.2 }}>
          <ActivityChart activityTrend={results.valuable_insights.activity_trends} />
        </motion.div>
        <motion.div whileHover={{ y: -5 }} transition={{ duration: 0.2 }}>
          <RepositoryStats repoImpact={results.valuable_insights.repository_impact} />
        </motion.div>
        <motion.div whileHover={{ y: -5 }} transition={{ duration: 0.2 }}>
          <FollowerNetwork followerEngagement={results.valuable_insights.follower_engagement} />
        </motion.div>
      </div>

      {/* Motivational Message */}
      <motion.div
        initial={{ scale: 0.95 }}
        animate={{ scale: 1 }}
        whileHover={{ scale: 1.02 }}
        transition={{ duration: 0.2 }}
        className="backdrop-blur-lg bg-primary/10 rounded-lg p-8 text-center shadow-lg"
      >
        <p className="text-lg font-medium text-primary">
          {results.motivational_message}
        </p>
      </motion.div>
    </motion.div>
  );
}
