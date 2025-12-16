
import { useState } from 'react';
import { getBookTitle } from '../utils/bookUtils'; // Assuming this exists or I need to move it

export interface BookReaderState {
    fullTextModalOpen: boolean;
    fullTextContent: string;
    fullTextTitle: string;
    currentHtmlPath: string;
}

export const useBookReader = (language: 'en' | 'ru') => {
    const [state, setState] = useState<BookReaderState>({
        fullTextModalOpen: false,
        fullTextContent: '',
        fullTextTitle: '',
        currentHtmlPath: ''
    });

    const setFullTextModalOpen = (open: boolean) => setState(prev => ({ ...prev, fullTextModalOpen: open }));

    const loadFullText = async (path: string, title?: string) => {
        try {
            let response = await fetch(path);
            if (!response.ok) {
                let fallbackPath = '';
                if (path.includes('/books/en/')) {
                    fallbackPath = path.replace('/books/en/', '/books/ru/');
                } else if (path.includes('/books/ru/')) {
                    fallbackPath = path.replace('/books/ru/', '/books/en/');
                }

                if (fallbackPath) {
                    const fallbackResponse = await fetch(fallbackPath);
                    if (fallbackResponse.ok) {
                        response = fallbackResponse;
                        path = fallbackPath;
                    }
                }
            }

            if (!response.ok) throw new Error(`Failed to load: ${response.statusText}`);

            const htmlContent = await response.text();

            if (htmlContent.includes('<div id="root">') || htmlContent.includes('<title>SHUKABASE</title>')) {
                throw new Error("File not found");
            }

            let contentToDisplay = htmlContent;
            const bodyMatch = htmlContent.match(/<body[^>]*>([\s\S]*)<\/body>/i);
            if (bodyMatch) contentToDisplay = bodyMatch[1];
            else {
                const mainMatch = htmlContent.match(/<main[^>]*>([\s\S]*)<\/main>/i);
                if (mainMatch) contentToDisplay = mainMatch[1];
            }
            contentToDisplay = contentToDisplay.replace(/<script\b[^>]*>([\s\S]*?)<\/script>/gim, "");

            let displayTitle = title || '';
            if (!displayTitle) {
                const titleMatch = htmlContent.match(/<h1[^>]*>(.*?)<\/h1>/i);
                if (titleMatch) displayTitle = titleMatch[1].replace(/<[^>]+>/g, '');
            }

            setState({
                fullTextContent: contentToDisplay,
                fullTextTitle: displayTitle || 'Text View',
                currentHtmlPath: path,
                fullTextModalOpen: true
            });
        } catch (error) {
            setState(prev => ({
                ...prev,
                fullTextContent: "Could not load full chapter text. Please try checking the source manually.",
                fullTextTitle: "Error Loading Text",
                fullTextModalOpen: true
            }));
            console.error("Error loading full text:", error);
        }
    };

    const handleReadFull = async (chunk: any) => {
        let chapterPath = '';
        const lang = language;

        try {
            // Logic to construct path
            // Check if chunk.chapter has full path
            const bookFolder = (chunk.bookTitle === 'Srimad-Bhagavatam' || chunk.bookTitle === 'Шримад-Бхагаватам') ? 'sb' :
                (chunk.bookTitle === 'Bhagavad-gita As It Is' || chunk.bookTitle === 'Бхагавад-гита как она есть') ? 'bg' :
                    (chunk.sourceUrl && chunk.sourceUrl.includes('/books/')) ? chunk.sourceUrl.split('/books/')[1].split('/')[1] :
                        'other';

            // Hardcoded map for simplicity if getBookTitle logic is complex to import, but ideally import it
            // For now, assume standard path construction logic duplicated here or imported.
            // I'll assume chunk.chapter can be a path.

            if (chunk.sourceUrl && chunk.sourceUrl.endsWith('.html')) {
                chapterPath = chunk.sourceUrl;
            } else {
                let normalizedChapter = String(chunk.chapter).replace(/\\/g, '/');

                // Robust check for existing full path
                const cleanChapterPath = normalizedChapter.replace(/^\/+/, '');
                let validPathFound = false;

                if (bookFolder) {
                    const regex = new RegExp(`^${bookFolder}(/|$)`, 'i');
                    if (regex.test(cleanChapterPath)) {
                        chapterPath = `/books/${lang}/${cleanChapterPath}`;
                        validPathFound = true;
                    }
                }

                if (!validPathFound && bookFolder) {
                    chapterPath = `/books/${lang}/${bookFolder}/${cleanChapterPath}/index.html`;
                    // Simple heuristic, might need the full logic from App.tsx if it was complex
                }

                // Fallback for numbered
                if (!chapterPath.includes('.html')) {
                    // Reconstruct from 1.2.3 logic
                    const parts = String(chunk.chapter).split('.');
                    if (parts.length > 0) {
                        chapterPath = `/books/${lang}/${bookFolder}/${parts.join('/')}/${chunk.verse ? chunk.verse + '/' : ''}index.html`;
                    }
                }
            }

            // Better title formatting
            const niceBookTitle = getBookTitle(chunk.bookTitle, language);
            let niceChapter = chunk.chapter;
            let niceVerse = chunk.verse;

            if (typeof chunk.chapter === 'string' && (chunk.chapter.includes('/') || chunk.chapter.includes('\\'))) {
                const parts = chunk.chapter.replace(/\\/g, '/').split('/');
                if (parts.length >= 2) {
                    const numbers = parts.filter(p => /^\d+$/.test(p));
                    if (numbers.length >= 2) {
                        niceChapter = numbers[numbers.length - 2];
                        niceVerse = numbers[numbers.length - 1];
                    }
                }
            }

            const titleSuffix = niceVerse ? `${niceChapter ? niceChapter + '.' : ''}${niceVerse}` : (niceChapter ? `Chapter ${niceChapter}` : '');
            await loadFullText(chapterPath, `${niceBookTitle} ${titleSuffix}`);

        } catch (e) {
            console.error("Path construction error", e);
            // Fallback
            setState(prev => ({
                ...prev,
                fullTextContent: chunk.content,
                fullTextTitle: chunk.bookTitle,
                fullTextModalOpen: true
            }));
        }
    };

    const handleModalClick = (e: React.MouseEvent<HTMLDivElement>) => {
        const target = e.target as HTMLElement;
        const anchor = target.closest('a');
        if (anchor && anchor.href) {
            const href = anchor.getAttribute('href');
            if (href && !href.startsWith('http') && !href.startsWith('#')) {
                e.preventDefault();
                e.stopPropagation();

                const currentDir = state.currentHtmlPath.substring(0, state.currentHtmlPath.lastIndexOf('/'));
                const parts = currentDir.split('/');
                const relativeParts = href.split('/');

                const newParts = [...parts];

                for (const part of relativeParts) {
                    if (part === '.') continue;
                    if (part === '..') newParts.pop();
                    else newParts.push(part);
                }

                const newPath = newParts.join('/');
                loadFullText(newPath);
            }
        }
    };

    return {
        ...state,
        setFullTextModalOpen,
        handleReadFull,
        handleModalClick,
        loadFullText
    };
};
