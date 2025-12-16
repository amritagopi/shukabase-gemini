/// <reference types="vitest/globals" />
import { generateChapterPath } from '../utils/bookUtils';

describe('bookUtils', () => {
    describe('generateChapterPath', () => {
        it('correctly generates path for Srimad-Bhagavatam 1.2.3', () => {
            const path = generateChapterPath('en', 'Srimad-Bhagavatam', '1.2', '3');
            expect(path).toBe('/books/en/sb/1/2/3/index.html');
        });

        it('correctly generates path for Bhagavad-gita 2.12', () => {
            const path = generateChapterPath('en', 'Bhagavad-gita As It Is', '2', '12');
            expect(path).toBe('/books/en/bg/2/12/index.html');
        });

        it('handles complex chapters like 1.2.3 (should be split)', () => {
            const path = generateChapterPath('en', 'Srimad-Bhagavatam', '1.2.3', '4');
            expect(path).toBe('/books/en/sb/1/2/3/4/index.html');
        });

        it('handles missing verse (chapter index)', () => {
            const path = generateChapterPath('en', 'Nectar of Devotion', '1');
            expect(path).toBe('/books/en/nod/1/index.html');
        });

        it('handles backslashes in chapter string', () => {
            // If chunks come as paths
            const path = generateChapterPath('en', 'Srimad-Bhagavatam', '1\\2', '3');
            expect(path).toBe('/books/en/sb/1/2/3/index.html');
        });

        it('falls back to direct path if no book folder found but chapter looks like path', () => {
            const path = generateChapterPath('en', 'Unknown Book', 'some/path/file.html');
            expect(path).toBe('/books/en/some/path/file.html');
        });

        it('returns null if no book folder and invalid chapter structure', () => {
            const path = generateChapterPath('en', 'Unknown Book', '1');
            expect(path).toBeNull();
        });
    });
});
