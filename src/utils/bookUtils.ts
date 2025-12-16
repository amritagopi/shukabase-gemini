
import { TRANSLATIONS } from '../../translations';

export const getBookTitle = (code: string, language: string = 'en') => {
    // @ts-ignore
    const books = TRANSLATIONS[language]?.books || TRANSLATIONS['en'].books;
    const normalizedCode = code.toLowerCase();
    return books[normalizedCode] || code.toUpperCase();
};

export const BOOK_MAP: Record<string, string> = {
    'Srimad-Bhagavatam': 'sb', 'Bhagavad-gita As It Is': 'bg', 'Sri Caitanya-caritamrta': 'cc',
    'Nectar of Devotion': 'nod', 'Nectar of Instruction': 'noi', 'Teachings of Lord Caitanya': 'tqk',
    'Sri Isopanisad': 'iso', 'Light of the Bhagavata': 'lob', 'Perfect Questions, Perfect Answers': 'pop',
    'Path of Perfection': 'pop', 'Science of Self Realization': 'sc', 'Life Comes from Life': 'lcfl',
    'Krishna Book': 'kb', 'Raja-Vidya': 'rv', 'Beyond Birth and Death': 'bbd',
    'Civilization and Transcendence': 'ct', 'Krsna Consciousness The Matchless Gift': 'mg',
    'Easy Journey to Other Planets': 'ej', 'On the Way to Krsna': 'owk', 'Perfection of Yoga': 'poy',
    'Spiritual Yoga': 'sy', 'Transcendental Teachings of Prahlad Maharaja': 'ttpm',
    'sb': 'sb', 'bg': 'bg', 'cc': 'cc', 'nod': 'nod', 'noi': 'noi', 'tqk': 'tqk', 'iso': 'iso',
    'lob': 'lob', 'pop': 'pop', 'sc': 'sc', 'rv': 'rv', 'bbd': 'bbd', 'owk': 'owk', 'poy': 'poy', 'spl': 'spl'
};

export const getBookFolder = (bookTitle: string): string | null => {
    let bookFolder = BOOK_MAP[bookTitle] || null;
    if (!bookFolder) {
        for (const [title, folder] of Object.entries(BOOK_MAP)) {
            if (bookTitle.includes(title) || title.includes(bookTitle)) {
                bookFolder = folder;
                break;
            }
        }
    }
    return bookFolder;
};

export const generateChapterPath = (
    lang: string,
    bookTitle: string,
    chapter: string | number | undefined,
    verse?: string | number
): string | null => {
    const bookFolder = getBookFolder(bookTitle);

    if (bookFolder) {
        let chapterSegments: string[] = [];
        if (typeof chapter === 'string') {
            // Split by dot, slash, or backslash
            chapterSegments = chapter.split(/[./\\]/).filter(s => s.trim());
        } else if (chapter) {
            chapterSegments = [String(chapter)];
        }

        // If chapterSegments is empty (e.g. 0), default to '1'
        if (chapterSegments.length === 0) chapterSegments = ['1'];

        const chapterUrlPart = chapterSegments.join('/');

        if (verse) {
            return `/books/${lang}/${bookFolder}/${chapterUrlPart}/${verse}/index.html`;
        } else {
            return `/books/${lang}/${bookFolder}/${chapterUrlPart}/index.html`;
        }
    } else {
        // Fallback or explicit path checking
        if (chapter && typeof chapter === 'string' && (chapter.includes('/') || chapter.includes('\\'))) {
            const normalizedPath = chapter.replace(/\\/g, '/');
            return `/books/${lang}/${normalizedPath}`;
        }
    }
    return null;
};
