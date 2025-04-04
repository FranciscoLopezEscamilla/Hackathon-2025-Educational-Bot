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

export interface ChatMessage {
  id: string;
  content: string;
  type: "assistant" | "user" | "system";
}
