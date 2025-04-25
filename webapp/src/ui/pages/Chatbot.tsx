import MagnifyingGlass from "@/assets/MagnifyingGlass";
import ContentList from "@/ui/components/ContentList";
import ConversationalChat from "@/ui/components/ConversationalChat";
import PromptSuggestionList from "@/ui/components/PromptSuggestionList";
import { useEffect, useState } from "react";
import { useChatStore } from "../state/chatStore";
import { historyStore } from "../state/historyStore";
import { showSuccessToast } from "../utils/toast";
import { useNavigate, useParams } from "@tanstack/react-router";
import { loadHistory, saveHistory } from "../utils/persistentStorage";
import { callToAgent } from "@/infrastructure/api/agent";

const Chatbot = () => {
  const { id: paramId } = useParams({ strict: false });
  const [loadingChatResponse, setLoadingChatResponse] =
    useState<boolean>(false);
  const [promptMessage, setPromptMessage] = useState<string>("");
  const navigate = useNavigate();

  const {
    addMessageToChat,
    removeMessagesFromChat,
    messages,
    id,
    setId,
    loadState,
  } = useChatStore();
  const { setHistory, chats } = historyStore();

  const handleChangeMessage = (value: string) => {
    setPromptMessage(value);
  };

  const handleOnSubmitForm = async (formData: FormData) => {
    const randomUUID = crypto.randomUUID();
    const isFirstMessage = messages.length === 0;
    const message = formData.get("query") as string;

    handleChangeMessage("");
    addMessageToChat({
      id: crypto.randomUUID(),
      content: message,
      type: "user",
    });

    setLoadingChatResponse(true);

    try {
      const response = await callToAgent(formData);
      addMessageToChat({
        id: crypto.randomUUID(),
        content: response.messages[response.messages.length - 1].content,
        type: "assistant",
      });
    } catch (error) {
      console.log(error);
      addMessageToChat({
        id: crypto.randomUUID(),
        content: "Sorry, I couldn't understand your message.",
        type: "assistant",
      });
    } finally {
      setLoadingChatResponse(false);
      if (isFirstMessage) {
        setId(randomUUID);
        navigate({ to: `/${randomUUID}` });
      }
    }
  };

  useEffect(() => {
    loadHistory().then((history) => {
      setHistory(history);
    });

    return () => {
      //reset the state when the component is unmounted
      loadState({
        messages: [],
        id: null,
        updatedAt: new Date().toISOString(),
      });
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const newChatsState = [...chats];

    if (id && messages.length > 0) {
      const foundChatIndex = newChatsState.findIndex((chat) => chat.id === id);
      if (foundChatIndex !== -1) {
        newChatsState[foundChatIndex].messages = messages;
        saveHistory({
          chats: newChatsState,
          user: null,
        });
      } else {
        newChatsState.push({
          id,
          updatedAt: new Date().toISOString(),
          messages,
        });
        saveHistory({
          chats: newChatsState,
          user: null,
        });
      }
    }

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [messages, id]);

  const reSendLastMessage = () => {
    removeMessagesFromChat(2);
    const lastMessage = messages[messages.length - 2];
    const formData = new FormData();
    formData.append("query", lastMessage.content);
    handleOnSubmitForm(formData);
  };

  useEffect(() => {
    if (paramId && chats.length > 0) {
      const foundChatIndex = chats.findIndex((chat) => chat.id === paramId);
      if (foundChatIndex !== -1) {
        loadState(chats[foundChatIndex]);
      }
    }
  }, [paramId, chats, loadState]);

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
          className={`h-4/7 flex justify-center lg:${messages.length > 0 ? "items-end" : "items-center"} box-border sm:h-full sm:items-end transition-all`}
        >
          <ConversationalChat
            handleChangeMessage={handleChangeMessage}
            message={promptMessage}
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

export default Chatbot;
