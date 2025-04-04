import { ChatMessage } from "@/types/types";
import axios from "axios";

const AGENT_API_BASE_URL = "http://127.0.0.1:8000";

export const callToAgent = async (
  message: string,
  chatHistory: ChatMessage[]
) => {
  const response = await axios.post(
    `${AGENT_API_BASE_URL}/api/agents/multiagent`,
    {
      query: message,
      messages: chatHistory,
    },
    {
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
    }
  );

  return response.data;
};
