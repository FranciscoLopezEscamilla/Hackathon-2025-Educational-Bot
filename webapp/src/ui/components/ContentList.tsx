import FolderIcon from "@/assets/FolderIcon";
import { FolderItem } from "@/types/types";
import { useState } from "react";

interface IProps {
  folders: FolderItem[];
}

const ContentList = ({ folders = [] }: IProps) => {
  const [activeCategories, setActiveCategories] = useState<string[]>(
    folders[0] ? [folders[0].name] : ["NebulaCore Project"]
  );

  const handleCategoryClick = (category: string) => {
    if (activeCategories.includes(category)) {
      setActiveCategories(activeCategories.filter((item) => item !== category));
    } else {
      setActiveCategories([...activeCategories, category]);
    }
  };

  return (
    <div className="flex flex-col gap-2">
      <div
        onClick={() => handleCategoryClick("NebulaCore Project")}
        className="flex flex-row items-center gap-2 cursor-pointer hover:bg-zinc-700 p-2 rounded-md transition-all select-none border-1 border-transparent hover:border-zinc-600"
      >
        <FolderIcon />
        <span className="font-semibold">NebulaCore Project</span>
      </div>
      <ul
        className={`flex flex-col gap-2 pl-4 text-gray-400 ${activeCategories.includes("NebulaCore Project") ? "block" : "hidden"}`}
      >
        <li>Report_Q1_2024.pdf</li>
        <li>Invoice_34567.xlsx</li>
        <li>Project_Plan.docx</li>
        <li>Meeting_Notes_0415.txt</li>
        <li>Budget_Analysis_2024.xlsx</li>
        <li>Presentation_Slides.pptx</li>
        <li>UI_Design_Sketch.fig</li>
        <li>Customer_Feedback.csv</li>
        <li>Marketing_Strategy_Deck.pdf</li>
        <li>HR_Policies.docx</li>
        <li>Backend_API_Docs.md</li>
        <li>Product_Requirements_Specs.pdf</li>
        <li>Sales_Data_Q2.xlsx</li>
        <li>Onboarding_Guide.pdf</li>
        <li>Security_Audit_Report.docx</li>
        <li>Quarterly_Performance_Review.pdf</li>
        <li>System_Architecture_Diagram.png</li>
        <li>Developer_Handbook.md</li>
        <li>Expense_Report_2024.xlsx</li>
        <li>Legal_Agreement_Contract.pdf</li>
        <li>Client_Proposal.pptx</li>
        <li>Research_Paper_Final.docx</li>
        <li>Workshop_Agenda.pdf</li>
        <li>Bug_Report_List.xlsx</li>
      </ul>
      <div
        onClick={() => handleCategoryClick("My Content")}
        className="flex flex-row items-center gap-2 cursor-pointer hover:bg-zinc-700 p-2 rounded-md transition-all select-none border-1 border-transparent hover:border-zinc-600"
      >
        <FolderIcon />
        <span className="font-semibold">My Content</span>
      </div>
    </div>
  );
};

export default ContentList;
