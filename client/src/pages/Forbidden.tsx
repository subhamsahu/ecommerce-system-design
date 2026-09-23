import { useNavigate } from "react-router-dom";
import { ShieldOff } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function Forbidden() {
  const navigate = useNavigate();
  return (
    <div className="flex flex-col items-center justify-center min-h-screen gap-4 text-center px-6">
      <div className="p-4 rounded-full bg-destructive/10">
        <ShieldOff className="w-10 h-10 text-destructive" />
      </div>
      <h1 className="text-2xl font-bold">Access Denied</h1>
      <p className="text-muted-foreground max-w-sm">
        You don't have permission to view this page. Contact your administrator
        if you think this is a mistake.
      </p>
      <Button variant="outline" onClick={() => navigate("/")}>
        Go to Dashboard
      </Button>
    </div>
  );
}
