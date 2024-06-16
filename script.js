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
    document.getElementById(moduleId).style.display = 'block'
    const links = document.querySelectorAll('.nav-link')
    links.forEach(link => link.classList.remove('active'))
    const selectedModule = document.querySelector(`[onclick="switchModule('${moduleId}')"]`)
    selectedModule.classList.add('active')
    const firstTabButton = selectedModule.querySelector('.tab-button')
    if (firstTabButton) {
        const firstTabId = firstTabButton.onclick.toString().match(/'([^']+)'/)[1]
        switchTab(firstTabId)
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
