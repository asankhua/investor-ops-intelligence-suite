import { createGlobalStyle } from 'styled-components';

const GlobalStyles = createGlobalStyle`
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
      'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
      sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    background: #E8F4FC;
    min-height: 100vh;
  }

  code {
    font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
      monospace;
  }

  /* Scrollbar styling */
  ::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }

  ::-webkit-scrollbar-track {
    background: #E8F4FC;
    border-radius: 4px;
  }

  ::-webkit-scrollbar-thumb {
    background: #5DADE2;
    border-radius: 4px;
  }

  ::-webkit-scrollbar-thumb:hover {
    background: #1E3A5F;
  }

  /* Utility classes */
  .card {
    background: #FFFFFF;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(30, 58, 95, 0.1);
    padding: 20px;
  }

  .btn-primary {
    background: #1E3A5F;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.2s ease;

    &:hover {
      background: #2a4a73;
      transform: translateY(-1px);
    }
  }

  .btn-secondary {
    background: #5DADE2;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.2s ease;

    &:hover {
      background: #4a9ad1;
      transform: translateY(-1px);
    }
  }

  .text-navy {
    color: #1E3A5F;
  }

  .text-sky {
    color: #5DADE2;
  }

  .bg-light-blue {
    background: #E8F4FC;
  }

  .bg-navy {
    background: #1E3A5F;
  }
`;

export default GlobalStyles;
