import Chatbot from "@/ui/pages/Chatbot";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/")({
  component: RouteComponent,
});

function RouteComponent() {
  return <Chatbot />;
}
