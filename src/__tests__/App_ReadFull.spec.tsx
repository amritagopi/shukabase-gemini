/// <reference types="vitest/globals" />
import { renderHook, act, waitFor } from '@testing-library/react';
import { useBookReader } from '../hooks/useBookReader';

// Mock getBookTitle if needed, or rely on it handling it
vi.mock('../utils/bookUtils', () => ({
    getBookTitle: (t: string) => t
}));

describe('useBookReader', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        global.fetch = vi.fn((url) => {
            if (url && url.toString().endsWith('.html')) {
                return Promise.resolve({
                    ok: true,
                    text: () => Promise.resolve('<html><body><div id="content">Mock Chapter Content <a href="../4/index.html">Next</a></div></body></html>')
                });
            }
            return Promise.resolve({ ok: false, statusText: 'Not Found' });
        }) as any;
    });

    it('loads full text correctly', async () => {
        const { result } = renderHook(() => useBookReader('en'));

        await act(async () => {
            await result.current.loadFullText('/books/en/sb/1/2/3/index.html', 'Test Title');
        });

        expect(result.current.fullTextModalOpen).toBe(true);
        expect(result.current.fullTextContent).toContain('Mock Chapter Content');
        expect(result.current.fullTextTitle).toBe('Test Title');
    });

    it('handles navigation via handleModalClick', async () => {
        const { result } = renderHook(() => useBookReader('en'));

        // Load initial
        await act(async () => {
            await result.current.loadFullText('/books/en/sb/1/2/3/index.html');
        });

        // Simulate click
        const mockEvent = {
            target: {
                closest: () => ({
                    href: '../4/index.html',
                    getAttribute: () => '../4/index.html'
                })
            },
            preventDefault: vi.fn(),
            stopPropagation: vi.fn()
        } as any;

        await act(async () => {
            result.current.handleModalClick(mockEvent);
        });

        // Expect fetch to be called with resolved path
        expect(global.fetch).toHaveBeenCalledWith(
            expect.stringMatching(/\/books\/en\/sb\/1\/2\/4\/index\.html$/)
        );
    });
});

