import { useState } from "react";
import "./App.css";
import { Message } from "./types/globalTypes";
import TypeWriterContainer from "./components/TypeWriterContainer";

function App() {
  const [messageHistory, setMessageHistory] = useState<Message[]>([]);
  const [message, setMessage] = useState<string>("");

  const sendMessage = async () => {
    const response = await fetch(
      "http://192.168.100.5:3000/api/chat/completions",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer [DEEPSEEK_API_KEY]",
        },
        body: JSON.stringify({
          model: "deepseek-r1:8b",
          messages: [
            ...messageHistory,
            {
              role: "user",
              content: message,
            },
          ],
        }),
      }
    );

    const data = await response.json();
    console.log(data);

    const responseMessage = data.choices[0].message.content;
    const findThink = responseMessage.indexOf("<think>");
    const findThinkEnd = responseMessage.indexOf("</think>");
    const otherMessage =
      responseMessage.slice(0, findThink) +
      responseMessage.slice(findThinkEnd + 8);

    const newMessageHistory: Message[] = [
      ...messageHistory,
      {
        content: message,
        role: "user",
        id: new Date().toISOString(),
      },
      {
        content: otherMessage,
        role: "assistant",
        id: new Date().toISOString() + "bot",
      },
    ];

    setMessageHistory(newMessageHistory);
  };

  return (
    <main>
      <section className="title">
        <h1>AI Tool with Chatbot</h1>
        <p>
          AI Tool is a web application that allows users to consult upskilling
          content and be assisted by a chatbot.
        </p>
      </section>
      <section className="chat-history">
        {messageHistory
          .slice(0)
          .reverse()
          .map((message) => {
            return message.role === "user" ? (
              <div key={message.id} className="user">
                {message.content}
              </div>
            ) : (
              <TypeWriterContainer key={message.id} message={message} />
            );
          })}
      </section>
      <section className="chat-input">
        <form>
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
          />
          <button
            onClick={(e) => {
              e.preventDefault();
              sendMessage();
              setMessage("");
            }}
          >
            Send
          </button>
        </form>
      </section>
    </main>
  );
}

export default App;
