import React from 'react';
import { BookOpen } from 'lucide-react';
import { CitationClickHandler } from '../types';

interface ParsedContentProps {
  content: string;
  onCitationClick: CitationClickHandler;
}

export const ParsedContent: React.FC<ParsedContentProps> = ({ content, onCitationClick }) => {
  // Regex to match [[source_id]]
  const parts = content.split(/(\[\[.*?\]\])/g);

  return (
    <div className="markdown-body text-slate-300 leading-relaxed text-sm md:text-base">
      {parts.map((part, index) => {
        const match = part.match(/^\[\[(.*?)\]\]$/);
        if (match) {
          const id = match[1];
          return (
            <button
              key={index}
              onClick={() => onCitationClick(id)}
              className="citation-link inline-flex items-center mx-1 px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300 hover:bg-indigo-500/30 border border-indigo-500/30 text-xs align-baseline"
              title={`Jump to source ${id}`}
            >
              <BookOpen size={10} className="mr-1" />
              ref
            </button>
          );
        }
        // Basic newline handling
        return <span key={index}>{part}</span>;
      })}
    </div>
  );
};
