import React, { Dispatch, SetStateAction } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export default function YoutubeLink({ loading, handleClick }: { loading: boolean, handleClick: React.MouseEventHandler<HTMLButtonElement>}) {

  return (
    <div className="w-[600px] flex flex-col gap-2 items-center justify-center">
      <Input />
      <Button
        variant="secondary"
        className="flex flex-row gap-2"
        onClick={handleClick}
        disabled={loading}
      >
        {loading && (
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
        {loading ? "Generating..." : "Generate highlights"}
      </Button>
    </div>
  );
}
