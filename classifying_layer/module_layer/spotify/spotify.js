const clientId = '8eed3f3a49c84fea9b47fd39a80d94a1';  // Spotify Client ID from environment variables
const clientSecret = 'd19f4b6754944fa7a38446d7e9f5c2d6'; // Spotify Client Secret from environment variables
const redirectUri = 'aiassistant://callback';  // Match this with the custom protocol handler in main.js

const scopes = [
    'user-read-private',
    'user-read-email',
    'playlist-read-private',
    'playlist-modify-public',
    'user-modify-playback-state'
];

function generateRandomString(length) {
    let text = '';
    const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    for (let i = 0; i < length; i++) {
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
}

function authenticateUser() {
    const state = generateRandomString(16);
    localStorage.setItem('spotify_auth_state', state);

    let url = `https://accounts.spotify.com/authorize?response_type=code&client_id=${encodeURIComponent(clientId)}&scope=${encodeURIComponent(scopes.join(' '))}&redirect_uri=${encodeURIComponent(redirectUri)}&state=${encodeURIComponent(state)}`;

    window.location = url;
}

function handleRedirectCallback() {
    const params = new URLSearchParams(window.location.search);
    const code = params.get('code');
    const state = params.get('state');
    const storedState = localStorage.getItem('spotify_auth_state');

    if (!state || state !== storedState) {
        console.error('State mismatch or state missing');
        return;
    }

    localStorage.removeItem('spotify_auth_state');
    fetchAccessToken(code);
}

function fetchAccessToken(code) {
    const body = new URLSearchParams();
    body.append('grant_type', 'authorization_code');
    body.append('code', code);
    body.append('redirect_uri', redirectUri);

    fetch('https://accounts.spotify.com/api/token', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Basic ' + btoa(`${clientId}:${clientSecret}`)
        },
        body: body
    })
    .then(response => response.json())
    .then(data => {
        localStorage.setItem('spotify_access_token', data.access_token);
        console.log('Access Token Set:', data.access_token); // Confirm token is set
    })
    .catch(error => {
        console.error('Error fetching access token', error);
    });
}