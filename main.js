const { app, BrowserWindow, ipcMain } = require('electron')
const sqlite3 = require('sqlite3').verbose()
const path = require('node:path')

const createWindow = () => {
    const win = new BrowserWindow({
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
            db.run('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, rememberme BOOLEAN DEFAULT FALSE)', (err) => {
                if (err) {
                    console.error(`Error creating user table: ${err.message}`)
                }
                else {
                    console.log('Successfully created users table')
                }
            });
        }
        
        const createSentEmailTable = () => {
            db.run('CREATE TABLE IF NOT EXISTS sent_emails (id INTEGER PRIMARY KEY, user_id INTEGER, subject TEXT, body TEXT, recipient TEXT, date TEXT, timestamp TEXT, FOREIGN KEY(user_id) REFERENCES users(id))', (err) => {
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
    });

    let currentUsername = null

    // Validate input user account details
    ipcMain.on('login', (event, username, password, rememberMe, autoLogin) => {
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
                // send success and user details back to renderer
                event.reply('login-response', { success: true, message: 'Login Successful', rememberMe, username, password, autoLogin })
                currentUsername = username
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
}

app.whenReady().then(() => {
    createWindow()
    
    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) createWindow()
    })
})

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit()
})
