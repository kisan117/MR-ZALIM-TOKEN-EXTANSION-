export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).end();

  const { cookie } = req.body;

  try {
    const response = await fetch('https://business.facebook.com/business_locations', {
      headers: {
        'Cookie': cookie,
        'User-Agent': 'Mozilla/5.0',
      },
    });

    const text = await response.text();
    const match = text.match(/EAAB\w+/);
    if (match) {
      return res.status(200).json({ token: match[0] });
    } else {
      return res.status(200).json({ token: null });
    }
  } catch (error) {
    return res.status(500).json({ token: null });
  }
}
