
const axios = require('axios');

async function getTokenFromCookies(c_user, xs) {
    const cookies = `c_user=${c_user}; xs=${xs};`;

    try {
        const res = await axios.get('https://business.facebook.com/creatorstudio', {
            headers: {
                'Cookie': cookies,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            }
        });

        const match = res.data.match(/EAAB\w+/);
        if (match) {
            return { token: match[0] };
        } else {
            return { error: 'Token not found. Invalid cookies or format changed.' };
        }
    } catch (error) {
        return { error: 'Failed to fetch token: ' + error.message };
    }
}

module.exports = { getTokenFromCookies };
