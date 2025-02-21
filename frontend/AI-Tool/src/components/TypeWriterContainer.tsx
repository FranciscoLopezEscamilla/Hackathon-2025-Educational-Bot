import { useEffect, useState } from "react";
import { Message } from "../types/globalTypes";
import Markdown from "react-markdown";

interface IProps {
  message: Message;
}

const TypeWriterContainer = ({ message }: IProps) => {
  const [messageIndex, setMessageIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setMessageIndex((prev) => {
        if (prev >= message.content.length) {
          clearInterval(interval);
        }
        return prev + 5;
      });

      console.log("clear");
    }, 20);

    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="assistant">
      <Markdown>{message.content.slice(0, messageIndex)}</Markdown>
    </div>
  );
};

export default TypeWriterContainer;
