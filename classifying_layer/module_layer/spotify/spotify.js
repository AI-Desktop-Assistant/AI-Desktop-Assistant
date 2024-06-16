const clientId = 'YOUR_SPOTIFY_CLIENT_ID';  // Replace with your Spotify client ID
const clientSecret = 'YOUR_SPOTIFY_CLIENT_SECRET'; // Replace with your Spotify client secret
const redirectUri = 'YOUR_REDIRECT_URI';  // Replace with your redirect URI registered in the Spotify dashboard
const scopes = [
    'user-read-private',
    'user-read-email',
    'playlist-read-private',
    'playlist-modify-public',
    'user-modify-playback-state'
];  // Define scopes based on the functionalities you need

// Generate a random string for the state parameter to prevent CSRF attacks
function generateRandomString(length) {
    let text = '';
    const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    for (let i = 0; i < length; i++) {
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
}

// Redirects the user to Spotify's authorization page
function authenticateUser() {
    const state = generateRandomString(16);
    localStorage.setItem('spotify_auth_state', state); // Save the state in local storage to verify later

    let url = 'https://accounts.spotify.com/authorize';
    url += '?response_type=code';
    url += '&client_id=' + encodeURIComponent(clientId);
    url += '&scope=' + encodeURIComponent(scopes.join(' '));
    url += '&redirect_uri=' + encodeURIComponent(redirectUri);
    url += '&state=' + encodeURIComponent(state);

    window.location = url; // Redirect user to Spotify's authorization page
}

// Called from the page that handles the redirect from Spotify
function handleRedirectCallback() {
    const params = new URLSearchParams(window.location.search);
    const code = params.get('code');
    const state = params.get('state');

    // Retrieve the state saved in localStorage and compare it with the received state
    const storedState = localStorage.getItem('spotify_auth_state');
    if (state === null || state !== storedState) {
        console.error('State mismatch or state missing');
        return;
    }
    localStorage.removeItem('spotify_auth_state');

    fetchAccessToken(code);
}

// Fetches an access token using the authorization code
function fetchAccessToken(code) {
    const body = new URLSearchParams();
    body.append('grant_type', 'authorization_code');
    body.append('code', code);
    body.append('redirect_uri', redirectUri);

    fetch('https://accounts.spotify.com/api/token', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            // Encode clientId and clientSecret to base64
            'Authorization': 'Basic ' + btoa(clientId + ':' + clientSecret)
        },
        body: body
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            throw new Error(data.error);
        }
        console.log('Access Token:', data.access_token);
        localStorage.setItem('spotify_access_token', data.access_token);
        // Here you can redirect or perform additional actions as needed
    })
    .catch(error => {
        console.error('Error fetching access token', error);
    });
}

// Add these scripts to your HTML to ensure it's ready to use
document.addEventListener('DOMContentLoaded', function() {
    const path = window.location.pathname;
    if (path === "/your-callback-endpoint") {  // Update to match your callback path
        handleRedirectCallback();
    }
});