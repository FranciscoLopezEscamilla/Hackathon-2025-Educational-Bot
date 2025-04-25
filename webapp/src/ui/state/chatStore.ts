/* eslint-disable @typescript-eslint/no-explicit-any */
import { ChatMessage } from "@/types/types";
import { create } from "zustand";

export const useChatStore = create((set): any => ({
  chatHistory: [],
  addMessageToChatHistory: (message: ChatMessage) =>
    set((state: any) => ({
      chatHistory: [...state.chatHistory, message],
    })),
}));
