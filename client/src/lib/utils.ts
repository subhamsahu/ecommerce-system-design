import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/** Returns { start_date, end_date } as 'YYYY-MM-DD' strings for the current calendar month. */
export function currentMonthRange(): { start_date: string; end_date: string } {
  const now = new Date();
  const y = now.getFullYear();
  const m = now.getMonth(); // 0-indexed
  const lastDay = new Date(y, m + 1, 0).getDate();
  // Use local date parts to avoid UTC offset shifting the date
  const pad = (n: number) => String(n).padStart(2, "0");
  const mm = pad(m + 1);
  return {
    start_date: `${y}-${mm}-01`,
    end_date: `${y}-${mm}-${pad(lastDay)}`,
  };
}
