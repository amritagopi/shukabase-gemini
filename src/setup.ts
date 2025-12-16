/// <reference types="vitest/globals" />
import { cleanup } from '@testing-library/react';
import React from 'react';

// Polyfills
if (!window.TextEncoder) {
    const { TextEncoder, TextDecoder } = require('util');
    window.TextEncoder = TextEncoder;
    window.TextDecoder = TextDecoder;
}

afterEach(() => {
    cleanup();
});
