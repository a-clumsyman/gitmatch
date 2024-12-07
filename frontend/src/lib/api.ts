import { z } from "zod";

const baseUrl = import.meta.env.VITE_BACKEND_URL || 'https://gitmatch-backend.vercel.app/';

export const compareUsersResponseSchema = z.object({
  match_type: z.string(),
  compatibility_summary: z.string(),
  strengths_and_opportunities: z.string(),
  collaboration_plan: z.string(),
  motivational_message: z.string(),
  valuable_insights: z.object({
    activity_trends: z.string(),
    repository_impact: z.string(),
    follower_engagement: z.string()
  })
});

export type CompareUsersResponse = z.infer<typeof compareUsersResponseSchema>;

export async function compareUsers(username1: string, username2: string): Promise<CompareUsersResponse> {
  const response = await fetch(`${baseUrl}/analyze-compatibility?username1=${encodeURIComponent(username1)}&username2=${encodeURIComponent(username2)}`);
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to compare users');
  }

  const data = await response.json();
  return compareUsersResponseSchema.parse(data);
}
