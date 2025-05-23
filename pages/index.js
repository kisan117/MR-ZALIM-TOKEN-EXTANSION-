import { useState } from 'react';

export default function Home() {
  const [cookie, setCookie] = useState('');
  const [token, setToken] = useState('');
  const [loading, setLoading] = useState(false);

  const extractToken = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/extract', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cookie }),
      });
      const data = await response.json();
      setToken(data.token || 'Token not found');
    } catch (error) {
      setToken('Error extracting token');
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center px-4">
      <div className="max-w-2xl w-full bg-gray-800 p-6 rounded-2xl shadow-lg flex flex-col gap-4">
        <h1 className="text-2xl font-bold text-center">Facebook Cookies to Token</h1>
        <textarea
          rows={4}
          className="w-full p-3 bg-gray-700 text-white rounded-xl"
          placeholder="Paste your Facebook Cookies here..."
          value={cookie}
          onChange={(e) => setCookie(e.target.value)}
        />
        <button
          className="bg-blue-600 hover:bg-blue-700 p-3 rounded-xl font-semibold"
          onClick={extractToken}
          disabled={loading}
        >
          {loading ? 'Extracting...' : 'Get Token'}
        </button>
        {token && (
          <div className="bg-black p-3 rounded-xl break-words">
            <strong>Token:</strong> {token}
          </div>
        )}
      </div>
    </div>
  );
}
