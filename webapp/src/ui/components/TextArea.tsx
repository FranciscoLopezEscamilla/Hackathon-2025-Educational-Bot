import { useState } from "react";
import TextareaAutosize from "react-textarea-autosize";

export const TextArea = () => {
  const [promptMessage, setPromptMessage] = useState<string>("");

  const handleChangeMessage = (value: string) => {
    setPromptMessage(value);
  };

  return (
    <TextareaAutosize
      minRows={2}
      className="w-full text-gray-300 rounded-md outline-none resize-none overflow-hidden"
      placeholder="Type your message here..."
      value={promptMessage}
      onChange={(e) => handleChangeMessage(e.target.value)}
      required
    />
  );
};
