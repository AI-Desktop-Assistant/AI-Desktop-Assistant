// check for remembered user before page loads
document.addEventListener("DOMContentLoaded", function () {
    getWeather();
    // check if user is a remembered user
    console.log('Checking for remembered user')
    window.electron.getRemUser()
    // handle success and failure response from main process
    window.electron.onGetRemUserResponse((event, response) => {
        // if user is remembered
        // automatically login
        if (response.success) {
            console.log(`Auto-logging-in: ${response.username}`)
            login(response.username, response.password, true, true)
        } 
        // if user is not remembered
        // display login container
        else {
            document.querySelector(".login-container").classList.add("active")
        }
    })
})

function toggleEmailBody(button) {
    console.log(`Expanding body from: ${button}`)
    const snippet = button.previousElementSibling.previousElementSibling
    const fullText = button.previousElementSibling
    if (fullText.style.display === 'none') {
        fullText.style.display = 'block'
        snippet.style.display = 'none'
        button.textContent = 'Collapse'
    } 
    else {
        fullText.style.display = 'none'
        snippet.style.display = 'block'
        button.textContent = 'Expand'
    }
}

function switchModule(moduleId) {
    console.log(`Switching module to: ${moduleId}`)
    const modules = document.querySelectorAll('.module')
    modules.forEach(mod => mod.style.display = 'none')
    console.log(`Displaying ${moduleId}`)
    const module = document.getElementById(moduleId)
    module.style.display = 'block'
    const links = document.querySelectorAll('.nav-link')
    links.forEach(link => link.classList.remove('active'))
    const successMessages = document.querySelectorAll('.message-success')
    successMessages.forEach(successMessage => successMessage.textContent = null)
    const successInputs = document.querySelectorAll('.input-success')
    successInputs.forEach(successInput => successInput.classList.remove('input-success'))
    console.log(`Success inputs: ${successInputs}`)
    const errorMessages = document.querySelectorAll('.message-error')
    errorMessages.forEach(errorMessage => errorMessage.textContent = null)
    const errorInputs = document.querySelectorAll('.input-error')
    errorInputs.forEach(errorInput => errorInput.classList.remove('input-error'))
    selectedModule = document.querySelector(`[onclick="switchModule('${moduleId}')"]`)
    selectedModule.classList.add('active')

    const tabButtons = document.getElementById(moduleId).querySelector('.tab-buttons')
    const moduleContent = module.querySelector('.module-content')
    console.log(`Tab Buttons: ${tabButtons}`)
    if (tabButtons) {
        firstTab = tabButtons.querySelector('.tab-button')
        console.log(`First tab: ${firstTab.className}`)
        firstTab.click()
    }
    else if (moduleContent) {
        console.log(`Module Content: ${moduleContent}`)
        moduleContent.classList.add('active')
        content = moduleContent.querySelectorAll('.tab-content')
        content.forEach(cont => cont.classList.add('active'))

    }
}

function switchTab(tabId) {
    console.log(`Switching tab to ${tabId}`)
    const tabs = document.querySelectorAll('.tab')
    tabs.forEach(tab => tab.classList.remove('active'))
    document.getElementById(tabId).classList.add('active')
    const tabButtons = document.querySelectorAll('.tab-button')
    tabButtons.forEach(button => button.classList.remove('active')) 
    document.querySelector(`[onclick="switchTab('${tabId}')"]`).classList.add('active')
}

