/* eslint-disable @typescript-eslint/no-explicit-any */
import { ChatMessage } from "@/types/types";
import { create } from "zustand";

export const useChatStore = create((set): any => ({
  chatHistory: [],
  addMessageToChatHistory: (message: ChatMessage) =>
    set((state: any) => ({
      chatHistory: [...state.chatHistory, message],
    })),
  removeMessagesFromChatHistory: (amount: number) =>
    set((state: any) => ({
      chatHistory: state.chatHistory.slice(
        0,
        state.chatHistory.length - amount
      ),
    })),
}));
