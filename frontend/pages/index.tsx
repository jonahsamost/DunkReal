import Image from "next/image";
import { Inter } from "next/font/google";
import YoutubeLink from "@/components/YoutubeLink";
import { YoutubeGrid } from "@/components/youtube-grid";
import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import logo from "@/public/logo.svg";
import ReactPlayer from "react-player";

const inter = Inter({ subsets: ["latin"] });

const urls = [
  "https://www.youtube.com/watch?v=e4QLHWLNt9U",
  "https://www.youtube.com/watch?v=e4QLHWLNt9U",
  "https://www.youtube.com/watch?v=e4QLHWLNt9U",
  "https://www.youtube.com/watch?v=e4QLHWLNt9U",
  "https://www.youtube.com/watch?v=e4QLHWLNt9U",
  "https://www.youtube.com/watch?v=e4QLHWLNt9U",
  "https://www.youtube.com/watch?v=e4QLHWLNt9U",
  "https://www.youtube.com/watch?v=e4QLHWLNt9U",
];

export default function Home() {
  const [loadingSnippets, setLoadingSnippets] = useState(false);
  const [snippetsUrl, setSnippetsUrl] = useState<string[]>([]);
  const [loadingReel, setLoadingReel] = useState(false);
  const [reelUrl, setReelUrl] = useState("");

  const handleSnippetClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    setLoadingSnippets(true);
    setTimeout(() => {
      setLoadingSnippets(false);
      setSnippetsUrl(urls);
    }, 10000);
  };

  const handleGeneratingClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    setLoadingReel(true);
    setTimeout(() => {
      setLoadingReel(false);
      setReelUrl("https://vimeo.com/manage/videos/883092658");
    }, 30000);
  };

  return (
    <main
      className={`flex min-h-screen flex-col items-center gap-6 p-8 ${inter.className} bg-[#0E121B]`}
    >
      <Image src={logo} alt="logo" width={300} height={120} />
      <div className="w-[600px] flex flex-col gap-4 items-center justify-center">
        <Input />
        {snippetsUrl.length === 0 && (
          <Button
            variant="secondary"
            className="flex flex-row gap-2"
            onClick={handleSnippetClick}
            disabled={loadingSnippets}
          >
            {loadingSnippets && (
              <svg
                className="animate-spin h-5 w-5"
                fill="none"
                height="24"
                stroke="currentColor"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                viewBox="0 0 24 24"
                width="24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <line x1="12" x2="12" y1="2" y2="6" />
                <line x1="12" x2="12" y1="18" y2="22" />
                <line x1="4.93" x2="7.76" y1="4.93" y2="7.76" />
                <line x1="16.24" x2="19.07" y1="16.24" y2="19.07" />
                <line x1="2" x2="6" y1="12" y2="12" />
                <line x1="18" x2="22" y1="12" y2="12" />
                <line x1="4.93" x2="7.76" y1="19.07" y2="16.24" />
                <line x1="16.24" x2="19.07" y1="7.76" y2="4.93" />
              </svg>
            )}
            {loadingSnippets ? "Generating..." : "Generate highlights"}
          </Button>
        )}
      </div>
      {!loadingReel && snippetsUrl && !reelUrl && (
        <YoutubeGrid urls={snippetsUrl} />
      )}
      {snippetsUrl.length !== 0 && !reelUrl && (
        <Button
          variant="secondary"
          className="flex flex-row gap-2"
          onClick={handleGeneratingClick}
          disabled={loadingReel}
        >
          {loadingReel && (
            <svg
              className="animate-spin h-5 w-5"
              fill="none"
              height="24"
              stroke="currentColor"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              viewBox="0 0 24 24"
              width="24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <line x1="12" x2="12" y1="2" y2="6" />
              <line x1="12" x2="12" y1="18" y2="22" />
              <line x1="4.93" x2="7.76" y1="4.93" y2="7.76" />
              <line x1="16.24" x2="19.07" y1="16.24" y2="19.07" />
              <line x1="2" x2="6" y1="12" y2="12" />
              <line x1="18" x2="22" y1="12" y2="12" />
              <line x1="4.93" x2="7.76" y1="19.07" y2="16.24" />
              <line x1="16.24" x2="19.07" y1="7.76" y2="4.93" />
            </svg>
          )}
          {loadingReel
            ? "Stitching highlights..."
            : "Stitch highlights into reel"}
        </Button>
      )}
      {reelUrl && (
        <ReactPlayer url={reelUrl} playing={true} width="900" height="507" />
      )}
      {reelUrl && (
        <Button
          onClick={(e) => {
            e.preventDefault();
            setLoadingSnippets(false);
            setSnippetsUrl([]);
            setLoadingReel(false);
            setReelUrl("");
          }}
        >
          Do again
        </Button>
      )}
    </main>
  );
}
