import FolderIcon from "@/assets/FolderIcon";
import { FolderItem } from "@/types/types";
import { useState } from "react";

interface IProps {
  folders: FolderItem[];
}

const ContentList = ({ folders = [] }: IProps) => {
  const [activeCategories, setActiveCategories] = useState<string[]>(
    folders[1] ? [folders[1].name] : []
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
      {folders.map((folder) => (
        <>
          <div
            key={folder.id}
            onClick={() => handleCategoryClick(folder.name)}
            className="flex flex-row items-center gap-2 cursor-pointer hover:bg-zinc-700 p-2 rounded-md transition-all select-none border-1 border-transparent hover:border-zinc-600"
          >
            <FolderIcon />
            <span className="font-semibold">{folder.name}</span>
          </div>
          <ul
            className={`flex flex-col gap-2 pl-4 text-gray-400 ${
              activeCategories.includes(folder.name) ? "block" : "hidden"
            }`}
          >
            {folder.files.map((file) => (
              <li key={file.name}>
                <span>{file.name}</span>
              </li>
            ))}
          </ul>
        </>
      ))}
    </div>
  );
};

export default ContentList;
