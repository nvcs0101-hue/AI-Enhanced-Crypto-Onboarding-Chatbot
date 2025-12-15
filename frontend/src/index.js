import React from 'react';
import ReactDOM from 'react-dom/client';
import ChatWidget from './ChatWidget';

const App = () => {
  return (
    <div>
      <ChatWidget apiEndpoint={process.env.REACT_APP_API_ENDPOINT || 'http://localhost:5000/api/chat'} />
    </div>
  );
};

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
