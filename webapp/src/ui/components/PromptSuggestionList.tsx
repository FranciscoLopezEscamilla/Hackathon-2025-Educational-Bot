const cardStyle =
  "w-60 h-45 flex text-wrap p-4 text-gray-400 border-1 border-zinc-600 rounded-md hover:bg-zinc-700 hover:text-white cursor-pointer transition-all select-none";

interface IProps {
  handleOnSubmitForm: (message: string) => void;
}

const PromptSuggestionList = ({ handleOnSubmitForm }: IProps) => {
  return (
    <>
      <div
        className={cardStyle}
        onClick={() =>
          handleOnSubmitForm(
            "What should I start doing as a new joiner in ABC Project?"
          )
        }
      >
        <p>What should I start doing as a new joiner in ABC Project?</p>
      </div>
      <div
        className={cardStyle}
        onClick={() =>
          handleOnSubmitForm("Give me a summary of the Sales_Data_Q2.xlsx file")
        }
      >
        <p>Give me a summary of the Sales_Data_Q2.xlsx file</p>
      </div>
      <div
        className={cardStyle}
        onClick={() => handleOnSubmitForm("When is the next major release?")}
      >
        <p>When is the next major release?</p>
      </div>
    </>
  );
};

export default PromptSuggestionList;
