import Chatbot from "@/ui/pages/Chatbot";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/$id")({
  component: RouteComponent,
});

function RouteComponent() {
  return <Chatbot />;
}
