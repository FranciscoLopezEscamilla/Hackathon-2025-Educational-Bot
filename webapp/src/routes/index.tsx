import ChatbotView from "@/ui/pages/ChatbotView";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/")({
  component: RouteComponent,
});

function RouteComponent() {
  return <ChatbotView />;
}
