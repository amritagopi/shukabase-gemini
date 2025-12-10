import React, { useState, useEffect } from 'react';
import { X, ChevronDown, Sparkles, Send, ArrowRight } from 'lucide-react';
import { PROMPT_TEMPLATES, PromptTemplate } from './promptTemplates';

interface PromptDrawerProps {
    isOpen: boolean;
    onClose: () => void;
    onSelectDevice: (prompt: string, templateTitle: string) => void;
    initialTemplateId?: string | null;
    initialData?: Record<string, any> | null;
}

const PromptDrawer: React.FC<PromptDrawerProps> = ({ isOpen, onClose, onSelectDevice, initialTemplateId, initialData }) => {
    const [selectedCategory, setSelectedCategory] = useState<string>('academy');
    const [selectedTemplate, setSelectedTemplate] = useState<PromptTemplate | null>(null);
    const [inputValues, setInputValues] = useState<Record<string, string>>({});
    const [isAnimating, setIsAnimating] = useState(false);

    useEffect(() => {
        if (isOpen) {
            setIsAnimating(true);

            // Handle Direct Open (Generative UI)
            if (initialTemplateId) {
                // Search for the template across all categories
                for (const category in PROMPT_TEMPLATES) {
                    const found = PROMPT_TEMPLATES[category].find(t => t.id === initialTemplateId);
                    if (found) {
                        setSelectedTemplate(found);
                        setSelectedCategory(category);
                        if (initialData) {
                            setInputValues(initialData);
                        }
                        break;
                    }
                }
            }
        } else {
            const timer = setTimeout(() => {
                setIsAnimating(false);
                // Reset state on close
                if (!initialTemplateId) {
                    setSelectedTemplate(null);
                    setInputValues({});
                }
            }, 300);
            return () => clearTimeout(timer);
        }
    }, [isOpen, initialTemplateId, initialData]);

    if (!isOpen && !isAnimating) return null;

    const categories = [
        { id: 'academy', label: 'Academy', icon: '🏛️' },
        { id: 'preaching', label: 'Preaching', icon: '🎤' },
        { id: 'creative', label: 'Creative', icon: '🎨' },
        { id: 'sadhana', label: 'Sadhana', icon: '🧘' },
    ];

    const handleTemplateClick = (template: PromptTemplate) => {
        setSelectedTemplate(template);
        setInputValues({});
    };

    const handleInputChange = (key: string, value: string) => {
        setInputValues(prev => ({ ...prev, [key]: value }));
    };

    const handleGenerate = () => {
        if (!selectedTemplate) return;

        let finalPrompt = selectedTemplate.systemPrompt;
        let missingInput = false;

        selectedTemplate.inputs.forEach(input => {
            const val = inputValues[input.key] || '';
            if (!val && input.type !== 'select') missingInput = true; // Select might have default
            // Simple handlebars-style replacement
            finalPrompt = finalPrompt.replace(new RegExp(`{{${input.key}}}`, 'g'), val);
        });

        if (missingInput) {
            // Basic validation visual cue could be added here
            // For now just proceed, or return
        }

        onSelectDevice(finalPrompt, selectedTemplate.title);
        onClose();
        setSelectedTemplate(null);
    };

    return (
        <>
            {/* Backdrop */}
            <div
                className={`fixed inset-0 bg-black/60 backdrop-blur-sm z-40 transition-opacity duration-300 ${isOpen ? 'opacity-100' : 'opacity-0'}`}
                onClick={onClose}
            />

            {/* Drawer */}
            <div
                className={`fixed top-0 left-0 right-0 z-50 bg-[#0B0F19] border-b border-cyan-500/20 shadow-[0_10px_50px_rgba(0,0,0,0.8)] transform transition-transform duration-300 ease-out flex flex-col max-h-[85vh] ${isOpen ? 'translate-y-0' : '-translate-y-full'}`}
            >
                {/* Pull Handle (Visual only) */}
                <div className="absolute bottom-2 left-1/2 -translate-x-1/2 w-20 h-1 bg-slate-700/50 rounded-full mb-2"></div>

                <div className="flex-1 flex flex-col overflow-hidden relative">
                    {/* Cyber Grid Background */}
                    <div className="absolute inset-0 pointer-events-none opacity-10"
                        style={{ backgroundImage: 'linear-gradient(rgba(34, 211, 238, 0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(34, 211, 238, 0.1) 1px, transparent 1px)', backgroundSize: '30px 30px' }}>
                    </div>

                    {/* Header */}
                    <div className="p-6 border-b border-slate-800/60 flex justify-between items-center relative z-10 bg-[#0B0F19]/90 backdrop-blur">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center">
                                <Sparkles className="w-5 h-5 text-cyan-400 animate-pulse-slow" />
                            </div>
                            <div>
                                <h2 className="text-xl font-bold text-slate-100 tracking-tight glow-text-cyan">Shuka Studio</h2>
                                <p className="text-xs text-slate-500 font-mono tracking-wide">AI POWERED SPIRITUAL TOOLS</p>
                            </div>
                        </div>
                        <button onClick={onClose} className="p-2 hover:bg-slate-800 rounded-full transition-colors text-slate-400 hover:text-white">
                            <X size={24} />
                        </button>
                    </div>

                    <div className="flex flex-1 overflow-hidden relative z-10">
                        {/* Sidebar (Categories) */}
                        <div className="w-20 md:w-64 border-r border-slate-800/60 flex flex-col bg-slate-900/30 backdrop-blur-sm">
                            {categories.map(cat => (
                                <button
                                    key={cat.id}
                                    onClick={() => { setSelectedCategory(cat.id); setSelectedTemplate(null); }}
                                    className={`p-4 md:px-6 md:py-5 flex flex-col md:flex-row items-center md:gap-4 transition-all border-l-2
                                        ${selectedCategory === cat.id
                                            ? 'bg-cyan-500/10 border-cyan-400 text-cyan-100 shadow-[inset_10px_0_20px_-10px_rgba(34,211,238,0.2)]'
                                            : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'}
                                    `}
                                >
                                    <span className="text-2xl mb-1 md:mb-0 filter drop-shadow-[0_0_5px_rgba(255,255,255,0.3)]">{cat.icon}</span>
                                    <span className="text-[10px] md:text-sm font-medium tracking-wide uppercase md:normal-case">{cat.label}</span>
                                    {selectedCategory === cat.id && <ArrowRight className="ml-auto hidden md:block w-4 h-4 opacity-50" />}
                                </button>
                            ))}
                        </div>

                        {/* Main Content Area */}
                        <div className="flex-1 overflow-y-auto p-6 md:p-8 bg-[#0B0F19]/50 w-full relative">

                            {selectedTemplate ? (
                                // --- DETAIL VIEW (Inputs) ---
                                <div className="max-w-2xl mx-auto animate-fade-in">
                                    <button
                                        onClick={() => setSelectedTemplate(null)}
                                        className="mb-6 flex items-center gap-2 text-sm text-cyan-500 hover:text-cyan-300 transition-colors font-mono"
                                    >
                                        <ArrowRight className="rotate-180 w-4 h-4" /> BACK TO TOOLS
                                    </button>

                                    <div className="glass-panel p-8 rounded-2xl border border-cyan-500/20 shadow-[0_0_40px_rgba(0,0,0,0.3)] bg-[#0f1623]">
                                        <div className="flex items-center gap-4 mb-6">
                                            <div className={`p-3 rounded-xl bg-slate-800/50 border border-slate-700 ${selectedTemplate.color}`}>
                                                <selectedTemplate.icon size={32} />
                                            </div>
                                            <div>
                                                <h3 className="text-2xl font-bold text-slate-100">{selectedTemplate.title}</h3>
                                                <p className="text-slate-400">{selectedTemplate.description}</p>
                                            </div>
                                        </div>

                                        <div className="space-y-6">
                                            {selectedTemplate.inputs.map(input => (
                                                <div key={input.key} className="space-y-2">
                                                    <label className="block text-sm font-medium text-slate-300 ml-1">
                                                        {input.label}
                                                    </label>
                                                    {input.type === 'select' ? (
                                                        <div className="relative">
                                                            <select
                                                                value={inputValues[input.key] || ''}
                                                                onChange={(e) => handleInputChange(input.key, e.target.value)}
                                                                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-3 text-slate-200 focus:ring-1 focus:ring-cyan-500 focus:border-cyan-500/50 appearance-none outline-none transition-all"
                                                            >
                                                                <option value="" disabled selected>{input.placeholder}</option>
                                                                {input.options?.map(opt => (
                                                                    <option key={opt} value={opt}>{opt}</option>
                                                                ))}
                                                            </select>
                                                            <ChevronDown className="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 pointer-events-none" />
                                                        </div>
                                                    ) : input.type === 'textarea' ? (
                                                        <textarea
                                                            value={inputValues[input.key] || ''}
                                                            onChange={(e) => handleInputChange(input.key, e.target.value)}
                                                            placeholder={input.placeholder}
                                                            rows={3}
                                                            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-3 text-slate-200 focus:ring-1 focus:ring-cyan-500 focus:border-cyan-500/50 outline-none transition-all placeholder:text-slate-600 resize-none"
                                                        />
                                                    ) : (
                                                        <input
                                                            type="text"
                                                            value={inputValues[input.key] || ''}
                                                            onChange={(e) => handleInputChange(input.key, e.target.value)}
                                                            placeholder={input.placeholder}
                                                            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-3 text-slate-200 focus:ring-1 focus:ring-cyan-500 focus:border-cyan-500/50 outline-none transition-all placeholder:text-slate-600"
                                                        />
                                                    )}
                                                </div>
                                            ))}

                                            <button
                                                onClick={handleGenerate}
                                                className="w-full py-4 mt-4 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-bold rounded-xl shadow-[0_0_20px_rgba(6,182,212,0.3)] transition-all transform active:scale-[0.98] flex items-center justify-center gap-2 group"
                                            >
                                                <Sparkles className="w-5 h-5 group-hover:rotate-12 transition-transform" />
                                                Start Generating
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            ) : (
                                // --- GRID VIEW (Templates) ---
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 md:gap-6 animate-stagger-in">
                                    {PROMPT_TEMPLATES[selectedCategory]?.map((template) => (
                                        <button
                                            key={template.id}
                                            onClick={() => handleTemplateClick(template)}
                                            className="group relative flex flex-col p-5 rounded-2xl bg-slate-900/40 border border-slate-800 hover:border-cyan-500/40 backdrop-blur-sm transition-all duration-300 hover:shadow-[0_0_25px_rgba(6,182,212,0.15)] hover:-translate-y-1 text-left"
                                        >
                                            <div className={`p-3 rounded-xl bg-slate-800/50 w-fit mb-4 group-hover:scale-110 transition-transform duration-300 ${template.color}`}>
                                                <template.icon size={24} />
                                            </div>
                                            <h3 className="text-lg font-bold text-slate-200 mb-1 group-hover:text-cyan-400 transition-colors">{template.title}</h3>
                                            <p className="text-sm text-slate-400 leading-relaxed">{template.description}</p>

                                            {/* Glow Effect */}
                                            <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-cyan-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"></div>
                                        </button>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </>
    );
};

export default PromptDrawer;
