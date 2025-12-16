/// <reference types="vitest/globals" />
import '@testing-library/jest-dom';
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import ToolCardWidget from '../../ToolCardWidget.tsx';

// Mock dependencies
vi.mock('lucide-react', () => ({
    ArrowRight: () => <span data-testid="arrow">Arrow</span>,
    Sparkles: () => <span data-testid="sparkles">Sparkles</span>,
    default: () => <span>Icon</span>,
}));

// Use a mock that matches the structure expected by ToolCardWidget
vi.mock('../../promptTemplates', () => {
    return {
        PROMPT_TEMPLATES: {
            'test_cat': [{
                id: 'test_tool',
                title: { en: 'Test Tool', ru: 'Тест Инстумент' },
                description: { en: 'Test Desc', ru: 'Тест Описание' },
                icon: () => <span>Icon</span>,
                color: 'blue',
                inputs: []
            }]
        }
    };
});

describe('ToolCardWidget', () => {
    const defaultProps = {
        toolId: 'test_tool',
        initialData: { key: 'value' },
        onOpenTool: vi.fn()
    };

    it('renders tool info', () => {
        render(<ToolCardWidget {...defaultProps} />);
        expect(screen.getByText('Test Tool')).toBeInTheDocument();
    });
});
