import { StrictMode } from "react";
import "./globals.css";
import ReactDOM from "react-dom/client";
import App from "./App";
import { Toaster } from "sonner";

const rootElement = document.getElementById("root")!;
if (!rootElement.innerHTML) {
  const root = ReactDOM.createRoot(rootElement);
  root.render(
    <StrictMode>
      <Toaster position="top-right" />
      <App />
    </StrictMode>
  );
}
