/* eslint-disable @typescript-eslint/no-explicit-any */
import { Chat, Message, ChatStoreActions } from "@/types/types";
import { create } from "zustand";

export const useChatStore = create<Chat & ChatStoreActions>((set): any => ({
  updatedAt: new Date().toISOString(),
  id: null,
  messages: [],
  addMessageToChat: (message: Message) =>
    set((state) => ({
      messages: [...state.messages, message],
      updatedAt: new Date().toISOString(),
    })),
  removeMessagesFromChat: (amount: number) =>
    set((state) => ({
      messages: state.messages.slice(0, state.messages.length - amount),
      updatedAt: new Date().toISOString(),
    })),
  setId: (id: string) => set({ id }),
  loadState: (state: Chat) => {
    set(state);
  },
}));
