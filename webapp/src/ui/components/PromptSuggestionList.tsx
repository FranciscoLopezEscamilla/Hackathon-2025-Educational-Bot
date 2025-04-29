const cardStyle =
  "w-60 h-45 flex text-wrap p-4 text-gray-400 border-1 border-zinc-600 rounded-md hover:bg-zinc-700 hover:text-white cursor-pointer transition-all select-none";

interface IProps {
  handleOnSubmitForm: (formData: FormData) => void;
}

const PromptSuggestionList = ({ handleOnSubmitForm }: IProps) => {
  return (
    <>
      <div
        className={cardStyle}
        onClick={() => {
          const text =
            "What should I start doing as a new joiner in NebulaCore Project?";
          const formData = new FormData();
          formData.append("query", text);
          handleOnSubmitForm(formData);
        }}
      >
        <p>What should I start doing as a new joiner in NebulaCore Project?</p>
      </div>
      <div
        className={cardStyle}
        onClick={() => {
          const text = "What is the purpose of the Sales_Data_Q2.xlsx file?";
          const formData = new FormData();
          formData.append("query", text);
          handleOnSubmitForm(formData);
        }}
      >
        <p>Give me a summary of the onboarding file</p>
      </div>
      <div
        className={cardStyle}
        onClick={() => {
          const text = "When is the next major release?";
          const formData = new FormData();
          formData.append("query", text);
          handleOnSubmitForm(formData);
        }}
      >
        <p>When is the next major release?</p>
      </div>
    </>
  );
};

export default PromptSuggestionList;
