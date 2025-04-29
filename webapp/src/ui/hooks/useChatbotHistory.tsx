import { useEffect } from "react";
import { loadHistory, saveHistory } from "../utils/persistentStorage";
import { historyStore } from "../state/historyStore";
import { useChatStore } from "../state/chatStore";

export function useChatbotHistory(paramId: string | undefined) {
  const { setHistory, chats } = historyStore();
  const { id, messages, loadState } = useChatStore();

  // Load history on mount
  useEffect(() => {
    loadHistory().then((history) => {
      setHistory(history);
    });

    return () => {
      loadState({
        messages: [],
        id: null,
        updatedAt: new Date().toISOString(),
      });
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Sync chat changes to history
  useEffect(() => {
    const newChatsState = [...chats];

    if (id && messages.length > 0) {
      const foundChatIndex = newChatsState.findIndex((chat) => chat.id === id);
      if (foundChatIndex !== -1) {
        newChatsState[foundChatIndex].messages = messages;
        saveHistory({
          chats: newChatsState,
          user: null,
        });
      } else {
        newChatsState.push({
          id,
          updatedAt: new Date().toISOString(),
          messages,
        });
        saveHistory({
          chats: newChatsState,
          user: null,
        });
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [messages, id]);

  // Load chat state if paramId changes
  useEffect(() => {
    if (paramId && chats.length > 0) {
      const foundChatIndex = chats.findIndex((chat) => chat.id === paramId);
      if (foundChatIndex !== -1) {
        loadState(chats[foundChatIndex]);
      }
    }
  }, [paramId, chats, loadState]);
}
