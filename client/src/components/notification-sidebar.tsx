import { useState } from "react";
import {
  Bell,
  CheckCircle,
  AlertCircle,
  Info,
  Clock,
  BellOff,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";

type NotificationType = "success" | "warning" | "error" | "info";

interface Notification {
  id: number;
  type: NotificationType;
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
}

const INITIAL_NOTIFICATIONS: Notification[] = [
  {
    id: 1,
    type: "info",
    title: "System notification",
    message:
      "Welcome to your application. This notification system is ready for your custom notifications.",
    timestamp: "Just now",
    read: false,
  },
  {
    id: 2,
    type: "success",
    title: "Setup complete",
    message: "Your application base template is configured and ready to use.",
    timestamp: "1 hour ago",
    read: false,
  },
  {
    id: 3,
    type: "info",
    title: "Getting started",
    message:
      "Check the README for guides on adding your custom features and functionality.",
    timestamp: "Yesterday",
    read: true,
  },
];

const getNotificationIcon = (type: NotificationType) => {
  switch (type) {
    case "success":
      return <CheckCircle className="h-4 w-4 text-green-500 shrink-0" />;
    case "warning":
      return <AlertCircle className="h-4 w-4 text-yellow-500 shrink-0" />;
    case "error":
      return <AlertCircle className="h-4 w-4 text-red-500 shrink-0" />;
    case "info":
    default:
      return <Info className="h-4 w-4 text-blue-500 shrink-0" />;
  }
};

export function NotificationSidebar() {
  const [notifications, setNotifications] = useState<Notification[]>(
    INITIAL_NOTIFICATIONS,
  );

  const unreadCount = notifications.filter((n) => !n.read).length;

  const markAllRead = () =>
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));

  const clearAll = () => setNotifications([]);

  const markRead = (id: number) =>
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, read: true } : n)),
    );

  return (
    <Sheet>
      <SheetTrigger asChild>
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-4 w-4" />
          {unreadCount > 0 && (
            <Badge
              variant="destructive"
              className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0 text-xs"
            >
              {unreadCount}
            </Badge>
          )}
        </Button>
      </SheetTrigger>
      <SheetContent className="flex flex-col gap-0 p-0">
        <SheetHeader className="px-4 pt-5 pb-3">
          <SheetTitle className="flex items-center gap-2">
            <Bell className="h-4 w-4" />
            Notifications
            {unreadCount > 0 && (
              <Badge variant="secondary" className="ml-1">
                {unreadCount} new
              </Badge>
            )}
          </SheetTitle>
        </SheetHeader>

        <Separator />

        {notifications.length > 0 && (
          <div className="flex items-center justify-between px-4 py-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={markAllRead}
              disabled={unreadCount === 0}
            >
              Mark all as read
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="text-destructive hover:text-destructive"
              onClick={clearAll}
            >
              Clear all
            </Button>
          </div>
        )}

        <ScrollArea className="flex-1 px-4">
          {notifications.length === 0 ? (
            <div className="flex flex-col items-center justify-center gap-3 py-20 text-center">
              <BellOff className="h-10 w-10 text-muted-foreground/40" />
              <p className="text-sm font-medium text-muted-foreground">
                No notifications
              </p>
              <p className="text-xs text-muted-foreground/70">
                You're all caught up!
              </p>
            </div>
          ) : (
            <div className="space-y-2 pb-4">
              {notifications.map((n) => (
                <div
                  key={n.id}
                  onClick={() => markRead(n.id)}
                  className={`cursor-pointer rounded-lg border p-3 transition-colors hover:bg-muted/60 ${
                    !n.read
                      ? "bg-muted/40 border-l-4 border-l-primary"
                      : "bg-background border-border"
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <div className="mt-0.5">{getNotificationIcon(n.type)}</div>
                    <div className="flex-1 space-y-0.5 min-w-0">
                      <div className="flex items-center justify-between gap-2">
                        <h4
                          className={`text-sm truncate ${!n.read ? "font-semibold" : "font-medium"}`}
                        >
                          {n.title}
                        </h4>
                        {!n.read && (
                          <div className="h-2 w-2 shrink-0 bg-primary rounded-full" />
                        )}
                      </div>
                      <p className="text-xs text-muted-foreground leading-relaxed">
                        {n.message}
                      </p>
                      <div className="flex items-center gap-1 text-xs text-muted-foreground/70 pt-0.5">
                        <Clock className="h-3 w-3" />
                        {n.timestamp}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
      </SheetContent>
    </Sheet>
  );
}
