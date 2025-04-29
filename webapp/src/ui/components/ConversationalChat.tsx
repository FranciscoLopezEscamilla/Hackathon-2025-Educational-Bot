import AttachmentIcon from "@/assets/AttachmentIcon";
import RemoveIcon from "@/assets/RemoveIcon";
import { Message } from "@/types/types";
import { useEffect, useRef, useState } from "react";
import Markdown from "react-markdown";
import TextareaAutosize from "react-textarea-autosize";
import { CopyIcon } from "@/assets/CopyIcon";
import { ArrowPath } from "@/assets/ArrowPath";
import { useChatStore } from "@/ui/state/chatStore";

interface IProps {
  handleOnSubmitForm: (formData: FormData) => void;
  loadingChatResponse: boolean;
  reSendLastMessage: () => void;
  showToast: (message: string) => void;
  inputRef: React.RefObject<HTMLTextAreaElement | null>;
}

const ConversationalChat = ({
  handleOnSubmitForm,
  loadingChatResponse,
  reSendLastMessage,
  showToast,
  inputRef,
}: IProps) => {
  const [selectedAvailableTools, setSelectedAvailableTools] = useState<
    string[]
  >([]);
  const [uploadedFiles, setUploadedFiles] = useState<FileList | null>(null);
  const chatHistory = useChatStore((state) => state.messages);
  const scrollRef = useRef<HTMLInputElement>(null);
  const filesRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (scrollRef.current && chatHistory.length > 0) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [chatHistory]);

  const handleToggleAvailableTools = (tool: string) => {
    if (selectedAvailableTools.includes(tool)) {
      setSelectedAvailableTools(
        selectedAvailableTools.filter((t) => t !== tool)
      );
    } else {
      setSelectedAvailableTools([...selectedAvailableTools, tool]);
    }
  };

  const getFilesList = () => {
    const files = filesRef.current?.files || null;
    console.log(files);
    setUploadedFiles(files);
  };

  const removeFiles = () => {
    setUploadedFiles(null);
    if (filesRef.current) {
      filesRef.current.value = "";
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log(e);
    const fileList = filesRef.current?.files;
    // Build FormData
    const formData = new FormData();
    Array.from(fileList || []).forEach(
      (file) => formData.append("files", file) // must match FastAPI
    );
    if (inputRef?.current) {
      formData.append("query", inputRef.current.value);
    }
    formData.append("message_history", JSON.stringify(chatHistory));

    for (const [key, val] of formData.entries()) {
      console.log(key, val);
    }

    handleOnSubmitForm(formData);

    removeFiles();
  };

  return (
    <div className="w-full h-full flex flex-col min-h-0 grow gap-2 justify-center items-center">
      {chatHistory.length > 0 && (
        <div
          className="overflow-auto h-full grow shrink basis-0 w-full gutter-stable"
          ref={scrollRef}
        >
          <div className="flex flex-col gap-4 w-full sm:w-full lg:w-5/8 mx-auto my-16">
            {chatHistory.map(({ content, type }: Message) => {
              return (
                <div
                  key={crypto.randomUUID()}
                  className={`transition-all w-fit rounded-t-xl py-2 text-gray-100  ${
                    type === "user"
                      ? "self-end rounded-bl-xl bg-cyan-900 border-gray-600 border-1 px-3 my-4  max-w-7/10 "
                      : "self-start rounded-br-xl w-full max-w-9/10"
                  }`}
                >
                  <article
                    className={`prose prose-md prose-invert ${
                      type === "user" ? "text-white" : "max-w-none"
                    }`}
                  >
                    <Markdown>{content}</Markdown>
                  </article>
                </div>
              );
            })}
            {loadingChatResponse && (
              <div className="flex flex-col w-full sm:w-full lg:w-5/8 animate-pulse ">
                <p className="text-zinc-400">Thinking...</p>
              </div>
            )}
            {!loadingChatResponse && (
              <div className="flex flex-row w-full gap-1">
                <button
                  className="px-2 py-1 text-zinc-400 rounded-md align-middle hover:bg-zinc-700 cursor-pointer transition-all select-none"
                  onClick={() => {
                    navigator.clipboard.writeText(
                      chatHistory[chatHistory.length - 1].content
                    );
                    showToast("Message copied to clipboard");
                  }}
                >
                  <CopyIcon size="16" />
                </button>
                <button
                  className="px-2 py-1 text-zinc-400 rounded-md align-middle hover:bg-zinc-700 cursor-pointer transition-all select-none"
                  onClick={reSendLastMessage}
                >
                  <ArrowPath size="16" />
                </button>
              </div>
            )}
          </div>
        </div>
      )}
      {chatHistory.length === 0 && (
        <h1 className="text-2xl font-semibold">
          Welcome to NebulaCore Project
        </h1>
      )}
      {/* message box */}
      <div className="w-full sm:w-full lg:w-5/8 bg-zinc-700 rounded-xl p-4 flex flex-col gap-2 box-border">
        <form
          id="prompt-form"
          onSubmit={handleSubmit}
          encType="multipart/form-data"
        >
          <TextareaAutosize
            minRows={2}
            className="w-full text-gray-300 rounded-md outline-none resize-none overflow-hidden"
            placeholder="Type your message here..."
            ref={inputRef}
            itemRef="input"
            required
          />
        </form>
        <div className="flex flex-row gap-2 justify-between ">
          <span className="flex flex-row gap-4 items-end ">
            <span className=" text-white rounded-md transition-all select-none flex justify-between items-center gap-1 cursor-pointer hover:text-zinc-400 ">
              <AttachmentIcon size="16" />
              <input
                type="file"
                name="files"
                className="hidden"
                id="file"
                placeholder="w"
                ref={filesRef}
                onChange={getFilesList}
                multiple
              />
              <label htmlFor="file" className="cursor-pointer">
                Attach files
              </label>
            </span>
          </span>
          <button
            type="submit"
            form="prompt-form"
            disabled={loadingChatResponse}
            className={`bg-cyan-800 text-white rounded-md p-2 px-4 hover:bg-cyan-900 transition-all select-none  border-1 border-transparent hover:border-cyan-800 ${loadingChatResponse ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}
          >
            Send
          </button>
        </div>
        {Array.from(uploadedFiles ?? []).length > 0 && (
          <div className="flex flex-row gap-2 w-full items-center justify-between ">
            <div className="flex gap-4 ">
              {Array.from(uploadedFiles ?? []).map(({ lastModified, name }) => {
                return (
                  <div className="flex" key={lastModified}>
                    <p className="text-gray-400 truncate max-w-20">{name}</p>
                  </div>
                );
              })}
            </div>
            <button
              className="hover:bg-zinc-600 rounded-md h-fit flex flex-row items-center gap-1"
              onClick={() => removeFiles()}
            >
              <RemoveIcon size="16" />
            </button>
          </div>
        )}
      </div>
      {/* available tools */}
      <div className="w-full flex flex-col gap-2 box-border text-gray-300 pt-4 items-center text-center">
        <div className="w-full">Available Tools:</div>
        <div className="flex flex-row gap-2 ">
          <div
            className={`${selectedAvailableTools.includes("Image Generation") ? "bg-zinc-700 text-cyan-500" : "bg-zinc-800 text-gray-300"} p-2 px-4 border-1 border-zinc-600 rounded-md hover:bg-zinc-700 transition-all cursor-pointer select-none`}
            onClick={() => handleToggleAvailableTools("Image Generation")}
          >
            Image Generation
          </div>{" "}
          <div
            className={`${selectedAvailableTools.includes("Diagram Generation") ? "bg-zinc-700 text-cyan-500" : "bg-zinc-800 text-gray-300"} p-2 px-4 border-1 border-zinc-600 rounded-md hover:bg-zinc-700 transition-all cursor-pointer select-none`}
            onClick={() => handleToggleAvailableTools("Diagram Generation")}
          >
            Diagram Generation
          </div>
          <div
            className={`${selectedAvailableTools.includes("Content Writer") ? "bg-zinc-700 text-cyan-500" : "bg-zinc-800 text-gray-300"} p-2 px-4 border-1 border-zinc-600 rounded-md hover:bg-zinc-700 transition-all cursor-pointer select-none`}
            onClick={() => handleToggleAvailableTools("Content Writer")}
          >
            PDF Writer
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConversationalChat;