function getWeather() {
    const apiKey = "714a7b0b20794a4aa3eaac01c8d888ad";
    const city = document.getElementById("city-input").value;
    const unit = document.getElementById("unit-select").value;
    const weatherUrl = `http://api.openweathermap.org/data/2.5/weather?q=${city}&appid=${apiKey}&units=${unit}`;

    fetch(weatherUrl)
        .then(response => response.json())
        .then(data => {
            if (data.cod === 200) {
                updateWeatherWidget(data);
            } else {
                console.error('Failed to retrieve weather data:', data.message);
            }
        })
        .catch(error => console.error('Network or other error:', error));
}
function updateWeatherWidget(data) {
    function updateWeatherWidget(data) {
        if (!data || data.cod !== 200) {
            document.getElementById('customWeatherWidget').innerHTML = `<p>Failed to load weather data.</p>`;
            return;
        }
    }    
    document.getElementById('widgetCityName').textContent = data.name;
    document.getElementById('widgetTemp').textContent = `${data.main.temp} ${data.units === 'metric' ? '°C' : '°F'}`;
    const iconCode = data.weather[0].icon;
    const iconUrl = `http://openweathermap.org/img/wn/${iconCode}.png`;
    document.getElementById('weatherIcon').src = iconUrl;
    document.getElementById('weatherIcon').alt = data.weather[0].description;
    document.getElementById('widgetCityName').textContent = data.name;
    document.getElementById('widgetTemp').textContent = `${data.main.temp} ${data.units === 'metric' ? '°C' : '°F'}`;
    document.getElementById('widgetFeelsLike').textContent = `${data.main.feels_like} ${data.units === 'metric' ? '°C' : '°F'}`;
    document.getElementById('widgetHumidity').textContent = `${data.main.humidity}%`;
    document.getElementById('widgetPressure').textContent = `${data.main.pressure} hPa`;
    document.getElementById('widgetDescription').textContent = data.weather[0].description;
    document.getElementById('widgetWind').textContent = `${data.wind.speed} m/s, ${windDirection(data.wind.deg)}`;
    document.getElementById('widgetClouds').textContent = `${data.clouds.all}%`;
    document.getElementById('widgetVisibility').textContent = `${data.visibility} meters`;
    document.getElementById('widgetSunrise').textContent = new Date(data.sys.sunrise * 1000).toLocaleTimeString();
    document.getElementById('widgetSunset').textContent = new Date(data.sys.sunset * 1000).toLocaleTimeString();
}
function windDirection(degrees) {
    const directions = ['North', 'Northeast', 'East', 'Southeast', 'South', 'Southwest', 'West', 'Northwest'];
    const index = Math.round(degrees / 45) % 8;
    return directions[index];
}

switchModule('chat')

// switch between login and signup pages
function toggleForm() {
    console.log('Switching form')
    // toggle both containers
    document.querySelector(".login-container").classList.toggle("active")
    document.querySelector(".signup-container").classList.toggle("active")
    // Remove Error indicators
    document.getElementById('login-status-message').style.display = 'none'
    document.getElementById('login-username').classList.remove('input-error')
    document.getElementById('login-password').classList.remove('input-error')
    document.getElementById('signup-status-message').style.display = 'none'
    document.getElementById('signup-password').classList.remove('input-error')
    document.getElementById('signup-confirm-password').classList.remove('input-error')
}

// Ran on login button click
function login(username, password, rememberMe, autoLogin = false) {
    // If user is not remembered
    if (!autoLogin) {
        username = document.getElementById('login-username').value
        password = document.getElementById('login-password').value
        rememberMe = document.getElementById('remember-me').checked
    }
    console.log(`Attempting to login as username: ${username}`)
    // validate details in main process
    window.electron.login(username, password, rememberMe, autoLogin)
}

// handle login success and failure responses from main process
window.electron.onLoginResponse((event, response) => {
    const usernameInput = document.getElementById('login-username')
    const passwordInput = document.getElementById('login-password')
    const loginStatusMessage = document.getElementById('login-status-message')
    // if login was successful
    if (response.success) {
        console.log(response.message)
        // remove invalid input indicators 
        loginStatusMessage.style.display = 'none'
        loginStatusMessage.classList.remove('message-error')
        usernameInput.classList.remove('input-error')
        passwordInput.classList.remove('input-error')
        // if user selected to remember login
        // send user details to main process to remember login
        if (response.rememberMe && !response.autoLogin) {
            console.log(`Remembering user: ${response.username}`)
            window.electron.setRemUser(response.rememberMe, response.username, response.password)
        }
        // remove login page from view and show the main app UI
        document.getElementById('login-signup-screen').style.display = 'none'
        document.getElementById('main-app').style.display = 'block'
        load_user_data()
    } 
    // if login was unsuccessful
    // Alert that login was unsuccessful
    else {    
        console.log(`Invalid credentials: ${response.message}`)
        // alert user of invalid login
        loginStatusMessage.textContent = response.message
        loginStatusMessage.classList.add('message-error')
        loginStatusMessage.style.display = 'block'
        usernameInput.classList.add('input-error')
        passwordInput.classList.add('input-error')
    }
})

