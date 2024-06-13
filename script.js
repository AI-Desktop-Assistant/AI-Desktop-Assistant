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

switchModule('chat');
switchTab('composeEmail');
switchTab('currentWeather');
switchTab('upcomingTasks');
switchTab('search');
switchTab('previousLaunches');
switchTab('historyTab');