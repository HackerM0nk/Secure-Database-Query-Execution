#!/usr/bin/env python3

import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from simple_privatebin import SimplePrivateBin

class CredentialViewerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests for viewing credentials"""

        parsed_path = urlparse(self.path)

        if parsed_path.path.startswith('/view/'):
            # Extract paste ID
            paste_id = parsed_path.path.split('/view/')[-1]

            # Retrieve paste
            pb = SimplePrivateBin()
            paste_data = pb.retrieve_paste(paste_id)

            if paste_data:
                # Display credentials
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>🔐 Secure Database Credentials</title>
                    <style>
                        body {{ font-family: 'Courier New', monospace; background: #1a1a1a; color: #00ff00; padding: 20px; }}
                        .container {{ max-width: 800px; margin: 0 auto; }}
                        .warning {{ background: #ff3333; color: white; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                        .credentials {{ background: #333; padding: 20px; border-radius: 5px; white-space: pre-wrap; }}
                        .burned {{ color: #ff6666; font-weight: bold; }}
                        .button {{ background: #ff3333; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }}
                    </style>
                    <script>
                        // Auto-destruct page after viewing
                        setTimeout(function() {{
                            document.body.innerHTML = '<div class="container"><h1>🔥 CREDENTIALS DESTROYED</h1><p>This page has self-destructed for security.</p></div>';
                        }}, 30000); // 30 seconds

                        // Prevent copying/printing
                        document.addEventListener('keydown', function(e) {{
                            if (e.ctrlKey && (e.key === 'c' || e.key === 'p' || e.key === 's')) {{
                                e.preventDefault();
                                alert('Copying/printing disabled for security');
                            }}
                        }});
                    </script>
                </head>
                <body>
                    <div class="container">
                        <div class="warning">
                            ⚠️ SECURITY NOTICE: These credentials are temporary and will auto-expire.
                            This page will self-destruct in 30 seconds.
                        </div>

                        <h1>🔐 Ephemeral Database Credentials</h1>

                        <div class="credentials">{paste_data['content']}</div>

                        {f'<p class="burned">🔥 This link has been burned and can no longer be accessed.</p>' if paste_data.get('burned') else ''}

                        <div class="warning">
                            Created: {paste_data['created_at']}<br>
                            Expires: {paste_data['expires_at']}<br>
                            🚨 Do NOT save, screenshot, or share these credentials!
                        </div>

                        <button class="button" onclick="window.close();">Close Window</button>
                    </div>
                </body>
                </html>
                """

                self.wfile.write(html_content.encode())
            else:
                # Paste not found or expired
                self.send_response(404)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                html_content = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>🔥 Credentials Not Found</title>
                    <style>
                        body { font-family: Arial, sans-serif; background: #1a1a1a; color: #ff3333; padding: 20px; text-align: center; }
                        .container { max-width: 600px; margin: 0 auto; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>🔥 Credentials Destroyed or Expired</h1>
                        <p>The requested credentials have either:</p>
                        <ul style="text-align: left;">
                            <li>Already been viewed (burned after reading)</li>
                            <li>Expired (TTL exceeded)</li>
                            <li>Never existed</li>
                        </ul>
                        <p><strong>This is normal security behavior.</strong></p>
                        <p>If you need new access, request fresh credentials through the system.</p>
                    </div>
                </body>
                </html>
                """

                self.wfile.write(html_content.encode())

        else:
            # Default page
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>🔐 Secure Credential Viewer</title>
                <style>
                    body { font-family: Arial, sans-serif; background: #1a1a1a; color: #00ff00; padding: 20px; text-align: center; }
                    .container { max-width: 600px; margin: 0 auto; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🔐 Secure Database Credential Viewer</h1>
                    <p>This service provides secure, self-destructing access to ephemeral database credentials.</p>
                    <p><strong>Security Features:</strong></p>
                    <ul style="text-align: left;">
                        <li>🔥 Burn after reading (one-time view)</li>
                        <li>⏰ Auto-expiration (1 hour TTL)</li>
                        <li>🚫 Copy/print protection</li>
                        <li>📝 Complete audit logging</li>
                    </ul>
                    <p>To view credentials, you need a secure link from the system.</p>
                </div>
            </body>
            </html>
            """

            self.wfile.write(html_content.encode())

    def log_message(self, format, *args):
        """Override to reduce noise in logs"""
        pass

def start_credential_viewer(port=8081):
    """Start the credential viewer server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, CredentialViewerHandler)
    print(f"🔐 Credential viewer running at http://localhost:{port}")
    print("Use Ctrl+C to stop")
    httpd.serve_forever()

if __name__ == "__main__":
    start_credential_viewer()