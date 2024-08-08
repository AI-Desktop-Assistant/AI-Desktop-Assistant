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
    document.getElementById('load-playlists-button').addEventListener('click', fetchPlaylists);
    document.getElementById('spotifySearchButton').addEventListener('click', searchTrack);
    const volumeSlider = document.getElementById('volume')

    if (volumeSlider) {
        volumeSlider.addEventListener('input', (event) => {
            const volume = event.target.value
            console.log(`Volume changed to: ${volume}`)
            window.electron.volumeChanged(volume)
        })
    }
    const voiceSelector = document.getElementById('voice')

    if (voiceSelector) {
        voiceSelector.addEventListener('change', (event) => {
            const voice = event.target.value
            console.log(`Voice changed to: ${voice}`)
            window.electron.voiceChanged(voice)
        })
    }
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
    module.style.display = 'flex'
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
    if (moduleId === 'chat') {
        document.getElementById("chat").classList.remove("sidebar")
        document.getElementById("chat").classList.add("main")
    } 
    else {
        document.getElementById("chat").classList.add("sidebar")
        document.getElementById("chat").classList.remove("main")
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

window.electron.getWeather(async (event, data) => {
    console.log(data.data);
    const weatherData = await getWeather(false, data.data, 'imperial');
    weatherData['purpose'] = 'get-weather-data';
    // window.electron.getWeatherResponse({'data': weatherData, 'purpose': 'get-weather-data'})
    window.electron.getWeatherResponse(weatherData);
});

async function getWeather(fromUi, city = '', unit = '') { 
    const apiKey = "714a7b0b20794a4aa3eaac01c8d888ad";
    if (fromUi) {
        city = document.getElementById("city-input").value.trim();
        unit = document.getElementById("unit-select").value;
    }
    const encodedCity = encodeURIComponent(city);
    console.log(`Fetching weather for city: ${encodedCity} with unit: ${unit}`);
    const weatherUrl = `http://api.openweathermap.org/data/2.5/weather?q=${encodedCity}&appid=${apiKey}&units=${unit || 'standard'}`;
    try {
        const response = await fetch(weatherUrl);
        const data = await response.json();

        if (data.cod === 200) {
            console.log('Weather data retrieved:', data);
            if (fromUi) {
                updateWeatherWidget(data, unit);
            } else {
                if (unit === 'standard' || !unit) {
                    // Convert from Kelvin to Fahrenheit
                    data.main.temp = Math.round((data.main.temp - 273.15) * 9/5 + 32);
                    data.main.feels_like = Math.round((data.main.feels_like - 273.15) * 9/5 + 32);
                    data.main.temp_min = Math.round((data.main.temp_min - 273.15) * 9/5 + 32);
                    data.main.temp_max = Math.round((data.main.temp_max - 273.15) * 9/5 + 32);
                // const weatherDict = {};
                // for (let property in data) {
                    // const value = data[property];
                    // weatherDict[property] = value;
                }   else if (unit === 'metric') {
                    // Convert from Celsius to Fahrenheit
                    data.main.temp = Math.round((data.main.temp * 9/5) + 32);
                    data.main.feels_like = Math.round((data.main.feels_like * 9/5) + 32);
                    data.main.temp_min = Math.round((data.main.temp_min * 9/5) + 32);
                    data.main.temp_max = Math.round((data.main.temp_max * 9/5) + 32);
                }   else if (unit === 'imperial') {
                    // No conversion needed for Fahrenheit (imperial)
                }
                console.log(`Sending weather data: city=${data.name}, temperature=${Math.round(data.main.temp)}, unit=${unit}`); // Debug log
                fetch('http://localhost:8888/report_weather', { // Update this URL
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        city: data.name,
                        temperature: Math.round(data.main.temp),
                        unit: unit
                    })
                });
                // return weatherDict;
                return data;
            }
        } else {
            console.error('Failed to retrieve weather data:', data.message);
        }
    } catch (error) {
        console.error('Network or other error:', error);
    }
}

