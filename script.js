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
    modules.forEach(mod => mod.style.display = 'none'); // Hide all modules
    document.getElementById(moduleId).style.display = 'block'; // Show the selected module
    const links = document.querySelectorAll('.nav-link');
    links.forEach(link => link.classList.remove('active')); // Remove active class from all links
    document.querySelector(`[onclick="switchModule('${moduleId}')"]`).classList.add('active'); // Set active class on selected link

    const firstTabButton = selectedModule.querySelector('.tab-button');
    if (firstTabButton) {
        const firstTabId = firstTabButton.onclick.toString().match(/'([^']+)'/)[1]; // Extract the tab ID from the onclick attribute
        switchTab(firstTabId);
    }
}
function switchTab(tabId) {
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => tab.classList.remove('active')); // Hide all tabs
    document.getElementById(tabId).classList.add('active'); // Show the selected tab
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => button.classList.remove('active')); // Remove active class from all tab buttons
    document.querySelector(`[onclick="switchTab('${tabId}')"]`).classList.add('active'); // Set active class on selected tab button
}
// Initialize the chat module and first tabs as visible
switchModule('chat');
switchTab('composeEmail');
switchTab('currentWeather');
switchTab('upcomingTasks');
switchTab('search');
switchTab('previousLaunches');
switchTab('historyTab');