import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { BookOpen } from 'lucide-react';
import { CitationClickHandler } from '../types';

interface ParsedContentProps {
  content: string;
  onCitationClick: CitationClickHandler;
}

export const ParsedContent: React.FC<ParsedContentProps> = ({ content, onCitationClick }) => {
  // Split content by citation markers [[source_id]]
  const parts = content.split(/(\[\[.*?\]\])/g);

  return (
    <div className="markdown-body prose prose-invert prose-slate max-w-none text-slate-300 leading-relaxed text-sm md:text-base">
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
        // Render markdown for text parts
        return (
          <ReactMarkdown
            key={index}
            remarkPlugins={[remarkGfm]}
            components={{
              // Customize rendering for specific elements if needed
              p: ({ children }) => <p className="mb-2">{children}</p>,
              ul: ({ children }) => <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>,
              ol: ({ children }) => <ol className="list-decimal list-inside mb-2 space-y-1">{children}</ol>,
              li: ({ children }) => <li className="ml-2">{children}</li>,
              strong: ({ children }) => <strong className="font-bold text-slate-100">{children}</strong>,
              em: ({ children }) => <em className="italic text-slate-300">{children}</em>,
              code: ({ children }) => <code className="bg-slate-800 px-1.5 py-0.5 rounded text-xs font-mono text-amber-400">{children}</code>,
              pre: ({ children }) => <pre className="bg-slate-950 p-3 rounded-lg overflow-x-auto mb-2 border border-slate-700">{children}</pre>,
            }}
          >
            {part}
          </ReactMarkdown>
        );
      })}
    </div>
  );
};
