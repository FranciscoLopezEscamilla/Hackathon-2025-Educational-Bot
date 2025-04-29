import { getFiles } from "@/infrastructure/api/agent";
import { useEffect, useState } from "react";

export const useFolderContent = () => {
  const [projectContent, setProjectContent] = useState([]);
  const [myContent, setMyContent] = useState([]);

  useEffect(() => {
    if (projectContent.length === 0 && myContent.length === 0) {
      fetchContents();
    }
  }, []);

  const fetchContents = async () => {
    try {
      const contents = await getFiles();

      const fetchedMyContent = contents[0]?.[1] ?? [];
      const fetchedProjectContent = contents[1]?.[1] ?? [];
      setProjectContent(fetchedProjectContent);
      setMyContent(fetchedMyContent);
      console.log("Fetched contents:", fetchedProjectContent, fetchedMyContent);
    } catch (error) {
      console.error("Error fetching contents:", error);
    }
  };

  return { projectContent, myContent };
};
