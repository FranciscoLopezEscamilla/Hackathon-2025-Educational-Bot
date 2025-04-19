export interface AuthenticationState {
  isAuthenticated: boolean;
  login: () => void;
  logout: () => void;
}

export interface FolderItem {
  id: number;
  name: string;
  files: string[];
}

export interface FileItem {
  id: string;
  name: string;
  extension: string;
}

export interface ChatHistory {
  chats: Chat[];
  user: string | null;
  //
}

export interface Chat {
  id: string;
  updatedAt: string;
  messages: Message[];
}

export interface Message {
  id: string;
  content: string;
  type: "assistant" | "user" | "system";
}

export interface ChatStoreActions {
  addMessageToChat: (message: Message) => void;
  removeMessagesFromChat: (amount: number) => void;
  setId: (id: string) => void;
  loadState: (state: Chat) => void;
}
