function toggleEmailBody(button) {
    const snippet = button.previousElementSibling.previousElementSibling;
    const fullText = button.previousElementSibling;
    if (fullText.style.display === 'none') {
        fullText.style.display = 'block';
        snippet.style.display = 'none';
        button.textContent = 'Collapse';
    } else {
        fullText.style.display = 'none';
        snippet.style.display = 'block';
        button.textContent = 'Expand';
    }
}
function switchModule(moduleId) {
    const modules = document.querySelectorAll('.module');
    modules.forEach(mod => mod.style.display = 'none');
    document.getElementById(moduleId).style.display = 'block';
    const links = document.querySelectorAll('.nav-link');
    links.forEach(link => link.classList.remove('active'));
    document.querySelector(`[onclick="switchModule('${moduleId}')"]`).classList.add('active');

    const selectedModule = document.getElementById(moduleId);
    const firstTabButton = selectedModule.querySelector('.tab-button');
    if (firstTabButton) {
        const firstTabId = firstTabButton.onclick.toString().match(/'([^']+)'/)[1];
        switchTab(firstTabId);
    }
}
function switchTab(tabId) {
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => tab.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => button.classList.remove('active')); 
    document.querySelector(`[onclick="switchTab('${tabId}')"]`).classList.add('active');
}
document.addEventListener("DOMContentLoaded", function() {
    getWeather();
    initWeatherWidget();
});
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

switchModule('chat');
switchTab('composeEmail');
switchTab('currentWeather');
switchTab('upcomingTasks');
switchTab('search');
switchTab('previousLaunches');
switchTab('historyTab');