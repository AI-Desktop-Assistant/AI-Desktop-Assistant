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
  signoutAndQuit: () => ipcRenderer.send('signout', true),
  sendEmail: (recipient, cc, subject, body) => ipcRenderer.send('send-email', recipient, cc, subject, body),
  fillUsername: () => ipcRenderer.send('fill-username'),
  fillEmail: () => ipcRenderer.send('fill-email'),
  onFillUsernameResponse: (callback) => ipcRenderer.on('fill-username-response', callback),
  onFillEmailResponse: (callback) => ipcRenderer.on('fill-email-response', callback),
  updateEmail: (newEmail) => ipcRenderer.send('update-email', newEmail),
  updateUsername: (username) => ipcRenderer.send('update-username', username),
  updateAppPassword: (appPassword) => ipcRenderer.send('update-app-password', appPassword),
  updatePassword: (password, confirmPassword) => ipcRenderer.send('update-password', password, confirmPassword),
  onUpdateInfoResponse: (callback) => ipcRenderer.on('update-info-response', callback)
})