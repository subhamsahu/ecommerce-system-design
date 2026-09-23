import { Component } from "react";
import type { ReactNode, ErrorInfo } from "react";
import { Button } from "@/components/ui/button";
import { AlertTriangle, RefreshCw, Home } from "lucide-react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Error caught by boundary:", error, errorInfo);
  }

  handleRefresh = () => {
    this.setState({ hasError: false, error: undefined });
    window.location.reload();
  };

  handleGoHome = () => {
    this.setState({ hasError: false, error: undefined });
    window.location.href = "/dashboard";
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-background flex items-center justify-center p-6">
          <div className="max-w-md w-full text-center space-y-8">
            {/* Error Icon */}
            <div className="flex justify-center">
              <div className="rounded-full bg-destructive/10 p-6">
                <AlertTriangle className="h-12 w-12 text-destructive" />
              </div>
            </div>

            {/* Error Content */}
            <div className="space-y-4">
              <h1 className="text-3xl font-bold text-foreground">
                Oops! Something went wrong
              </h1>
              <p className="text-muted-foreground">
                An unexpected error occurred. This has been logged and we'll
                look into it.
              </p>
              {process.env.NODE_ENV === "development" && this.state.error && (
                <details className="text-left bg-muted p-4 rounded-md text-sm">
                  <summary className="cursor-pointer font-medium mb-2">
                    Error Details (Development Mode)
                  </summary>
                  <pre className="text-xs overflow-auto">
                    {this.state.error.message}
                    {"\n\n"}
                    {this.state.error.stack}
                  </pre>
                </details>
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button
                onClick={this.handleRefresh}
                variant="default"
                className="flex items-center gap-2"
              >
                <RefreshCw className="h-4 w-4" />
                Try Again
              </Button>
              <Button
                onClick={this.handleGoHome}
                variant="outline"
                className="flex items-center gap-2"
              >
                <Home className="h-4 w-4" />
                Go to Dashboard
              </Button>
            </div>

            {/* Additional Help */}
            <div className="pt-8 border-t border-border">
              <p className="text-sm text-muted-foreground">
                If this problem persists, please contact our support team with
                the error details above.
              </p>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
