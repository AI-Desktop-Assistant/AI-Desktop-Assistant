const { app, protocol, BrowserWindow, ipcMain, shell } = require('electron')
const sqlite3 = require('sqlite3').verbose()
const path = require('node:path')
const { spawn } = require('child_process')
const axios = require('axios')
const io = require('socket.io-client')
const { time } = require('node:console')

let spotifyToken

let win

const createWindow = () => {
    win = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            contextIsolation: true
        }
    })
    
    win.loadFile('index.html')

    const db = new sqlite3.Database(path.join(__dirname, 'users.db'), (err) => {
        const createUsersTable = () => {
            db.run("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, email TEXT DEFAULT '', app_password TEXT DEFAULT '', rememberme BOOLEAN DEFAULT FALSE, footer TEXT DEFAULT '')", (err) => {
                if (err) {
                    console.error(`Error creating user table: ${err.message}`)
                }
                else {
                    console.log('Successfully created users table')
                }
            });
            
        }
        const createSentEmailTable = () => {
            db.run("CREATE TABLE IF NOT EXISTS sent_emails (id INTEGER PRIMARY KEY, user_id INTEGER, subject TEXT, body TEXT, recipient TEXT, cc TEXT DEFAULT '', date TEXT, timestamp TEXT, FOREIGN KEY(user_id) REFERENCES users(id))", (err) => {
                if (err) {
                    console.error(`Error creating sent_emails table: ${err.message}`)
                }
                else {
                    console.log('Successfully created sent_emails table')
                }
            });
        }

        const createContactsTable = () => {
            db.run('CREATE TABLE IF NOT EXISTS contacts (id INTEGER PRIMARY KEY, user_id INTEGER, contact_name TEXT, contact_email TEXT, timestamp TEXT, FOREIGN KEY(user_id) REFERENCES users(id))', (err) => {
                if (err) {
                    console.error(`Error creating contacts table: ${err.message}`)
                }
                else {
                    console.log('Successfully created contacts table')
                }
            });
        }

        const createTaskTable = () => {
            db.run('CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, user_id INTEGER, date TEXT, time TEXT, task TEXT, repetition TEXT, FOREIGN KEY(user_id) REFERENCES users(id))', (err) => {
                if (err) {
                    console.error(`Error creating task table: ${err.message}`)
                }
                else {
                    console.log('Successfully created tasks table')
                }
            });
        }
        
        const createChatHistoryTable = () => {
            db.run('CREATE TABLE IF NOT EXISTS chat_history (id INTEGER PRIMARY KEY, user_id INTEGER, sender TEXT, message TEXT, timestamp TEXT, FOREIGN KEY(user_id) REFERENCES users(id))', (err) => {
                if (err) {
                    console.error(`Error creating chat history table: ${err.message}`)
                }
                else {
                    console.log('Successfully created chat_history table')
                }
            });
        }

        const createRememberedAppsTable = () => {
            db.run('CREATE TABLE IF NOT EXISTS remembered_apps (id INTEGER PRIMARY KEY, user_id INTEGER, app_name TEXT, app_path TEXT, timestamp TEXT, FOREIGN KEY(user_id) REFERENCES users(id))', (err) => {
                if (err) {
                    console.error(`Error creating chat history table: ${err.message}`)
                }
                else {
                    console.log('Successfully created remembered_apps table')
                }
            });
        }

        if (err) {
            console.error(`Error opening database: ${err.message}`);
        } else {
            createUsersTable()
            createSentEmailTable()
            createContactsTable()
            createTaskTable()
            createChatHistoryTable()
            createRememberedAppsTable()
        }
    })
    
    let mainPythonProcess = null

    function sendUpdateToPython(endpoint, data) {
        axios.post(`http://localhost:8888/${endpoint}`, data)
            .then(response => {
                console.log(response.data.message);
            })
            .catch(error => {
                console.error(`Error updating ${endpoint}: ${error.message}`);
            });
    }

    // save current user
    let currentUsername = null
    let currentUserId = null
    // Validate input user account details
    ipcMain.on('login', (event, username, password, rememberMe, autoLogin) => {
        console.log('testing credentials')
        // Query username and password to check if user is signed up
        db.get('SELECT * FROM users WHERE username = ? AND password = ?', [username, password], (err, row) => {
            // if an error occured with the query
            if (err) {
                // Output error and send failure and error message to renderer process
                console.error(`Error querying database: ${err.message}`)
                event.reply('login-response', { success: false, message: 'Error querying database' })
            }
            // if username and password are present
            else if (row) {
                console.log('credentials valid')
                // send success and user details back to renderer
                event.reply('login-response', { success: true, message: 'Login Successful', rememberMe, username, password, autoLogin, userId: row.id })
                currentUsername = username
                currentUserId = row.id
                if (!mainPythonProcess){
                    // console.log('starting python process')
                    const main = path.join(__dirname, 'main.py')
                    
                    mainPythonProcess = spawn('python', ['-u', main, row.id, username, row.email])

                    mainPythonProcess.stdout.on('data', (data) => {
                        console.log(`Python stdout: ${data}`)
                    })
                    
                    mainPythonProcess.stderr.on('data', (data) => {
                        // console.error(`Python stderr: ${data}`)
                    })

                    mainPythonProcess.on('close', (code) => {
                        console.log(`Python process exited with code ${code}`)
                        mainPythonProcess = null
                    })
                }
            }
            // if user and password were not found
            else {
                // send failer and invalid credentials to renderer process
                event.reply('login-response', { success: false, message: 'Username and/or Password are invalid' })
            }
        })
    })
    
    // Remember user login
    ipcMain.on('set-rem-user', (event) => {
        // set rememberme status to true
        console.log(`Remembering: ${currentUsername}`)
        db.run('UPDATE users SET rememberme = ? WHERE username = ?', [true, currentUsername], (err) => {
            // output error setting rememberme status
            if (err) {
                console.error(`Error updating Remember Me Status: ${err.message}`)
            }
        })
    })

    // check for a remembered user
    ipcMain.on('get-rem-user', (event) => {
        // Query db for a remembered user details
        db.get('SELECT * FROM users WHERE rememberme = TRUE', (err, row) => {
            // if error occured with query
            if (err) {
                // output error with query and send failure and error message to renderer process
                console.error('Error querying database:', err.message);
                event.reply('rem-user-response', { success: false, message: 'Error querying database' })
            } 
            // if a remembered user exists
            else if (row){
                // send success and user details to renderer process
                event.reply('rem-user-response', { success: true, username: row.username, password: row.password })
            } 
            //if no remembered users exists
            else {
                // send failure and failure message to renderer process
                event.reply('rem-user-response', { success: false, message: 'No Remembered Users' })
            }
        })        
    })
    
    ipcMain.on('fill-username', (event) => {
        event.reply('fill-username-response', { username: currentUsername })
    })

    ipcMain.on('fill-email', (event) => {
        db.get('SELECT * FROM users WHERE rememberme = TRUE', (err, row) => {
            if (err) {
                // output error with query and send failure and error message to renderer process
                console.error('Error querying database:', err.message);
                event.reply('fill-email-response', { success: false, message: 'Error querying database' })
            } 
            else if (row){
                // send success and user details to renderer process
                event.reply('fill-email-response', { success: true, email: row.email })
            } 
            else {
                // send failure and failure message to renderer process
                event.reply('fill-email-response', { success: false, message: 'No Remembered Users' })
            }
        })        
    })

    ipcMain.on('fill-app-pass', (event) => {
        console.log('Querying app password')
        db.get('SELECT * FROM users WHERE username = ?', [currentUsername], (err, row) => {
            if (err) {
                console.log(`Error Querying Database: ${err}`)
                event.reply('fill-app-pass-response', { success: false })
            }
            else {
                const app_password = row.app_password
                console.log(`found app pass: ${app_password.trim().length !== 0}`)
                event.reply('fill-app-pass-response', { success: true, app_password: app_password.trim().length !== 0 })
            }
        })
    })

    ipcMain.on('fill-sent-emails', (event) => {
        console.log('filling Sent Emails')
        db.all('SELECT * FROM sent_emails WHERE user_id = ?', [currentUserId], (err, rows) => {
            if (err) {
                console.log(`Error Querying Database: ${err}`)
                win.webContents.send('fill-sent-emails-response', { success: false })
            }
            else {
                console.log(`Rows Queried: ${rows}`)
                if (rows.length > 0) {
                    // Initialize arrays for each column
                    const subjects = []
                    const bodies = []
                    const recipients = []
                    const ccs = []
                    const bccs = []
                    const timestamps = []
        
                    // Populate arrays with data from each row
                    rows.forEach(row => {
                        subjects.push(row.subject)
                        bodies.push(row.body)
                        recipients.push(row.recipient)
                        ccs.push(row.cc)
                        bccs.push(row.bcc)
                        timestamps.push(row.timestamp)
                    })
        
                    // Send the arrays back to the renderer process
                    event.reply('fill-sent-emails-response', {success: true, subjects: subjects, bodies: bodies, recipients: recipients, ccs: ccs, bccs: bccs, timestamps: timestamps})
                } else {
                    event.reply('fill-sent-emails-response', { success: false})
                }
            }
        })
        console.log('Querying Contacts')
        db.all('SELECT * FROM contacts WHERE user_id = ?', [currentUserId], (err, rows) => {
            if (err) {
                console.log(`Error Querying Database: ${err}`)
                win.webContents.send('fill-contacts-response', { success: false })
            }
            else {
                console.log(`Rows Queried: ${rows}`)
                if (rows.length > 0) {
                    // Initialize arrays for each column
                    const contactNames = []
                    const contactEmails = []
                    const timestamps = []
        
                    // Populate arrays with data from each row
                    rows.forEach(row => {
                        contactNames.push(row.contact_name)
                        contactEmails.push(row.contact_email)
                        timestamps.push(row.timestamp)
                    })
        
                    // Send the arrays back to the renderer process
                    event.reply('fill-contacts-response', {success: true, contactNames: contactNames, contactEmails: contactEmails, timestamps: timestamps})
                } else {
                    event.reply('fill-contacts-response', { success: false})
                }
            }
        })
    })

    ipcMain.on('fill-tasks', (event) => {
        console.log('Getting All Tasks')
        db.all('SELECT * FROM tasks WHERE user_id = ? ORDER BY date, time', [currentUserId], (err, rows) => {
            if (err) {
                console.log(`Error Querying Database: ${err}`)
                event.reply('fill-tasks-response', { success: false })
            }
            else {
                console.log(`Rows Queried: ${rows}`)
                if (rows.length > 0) {
                    // Initialize arrays for each column
                    const dates = []
                    const times = []
                    const tasks = []
                    const repeatings = []
        
                    // Populate arrays with data from each row
                    rows.forEach(row => {
                        dates.push(row.date)
                        times.push(row.time)
                        tasks.push(row.task)
                        repeatings.push(row.repetion)
                    })
                    // Send the arrays back to the renderer process
                    event.reply('fill-tasks-response', { success: true, dates: dates, times: times, tasks: tasks, repeatings: repeatings })
                } else {
                    event.reply('fill-tasks-response', { success: false })
                }
            }
        })
    })

    ipcMain.on('fill-app-paths', (event) => {
        console.log('Getting all app paths')
        db.all('SELECT * FROM remembered_apps WHERE user_id = ?', [currentUserId], (err, rows) => {
            if (err) {
                console.log(`Error Querying Database: ${err}`)
                event.reply('fill-app-paths-response', { success: false })
            }
            else {
                console.log(`Rows Queried: ${rows}`)
                if (rows.length > 0) {
                    // Initialize arrays for each column
                    const appNames = []
                    const appPaths = []
        
                    // Populate arrays with data from each row
                    rows.forEach(row => {
                        appNames.push(row.app_name)
                        appPaths.push(row.app_path)
                    })
        
                    // Send the arrays back to the renderer process
                    event.reply('fill-app-paths-response', {success: true, appNames: appNames, appPaths: appPaths})
                } else {
                    event.reply('fill-app-paths-response', { success: false})
                }
            }
        })
    })

    // Add user to database
    ipcMain.on('signup', (event, username, password, confirmPassword) => {
        console.log(`Attempting to sign up username: ${username} password: ${password}`)
        if (username.trim().length === 0 || username.includes(' ')) {
            event.reply('signup-response', { success: false, message: 'Username must not be empty or contain spaces' })
        } 
        else if (password.trim().length === 0 ||  password.includes(' ')) {
            event.reply('signup-response', { success: false, message: 'Password must not be empty or contain spaces' })
        }
        else if (password !== confirmPassword) {
            event.reply('signup-response', { success: false, message: "Passwords don't match." })
        }
        else {
            // attempt to add username and password and initialize rememberme as 0
            db.run('INSERT INTO users (username, password) VALUES (?, ?)', [username, password], (err) => {
                // if an error occured with the insertion
                if (err) {
                    // if user name exists
                    if (err.message.includes('UNIQUE constraint failed')) {
                        // send failure and error message to renderer process
                        event.reply('signup-response', { success: false, message: 'Username already exists' })
                    } 
                    // if other error inserting
                    else {
                        // output error and send failure and error message to renderer process
                        console.error('Error inserting into database:', err.message)
                        event.reply('signup-response', { success: false, message: 'Error inserting into database' })
                    }
                } 
                // if user was successfully added to db
                else {
                    // send success to renderer process
                    event.reply('signup-response', { success: true, message: 'Sign-up successful! Please log in.' })
                }
            })
        }
    })

    ipcMain.on('signout', (event, quit) => {
        console.log('Updating user rememberme status')
        db.run(
            `UPDATE users SET rememberme = FALSE WHERE username = ?`, [currentUsername], (err) => {
                if (err) {
                    console.log(`Failed to set rememberme to false: ${err.message}`)
                }
                else {
                    if (quit) {
                        app.quit()
                    }
                    else {
                        event.reply('signout-response')
                    }
                }
            }
        )
    })

    ipcMain.on('update-email', (event, newEmail) => {
        emailValid = false
        if (newEmail.endsWith('@gmail.com')) {
            emailValid = true
        }

        if (emailValid) {
            db.run(
                `UPDATE users SET email = ? WHERE username = ?`, [newEmail, currentUsername], (err) => {
                    if (err) {
                        event.reply('update-info-response', { success: false, section: 'email', message: `Failed to set rememberme to false: ${err.message}` })
                    }
                    else {
                        event.reply('update-info-response', { success: true, section: 'email', message: 'Email Successfuly Updated!' })
                        sendUpdateToPython('update_email', { email: newEmail });
                    }
                }
            )
        }
        else {
            event.reply('update-info-response', { success: false, section: 'email', message: 'Enter a Google email' })
        }
    })

    ipcMain.on('update-signature', (event, signature) => {
        console.log('Attempting signature update')
        if (signature.trim().length === 0) {
            console.log('update failed')
            event.reply('update-info-response', { success: false, section: 'signature', message: 'Signature must not be empty' })
        }
        else {
            console.log('signature syntax valid')
            db.run(`UPDATE users SET footer = ? WHERE username = ?`, [signature, currentUsername], (err) => {
                if (err) {
                    console.log('Error updating signature')
                    event.reply('update-info-response', { success: false, section: 'signature', message: 'Error updating signature' })
                } 
                // if user was successfully added to db
                else {
                    console.log('successfully updated signature')
                    // send success to renderer process
                    event.reply('update-info-response', { success: true, section: 'signature', message: 'Signature Successfully Updated!' })
                }
            })
        }
    })

    ipcMain.on('update-username', (event, username) => {
        console.log('Attempting username update')
        if (username.trim().length === 0 || username.includes(' ')) {
            console.log('update failed')
            event.reply('update-info-response', { success: false, section: 'username', message: 'Username must not be empty or contain spaces' })
        }
        else {
            console.log('username syntax valid')
            db.run(
                `UPDATE users SET username = ? WHERE username = ?`, [username, currentUsername], (err) => {
                    if (err) {
                        // if user name exists
                        if (err.message.includes('UNIQUE constraint failed')) {
                            console.log('Username exists')
                            // send failure and error message to renderer process
                            event.reply('update-info-response', { success: false, section: 'username', message: 'Username already exists' })
                        } 
                        // if other error inserting
                        else {
                            console.log('Other error')
                            // output error and send failure and error message to renderer process
                            console.error('Error inserting into database:', err.message)
                            event.reply('update-info-response', { success: false, section: 'username', message: 'Error inserting into database' })
                        }
                    } 
                    // if user was successfully added to db
                    else {
                        console.log('successfully updated username')
                        // send success to renderer process
                        event.reply('update-info-response', { success: true, section: 'username', message: 'Username Successfully Updated!' })
                        currentUsername = username
                        sendUpdateToPython('update_username', { username });
                    }
                }
            )
        }
    })

    ipcMain.on('update-app-password', (event, appPassword) => {
        console.log('Attempting update app password')
        db.run(
            `UPDATE users SET app_password = ? WHERE username = ?`, [appPassword, currentUsername], (err) => {
                if (err) {
                    // output error and send failure and error message to renderer process
                    console.error('Error inserting into database:', err.message)
                    event.reply('update-info-response', { success: false, section: 'app-password', message: 'Error inserting into database' })
                } 
                // if user was successfully added to db
                else {
                    console.log('successfully updated app password')
                    // send success to renderer process
                    event.reply('update-info-response', { success: true, section: 'app-password', message: 'App Password Successfully Set!' })
                }
            }
        )
    })

    ipcMain.on('update-password', (event, password, confirmPassword) => {
        console.log(`Pass: ${password}, Conf: ${confirmPassword}`)
        if (password.trim().length === 0 ||  password.includes(' ')) {
            console.log('Empty Password')
            event.reply('update-info-response', { success: false, section: 'password', message: 'Password must not be empty or contain spaces' })
        }
        else if (password !== confirmPassword) {
            console.log('Passwords not equal')
            event.reply('update-info-response', { success: false, section: 'password', message: "Passwords don't match." })
        }
        else {
            console.log('Password valid')
            db.run(
                `UPDATE users SET password = ? WHERE username = ?`, [password, currentUsername], (err) => {
                    if (err) {
                        // output error and send failure and error message to renderer process
                        console.error('Error inserting into database:', err.message)
                        event.reply('update-info-response', { success: false, section: 'password', message: 'Error inserting into database' })
                    } 
                    // if user was successfully added to db
                    else {
                        console.log('successfully updated password')
                        // send success to renderer process
                        event.reply('update-info-response', { success: true, section: 'password', message: 'Password Successfully Set!' })
                    }
                }
            )
        }
        console.log('Replied to event')
    })

    ipcMain.on('update-volume', (event, newVolume) => {
        db.run(
            `UPDATE users SET email = ? WHERE username = ?`, [newVolume, currentUsername], (err) => {
                if (err) {
                    event.reply('update-info-response', { success: false, section: 'email', message: `Failed to set rememberme to false: ${err.message}` })
                }
                else {
                    event.reply('update-info-response', { success: true, section: 'email', message: 'Email Successfuly Updated!' })
                    sendUpdateToPython('update_volume', { email: newEmail });
                }
            }
        )        
    })

    ipcMain.on('update-voice', (event, newVoice) => {
        db.run(
            `UPDATE users SET voice = ? WHERE username = ?`, [newEmail, currentUsername], (err) => {
                if (err) {
                    event.reply('update-info-response', { success: false, section: 'email', message: `Failed to set rememberme to false: ${err.message}` })
                }
                else {
                    event.reply('update-info-response', { success: true, section: 'email', message: 'Email Successfuly Updated!' })
                    sendUpdateToPython('update_email', { email: newEmail });
                }
            }
        )
        
        event.reply('update-info-response', { success: false, section: 'email', message: 'Enter a Google email' })
        
    })    

    ipcMain.on('send-email', (event, recipients, cc, bcc, subject, body) => {
        console.log('Attempting Send Email')
        // Query users email
        db.get('SELECT * FROM users WHERE id = ?', [currentUserId], (err, row) => {
            if (err) {
                console.log(`Error Querying Database: ${err}`)
            }
            else {
                appPassword = row.app_password
                email = row.email
                console.log(`Query Successful: ${appPassword.trim().length !== 0} App Password: ${appPassword} Trimmed Pass: ${appPassword.trim()}`)

                if (appPassword.trim().length === 0) {
                    event.reply('send-email-response', {success: false, message: 'App Password Not Set'})
                }
                else {
                    socket.emit('message', {purpose: 'email', email, appPassword, recipients, cc, bcc, subject, body})
                    event.reply('send-email-response', {success: true, message: 'Email Successfully Sent'})
                }
            }
        })
    })
}