function load_user_data() {
    window.electron.fillUsername()
    window.electron.fillEmail()
}

window.electron.onFillUsernameResponse((event, response) => {
    const username_field = document.getElementById('current-username')
    console.log(username_field)
    username_field.textContent = `Current Username: ${response.username}`
}) 

window.electron.onFillEmailResponse((event, response) => {
    const email_field = document.getElementById('current-email')
    console.log(email_field)
    email_field.textContent = `Current Email: ${response.email}`
})

// ran on signup button click
function signup() {
    const username = document.getElementById('signup-username').value
    const password = document.getElementById('signup-password').value
    const confirmPassword = document.getElementById('signup-confirm-password').value
    window.electron.signup(username, password, confirmPassword)
}

// handle signup success and failure response from main process
window.electron.onSignupResponse((event, response) => {
    const loginStatusMessage = document.getElementById('login-status-message')
    const signupStatusMessage = document.getElementById('signup-status-message')
    const signupUsernameInput = document.getElementById('signup-username')
    const signupPasswordInput = document.getElementById('signup-password')
    const signupConfirmPassInput = document.getElementById('signup-confirm-password')

    // if user was successfully signed up
    // alert user of success and toggle log in form
    if (response.success) {
        console.log('Sign up successful')
        toggleForm()
        loginStatusMessage.textContent = response.message
        loginStatusMessage.classList.remove('message-error')
        loginStatusMessage.classList.add('message-success')
        loginStatusMessage.style.display = 'block'
    } 
    // alert user signup was unsuccessful
    else {
        // if users username was taken
        // output username taken 
        // display visual error indicators
        if (response.message.includes('Username')) {
            console.log(response.message)
            signupStatusMessage.textContent = response.message
            signupStatusMessage.classList.add('message-error')
            signupStatusMessage.style.display = 'block'
            signupUsernameInput.classList.add('input-error')
        }
        // if passwords do not match
        // output passwords dont match
        // display error indicators
        else if (response.message.includes('Password')) {
            console.log(response.message)
            signupStatusMessage.textContent = response.message
            signupStatusMessage.classList.add('message-error')
            signupStatusMessage.style.display = 'block'
            signupUsernameInput.classList.remove('input-error')
            signupPasswordInput.classList.add('input-error')
            signupConfirmPassInput.classList.add('input-error')
        }
        else {
            console.log(response.message)
            alert(response.message)
            document.getElementById('signup-username').focus()
        }
    }
})

function delimit_array(array) {
    arrayAsStr = ''
    for (let i = 0; i < array.length; i++) {
        arrayAsStr += array[i]
        if (array.length - 1 != i) {
            arrayAsStr += ', '
        }
    }

    return arrayAsStr
}

function showEmail(data) {
    body = data.body
    subject = data.subject
    recipients = data.recipients
    cc = data.cc
    bcc = data.bcc
    recipientsAsStr = delimit_array(recipients)
    ccAsStr = delimit_array(cc)
    bccAsStr = delimit_array(bcc)
    document.getElementById('recipient').value = recipientsAsStr
    document.getElementById('cc').value = ccAsStr
    document.getElementById('bcc').value = bccAsStr
    document.getElementById('subject').value = subject 
    document.getElementById('body').value = body
    switchModule('email')
    switchTab('composeEmail')
}

window.electron.toRenderer((event, data) => {
    const purpose = data.purpose
    console.log("Recieved renderer data..........", data)
    if (purpose === 'show-email') {
        showEmail(data.data)
    }
    if (data.purpose === 'spotify') {
        updateSpotifyUI(data.data);
    }
})

function toggleDropdown() {
    document.getElementById("accountDropdown").classList.toggle("show")
}

window.onclick = function(event) {
    if (!event.target.matches('.account-icon, .account-icon *')) {
        var dropdowns = document.getElementsByClassName("dropdown-content")
        for (var i = 0; i < dropdowns.length; i++) {
            var openDropdown = dropdowns[i]
            if (openDropdown.classList.contains('show')) {
                openDropdown.classList.remove('show')
            }
        }
    }
}

function signoutAndQuit() {
    console.log('Attempting sign out and quit')
    window.electron.signoutAndQuit()
}

