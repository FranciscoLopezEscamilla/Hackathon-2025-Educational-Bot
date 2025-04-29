/* eslint-disable @typescript-eslint/no-explicit-any */
import { ChatHistory } from "@/types/types";
import { create } from "zustand";

type Actions = {
  setHistory: (chatHistory: ChatHistory) => void;
};

export const historyStore = create<ChatHistory & Actions>((set): any => ({
  user: null,
  chats: [],
  setHistory: (chatHistory: ChatHistory) =>
    set({ chats: chatHistory.chats, user: chatHistory.user }),
}));
