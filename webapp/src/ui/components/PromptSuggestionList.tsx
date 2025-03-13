import React from "react";

const cardStyle =
  "w-60 h-45 flex text-wrap p-4 text-gray-400 border-1 border-zinc-600 rounded-md hover:bg-zinc-700 hover:text-white cursor-pointer transition-all select-none";

const PromptSuggestionList = () => {
  return (
    <>
      <div className={cardStyle}>
        <p>What should I start doing as a new joiner in ABC Project?</p>
      </div>
      <div className={cardStyle}>
        <p>Give me a summary of the project requirements</p>
      </div>
      <div className={cardStyle}>
        <p>When is the next major release?</p>
      </div>
    </>
  );
};

export default PromptSuggestionList;
