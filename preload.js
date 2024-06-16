const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electron', {
  login: (username, password, rememberMe, autoLogin) => ipcRenderer.send('login', username, password, rememberMe, autoLogin),
  onLoginResponse: (callback) => ipcRenderer.on('login-response', callback),
  setRemUser: () => ipcRenderer.send('set-rem-user'),
  getRemUser: () => ipcRenderer.send('get-rem-user'),
  onGetRemUserResponse: (callback) => ipcRenderer.on('rem-user-response', callback),
  signup: (username, password, confirmPassword) => ipcRenderer.send('signup', username, password, confirmPassword),
  onSignupResponse: (callback) => ipcRenderer.on('signup-response', callback),
  signout: () => ipcRenderer.send('signout', false),
  signoutAndQuit: () => ipcRenderer.send('signout', true)
})