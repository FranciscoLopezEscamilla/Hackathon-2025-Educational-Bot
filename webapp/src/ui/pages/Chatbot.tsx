import MagnifyingGlass from "@/assets/MagnifyingGlass";
import ContentList from "@/ui/components/ContentList";
import ConversationalChat from "@/ui/components/ConversationalChat";
import PromptSuggestionList from "@/ui/components/PromptSuggestionList";
import { useState } from "react";
import { useChatStore } from "../state/chatStore";

const Chatbot = () => {
  const [promptMessage, setPromptMessage] = useState<string>("");
  const chatHistory = useChatStore((state) => state.chatHistory);
  const setChatHistory = useChatStore((state) => state.addMessageToChatHistory);

  const handleChangeMessage = (value: string) => {
    setPromptMessage(value);
  };

  const addUserMessageToChatHistory = (message: string) => {
    setChatHistory({ id: crypto.randomUUID(), message, type: "user" });
  };

  const handleOnSubmitForm = (message: string) => {
    addUserMessageToChatHistory(message);
    handleChangeMessage("");
  };

  return (
    <>
      <aside className=" bg-zinc-800 rounded-l-xl border-r-1 border-zinc-700 flex flex-col w-2/9 min-w-70 ">
        <div className="flex justify-between items-center p-4 border-b-1 text-gray-400 border-zinc-700  font-semibold">
          <header className="text-2xl">Sources</header>
          <div className="cursor-pointer hover:text-gray-50 p-2 hover:bg-zinc-700 rounded-md transition-all select-none">
            <MagnifyingGlass />
          </div>
        </div>
        <div className="p-4 h-full overflow-y-auto scroll-p-4 ">
          <ContentList folders={[]} />
        </div>

        <div className="text-md border-t-1 text-gray-400 border-zinc-700 p-4 flex flex-row gap-2 justify-between">
          <span>Source of information for the chatbot.</span>
        </div>
      </aside>
      <section className=" bg-zinc-800 rounded-r-xl p-4 flex flex-col w-full h-full ">
        <div
          className={`h-4/7 flex justify-center lg:${chatHistory.length > 0 ? "items-end" : "items-center"} box-border sm:h-full sm:items-end transition-all`}
        >
          <ConversationalChat
            handleChangeMessage={handleChangeMessage}
            message={promptMessage}
            handleOnSubmitForm={handleOnSubmitForm}
          />
        </div>
        {chatHistory.length === 0 && (
          <div className="h-3/7 flex justify-center flex-row flex-wrap box-border overflow-auto content-start gap-2 lg:hidden sm:hidden xl:flex">
            <PromptSuggestionList handleOnSubmitForm={handleOnSubmitForm} />
          </div>
        )}
      </section>
    </>
  );
};

export default Chatbot;
