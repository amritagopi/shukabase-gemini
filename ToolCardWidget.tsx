import React from 'react';
import { PromptTemplate, PROMPT_TEMPLATES } from './promptTemplates';
import { Sparkles, ArrowRight } from 'lucide-react';

interface ToolCardWidgetProps {
    toolId: string;
    initialData: Record<string, any>;
    onOpenTool: (tool: PromptTemplate, prefilledData: Record<string, any>) => void;
}

const ToolCardWidget: React.FC<ToolCardWidgetProps> = ({ toolId, initialData, onOpenTool }) => {
    // Find the template by ID across all categories
    let template: PromptTemplate | undefined;
    for (const category in PROMPT_TEMPLATES) {
        const found = PROMPT_TEMPLATES[category].find(t => t.id === toolId);
        if (found) {
            template = found;
            break;
        }
    }

    if (!template) return null;

    return (
        <div className="mt-4 mb-2 max-w-sm w-full">
            <div
                className={`
                    relative overflow-hidden rounded-xl border border-slate-700/50 bg-slate-900/40 backdrop-blur-md 
                    transition-all duration-300 hover:border-cyan-500/40 hover:shadow-[0_0_20px_rgba(6,182,212,0.15)]
                    group cursor-pointer
                `}
                onClick={() => onOpenTool(template!, initialData)}
            >
                {/* Header Strip */}
                <div className={`h-1 w-full bg-gradient-to-r from-transparent via-cyan-500 to-transparent opacity-50`}></div>

                <div className="p-4 flex items-start gap-4">
                    <div className={`p-2.5 rounded-lg bg-slate-800/80 border border-slate-700 ${template.color} shrink-0 group-hover:scale-110 transition-transform`}>
                        <template.icon size={20} />
                    </div>

                    <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                            <Sparkles size={12} className="text-cyan-400 animate-pulse" />
                            <span className="text-xs font-bold uppercase tracking-widest text-cyan-500/80">Suggested Tool</span>
                        </div>
                        <h4 className="font-bold text-slate-100 truncate pr-2 group-hover:text-cyan-400 transition-colors">{template.title}</h4>
                        <p className="text-xs text-slate-400 mt-0.5 line-clamp-2">{template.description}</p>

                        {/* Preview of pre-filled data */}
                        {Object.keys(initialData).length > 0 && (
                            <div className="mt-3 flex flex-wrap gap-2">
                                {Object.entries(initialData).map(([key, value]) => (
                                    <span key={key} className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-300 border border-slate-700">
                                        {key}: <span className="text-cyan-300 ml-1 truncate max-w-[80px]">{String(value)}</span>
                                    </span>
                                ))}
                            </div>
                        )}
                    </div>

                    <div className="self-center">
                        <div className="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center text-slate-400 group-hover:bg-cyan-600 group-hover:text-white transition-colors">
                            <ArrowRight size={16} className="-ml-0.5" />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ToolCardWidget;
