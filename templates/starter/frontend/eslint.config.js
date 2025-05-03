import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import eslintPluginPrettier from 'eslint-plugin-prettier'
import prettierConfig from 'eslint-config-prettier'

export default [
  {
    ignores: ['dist'],
  },
  {
    files: ['**/*.{js,jsx}'],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
      parserOptions: {
        ecmaVersion: 'latest',
        ecmaFeatures: {
          jsx: true,
        },
        sourceType: 'module',
      },
    },
    plugins: {
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
      prettier: eslintPluginPrettier,
    },
    rules: {
      ...js.configs.recommended.rules,
      ...reactHooks.configs.recommended.rules,
      'no-unused-vars': ['warn', { varsIgnorePattern: '^[A-Z_]' }],
      'react-refresh/only-export-components': ['warn', { allowConstantExport: true }],
      'prettier/prettier': 'error',
      'eslint-disable-next-line': 'off',
      'react-hooks/exhaustive-deps': 'off',
      'react/display-name': 'off',
      'jsx-quotes': ['error', 'prefer-double'],
      quotes: ['error', 'single'],
      semi: ['error', 'never'],
      indent: ['error', 2],
      'no-multi-spaces': ['error'],
      'padded-blocks': ['error', 'always', { allowSingleLineBlocks: true }],
      'no-multiple-empty-lines': ['error', { max: 3, maxBOF: 1, maxEOF: 1 }],
      'space-before-blocks': 'error',
    },
  },
  prettierConfig,
]
