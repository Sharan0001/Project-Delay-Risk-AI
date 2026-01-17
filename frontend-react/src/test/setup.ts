/**
 * Test Setup
 * 
 * Global setup for Vitest tests with jsdom and testing-library
 */

import '@testing-library/jest-dom';

// Mock scrollIntoView which doesn't exist in jsdom
Element.prototype.scrollIntoView = () => { };
