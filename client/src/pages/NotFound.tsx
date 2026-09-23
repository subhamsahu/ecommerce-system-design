import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Home, ArrowLeft, AlertTriangle } from "lucide-react";

export default function NotFoundPage() {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-6">
      <div className="max-w-md w-full text-center space-y-8">
        {/* Error Icon */}
        <div className="flex justify-center">
          <div className="rounded-full bg-muted p-6">
            <AlertTriangle className="h-12 w-12 text-muted-foreground" />
          </div>
        </div>

        {/* Error Content */}
        <div className="space-y-4">
          <h1 className="text-6xl font-bold text-primary">404</h1>
          <h2 className="text-2xl font-semibold text-foreground">
            Page Not Found
          </h2>
          <p className="text-muted-foreground text-lg">
            Sorry, the page you are looking for doesn't exist or has been moved.
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button asChild variant="default" className="flex items-center gap-2">
            <Link to="/dashboard">
              <Home className="h-4 w-4" />
              Go to Dashboard
            </Link>
          </Button>
          <Button
            variant="outline"
            className="flex items-center gap-2"
            onClick={() => window.history.back()}
          >
            <ArrowLeft className="h-4 w-4" />
            Go Back
          </Button>
        </div>

        {/* Additional Help */}
        <div className="pt-8 border-t border-border">
          <p className="text-sm text-muted-foreground">
            If you believe this is an error, please{" "}
            <Link
              to="/settings"
              className="text-primary hover:underline font-medium"
            >
              contact support
            </Link>{" "}
            or try one of these common pages:
          </p>
          <div className="mt-4 flex flex-wrap justify-center gap-4 text-sm">
            <Link to="/tests" className="text-primary hover:underline">
              Test Management
            </Link>
            <Link to="/reports" className="text-primary hover:underline">
              Reports
            </Link>
            <Link to="/settings" className="text-primary hover:underline">
              Settings
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
