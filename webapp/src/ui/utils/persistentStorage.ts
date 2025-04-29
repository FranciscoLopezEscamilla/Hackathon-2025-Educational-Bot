import { ChatHistory } from "@/types/types";
import { get, set } from "idb-keyval";

export const loadHistory = async () => {
  const history = (await get("persistent-history")) ?? {
    user: null,
    chats: [],
  };
  return history;
};

export const saveHistory = async (history: ChatHistory) => {
  await set("persistent-history", history);
};
