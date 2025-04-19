import { Chat } from "@/types/types";

interface IProps {
  chat: Chat;
}

export const ChatCard = ({ chat }: IProps) => {
  return (
    <div className="flex flex-col gap-2 p-4 border-1 border-zinc-700 rounded-xl">
      <h1>{chat.id}</h1>
      <p>{chat.updatedAt}</p>
      <p>{chat.messages.length} messages</p>
    </div>
  );
};
