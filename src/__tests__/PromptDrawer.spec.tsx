/// <reference types="vitest/globals" />
import '@testing-library/jest-dom';
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import PromptDrawer from '../../PromptDrawer.tsx';

// Mock dependencies
vi.mock('lucide-react', () => ({
    X: () => <span data-testid="icon-close">X</span>,
    ChevronDown: () => <span>v</span>,
    Sparkles: () => <span>*</span>,
    ArrowRight: () => <span>-&gt;</span>,
    ChevronLeft: () => <span>&lt;-</span>,
    Send: () => <span>Send</span>,
    Search: () => <span>SearchIcon</span>,
    default: () => <span>Icon</span>
}));

const mockTemplate = {
    id: 'test_tool',
    title: { en: 'Test Tool', ru: 'Тест Инстумент' },
    description: { en: 'Test Desc', ru: 'Тест Описание' },
    icon: () => <span>Icon</span>,
    color: 'text-blue-400',
    systemPrompt: 'System prompt {{input1}}',
    inputs: [
        {
            key: 'input1',
            label: { en: 'Input Label', ru: 'Ввод' },
            placeholder: { en: 'Placeholder', ru: 'Плейсхолдер' },
            type: 'text'
        }
    ]
};

vi.mock('../../promptTemplates', () => {
    return {
        PROMPT_TEMPLATES: {
            'test_cat': [{
                id: 'test_tool',
                title: { en: 'Test Tool', ru: 'Тест Инстумент' },
                description: { en: 'Test Desc', ru: 'Тест Описание' },
                icon: () => <span>Icon</span>,
                color: 'text-blue-400',
                systemPrompt: 'System prompt {{input1}}',
                inputs: [
                    {
                        key: 'input1',
                        label: { en: 'Input Label', ru: 'Ввод' },
                        placeholder: { en: 'Placeholder', ru: 'Плейсхолдер' },
                        type: 'text'
                    }
                ]
            }]
        }
    };
});

describe('PromptDrawer', () => {
    const defaultProps = {
        isOpen: true,
        onClose: vi.fn(),
        onSelectDevice: vi.fn(),
        t: (key: string) => key,
        language: 'en' as const,
        initialTemplateId: null,
        initialData: null
    };

    it('renders nothing when closed', () => {
        const { container } = render(<PromptDrawer {...defaultProps} isOpen={false} />);
        expect(container).toBeEmptyDOMElement();
    });

    it('renders grid view when open', () => {
        render(<PromptDrawer {...defaultProps} />);
        expect(screen.getByText('commandDeck')).toBeInTheDocument();
        expect(screen.getByText('Test Tool')).toBeInTheDocument();
    });
});
