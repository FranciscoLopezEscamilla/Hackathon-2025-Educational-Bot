import MagnifyingGlass from "@/assets/MagnifyingGlass";
import ContentList from "@/ui/components/ContentList";
import ConversationalChat from "@/ui/components/ConversationalChat";
import PromptSuggestionList from "@/ui/components/PromptSuggestionList";
import { useParams } from "@tanstack/react-router";
import { showSuccessToast } from "../utils/toast";
import { useChatStore } from "../state/chatStore";
import { useChatbotHistory } from "../hooks/useChatbotHistory";
import { useChatbotActions } from "../hooks/useChatbotActions";
import { useFolderContent } from "../hooks/useFolderContent";

const ChatbotView = () => {
  const { id: paramId } = useParams({ strict: false });
  const { messages } = useChatStore();
  const { projectContent, myContent } = useFolderContent();

  useChatbotHistory(paramId);

  const {
    inputRef,
    loadingChatResponse,
    handleOnSubmitForm,
    reSendLastMessage,
  } = useChatbotActions();

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
          <ContentList
            folders={[
              { id: 1, name: "My Content", files: myContent },
              { id: 2, name: "NebulaCore Project", files: projectContent },
            ]}
          />
        </div>
        <div className="text-md border-t-1 text-gray-400 border-zinc-700 p-4 flex flex-row gap-2 justify-between">
          <span>Source of information for the chatbot.</span>
        </div>
      </aside>
      <section className=" bg-zinc-800 rounded-r-xl p-4 flex flex-col w-full h-full ">
        <div
          className={`h-4/7 flex justify-center lg:${messages.length > 0 ? "items-end" : "items-center"} box-border sm:h-full sm:items-end transition-all`}
        >
          <ConversationalChat
            inputRef={inputRef}
            handleOnSubmitForm={handleOnSubmitForm}
            loadingChatResponse={loadingChatResponse}
            reSendLastMessage={reSendLastMessage}
            showToast={showSuccessToast}
          />
        </div>
        {messages.length === 0 && (
          <div className="h-3/7 flex justify-center flex-row flex-wrap box-border overflow-auto content-start gap-2 lg:hidden sm:hidden xl:flex">
            <PromptSuggestionList handleOnSubmitForm={handleOnSubmitForm} />
          </div>
        )}
      </section>
    </>
  );
};

export default ChatbotView;
