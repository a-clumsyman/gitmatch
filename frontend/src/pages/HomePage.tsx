import { motion } from "framer-motion";
import ComparisonForm from "../components/ComparisonForm";
import ResultsDisplay from "../components/ResultsDisplay";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { compareUsers } from "@/lib/api";
import { Card } from "@/components/ui/card";
import ParticleBackground from "../components/ParticleBackground";

export default function HomePage() {
  const [usernames, setUsernames] = useState<{username1: string; username2: string} | null>(null);
  
  const { data: results, isLoading, error } = useQuery({
    queryKey: ['compareUsers', usernames?.username1, usernames?.username2],
    queryFn: () => usernames ? compareUsers(usernames.username1, usernames.username2) : null,
    enabled: !!usernames
  });

  return (
    <div className="min-h-screen relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-background via-primary/20 to-primary/5" />
      <ParticleBackground />
      <div className="relative p-4 md:p-8 lg:p-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className="max-w-7xl mx-auto space-y-12 md:space-y-16"
        >
          <header className="text-center mb-12">
            <h1 className="text-4xl md:text-6xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-primary/70 mb-4">
              GitMatch
            </h1>
            <p className="text-muted-foreground text-lg md:text-xl">
              Find your perfect GitHub collaboration match
            </p>
          </header>

          <Card className="p-6 md:p-8 backdrop-blur-lg bg-background/80 shadow-lg border-primary/10">
            <ComparisonForm onSubmit={setUsernames} />
            
            {isLoading && (
              <div className="flex justify-center my-8">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
              </div>
            )}

            {error && (
              <div className="text-destructive text-center my-8">
                {error instanceof Error ? error.message : 'An error occurred'}
              </div>
            )}

            {results && <ResultsDisplay results={results} />}
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
