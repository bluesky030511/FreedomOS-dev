import { ESLint } from 'eslint';
import prettierConfig from 'eslint-config-prettier';
import importPlugin from 'eslint-plugin-import';
import typescriptPlugin from '@typescript-eslint/eslint-plugin';
import typescriptParser from '@typescript-eslint/parser';

export default [
  {
    // ignore globally
    ignores: ['node_modules', 'dist', '.next/'],
  },
  {
    files: ['**/*.{js,jsx,ts,tsx}'],
    languageOptions: {
      parser: typescriptParser,
      parserOptions: {
        ecmaVersion: 2021,
        sourceType: 'module',
        project: './tsconfig.json',
      },
    },
    plugins: {
      import: importPlugin,
      '@typescript-eslint': typescriptPlugin,
    },
    rules: {
      'no-console': 'error',
      'import/order': [
        'error',
        {
          alphabetize: {
            order: 'asc',
            caseInsensitive: true,
          },
          groups: [['builtin', 'external'], 'internal'],
          'newlines-between': 'always',
        },
      ]
    },
    settings: {
      react: {
        version: 'detect',
      },
    },
  },
  prettierConfig,
];
