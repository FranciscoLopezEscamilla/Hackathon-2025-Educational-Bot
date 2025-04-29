import { useRef, useState } from "react";
import { useNavigate } from "@tanstack/react-router";
import { useChatStore } from "../state/chatStore";
import { callToAgent } from "@/infrastructure/api/agent";

export function useChatbotActions() {
  const inputRef = useRef<HTMLTextAreaElement | null>(null);
  const [loadingChatResponse, setLoadingChatResponse] = useState(false);
  const navigate = useNavigate();

  const { addMessageToChat, removeMessagesFromChat, messages, setId } =
    useChatStore();

  const handleChangeMessage = (value: string) => {
    if (inputRef.current) {
      inputRef.current.value = value;
    }
  };

  const handleOnSubmitForm = async (formData: FormData) => {
    const randomUUID = crypto.randomUUID();
    const isFirstMessage = messages.length === 0;
    const message = formData.get("query") as string;

    handleChangeMessage("");
    addMessageToChat({
      id: crypto.randomUUID(),
      content: message,
      type: "user",
    });

    setLoadingChatResponse(true);

    try {
      const response = await callToAgent(formData);
      addMessageToChat({
        id: crypto.randomUUID(),
        content: response.messages[response.messages.length - 1].content,
        type: "assistant",
      });
    } catch (error) {
      console.log(error);
      addMessageToChat({
        id: crypto.randomUUID(),
        content: "Sorry, I couldn't understand your message.",
        type: "assistant",
      });
    } finally {
      setLoadingChatResponse(false);
      if (isFirstMessage) {
        setId(randomUUID);
        navigate({ to: `/${randomUUID}` });
      }
    }
  };

  const reSendLastMessage = () => {
    removeMessagesFromChat(2);
    const withoutLastMessage = messages.slice(0, messages.length - 1);
    const lastMessage = messages[messages.length - 2];
    const formData = new FormData();
    formData.append("query", lastMessage.content);
    formData.append("message_history", JSON.stringify(withoutLastMessage));
    handleOnSubmitForm(formData);
  };

  return {
    inputRef,
    loadingChatResponse,
    handleOnSubmitForm,
    reSendLastMessage,
  };
}
