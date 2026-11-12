import { createRoot } from "react-dom/client";
import { PlayScreen } from "./ui/PlayScreen.tsx";
import "./styles.css";

const root = document.getElementById("root");
if (root === null) {
  throw new Error("missing #root mount element");
}

createRoot(root).render(<PlayScreen />);
