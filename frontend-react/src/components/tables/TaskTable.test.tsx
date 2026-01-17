/**
 * TaskTable Component Tests
 * 
 * Tests for the main risk results table
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '../../test/test-utils';
import { TaskTable } from './TaskTable';
import type { TaskRiskResult } from '../../api';

// Mock data - using correct prop name "results"
const mockResults: TaskRiskResult[] = [
    {
        task_id: 'TASK-001',
        risk_level: 'High',
        risk_score: 75,
        delay_probability: 0.82,
        reasons: ['Frequent task blocking (3+ events)'],
        recommended_actions: ['Add resource'],
    },
    {
        task_id: 'TASK-002',
        risk_level: 'Medium',
        risk_score: 45,
        delay_probability: 0.45,
        reasons: ['Heavy dependency constraints'],
        recommended_actions: ['Review dependencies'],
    },
    {
        task_id: 'TASK-003',
        risk_level: 'Low',
        risk_score: 20,
        delay_probability: 0.12,
        reasons: [],
        recommended_actions: [],
    },
];

describe('TaskTable', () => {
    it('renders all task rows', () => {
        // Act - use "results" prop (not "tasks")
        render(<TaskTable results={mockResults} onTaskSelect={vi.fn()} />);

        // Assert - all task IDs are visible
        expect(screen.getByText('TASK-001')).toBeInTheDocument();
        expect(screen.getByText('TASK-002')).toBeInTheDocument();
        expect(screen.getByText('TASK-003')).toBeInTheDocument();
    });

    it('displays risk badges with correct levels', () => {
        // Act
        render(<TaskTable results={mockResults} onTaskSelect={vi.fn()} />);

        // Assert - risk badges are shown
        expect(screen.getByText('High')).toBeInTheDocument();
        expect(screen.getByText('Medium')).toBeInTheDocument();
        expect(screen.getByText('Low')).toBeInTheDocument();
    });

    it('calls onTaskSelect when a row is clicked', () => {
        // Arrange
        const mockOnSelect = vi.fn();

        // Act
        render(<TaskTable results={mockResults} onTaskSelect={mockOnSelect} />);

        // Click on first task row
        const firstRow = screen.getByText('TASK-001').closest('tr');
        if (firstRow) {
            fireEvent.click(firstRow);
        }

        // Assert
        expect(mockOnSelect).toHaveBeenCalledWith(mockResults[0]);
    });

    it('shows navigational hints in header', () => {
        // Act
        render(<TaskTable results={mockResults} onTaskSelect={vi.fn()} />);

        // Assert - individual keyboard hints exist (they're in separate elements)
        expect(screen.getByText('Navigate:')).toBeInTheDocument();
        expect(screen.getByText('Select:')).toBeInTheDocument();
    });
});
