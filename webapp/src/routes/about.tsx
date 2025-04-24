import { historyStore } from "@/ui/state/historyStore";
import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect } from "react";
import { loadHistory, saveHistory } from "@/ui/utils/persistentStorage";
import RemoveIcon from "@/assets/RemoveIcon";

export const Route = createFileRoute("/about")({
  component: RouteComponent,
});

function RouteComponent() {
  const { chats, setHistory } = historyStore();
  const navigate = useNavigate();

  useEffect(() => {
    loadHistory().then((history) => {
      setHistory(history);
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleDeleteChat = async (id: string | null) => {
    const newChatsState = [...chats];
    const filteredChats = newChatsState.filter((chat) => chat.id !== id);
    setHistory({
      chats: filteredChats,
      user: null,
    });
    await saveHistory({
      chats: filteredChats,
      user: null,
    });
  };

  return (
    <section className="bg-zinc-800 w-full h-full text-neutral-100 flex-col flex overflow-auto rounded-xl py-8 px-6 gap-4">
      <header className="text-2xl text-gray-400 font-semibold">
        Chat History
      </header>
      <div className="flex flex-row gap-4 w-full flex-wrap">
        {chats.map((chat) => {
          return (
            <div
              key={chat.id}
              className="flex flex-col gap-2 p-4 border-1 border-zinc-700 rounded-xl w-70 hover:bg-zinc-700 transition-all "
            >
              <div className="flex flex-row gap-2 items-center">
                <p className="text-xl font-bold ">{chat.updatedAt}</p>
                <button
                  className="hover:bg-zinc-600 rounded-md h-fit flex flex-row items-center gap-1 self-start"
                  onClick={() => handleDeleteChat(chat.id)}
                >
                  <RemoveIcon size="16" />
                </button>
              </div>
              <p>{chat.messages.length} messages</p>
              <button
                className="bg-cyan-800 text-white rounded-md p-2 px-4 hover:bg-cyan-900 transition-all select-none  border-1 border-transparent hover:border-cyan-800 cursor-pointer"
                onClick={() => navigate({ to: `/${chat.id}` })}
              >
                Go to chat
              </button>
            </div>
          );
        })}
      </div>
    </section>
  );
}
