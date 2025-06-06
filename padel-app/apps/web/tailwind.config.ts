import type { Config } from "tailwindcss"
import sharedConfig from "@workspace/ui/tailwind.config"

const config: Pick<Config, "content" | "presets"> = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
    "../../packages/ui/**/*.{js,ts,jsx,tsx}",
  ],
  presets: [sharedConfig],
}

export default config 