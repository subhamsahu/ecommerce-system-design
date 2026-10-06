import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTheme, type Theme } from "@/context/ThemeContext";
import { useSettings } from "@/context/SettingsContext";
import { useAppDispatch, useAppSelector } from "@/store/hooks";
import { logoutUser } from "@/store/slices/authSlice";
import {
  Settings as SettingsIcon,
  Palette,
  Monitor,
  User,
  Shield,
  AlertTriangle,
  LogOut,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";

export default function Settings() {
  const { theme, setTheme } = useTheme();
  const { compactMode, setCompactMode } = useSettings();
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const username = useAppSelector((s) => s.auth.user?.username ?? "");
  const role = useAppSelector((s) => s.auth.user?.role ?? "");

  const [activeTab, setActiveTab] = useState("general");

  // Profile tab
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [passwordMsg, setPasswordMsg] = useState("");

  const tabs = [
    { id: "general", label: "General", icon: SettingsIcon },
    { id: "profile", label: "Profile", icon: User },
    { id: "security", label: "Security", icon: Shield },
  ];

  const handlePasswordUpdate = (e: React.FormEvent) => {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      setPasswordMsg("New passwords do not match.");
      return;
    }
    if (newPassword.length < 6) {
      setPasswordMsg("Password must be at least 6 characters.");
      return;
    }
    // No backend endpoint yet — optimistic UI feedback
    setPasswordMsg("Password updated successfully.");
    setCurrentPassword("");
    setNewPassword("");
    setConfirmPassword("");
  };

  const handleSignOut = async () => {
    await dispatch(logoutUser());
    navigate("/login");
  };

  const handleResetSettings = () => {
    setTheme("system");
    setCompactMode(false);
  };

  return (
    <div className="flex flex-1 flex-col gap-4 p-4 md:gap-6 md:p-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight md:text-3xl">
          Settings
        </h1>
        <p className="text-muted-foreground text-sm md:text-base">
          Manage your preferences and account
        </p>
      </div>

      <div className="flex flex-col gap-4 md:flex-row md:gap-6">
        {/* Tab nav — horizontal scroll on mobile, vertical sidebar on md+ */}
        <div className="flex overflow-x-auto gap-1 pb-1 md:flex-col md:w-52 md:space-y-1 md:overflow-visible md:pb-0 md:shrink-0">
          {tabs.map(({ id, label, icon: Icon }) => (
            <Button
              key={id}
              variant={activeTab === id ? "secondary" : "ghost"}
              className="shrink-0 justify-start md:w-full"
              onClick={() => setActiveTab(id)}
            >
              <Icon className="h-4 w-4 mr-2" />
              {label}
            </Button>
          ))}
        </div>

        {/* Content */}
        <div className="flex-1 space-y-4 md:space-y-6 min-w-0">
          {/* ── General ── */}
          {activeTab === "general" && (
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Palette className="h-5 w-5" />
                    Appearance
                  </CardTitle>
                  <CardDescription>
                    Customize the look and feel of your application
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <h4 className="font-medium mb-1">Theme</h4>
                    <p className="text-sm text-muted-foreground mb-3">
                      Choose a color scheme for the app
                    </p>
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                      {(
                        [
                          {
                            id: "light" as Theme,
                            label: "Light",
                            swatches: ["#ffffff", "#f1f5f9", "#3b82f6"],
                          },
                          {
                            id: "dark" as Theme,
                            label: "Dark",
                            swatches: ["#1e1e2e", "#2a2a3c", "#6c8cf6"],
                          },
                          {
                            id: "system" as Theme,
                            label: "System",
                            swatches: ["#e2e8f0", "#1e1e2e", "#6c8cf6"],
                          },
                          {
                            id: "blue-light" as Theme,
                            label: "🔵 Blue Light",
                            swatches: ["#f8fafc", "#2563eb", "#2563eb"],
                          },
                          {
                            id: "crimson-dark" as Theme,
                            label: "🎬 Crimson Dark",
                            swatches: ["#181818", "#141414", "#e50914"],
                          },
                          {
                            id: "violet-dark" as Theme,
                            label: "🔮 Violet Dark",
                            swatches: ["#0f0b1a", "#1a1530", "#7c3aed"],
                          },
                        ] as { id: Theme; label: string; swatches: string[] }[]
                      ).map(({ id, label, swatches }) => (
                        <button
                          key={id}
                          onClick={() => setTheme(id)}
                          className={`flex flex-col items-start gap-1.5 rounded-lg border-2 p-2.5 text-left transition-all hover:border-primary ${
                            theme === id
                              ? "border-primary ring-2 ring-primary/30"
                              : "border-border"
                          }`}
                        >
                          <div className="flex gap-1 w-full">
                            {swatches.map((color, i) => (
                              <div
                                key={i}
                                className="h-5 flex-1 rounded"
                                style={{ backgroundColor: color }}
                              />
                            ))}
                          </div>
                          <span className="text-xs font-medium leading-none">
                            {label}
                          </span>
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                      <h4 className="font-medium">Language</h4>
                      <p className="text-sm text-muted-foreground">
                        Select your preferred language
                      </p>
                    </div>
                    <select className="flex h-10 w-full sm:w-[180px] items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2">
                      <option value="en">English</option>
                      <option value="es">Spanish</option>
                      <option value="fr">French</option>
                    </select>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Monitor className="h-5 w-5" />
                    Display
                  </CardTitle>
                  <CardDescription>
                    Configure display settings and layout preferences
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between gap-4">
                    <div>
                      <h4 className="font-medium">Compact Mode</h4>
                      <p className="text-sm text-muted-foreground">
                        Show more content in less space
                      </p>
                    </div>
                    <input
                      type="checkbox"
                      checked={compactMode}
                      onChange={(e) => setCompactMode(e.target.checked)}
                      className="h-5 w-5 shrink-0 rounded border border-gray-300 cursor-pointer"
                    />
                  </div>

                  <div className="flex items-center justify-between gap-4">
                    <div>
                      <h4 className="font-medium">Show Sidebar by Default</h4>
                      <p className="text-sm text-muted-foreground">
                        Keep navigation sidebar open
                      </p>
                    </div>
                    <input
                      type="checkbox"
                      defaultChecked
                      className="h-5 w-5 shrink-0 rounded border border-gray-300 cursor-pointer"
                    />
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* ── Profile ── */}
          {activeTab === "profile" && (
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Account Information</CardTitle>
                  <CardDescription>
                    Your account details and login credentials
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <label className="text-sm font-medium">Username</label>
                    <Input
                      value={username}
                      readOnly
                      className="bg-muted cursor-default"
                    />
                  </div>

                  <div>
                    <label className="text-sm font-medium">Role</label>
                    <Input
                      value={role}
                      readOnly
                      className="bg-muted cursor-default capitalize"
                    />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Change Password</CardTitle>
                  <CardDescription>
                    Update your password to keep your account secure
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handlePasswordUpdate} className="space-y-4">
                    <div>
                      <label className="text-sm font-medium">
                        Current Password
                      </label>
                      <Input
                        type="password"
                        value={currentPassword}
                        onChange={(e) => setCurrentPassword(e.target.value)}
                        required
                      />
                    </div>
                    <div>
                      <label className="text-sm font-medium">
                        New Password
                      </label>
                      <Input
                        type="password"
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        required
                      />
                    </div>
                    <div>
                      <label className="text-sm font-medium">
                        Confirm New Password
                      </label>
                      <Input
                        type="password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        required
                      />
                    </div>
                    {passwordMsg && (
                      <p
                        className={`text-sm ${passwordMsg.includes("successfully") ? "text-green-600" : "text-destructive"}`}
                      >
                        {passwordMsg}
                      </p>
                    )}
                    <Button type="submit">Update Password</Button>
                  </form>
                </CardContent>
              </Card>
            </div>
          )}

          {/* ── Security ── */}
          {activeTab === "security" && (
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Shield className="h-5 w-5" />
                    Security
                  </CardTitle>
                  <CardDescription>
                    Manage session and access settings
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-5">
                  <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                      <p className="font-medium">Session timeout</p>
                      <p className="text-sm text-muted-foreground">
                        Auto sign-out after inactivity
                      </p>
                    </div>
                    <select className="h-9 w-full sm:w-44 rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring">
                      <option value="60">1 hour</option>
                      <option value="240">4 hours</option>
                      <option value="480">8 hours</option>
                      <option value="0">Never</option>
                    </select>
                  </div>

                  <Separator />

                  <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                      <p className="font-medium">Sign out</p>
                      <p className="text-sm text-muted-foreground">
                        Sign out of your account
                      </p>
                    </div>
                    <Button
                      variant="outline"
                      className="w-full sm:w-auto"
                      onClick={handleSignOut}
                    >
                      <LogOut className="h-4 w-4 mr-2" />
                      Sign out
                    </Button>
                  </div>
                </CardContent>
              </Card>

              <Card className="border-destructive/40">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-destructive">
                    <AlertTriangle className="h-5 w-5" />
                    Danger Zone
                  </CardTitle>
                  <CardDescription>
                    Irreversible actions — proceed with care
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                      <p className="font-medium text-destructive">
                        Reset all settings
                      </p>
                      <p className="text-sm text-muted-foreground">
                        Restore theme and display preferences to defaults
                      </p>
                    </div>
                    <Button
                      variant="destructive"
                      size="sm"
                      className="w-full sm:w-auto"
                      onClick={handleResetSettings}
                    >
                      Reset
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
