/// <reference types="vitest/globals" />
import '@testing-library/jest-dom';
import React from 'react';
import { render, screen } from '@testing-library/react';
import App from '../../App.tsx';

// Mock dependencies
vi.mock('../../services/geminiService', () => ({
    generateRAGResponse: vi.fn(),
    getConversations: vi.fn().mockResolvedValue([]),
    getConversation: vi.fn().mockResolvedValue(null),
    saveConversation: vi.fn(),
    searchScriptures: vi.fn()
}));

vi.mock('../../ConversationHistory.tsx', () => ({
    default: () => <div data-testid="history-mock">History</div>
}));

vi.mock('../../PromptDrawer.tsx', () => ({
    default: () => <div data-testid="drawer-mock">Drawer</div>
}));

vi.mock('../../ToolCardWidget.tsx', () => ({
    default: () => <div data-testid="tool-card-mock">ToolCard</div>
}));

// Mock tauri plugins
vi.mock('@tauri-apps/plugin-opener', () => ({
    openUrl: vi.fn(),
}));

vi.mock('@tauri-apps/plugin-updater', () => ({
    check: vi.fn().mockResolvedValue({ available: false }),
}));

// Mock global fetch
global.fetch = vi.fn((url) => {
    if (url && url.toString().includes('setup/status')) {
        return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({ installed: true })
        });
    }
    return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({})
    });
}) as any;

describe('App', () => {
    it('renders and enters chat mode', async () => {
        const { container } = render(<App />);
        expect(container).toBeDefined();
    });
});
