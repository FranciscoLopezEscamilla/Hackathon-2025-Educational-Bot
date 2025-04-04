import AttachmentIcon from "@/assets/AttachmentIcon";
import ImageIcon from "@/assets/ImageIcon";
import RemoveIcon from "@/assets/RemoveIcon";
import { ChatMessage, FileItem } from "@/types/types";
import { useEffect, useRef, useState } from "react";
import { useChatStore } from "../state/chatStore";

interface IProps {
  handleChangeMessage: (value: string) => void;
  message: string;
  handleOnSubmitForm: (message: string) => void;
  loadingChatResponse: boolean;
}

const ConversationalChat = ({
  handleChangeMessage,
  message,
  handleOnSubmitForm,
  loadingChatResponse,
}: IProps) => {
  const [selectedAvailableTools, setSelectedAvailableTools] = useState<
    string[]
  >([]);
  const [uploadedFiles, setUploadedFiles] = useState<FileItem[]>([]);
  const chatHistory = useChatStore((state) => state.chatHistory);
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
    const files = filesRef.current?.files;
    if (files) {
      const fileList = Array.from(files).map((file): FileItem => {
        return {
          id: file.name + crypto.randomUUID(),
          name: file.name,
          extension: getFileExtension(file.name),
        };
      });
      console.log(Array.from(files));
      setUploadedFiles(fileList);
    }
  };

  const getFileExtension = (fileName: string) => {
    const fileExtension = fileName.split(".").pop() as string;
    return fileExtension;
  };

  const removeFiles = () => {
    setUploadedFiles([]);
    if (filesRef.current) {
      filesRef.current.value = "";
    }
  };

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    handleOnSubmitForm(message);
  };

  return (
    <div className="w-full h-full flex flex-col min-h-0 grow gap-2 justify-center items-center">
      {chatHistory.length > 0 && (
        <div
          className="overflow-auto h-full grow shrink basis-0 w-full gutter-stable"
          ref={scrollRef}
        >
          <div className="flex flex-col gap-4 w-full sm:w-full lg:w-5/8 mx-auto my-16">
            {chatHistory.map(({ id, content, type }: ChatMessage) => {
              return (
                <div
                  key={id}
                  className={`transition-all w-fit max-w-7/10 border-1 border-gray-600 rounded-t-xl px-3 py-2 bg-cyan-900 text-gray-100 ${
                    type === "user"
                      ? "self-end rounded-bl-xl"
                      : "self-start rounded-br-xl"
                  }`}
                >
                  <p>{content}</p>
                </div>
              );
            })}
            {loadingChatResponse && (
              <div className="flex flex-col w-full sm:w-full lg:w-5/8 animate-pulse ">
                <p className="text-zinc-400">Thinking...</p>
              </div>
            )}
          </div>
        </div>
      )}
      {chatHistory.length === 0 && (
        <h1 className="text-2xl font-semibold">
          Welcome to ABC Project, accenture.id
        </h1>
      )}
      {/* message box */}
      <div className="w-full sm:w-full lg:w-5/8 bg-zinc-700 rounded-xl p-4 flex flex-col gap-2 box-border">
        <form id="prompt-form" onSubmit={handleSubmit}>
          <textarea
            className="w-full h-full text-gray-300 rounded-md outline-none resize-none"
            placeholder="Type your message here..."
            value={message}
            onChange={(e) => handleChangeMessage(e.target.value)}
            required
          ></textarea>
        </form>
        <div className="flex flex-row gap-2 justify-between ">
          <span className="flex flex-row gap-4 items-end ">
            <span className=" text-white rounded-md transition-all select-none flex justify-between items-center gap-1 cursor-pointer hover:text-zinc-400 ">
              <AttachmentIcon size="16" />
              <input
                type="file"
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
            <button className=" text-white rounded-md transition-all select-none flex justify-between items-center gap-1 cursor-pointer hover:text-zinc-400">
              <ImageIcon size="16" />
              Use Image
            </button>
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
        {uploadedFiles.length > 0 && (
          <div className="flex flex-row gap-2 w-full items-center justify-between ">
            <div className="flex gap-4 ">
              {uploadedFiles.map(({ id, extension, name }) => {
                return (
                  <div className="flex" key={id}>
                    <p className="text-gray-400 truncate max-w-20">{name}</p>
                    <p className="text-gray-400 truncate">.{extension}</p>
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
            Content Writer
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConversationalChat;