function signout() {
    console.log('Attempting sign out')
    window.electron.signout()
    console.log('Going back to login page')
    document.getElementById('login-signup-screen').style.display = 'flex'
    document.getElementById('main-app').style.display = 'none'
}

function sendEmail() {
    const recipient = document.getElementById('recipient').value
    const cc = document.getElementById('cc').value
    const subject = document.getElementById('subject').value
    const body = document.getElementById('body').value
    window.electron.sendEmail(recipient, cc, subject, body)
}

function updateInfo(info) {
    if (info === 'email') {
        console.log('Updating email')
        window.electron.updateEmail(document.getElementById('new-email').value)
    }
    else if (info === 'username') {
        console.log('Updating username')
        window.electron.updateUsername(document.getElementById('new-username').value)
    }
    else if (info === 'app-password') {
        console.log('Updating app password')
        window.electron.updateAppPassword(document.getElementById('new-app-password').value)
    }
    else if (info === 'password') {
        console.log('Updating password')
        window.electron.updatePassword(document.getElementById('new-password').value, document.getElementById('confirm-password').value)
    }
    else if (info === 'signature') {
        console.log('Updating signature')
        window.electron.updateSignature(document.getElementById('new-signature').value)
    }
}

window.electron.onUpdateInfoResponse((event, response) => {
    console.log(`Response: ${response}`)
    if (response.success) {
        console.log(response.message)
        const successMessages = document.querySelectorAll('.message-success')
        successMessages.forEach(successMessage => successMessage.textContent = null)
        successMessages.forEach(successMessage => successMessage.classList.remove('message-success'))
        const successInputs = document.querySelectorAll('.input-success')
        successInputs.forEach(successInput => successInput.classList.remove('input-success'))
        console.log(`Success inputs: ${successInputs}`)
        const errorMessages = document.querySelectorAll('.message-error')
        errorMessages.forEach(errorMessage => errorMessage.textContent = null)
        errorMessages.forEach(errorMessage => errorMessage.classList.remove('message-error'))
        const errorInputs = document.querySelectorAll('.input-error')
        errorInputs.forEach(errorInput => errorInput.classList.remove('input-error'))
        
        document.getElementById(`new-${response.section}`).classList.add('input-success')
        document.getElementById(`${response.section}-update-status-message`).textContent = response.message
        document.getElementById(`${response.section}-update-status-message`).classList.add('message-success')
        if (response.section === 'password') {
            document.getElementById(`confirm-${response.section}`).classList.add('input-success')
        }
        load_user_data()
    }
    else {
        console.log('Update Failed')
        const successMessages = document.querySelectorAll('.message-success')
        successMessages.forEach(successMessage => successMessage.textContent = null)
        successMessages.forEach(successMessage => successMessage.classList.remove('message-success'))
        const successInputs = document.querySelectorAll('.input-success')
        successInputs.forEach(successInput => successInput.classList.remove('input-success'))
        console.log(`Success inputs: ${successInputs}`)
        const errorMessages = document.querySelectorAll('.message-error')
        errorMessages.forEach(errorMessage => errorMessage.textContent = null)
        errorMessages.forEach(errorMessage => errorMessage.classList.remove('message-error'))
        const errorInputs = document.querySelectorAll('.input-error')
        errorInputs.forEach(errorInput => errorInput.classList.remove('input-error'))

        console.log(response.message)
        console.log(response.section)
        document.getElementById(`new-${response.section}`).classList.add('input-error')
        document.getElementById(`${response.section}-update-status-message`).textContent = response.message
        document.getElementById(`${response.section}-update-status-message`).classList.add('message-error')
        if (response.section === 'password') {
            document.getElementById(`confirm-${response.section}`).classList.add('input-error')
        }
    }
})

function searchSpotify() {
    console.log("Search button has been hit")
    let userSearch = document.getElementById("spotifySearch").value
    data = {module:"spotify",data:userSearch}
    window.electron.sendMessage(data)
}

function updateSpotifyUI(spotifyData) {
    const artistElement = document.getElementById('artistInfo');
    artistElement.innerHTML = `Name: ${spotifyData.name}<br>Genre: ${spotifyData.genres.join(', ')}<br>Followers: ${spotifyData.followers.total}`;
}

