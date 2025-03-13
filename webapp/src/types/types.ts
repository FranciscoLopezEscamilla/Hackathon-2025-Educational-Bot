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
