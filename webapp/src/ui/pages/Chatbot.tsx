import MagnifyingGlass from "@/assets/MagnifyingGlass";
import ContentList from "../components/ContentList";
import ConversationalChat from "../components/ConversationalChat";
import PromptSuggestionList from "../components/PromptSuggestionList";

const Chatbot = () => {
  return (
    <>
      <aside className=" bg-zinc-800 rounded-l-xl border-r-1 border-zinc-700 flex flex-col w-2/9 min-w-70 ">
        <div className="flex justify-between items-center p-4 border-b-1 text-gray-400 border-zinc-700 text-2xl font-semibold">
          <header>Sources</header>
          <div className="cursor-pointer hover:text-gray-50 p-2 hover:bg-zinc-700 rounded-md transition-all select-none">
            <MagnifyingGlass />
          </div>
        </div>
        <div className="p-4 h-full overflow-y-auto scroll-p-4 ">
          <ContentList folders={[]} />
        </div>
      </aside>
      <section className=" bg-zinc-800 rounded-r-xl p-4 flex flex-col overflow-auto w-full">
        <div className="h-4/7 flex container justify-center  items-center">
          <ConversationalChat />
        </div>
        <div className="h-3/7 flex container justify-center flex-row flex-wrap box-border overflow-auto content-start gap-2">
          <PromptSuggestionList />
        </div>
      </section>
    </>
  );
};

export default Chatbot;
