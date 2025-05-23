export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  const { cookies } = req.body;

  if (!cookies) {
    return res.status(400).json({ error: "No cookies provided" });
  }

  try {
    const response = await fetch("https://graph.facebook.com/me?fields=id,name&access_token=invalid", {
      method: "GET",
      headers: {
        "Cookie": cookies,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
      },
    });

    const text = await response.text();

    const match = text.match(/EAAB\w+/);

    if (match) {
      return res.status(200).json({ token: match[0] });
    } else {
      return res.status(404).json({ error: "Token not found. Make sure the cookies are valid and from a Business Facebook account." });
    }
  } catch (err) {
    return res.status(500).json({ error: "Something went wrong", details: err.message });
  }
}
