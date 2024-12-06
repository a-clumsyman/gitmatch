import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useForm } from "react-hook-form";
import { Button } from "@/components/ui/button";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { motion } from "framer-motion";
import { useState, useEffect } from "react";
import { Avatar } from "@/components/ui/avatar";

const formSchema = z.object({
  username1: z.string().min(1, "GitHub username is required"),
  username2: z.string().min(1, "GitHub username is required")
});

interface GitHubUser {
  avatar_url?: string;
}

interface ComparisonFormProps {
  onSubmit: (values: { username1: string; username2: string }) => void;
}

async function fetchGitHubAvatar(username: string): Promise<string | null> {
  try {
    const response = await fetch(`https://api.github.com/users/${username}`);
    if (response.ok) {
      const data: GitHubUser = await response.json();
      return data.avatar_url || null;
    }
    return null;
  } catch {
    return null;
  }
}

export default function ComparisonForm({ onSubmit }: ComparisonFormProps) {
  const [avatars, setAvatars] = useState<{[key: string]: string}>({});
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      username1: "",
      username2: ""
    }
  });

  const updateAvatar = async (username: string, fieldName: string) => {
    const avatar = await fetchGitHubAvatar(username);
    if (avatar) {
      setAvatars(prev => ({ ...prev, [fieldName]: avatar }));
    }
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField
            control={form.control}
            name="username1"
            render={({ field }) => (
              <FormItem className="space-y-4">
                <FormLabel className="text-sm font-medium">First GitHub Username</FormLabel>
                <div className="flex items-center space-x-4">
                  <Avatar className="w-12 h-12 border border-border">
                    {avatars[field.name] && <img src={avatars[field.name]} alt="GitHub Avatar" className="object-cover" />}
                  </Avatar>
                  <FormControl className="flex-1">
                    <Input
                      placeholder="e.g. octocat"
                      {...field}
                      className="font-mono"
                      onChange={(e) => {
                        field.onChange(e);
                        if (e.target.value) updateAvatar(e.target.value, field.name);
                      }}
                    />
                  </FormControl>
                </div>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="username2"
            render={({ field }) => (
              <FormItem className="space-y-4">
                <FormLabel className="text-sm font-medium">Second GitHub Username</FormLabel>
                <div className="flex items-center space-x-4">
                  <Avatar className="w-12 h-12 border border-border">
                    {avatars[field.name] && <img src={avatars[field.name]} alt="GitHub Avatar" className="object-cover" />}
                  </Avatar>
                  <FormControl className="flex-1">
                    <Input
                      placeholder="e.g. torvalds"
                      {...field}
                      className="font-mono"
                      onChange={(e) => {
                        field.onChange(e);
                        if (e.target.value) updateAvatar(e.target.value, field.name);
                      }}
                    />
                  </FormControl>
                </div>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        <motion.div 
          className="flex justify-center"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <Button 
            type="submit" 
            className="w-full md:w-auto px-8 py-4 text-base font-medium bg-primary/10 hover:bg-primary/20 text-primary-foreground transition-colors duration-150"
            disabled={form.formState.isSubmitting}
          >
            {form.formState.isSubmitting ? (
              <span className="flex items-center gap-2">
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  className="w-4 h-4 border-2 border-white rounded-full border-t-transparent"
                />
                Matching...
              </span>
            ) : (
              "Find Match"
            )}
          </Button>
        </motion.div>
      </form>
    </Form>
  );
}
