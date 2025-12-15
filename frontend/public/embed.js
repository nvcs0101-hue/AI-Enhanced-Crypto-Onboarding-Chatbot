/**
 * Embeddable chat widget script
 * 
 * Usage:
 * <script src="path/to/embed.js"></script>
 * <script>
 *   CryptoChatWidget.init({
 *     apiEndpoint: 'https://your-api.com/api/chat',
 *     position: 'bottom-right', // or 'bottom-left'
 *     primaryColor: '#667eea'
 *   });
 * </script>
 */

(function() {
  'use strict';

  const CryptoChatWidget = {
    config: {
      apiEndpoint: 'http://localhost:5000/api/chat',
      position: 'bottom-right',
      primaryColor: '#667eea'
    },

    init: function(options) {
      // Merge options with default config
      this.config = { ...this.config, ...options };

      // Wait for DOM to be ready
      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => this.render());
      } else {
        this.render();
      }
    },

    render: function() {
      // Create container
      const container = document.createElement('div');
      container.id = 'crypto-chat-widget-container';
      document.body.appendChild(container);

      // Create iframe
      const iframe = document.createElement('iframe');
      iframe.id = 'crypto-chat-widget-iframe';
      iframe.style.cssText = `
        position: fixed;
        ${this.config.position === 'bottom-left' ? 'left: 20px;' : 'right: 20px;'}
        bottom: 20px;
        width: 380px;
        height: 600px;
        border: none;
        border-radius: 16px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
        z-index: 999999;
        transition: all 0.3s ease-in-out;
      `;

      // Set iframe source (you would host the built React app)
      iframe.src = this.config.widgetUrl || 'about:blank';

      container.appendChild(iframe);

      // Setup message passing
      this.setupMessaging(iframe);
    },

    setupMessaging: function(iframe) {
      window.addEventListener('message', (event) => {
        // Handle messages from iframe
        if (event.data.type === 'crypto-chat-widget') {
          if (event.data.action === 'minimize') {
            iframe.style.display = 'none';
          } else if (event.data.action === 'maximize') {
            iframe.style.display = 'block';
          }
        }
      });

      // Send config to iframe when loaded
      iframe.addEventListener('load', () => {
        iframe.contentWindow.postMessage({
          type: 'crypto-chat-widget-config',
          config: this.config
        }, '*');
      });
    }
  };

  // Expose to global scope
  window.CryptoChatWidget = CryptoChatWidget;
})();