function updateWeatherWidget(data, unit) {
        if (!data || data.cod !== 200) {
            document.getElementById('customWeatherWidget').innerHTML = `<p>Failed to load weather data.</p>`;
            return;
        }    
    document.getElementById('widgetCityName').textContent = data.name;
    document.getElementById('widgetTemp').textContent = `${Math.round(data.main.temp)} ${unit === 'metric' ? '°C' : '°F'}`;
    const iconCode = data.weather[0].icon;
    const iconUrl = `http://openweathermap.org/img/wn/${iconCode}.png`;
    document.getElementById('weatherIcon').src = iconUrl;
    document.getElementById('weatherIcon').alt = data.weather[0].description;
    document.getElementById('widgetCityName').textContent = data.name;
    document.getElementById('widgetFeelsLike').textContent = `${Math.round(data.main.temp)} ${unit === 'metric' ? '°C' : '°F'}`;
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
    console.log(`Login Response received ${response.success}`)
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
        console.log('Removing Login/Sign up Screen')
        document.getElementById('login-signup-screen').style.display = 'none'
        console.log('Displaying Main App')
        document.getElementById('main-app').style.display = 'flex'
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

window.electron.onLoading((event, response) => {
    console.log('Showing Loading Circle')
    document.getElementById('login-username').classList.add('hidden')
    document.getElementById('login-password').classList.add('hidden')
    document.getElementById('login-status-message').textContent = ''
    document.getElementById('login-button').classList.add('hidden')
    document.querySelector('.remember-me').classList.add('hidden')
    document.querySelector('.remember-me').textContent = ''
    // document.getElementById('remember-me').classList.add('hidden')
    document.getElementById('login-title').textContent = `Logging in as ${response.username}`
    document.getElementById('login-loading').classList.remove('hidden')
})

window.electron.onUndoLoading((event) => {
    console.log('Hiding Loading Circle')
    document.getElementById('login-username').classList.remove('hidden')
    document.getElementById('login-password').classList.remove('hidden')
    document.getElementById('login-button').classList.remove('hidden')
    document.querySelector('.remember-me').classList.remove('hidden')
    const remembermeBox = document.createElement('input')
    remembermeBox.setAttribute('type', 'checkbox')
    remembermeBox.setAttribute('id', 'remember-me')
    document.querySelector('.remember-me').appendChild(remembermeBox)
    const textNode = document.createTextNode(' Remember Me ')
    document.querySelector('.remember-me').appendChild(textNode)
    // document.getElementById('remember-me').classList.remove('hidden')
    document.getElementById('login-title').textContent = `Login`
    document.getElementById('login-loading').classList.add('hidden')
})

function load_user_data() {
    window.electron.fillUsername()
    window.electron.fillEmail()
    window.electron.fillAppPass()
    window.electron.fillSentEmails()
    window.electron.fillAppPaths()
    window.electron.fillTasks()
    window.electron.fillUpcomingTasks()
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

window.electron.onFillSentEmailResponse((event, response) => {
    console.log(`Got Sent Email Response: ${response}`)
    if (response.success) {
        const tbody = document.getElementById('email-tbody')
        tbody.innerHTML = ''
        const recipients = response.recipients
        const subjects = response.subjects
        const bodies = response.bodies
        const timestamps = response.timestamps
        const snippets = bodies.map(body => body.slice(0, 38) + (body.length > 38 ? '...' : ''));
        for (let i = 0; i < recipients.length; i++) {
            const row = createEmailRow(recipients[i], subjects[i], snippets[i], bodies[i], timestamps[i]);
            tbody.appendChild(row);
        }
    }
})

window.electron.onFillContactsResponse((event, response) => {
    console.log(`Got Contacts Response: ${response}`)
    if (response.success) {
        const tbody = document.getElementById('contact-tbody')
        tbody.innerHTML = ''
        const contactNames = response.contactNames
        const contactEmails = response.contactEmails
        const timestamps = response.timestamps
        for (let i = 0; i < contactNames.length; i++) {
            const row = createContactRow(contactNames[i], contactEmails[i], timestamps[i])
            tbody.appendChild(row)
        }
    }
})

window.electron.onFillAppPathsResponse((event, response) => {
    console.log(`Got App Paths Response: ${response}`)
    if (response.success) {
        const tbody = document.getElementById('apps-tbody')
        tbody.innerHTML = ''
        const appPaths = response.appPaths
        const appNames = response.appNames
        for (let i = 0; i < appPaths.length; i++) {
            const row = createAppPathRow(appNames[i], appPaths[i])
            tbody.appendChild(row)
        }
    }
})

window.electron.onFillTasksResponse((event, response) => {
    console.log(`Got Tasks Response ${response}`)
    if (response.success) {
        const tbody = document.getElementById(response.id)
        tbody.innerHTML = ''
        const dates = response.dates
        const times = response.times
        const tasks = response.tasks
        const repeatings = response.repeatings
        for (let i = 0; i < dates.length; i++) {
            const row = createTasksRow(dates[i], times[i], tasks[i], repeatings[i])
            tbody.appendChild(row)
        }
    }
})

window.electron.onReqFillTasksResponse((event) => {
    window.electron.fillTasks()
})

window.electron.onReqFillAppPathsResponse((event) => {
    window.electron.fillAppPaths()
})

window.electron.onReqFillSentEmailResponse((event) => {
    window.electron.fillSentEmails()
})

window.electron.onReqFillUpcomingTasks((event) => {
    window.electron.fillUpcomingTasks()
})

function createAppPathRow(appName, appPath) {
    const row = document.createElement('tr')

    const appNameCell = document.createElement('td')
    appNameCell.textContent = appName
    row.appendChild(appNameCell)

    const appPathCell = document.createElement('td')
    appPathCell.textContent = appPath
    row.appendChild(appPathCell)

    return row
}

function createContactRow(contactName, contactEmail, timestamp) {
    const row = document.createElement('tr')

    const contactNameCell = document.createElement('td')
    contactNameCell.textContent = contactName
    row.appendChild(contactNameCell)

    const contactEmailCell = document.createElement('td')
    contactEmailCell.textContent = contactEmail
    row.appendChild(contactEmailCell)

    const timestampCell = document.createElement('td')
    timestampCell.textContent = timestamp
    row.appendChild(timestampCell)

    return row
}

function createTasksRow(date, time, task, repeating) {
    const row = document.createElement('tr')

    const dateCell = document.createElement('td')
    dateCell.textContent = date
    row.appendChild(dateCell)

    const timeCell = document.createElement('td')
    timeCell.textContent = time
    row.appendChild(timeCell)

    const taskCell = document.createElement('td')
    taskCell.textContent = task
    row.appendChild(taskCell)

    const repeatingCell = document.createElement('td')
    repeatingCell.textContent = repeating
    row.appendChild(repeatingCell)
    row.setAttribute('onclick', 'openModal(this)')

    return row
}

function createEmailRow(recipient, subject, snippet, fullBody, timeSent) {
    const row = document.createElement('tr');

    const recipientCell = document.createElement('td');
    recipientCell.textContent = recipient;
    row.appendChild(recipientCell);

    const subjectCell = document.createElement('td');
    subjectCell.textContent = subject;
    row.appendChild(subjectCell);

    const bodyCell = document.createElement('td');
    bodyCell.classList.add('email-snippet');

    const snippetSpan = document.createElement('span');
    snippetSpan.classList.add('snippet-text');
    snippetSpan.textContent = snippet;

    const fullTextSpan = document.createElement('span');
    fullTextSpan.classList.add('full-text');
    fullTextSpan.style.display = 'none';
    fullTextSpan.textContent = fullBody;

    const expandButton = document.createElement('button');
    expandButton.classList.add('expand-btn');
    expandButton.textContent = 'Expand';
    expandButton.onclick = function () {
        toggleEmailBody(this);
    };

    bodyCell.appendChild(snippetSpan);
    bodyCell.appendChild(fullTextSpan);
    bodyCell.appendChild(expandButton);
    row.appendChild(bodyCell);

    const timeSentCell = document.createElement('td');
    timeSentCell.textContent = timeSent;
    row.appendChild(timeSentCell);

    return row;
}
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
        textarea.dispatchEvent(new Event('input'))
    }
    else if (data.purpose === 'search') {
        console.log("Updating Spotify UI with data")
        updateSpotifyUI(data.data);
    }
    else if (data.purpose === 'get-token') {
        window.electron.getCurrentlyPlaying()
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
    document.querySelector('.chat-history').innerHTML = ''
}

function sendEmail() {
    const recipient = document.getElementById('recipient').value
    const cc = document.getElementById('cc').value
    const bcc = document.getElementById('bcc').value
    const subject = document.getElementById('subject').value
    const body = document.getElementById('body').value
    window.electron.sendEmail(recipient, cc, bcc, subject, body)
}

window.electron.onSendEmailResponse((event, response) => {
    success = response.success
    const emailStatusMessage = document.getElementById('email-status-message')
    if (success) {
        document.getElementById('recipient').value = ''
        document.getElementById('cc').value = ''
        document.getElementById('bcc').value = ''
        document.getElementById('subject').value = ''
        document.getElementById('body').value = ''
        emailStatusMessage.textContent = response.message
        emailStatusMessage.classList.remove('message-error')
        emailStatusMessage.classList.add('message-success')
        emailStatusMessage.style.display = 'block'
        document.getElementById('recipient').classList.remove('input-error')
        document.getElementById('cc').classList.remove('input-error')
        document.getElementById('bcc').classList.remove('input-error')
        document.getElementById('subject').classList.remove('input-error')
        document.getElementById('body').classList.remove('input-error')
        document.getElementById('recipient').classList.add('input-success')
        document.getElementById('cc').classList.add('input-success')
        document.getElementById('bcc').classList.add('input-success')
        document.getElementById('subject').classList.add('input-success')
        document.getElementById('body').classList.add('input-success')
    } else {
        emailStatusMessage.textContent = response.message
        emailStatusMessage.classList.remove('message-success')
        emailStatusMessage.classList.add('message-error')
        emailStatusMessage.style.display = 'block'
        document.getElementById('recipient').classList.remove('input-success')
        document.getElementById('cc').classList.remove('input-success')
        document.getElementById('bcc').classList.remove('input-success')
        document.getElementById('subject').classList.remove('input-success')
        document.getElementById('body').classList.remove('input-success')
        document.getElementById('recipient').classList.add('input-error')
        document.getElementById('cc').classList.add('input-error')
        document.getElementById('bcc').classList.add('input-error')
        document.getElementById('subject').classList.add('input-error')
        document.getElementById('body').classList.add('input-error')
    }
})

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
    else if (info === 'volume') {
        console.log('Updating volume')
        window.electron.updateSignature(document.getElementById('new-volume').value)
    }
    else if (info === 'signature') {
        console.log('Updating voice')
        window.electron.updateSignature(document.getElementById('new-voice').value)
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
        document.getElementById(`new-${response.section}`).value = ''
        document.getElementById(`${response.section}-update-status-message`).textContent = response.message
        document.getElementById(`${response.section}-update-status-message`).classList.add('message-success')
        if (response.section === 'password') {
            document.getElementById(`confirm-${response.section}`).classList.add('input-success')
            document.getElementById(`confirm-${response.section}`).value = ''
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
    data = {purpose:"search",data:userSearch}
    window.electron.sendMessage(data)
}

function updateSpotifyUI(spotifyData) {
    console.log('Updating UI with Spotify data')
    const artistElement = document.getElementById('artistInfo');
    artistElement.innerHTML = `Name: ${spotifyData.name}<br>Genre: ${spotifyData.genres.join(', ')}<br>Followers: ${spotifyData.followers.total}`;
}

function fetchCurrentlyPlaying() {
    console.log("Fetching currently playing track");
    window.electron.sendMessage({purpose: "get-token"});
}

function updateNowPlayingUI(trackData) {
    console.log("Updating now playing UI with data:", trackData);
    const nowPlayingElement = document.getElementById('nowPlayingInfo');
    if (trackData && trackData.track_name) {
        nowPlayingElement.innerHTML = `
            <div>
                <img src="${trackData.album_image}" alt="Album cover" style="width: 100px; height: 100px;">
                <div class="track-details">
                    <strong>Track:</strong> ${trackData.track_name}<br>
                    <strong>Artist:</strong> ${trackData.artist_name}<br>
                    <strong>Album:</strong> ${trackData.album_name}<br>
                    <strong>Progress:</strong> ${Math.floor(trackData.progress_ms / 1000)}s / ${Math.floor(trackData.duration_ms / 1000)}s<br>
                </div>
            </div>
        `;
    } else {
        nowPlayingElement.innerHTML = 'No track currently playing.';
    }
}

function setTask() {
    const taskDetails = document.getElementById('task-details').value
    const taskDate = document.getElementById('task-date').value
    const taskTime = document.getElementById('task-time').value

    console.log('Task Details:', taskDetails)
    console.log('Task Date:', taskDate)
    console.log('Task Time:', taskTime)

    window.electron.setTask(taskDetails, taskDate, taskTime)
}

window.electron.onSetTaskResponse((event, response) => {
    console.log(`Recieved Task Set Response: ${response}`)
    const success = response.success
    console.log(`Success: ${success}`)
    if (success) {
        const taskDetails = document.getElementById('task-details')
        const taskDate = document.getElementById('task-date')
        const taskTime = document.getElementById('task-time')
        const setTaskStatusMessage = document.getElementById('set-task-status-message')
        
        taskDetails.value = ''
        taskDate.value = ''
        taskTime.value = ''
        taskDetails.classList.remove('input-error')
        taskDate.classList.remove('input-error')
        taskTime.classList.remove('input-error')
        setTaskStatusMessage.classList.remove('message-error')
        taskDetails.classList.add('input-success')
        taskDate.classList.add('input-success')
        taskTime.classList.add('input-success')
        setTaskStatusMessage.classList.add('message-success')
        console.log(`Response Message: ${response.message}`)
        setTaskStatusMessage.textContent = response.message
    }
})

document.getElementById("playNextButton").addEventListener("click", function() {
    controlPlayback("next");
});

document.getElementById("pauseButton").addEventListener("click", function() {
    controlPlayback("pause");
});

document.getElementById("resumeButton").addEventListener("click", function() {
    controlPlayback("resume");
});

function controlPlayback(action) {
    window.electron.sendMessage({purpose: "control-playback", action: action});
}

window.electron.onGetCurrentlyPlayingResponse((event, data) => {
    console.log("Received data in renderer:", data);
    updateNowPlayingUI(data.data);
});

async function fetchPlaylists() {
    try {
        const playlists = await window.electron.fetchPlaylists();
        updatePlaylistsUI(playlists);
    } catch (error) {
        console.error('Error fetching playlists:', error);
    }
}

function updatePlaylistsUI(playlists) {
    const playlistContainer = document.getElementById('playlist-container');
    playlistContainer.innerHTML = '';
    playlists.forEach(playlist => {
        const playlistElement = document.createElement('div');
        playlistElement.className = 'playlist';
        playlistElement.innerHTML = `
            <h2>${playlist.name}</h2>
            <img src="${playlist.images[0]?.url || 'default-image.png'}" alt="${playlist.name}">
            <p>${playlist.tracks.total} songs</p>
        `;
        playlistElement.addEventListener('click', () => startPlayback(playlist.uri, 'playlist'));
        playlistContainer.appendChild(playlistElement);
    });
}

document.addEventListener("DOMContentLoaded", function () {
    document.getElementById('load-playlists-button').addEventListener('click', fetchPlaylists);
});

async function startPlayback(uri, uriType) {
    try {
        const message = await window.electron.startPlayback(uri, uriType);
        console.log(message);
    } catch (error) {
        console.error('Error starting playback:', error);
    }
}

async function searchTrack() {
    const trackName = document.getElementById('spotifySearch').value;
    try {
        const response = await window.electron.searchTrack(trackName);
        if (response.data) {
            updateSearchUI(response.data);
        } else {
            console.error('Track not found');
        }
    } catch (error) {
        console.error('Error searching track:', error);
    }
}

function updateSearchUI(trackInfo) {
    const searchContainer = document.getElementById('search-container');
    searchContainer.innerHTML = `
        <h2>${trackInfo.name}</h2>
        <img src="${trackInfo.album_image}" alt="${trackInfo.name}" class="small-album-cover">
        <p>Artists: ${trackInfo.artists.join(', ')}</p>
        <p>Album: ${trackInfo.album}</p>
    `;
}

function sendChat() {
    const userInput = document.querySelector('.chat-input')
    const message = userInput.value
    if (message.trim() !== "") {
        appendChat('user', message)
        userInput.value = ""
        window.electron.sendMessage({purpose: 'chat', data:message})
    }
}

function appendChat(sender, message) {
    const chatBox = document.querySelector('.chat-history')
    const chatBubble = document.createElement('div')
    chatBubble.classList.add('chat-bubble', sender)
    chatBubble.innerText = message
    chatBox.appendChild(chatBubble)

    // Scroll to the bottom of the chat box
    chatBox.scrollTop = chatBox.scrollHeight;
}

window.electron.appendAssistantChat((event, data) => {
    appendChat('assistant', data)
})
window.electron.appendUserChat((event, data) => {
    appendChat('user', data)
})

function createHistoryRow(response) {
    console.log(`Creating history row...................... `, response)
    const row = document.createElement('tr');

    const cell = document.createElement('td');
    cell.textContent = ''
    row.appendChild(cell);
    const commandCell = document.createElement('td');
    commandCell.textContent = response.historyCommand
    row.appendChild(commandCell);
    const responseCell = document.createElement('td');
    responseCell.textContent = response.historyResponse
    row.appendChild(responseCell);

    return row;
}

window.electron.addHistoryRow((event, response) => {
    console.log(`Received response from main: ${response}`)
    if (response.success) {
        console.log(`Created a row for history table: ${response}`)
        const tbody = document.getElementById('historyTable')
        const row = createHistoryRow(response);
        tbody.appendChild(row);
    }
})

const textarea = document.getElementById('body')

textarea.addEventListener('input', function () {
    this.style.height = 'auto'
    this.style.height = this.scrollHeight + 'px'
})

var modal = document.getElementById("taskModal")

var span = document.getElementsByClassName("close")[0]

span.onclick = function() {
    modal.style.display = "none"
}

window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none"
    }
}
function openModal(row) {
    var cells = row.getElementsByTagName("td")
    let dateStr = cells[0].innerText
    let timeStr = cells[1].innerText
    let dateParts = dateStr.split('/')
    let day = dateParts[1].padStart(2, '0')
    let month = dateParts[0].padStart(2, '0')
    let formattedDate = `${dateParts[2]}-${month}-${day}`
    console.log(`Formatted Date: ${formattedDate}`)
    let [time, modifier] = timeStr.split(' ')
    let [hours, minutes] = time.split(':')
    if (hours === '12') {
        hours = '00'
    }
    if (modifier === 'PM') {
        hours = parseInt(hours, 10) + 12
    }
    console.log(`Hours: ${hours}, Minutes: ${minutes}`)
    if (hours.length < 2) {
        hours = hours.padStart(2, '0')
    }
    if (minutes.length < 2) {
        minutes = minutes.padStart(2, '0')
    }
    let formattedTime = `${hours}:${minutes}`
    console.log(`Formatted Time: ${formattedTime}`)
    document.getElementById('task-date-update').value = formattedDate
    document.getElementById('task-time-update').value = formattedTime
    console.log(document.getElementById('task-time-update').value)
    document.getElementById('task-details-update').value = cells[2].innerText
    document.getElementById('task-repeating-update').value = cells[3].innerText
        
    modal.style.display = "block"
}

function saveTask() {
    const taskDetails = document.getElementById('task-details-update').value
    const taskDate = document.getElementById('task-date-update').value
    const taskTime =  document.getElementById('task-time-update').value
    const repeating = document.getElementById('task-repeating-update').value
    console.log('Updating Task')
    console.log(`Task Date: ${taskDate}, Task Time: ${taskTime}, Task Details: ${taskDetails}, Repetition: ${repeating}`)

    window.electron.updateTask(taskDate, taskTime, taskDetails, repeating)
    modal.style.display = "none"
    alert("Task Updated!")
}

function deleteTask() {
    const taskDetails = document.getElementById('task-details-update').value
    const taskDate = document.getElementById('task-date-update').value
    const taskTime =  document.getElementById('task-time-update').value
    const repeating = document.getElementById('task-repeating-update').value
    console.log('Deleting Task')
    console.log(`Task Date: ${taskDate}, Task Time: ${taskTime}, Task Details: ${taskDetails}, Repetition: ${repeating}`)

    window.electron.deleteTask(taskDate, taskTime, taskDetails, repeating)
    modal.style.display = "none"
    alert("Task Deleted!")
}