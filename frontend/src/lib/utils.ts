import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

// Utility to merge conditional classNames with Tailwind conflict resolution
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

