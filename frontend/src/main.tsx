import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import { ToastProvider } from './contexts/ToastContext'
import App from './App'
import './index.css'

// Prevent browser confirm/alert dialogs from appearing
// This ensures only our custom ConfirmDialog is used
if (typeof window !== 'undefined') {
  const originalConfirm = window.confirm;
  const originalAlert = window.alert;
  
  // Override window.confirm to prevent browser dialogs
  window.confirm = function(message?: string): boolean {
    console.warn('window.confirm() was called but blocked. Message:', message);
    return false; // Always return false to prevent any default behavior
  };
  
  // Override window.alert to prevent browser dialogs
  window.alert = function(message?: string): void {
    console.warn('window.alert() was called but blocked. Message:', message);
    // Do nothing - prevent alert from showing
  };
  
  // Also prevent beforeunload confirm dialogs
  window.addEventListener('beforeunload', (e) => {
    e.preventDefault();
    e.returnValue = '';
  });
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <ToastProvider>
          <App />
        </ToastProvider>
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>,
)