app.whenReady().then(() => {
    createWindow()
    
    socket = io('http://localhost:8888')

    socket.on('connect', () => {
        console.log('Connected to Flask-SocketIO server')
    })

    socket.on('disconnect', () => {
        console.log('Disconnected from Flask-SocketIO server')
    })

    socket.on('response', (data) => {
        console.log('Received response from server:', data)
        purpose = data.purpose
        if (purpose === 'show-email') {
            if (win.isMinimized()) {
                win.restore()
            }
            win.focus()
            win.webContents.send('to-renderer', data)
        } else if (purpose === 'search') {
            if (win.isMinimized()) {
                win.restore()
            }
            // console.log('Sending data to renderer');
            win.focus()
            win.webContents.send('to-renderer', data)
        } else if (purpose === 'get-token') {
            if (win.isMinimized()) {
                win.restore()
            }
            win.focus()
            openSpotifyLogin(data.data)
        } else if (purpose == 'chat-assistant') {
            win.webContents.send('chat-assistant', data.data)
        } else if (purpose == 'chat-user') {
            win.webContents.send('chat-user', data.data)
        } else if (purpose == 'sent-email') {
            win.webContents.send('req-fill-sent-emails')
        } else if (purpose == 'added-path') {
            win.webContents.send('req-fill-app-paths')
        } else if (purpose == 'updated-task') {
            win.webContents.send('req-fill-tasks')
        }

    })
    socket.on('get-weather', (data) => {
        // console.log("Received weather response from Flask:", data);
        if (win.isMinimized()) {
            win.restore();
        }
        win.focus();
        win.webContents.send("get-weather", data);
    });
    socket.on('get-currently-playing-response', (data) => {
        // console.log("Received currently playing response from Flask:", data);
        if (win.isMinimized()) {
            win.restore();
        }
        win.focus();
        win.webContents.send("get-currently-playing-response", data);
    });

    socket.on('control-playback-response', (data) => {
        // console.log('Playback control response:', data);
    });    

    ipcMain.on('send-message', (event, message) => {
        // console.log("Sending message............:", message.purpose);
        socket.emit('message', message)
    })

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) createWindow()
    })
})

