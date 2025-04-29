import axios from "axios";

const AGENT_API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
console.log(AGENT_API_BASE_URL);

export const callToAgent = async (formData: FormData) => {
  console.log(formData);
  const resp = await axios.post(
    `${AGENT_API_BASE_URL}/api/agents/agentic_rag_v3`,
    formData
  );
  return resp.data;
};

export const getFiles = async () => {
  const resp = await axios.post(
    `${AGENT_API_BASE_URL}/api/storage_account/blobs`
  );
  return resp.data;
};
