import AttachmentIcon from "@/assets/AttachmentIcon";
import ImageIcon from "@/assets/ImageIcon";
import { useState } from "react";

const ConversationalChat = () => {
  const [selectedAvailableTools, setSelectedAvailableTools] = useState<
    string[]
  >([]);

  const handleToggleAvailableTools = (tool: string) => {
    if (selectedAvailableTools.includes(tool)) {
      setSelectedAvailableTools(
        selectedAvailableTools.filter((t) => t !== tool)
      );
    } else {
      setSelectedAvailableTools([...selectedAvailableTools, tool]);
    }
  };

  return (
    <span className="flex flex-col gap-2 w-full items-center">
      <h1 className="text-2xl font-semibold">Chat With AI 🤖</h1>
      <div className="w-full max-w-2/4 bg-zinc-700 rounded-xl p-4 flex flex-col gap-2 box-border">
        <textarea
          className="w-full h-full text-gray-300 rounded-md outline-none resize-none"
          placeholder="Type your message here..."
        ></textarea>
        <div className="flex flex-row gap-2 justify-between">
          <span className="flex flex-row gap-4 items-end">
            <button className=" text-white rounded-md transition-all select-none flex justify-between items-center gap-1 cursor-pointer hover:text-zinc-400 ">
              <AttachmentIcon size="16" />
              Attach File
            </button>
            <button className=" text-white rounded-md transition-all select-none flex justify-between items-center gap-1 cursor-pointer hover:text-zinc-400">
              <ImageIcon size="16" />
              Use Image
            </button>
          </span>
          <button className="bg-cyan-800 text-white rounded-md p-2 px-4 hover:bg-cyan-900 transition-all select-none cursor-pointer border-1 border-transparent hover:border-cyan-800 ">
            Send
          </button>
        </div>
      </div>
      <div className="w-full max-w-2/4 flex flex-col gap-2 box-border text-gray-300 pt-4">
        <div className="w-full">Available Tools:</div>
        <div className="flex flex-row gap-2 ">
          <div
            className={`${selectedAvailableTools.includes("Image Generation") ? "bg-zinc-700 text-cyan-500" : "bg-zinc-800 text-gray-300"} p-2 px-4 border-1 border-zinc-600 rounded-md hover:bg-zinc-700 transition-all cursor-crosshair select-none`}
            onClick={() => handleToggleAvailableTools("Image Generation")}
          >
            Image Generation
          </div>{" "}
          <div
            className={`${selectedAvailableTools.includes("Diagram Generation") ? "bg-zinc-700 text-cyan-500" : "bg-zinc-800 text-gray-300"} p-2 px-4 border-1 border-zinc-600 rounded-md hover:bg-zinc-700 transition-all cursor-crosshair select-none`}
            onClick={() => handleToggleAvailableTools("Diagram Generation")}
          >
            Diagram Generation
          </div>
          <div
            className={`${selectedAvailableTools.includes("Content Writer") ? "bg-zinc-700 text-cyan-500" : "bg-zinc-800 text-gray-300"} p-2 px-4 border-1 border-zinc-600 rounded-md hover:bg-zinc-700 transition-all cursor-crosshair select-none`}
            onClick={() => handleToggleAvailableTools("Content Writer")}
          >
            Content Writer
          </div>
        </div>
      </div>
    </span>
  );
};

export default ConversationalChat;