ipcMain.on('get-weather-response', (event, weatherData) => {
    try {
        console.log("Received weather response: ", weatherData)
        socket.emit('message', weatherData)
    } catch (error) {
        console.error('Error in get-weather handler:', error);
        throw error; // rethrow the error to send it to the renderer
    }
})

ipcMain.handle('get-currently-playing', async (event) => {
    try {
        const trackInfo = spotify.get_currently_playing_track(spotifyToken);
        return trackInfo;
    } catch (error) {
        console.error('Error in get-currently-playing handler:', error);
        throw error; // rethrow the error to send it to the renderer
    }
});

ipcMain.handle('fetch-playlists', async () => {
    try {
        const response = await axios.post('http://localhost:8888/get_playlists');
        return response.data.playlists;
    } catch (error) {
        console.error('Error fetching playlists:', error);
        return [];
    }
})

ipcMain.handle('start-playback', async (event, uri, uriType) => {
    try {
        const response = await axios.post('http://localhost:8888/start_playback', { uri: uri, uri_type: uriType });
        return response.data.message;
    } catch (error) {
        console.error('Error starting playback:', error);
        return 'Error starting playback';
    }
});

ipcMain.handle('search-track', async (event, trackName) => {
    try {
        const response = await axios.post('http://localhost:8888/search', { data: trackName, purpose: 'search' });
        return response.data;
    } catch (error) {
        console.error('Error searching track:', error);
        return { error: 'Error searching track' };
    }
});

function openSpotifyLogin(auth_url) {
    shell.openExternal(auth_url);
}

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit()
})