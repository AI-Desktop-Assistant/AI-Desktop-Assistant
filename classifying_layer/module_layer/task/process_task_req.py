from nltk.corpus import wordnet as wn
from classifying_layer.module_layer.task.dates_and_times import *
from classifying_layer.module_layer.response.response import *
from models.load_model import load_model
from classifying_layer.module_layer.handle_confirmation import get_y_or_n
from scipy.spatial.distance import cosine
from user_config import *
import torch
import sqlite3
import time

db_path = 'users.db'
req_model, tokenizer, device = load_model('models\\task_req_classification_model.pth')
task_intent_model, tokenizer, device = load_model('models\\task_intent_model.pth')
bert_model, tokenizer, device = load_model('bert') 
reminded_task = ''
remind_two_hours = ''
remind_thirty_mins = ''
remind_on_time = ''
check_tasks = True

def get_tasks_within_date_range(start_date, end_date):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        user_id = get_user_id()
        cursor.execute("SELECT * FROM tasks WHERE user_id = ? AND date BETWEEN ? AND ? ORDER BY date, time", (user_id, start_date, end_date))

        tasks = cursor.fetchall()

        return tasks

def update_task_complete(task_purpose):
    with sqlite3.connect('users.db') as conn:
        query = 'UPDATE tasks SET complete = ? WHERE user_id = ? AND task = ?'
        user_id = get_user_id()
        conn.execute(query, (True, user_id, task_purpose))
        conn.commit()

def complete_task(intent):
    task, confidence = get_task_intent(intent)
    update_task_complete(task[4])
    

# handle mark req
def handle_mark(req, intent):
    # find task to be marked and mark as complete
    complete_task(intent)
    
def update_task(task_purpose, date, time, day_repeat):
    print('Updating task')
    task_updated = False
    rows_to_update = ''
    values = []
    
    if date != '':
        print(f'Appending Date to values: {date}')
        rows_to_update += 'date = ?, '
        values.append(date)
    if time != '':
        print(f'Appending Time to values: {time}')
        rows_to_update += 'time = ?, '
        values.append(time)
    if day_repeat != '':
        print(f'Appending Day Repeat to values: {day_repeat}')
        rows_to_update += 'repetition = ? '
        values.append(day_repeat)
    print('Checking update rows_to_update string')
    if rows_to_update.endswith(', '):
        rows_to_update = rows_to_update[:-2]
        print(f'Updated Rows To Update')
    print(f'Rows To Update: {rows_to_update}')
    user_id = get_user_id()
    values.append(user_id)
    values.append(task_purpose)
    print(f'Values: {values}')
    if rows_to_update != '':
        with sqlite3.connect('users.db') as conn:
            query = f'UPDATE tasks SET {rows_to_update} WHERE user_id = ? AND task = ?'
            print(f'Query: {query}')
            conn.execute(query, values)
            conn.commit()
            task_updated = True
        socket = get_app_socket()[1]
        socket.emit('response', {'purpose': 'updated-task'})
    return task_updated, rows_to_update, values

def output_task_updated(intent, rows_to_update, values):
    response = f'I have updated your task {intent_as_response(intent)} '

    if 'date' in rows_to_update:
        response += f'to {date_to_response(values[0])} '
        for value in values:
            time = value.split(':')
            if len(time) == 2:
                response += f'at {value} '
                break
    elif 'time' in rows_to_update:
        for value in values:
            time = value.split(':')
            if len(time) == 2:
                response += f'to {value} '
                break
    if 'repetition' in rows_to_update:
        response += f'every {values[-1]}'
    output_tasks_to_user(response)

def handle_updating_task(intent, date, time, is_am, day_repeat):
    print('Attempting Update Task')
    task, confidence = get_task_intent(intent)
    print(f'Got task: {task}, Confidence: {confidence}')
    if date != '':
        date_str = f'{date.month}/{date.day}/{date.year}'
    else:
        date_str = ''
    time_str = time_to_string(time, is_am)[0]
    task_intent = task[4]
    task_updated, rows_to_update, values = update_task(task_intent, date_str, time_str, day_repeat)
    output_task_updated(intent, rows_to_update, values)
    refresh_next_task_list()
    

# handle move req
def handle_move(req, intent):
    # parse updated time for task
    tf = get_date_and_time_from_req(req)
    # interpret time from user
    date, time, day_repeat, is_am = interpret_time(tf)
    print(f'Retrieved time information: date: {date}, time: {time}, day_repeat: {day_repeat}, is_am: {is_am}')
    # handle updating task
    handle_updating_task(intent, date, time, is_am, day_repeat)
    

def predict_class_tokens(req, model):
    labels_to_index = {'query': 0, 'set': 1, 'update': 2}
    tokenized_input = tokenizer([req], padding=True, truncation=True, return_tensors="pt")
    
    input_ids = tokenized_input['input_ids'].to(device)
    attention_mask = tokenized_input['attention_mask'].to(device)

    with torch.no_grad():
        outputs = model(input_ids, attention_mask)
    
    logits = outputs.logits
    predicted_label_id = torch.argmax(logits, dim=1)
    
    for label, idx in labels_to_index.items():
        if predicted_label_id == idx:
            predicted_category = label
        
    return predicted_category

def predict_ner_tokens(req, model):
    tokenized_input = tokenizer([req], truncation=True, padding='max_length', is_split_into_words=True, return_tensors="pt")

    input_ids = tokenized_input['input_ids'].to(device)
    attention_mask = tokenized_input['attention_mask'].to(device)
    
    outputs = model(input_ids, attention_mask)

    logits = outputs.logits
    predicted_token_class_ids = logits.argmax(-1)

    tokens = tokenizer.convert_ids_to_tokens(input_ids.squeeze().tolist())
    predicted_tokens_classes = [model.config.id2label[t.item()] for t in predicted_token_class_ids[0]]

    return tokens, predicted_tokens_classes

def classify_request(req):
    req_model.eval()      

    predicted_category = predict_class_tokens(req, req_model)

    return predicted_category

def get_intent_tokens(tokens, predicted_token_classes):
    prediction = []
    for token, predicted_token_class in zip(tokens, predicted_token_classes):
        if predicted_token_class != 'LABEL_0' and token != '[CLS]' and token != '[PAD]' and token != '[SEP]':
            if token.startswith('##'):
                prediction[-1] += token
            else:
                prediction.append(token)
    return prediction

def get_intent(req):
    task_intent_model.eval()
    tokens, predicted_token_classes = predict_ner_tokens(req, task_intent_model)
    predicted_tokens = get_intent_tokens(tokens, predicted_token_classes)
    if len(predicted_tokens) == 0:
        intent = ''
    else:
        intent = ' '.join(predicted_tokens)

    return intent

def interpret_time(time):
    print(f'Interpretting Time: {time}')
    task_date = ''
    task_time = ''
    day_repeat = ''
    is_am = False
    if time == None:
        return task_date, task_time, day_repeat, is_am
    num = time['num']
    time_spec = time['time']
    day = time['day']
    repeat = time['repeat']
    print(f'Num: {num}')
    print(f'Time Spec: {time_spec}')
    print(f'Day: {day}')
    print(f'Repeat: {repeat}')
    if num != -1:
        if time['month'] != '' and num <= 31:
            task_date = get_date_by_month_and_num(time['month'], num)[1]
            print('Num, Month')
        elif time['days']:
            task_date = get_start_end_today_to_x_days(num)[1]
            print('Num, Days')
        elif time['weeks']:
            task_date = get_start_end_today_to_x_weeks(num)[1]
            print('Num, weeks')
        elif time['months']:
            task_date = get_start_end_today_to_x_months(num)[1]
            print('Num, Months')
        elif time['years']:
            task_date = get_start_end_today_to_x_years(num if num != -1 else 1)[1]
            print('Num, Years')
    elif day != '':
        print(f'Day: {day}, Next: {time["next"]}')
        task_date = get_dates_by_day_name(day, next=time.get('next'))
        if repeat:
            print(f'Day Repeat: {day_repeat}')
            day_repeat = day
    print(f'Task Date: {task_date}')

    if time_spec != '':
        print(f'Getting Time From Spec: {time_spec}')
        task_time, is_am = get_time_from_spec(time_spec, time['am'], time['pm'])
    elif time['hours'] and time['minutes']:
        print(f'Getting time from hours and minutes: {time["hours"]}, {time["minutes"]}')
        task_time = get_time_now_to_x_minutes_and_x_hours(time['hours'], time['minutes'])[1]
        is_am = True if task_time.hour >=0 and task_time.hour < 12 else False
    elif time['hours']:
        print(f'Getting time from hours: {time["hours"]}')
        task_time = get_time_now_to_x_hours(time['hours'])[1]
        is_am = True if task_time.hour >=0 and time.hour < 12 else False
        print('Num, Hours')
    elif time['minutes']:
        print(f'Getting time from minutes: {time["minutes"]}')
        task_time = get_time_now_to_x_minutes(time['minutes'])[1]
        
        print('Num, Minutes')
    print(f'Task Time: {task_time}\n')

    return task_date, task_time, day_repeat, is_am

def get_date_and_time_from_req(req):
    tf_item = {'num': -1, 'day': '', 'month': '', 'time': '', 'am': '', 'pm': '', 'next': False, 'years': False, 'months': False, 'weeks': False, 'days': False, 'hours': False, 'minutes': False, 'seconds': False, 'weekend': False, 'repeat': False}
    tf_item_copy = tf_item.copy()
    months_kw = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'november', 'december']
    dow_kw = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
    time_kw = ['minute', 'minutes', 'hour', 'hours', 'day', 'days', 'week', 'weeks', 'month', 'months', 'year', 'years']
    am_kw = ['morning', 'a.m.']
    repeat_kw = ['every', 'routine']
    pm_kw = ['noon', 'afternoon', 'evening', 'night', 'p.m.']
    rel_kw = ['today', 'tomorrow', 'yesterday']
    words = req.split()
    for word in words:
        if word.isdigit():
            print(f'Adding to num: {word}')
            tf_item['num'] = int(word)
        elif word in months_kw:
            print(f'Adding to month: {word}')
            tf_item['month'] = word
        elif word in dow_kw or word in rel_kw:
            print(f'Adding to day: {word}')
            tf_item['day'] = word
        elif word in time_kw:
            key = word
            if not key.endswith('s'):
                key += 's'
            print(f'Setting tf[{key}] to true')
            word_idx = words.index(word)
            time_idx = word_idx -1 
            time_num = words[time_idx-3] if 'and a half' in req else float(words[time_idx - 2] + (words[time_idx].split('/')[0]/words[time_idx].split('/')[1])) if len(words[time_idx].split('/')) == 2 and words[time_idx].split('/')[0].isdigit() and words[time_idx].split('/')[1].isdigit() and words[time_idx - 2].isdigit() else words[time_idx]

            if time_idx > 0:
                tf_item[key] = int(time_num) if time_num.isdigit() else 1 if time_num == 'an' else 0.5 if time_num == 'half' else True
                if 'and a half' in req:
                    tf_item['minutes'] = 30
        elif word in am_kw:
            print(f'Adding to am: {word}')
            tf_item['am'] = word
        elif word in pm_kw:
            print(f'Adding to pm: {word}')
            tf_item['pm'] = word
        elif ':' in word:
            time = word.split(':')
            print(f'Found potential time: {time}')
            if time[0].isdigit() and time[1].isdigit():
                if int(time[0]) >= 0 and int(time[1]) >= 0:
                    if int(time[0]) <= 12 and int(time[1]) <= 60:
                        try:                    
                            if 'from' not in words[words.index(word) - 1] and 'instead' not in words[words.index(word) - 2]:
                                print(f'Adding to time: {word}')
                                tf_item['time'] = word
                        except:
                            tf_item['time'] = word
        elif word == 'next':
            print(f'Found next')
            tf_item['next'] = True
        elif word in repeat_kw:
            print('Found repeat')
            tf_item['repeat'] = True
    print(f'Time Frame: {tf_item}')
    print(f'Time Frame Copy : {tf_item_copy}')
    return tf_item

def validate_date(date):
    val_date = False
    if date != '':
        val_date = True
    return val_date

def validate_time(time):
    val_time = False
    if time != '':
        val_time = True
    return val_time

def validate_date_and_time(date, time):
    val_date = validate_date(date)
    val_time = validate_time(time)
    return val_date, val_time

def handle_missing_info(task_date, task_time, val_date, val_time, chances=3):
    print('Handling missing info')
    new_chances = chances - 1
    missing_info = {}
    if chances == 0:
        return missing_info
    response = prompt_for_missing_date_or_time(val_date, val_time)

    if response == 'Sorry, I didn\'t understand your request':
        alert_not_understood()
        handle_missing_info(task_date, task_time, val_date, val_time, chances=new_chances)
    else:
        print('Processing Response')
        tf = get_date_and_time_from_req(response)
        task_date, task_time, day_repeat, is_am = interpret_time(tf)
        print(f'Task Date: {task_date}, Task Time: {task_time}, Reapeating Day: {day_repeat}')
        new_val_date = True
        new_val_time = True
        print('Checking Inputs Valid')
        if not val_time:
            new_val_date, new_val_time = validate_date_and_time(task_date, task_time)
            print(f'New Val Date: {new_val_date}, New Val Time: {new_val_time}')
            if not new_val_time:
                print('Not Val Time')
                handle_missing_info(task_date, task_time, new_val_date, new_val_time, chances=new_chances)
            else:
                print('Setting missing information')
                missing_info['date'] = task_date
                missing_info['time'] = task_time
                print(f'Missing Information: {missing_info}')
        # elif not val_date:
        #     new_val_date = validate_date(task_date)
        #     if not new_val_date:
        #         handle_missing_info(new_val_date, val_time, chances=new_chances)
        #     else:
        #         missing_info['date'] = task_date
        # elif not val_time:
        #     val_time = validate_time(task_time)
        #     if not new_val_time:
        #         handle_missing_info(val_date, new_val_time, chances=new_chances)
        #     else:
        #         missing_info['time'] = task_time
    return missing_info

def insert_new_task(intent, date_str, time_str, day_reapeat):
    with sqlite3.connect('users.db') as conn:
        query = 'INSERT INTO tasks (user_id, date, time, task, repetition) VALUES (?, ?, ?, ?, ?)'
        task = intent
        user_id = get_user_id()
        conn.execute(query, (user_id, date_str, time_str, task,  day_reapeat))
        print(f'Executing Inserting: user_id: {user_id}, date_str: {date_str}, time_str: {time_str}, task: {task},  day_reapeat: {day_reapeat}')
        if day_reapeat != '':
            date_obj = datetime.strptime(date_str, '%m/%d/%Y')
            new_date_obj = date_obj + timedelta(weeks=1)
            new_date = f'{new_date_obj.month}/{new_date_obj.day}/{new_date_obj.year}'
            new_query = 'INSERT INTO tasks (user_id, date, time, task, repetition) VALUES (?, ?, ?, ?, ?)'
            print(f'Inserting: user_id: {user_id}, date_str: {date_str}, time_str: {time_str}, task: {task},  day_reapeat: {day_reapeat}')
            conn.execute(new_query, (user_id, new_date, time_str, task, day_reapeat))
        conn.commit()
        print(f'Committing Inserted: user_id: {user_id}, date_str: {date_str}, time_str: {time_str}, task: {task},  day_reapeat: {day_reapeat}')
    socket = get_app_socket()[1]
    socket.emit('response', {'purpose': 'updated-task'})

def refresh_next_task_list():
    print('Refreshing Task List')
    tasks = get_next_tasks(3)
    set_next_task_list(tasks)
    first_task = tasks[0]
    date_str, time_str = first_task[2], first_task[3]
    print(f'First Task Date and Time: Date: {date_str}, Time: {time_str}')
    date = datetime.strptime(' '.join([date_str, time_str]), '%m/%d/%Y %I:%M %p')
    set_next_task_datetime(date)

def time_to_string(time, is_am):
    print(f'Converting time to string: {time}, is_am: {is_am}')
    if time.minute < 10:
        minute = f'0{time.minute}'
    else:
        minute = time.minute
    print(f'Minute: {minute}')
    if is_am:
        if time.hour == 0:
            hour = 12
        else:
            hour = time.hour
        am_or_pm = ' AM'
    else:
        if time.hour > 12:
            hour = time.hour - 12
        else:
            hour = time.hour
        am_or_pm = ' PM'
    time_str = f'{hour}:{minute} {am_or_pm}'
    print(f'Time as String: {time_str}')
    return time_str, hour, minute

def set_task(intent, date, time, day_reapeat, is_am):
    print(f'Setting Task: Intent: {intent}, Date: {date}, Time: {time}, Day Repeat: {day_reapeat}, Is AM: {is_am}')
    date_str = f'{date.month}/{date.day}/{date.year}'
    print(f'Date String: {date_str}')
    time_str, hour, minute = time_to_string(time, is_am)
    print(f'Time String: {time_str}, Hour: {hour}, Minute: {minute}')
    insert_new_task(intent, date_str, time_str, day_reapeat)
    print(f'Inserted New Task: Date: {date_str}, Time: {time_str}, Task Purpose: {intent}')
    refresh_next_task_list()
    return hour, minute

def query_tasks_at_date(date):
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        query = 'SELECT * FROM tasks WHERE user_id = ? AND date = ?'
        user_id = get_user_id()
        cursor.execute(query, (user_id, date))
        rows = cursor.fetchall()

    return rows

def query_tasks_at_time(time):
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        query = 'SELECT * FROM tasks WHERE user_id = ? AND time = ?'
        user_id = get_user_id()
        cursor.execute(query, (user_id, time))

def handle_get_tasks_time(time):
    time_str = f'{time.hour}:{time.minute}'
    tasks = query_tasks_at_time(time_str)
    return tasks

def handle_get_tasks_date(date):
    date_str = f'{date.month}/{date.day}/{date.year}'
    tasks = query_tasks_at_date(date_str)
    return tasks

def get_bert_embedding(text):
    try:
        print(f'Tokenizing text: {text}')
        inputs = tokenizer(text, return_tensors="pt", max_length=512, truncation=True, padding='max_length')
        inputs.to(device)
        print('Getting output from bert')
        with torch.no_grad():
            outputs = bert_model(**inputs)
        print('Getting embeddings from bert output')
        embeddings = outputs.last_hidden_state.mean(dim=1)
        print('Returning embeddings')
    except Exception as e:
        print(e)
    return embeddings

def cosine_similarity(embedding1, embedding2):
    try:
        embedding1 = embedding1.cpu()
        embedding2 = embedding2.cpu()
        similarity = 1 - cosine(embedding1.squeeze().numpy(), embedding2.squeeze().numpy())
    except Exception as e:
        print(e)
    return similarity

def compare_strings(str1, str2):
    print(f'Getting embeddings Str1: {str1}')
    emb_1 = get_bert_embedding(str1)
    print(f'Getting embeddings Str2: {str2}')
    emb_2 = get_bert_embedding(str2)
    print('Calculating cosine similarity')
    similarity = cosine_similarity(emb_1, emb_2)
    print(f'Similarity: {similarity}')
    return similarity

def get_ordered_tasks():
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        query = 'SELECT * FROM tasks WHERE user_id = ? ORDER BY date, time'
        user_id = get_user_id()
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        now = datetime.now()
        tasks_after_now = []
        for task in rows:
            print(f'Task: {task}')
            task_datetime = datetime.strptime(' '.join([task[2], task[3]]), '%m/%d/%Y %I:%M %p')
            print(f'Task Date Time: {task_datetime}')
            print(f'Now Date Time: {now}')
            diff = task_datetime - now
            zero = timedelta(0)
            print(f'Difference: {diff}')
            if diff > zero:
                print(f'Appending Task: {task}')
                tasks_after_now.append(task)
    return tasks_after_now

def get_next_tasks(num=-1):
    print(f'Getting Next {num} tasks')
    tasks_after_now = get_ordered_tasks()
    tasks_num = 3
    if num != -1:
        tasks_num = num
    tasks = tasks_after_now[:tasks_num]
    print(f'Got Tasks: {tasks}')
    return tasks

def get_max_similarity(rows, similarities):
    print('Getting max similarity')
    max_idx = similarities.index(max(similarities))
    return rows[max_idx], similarities[max_idx]

def get_task_intent(intent):
    print(f'Getting task by intent: {intent}')
    tasks_after_now = get_ordered_tasks()
    print(f'Got tasks: {tasks_after_now}')
    similarities = []
    print(f'\nGetting Similarities')
    for task in tasks_after_now:
        print('Getting intent')
        task_intent = task[4]
        print('Comparing strings')
        similarity = compare_strings(task_intent, intent)
        print(f'Appending Similarity: {similarity}')
        similarities.append(similarity)
    print(f'\nGot similarities: {similarities}')
    task, confidence = get_max_similarity(tasks_after_now, similarities)
    print(f'Most similar task: {task}, Confidence: {confidence}')
    return task, confidence

def handle_get_tasks_num(num):
    print('Handling get tasks num')
    if num:
        tasks = get_next_tasks(num=num)
    else:
        tasks = get_next_tasks()
    return tasks

def handle_get_tasks_month(month):
    start, end = get_month_start_and_end_by_name(month)
    tasks = get_tasks_within_date_range(start, end)
    return tasks

def handle_get_tasks_intent(intent):
    task, confidence = get_task_intent(intent)
    return task

def date_to_response(date):
    print(f'Getting Date as response')
    today = datetime.today()
    tomorrow = today + timedelta(days=1)
    if isinstance(date, str):
        if date == 'today':
            date_obj = today
        elif tomorrow == 'tomorrow':
            date_obj = tomorrow
        else:
            date_obj = datetime.strptime(date, '%m/%d/%Y')
    else:
        date_obj = date
    one_week = today + timedelta(weeks=1)
    two_weeks = today + timedelta(weeks=2)
    diff_ow = date_obj - one_week
    diff_tw = date_obj - two_weeks
    zero = timedelta(0)
    response = ''
    print(f'Date: {date}, Today: {today}, Tomorrow: {tomorrow}, One Week: {one_week}, Two Weeks: {two_weeks}')
    if today.month == date_obj.month and today.day == date_obj.day and today.year == date_obj.year:
        print('Returning Today')
        return 'Today'
    elif tomorrow.month == date_obj.month and tomorrow.day == date_obj.day and tomorrow.year == date_obj.year:
        print('Returning Tomorrow')
        return 'Tomorrow'
    print(f'Two Week Difference: {diff_tw}')
    if diff_tw <= zero:
        print('Within 2 Weeks')
        print(f'One Week Difference: {diff_ow}')
        if diff_ow >= zero:
            print('After One week')
            response += 'next '
        print(f'Response: {response}')
        days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        print(f'Weekday Num: {date_obj.weekday()}')
        response += f'{days[date_obj.weekday()]} '
        print(f'Response: {response}')
    else:
        print('Past 2 Weeks')
        response += f'On '
        months = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'november', 'december']
        month = months[date_obj.month - 1]
        print(f'Month: {month}')
        day_as_word = f'{date_obj.day}st' if str(date_obj.day).endswith('1') and date_obj.day != '11' else f'{date_obj.day}nd' if date_obj.day.endswith('2') and date_obj.day != '12' else f'{date_obj.day}rd' if date_obj.day.endswith('3') and date_obj.day != '13' else f'{date_obj.day}th'
        print(f'Day as word: {day_as_word}')
        response += f'{month} {day_as_word} '
        print(f'Response: {response}')
        if date_obj.year != today.year:
            print('Adding year to response')
            response += f'{date_obj.year} '
        print(f'Response: {response}')
    return response

def list_tasks(tasks, task_ref='task', list_all=False):
    print(f'Listing Tasks: {tasks}')
    print('Building Response')
    response = ''
    tasks_listed = 0
    confirm = False
    for task in tasks:
        print(f'Building Response with task: {task}')
        if not list_all:
            print(f'Checking Listed Tasks is 3: {tasks_listed}')
            if tasks_listed == 3 and len(tasks) > 3:
                print('Adding confirmation to response')
                strs = ['are' if len(tasks[3:]) > 1 else 'is', f'{task_ref} ' if len(tasks[3:]) == 1 else f'{task_ref}s ', 'they are' if len(tasks[3:]) > 1 else 'it is']
                print(f'Strs: {strs}')
                response += f'There {strs[0]} {len(tasks[3:])} other {strs[1]}, do you want to know what {strs[2]}?'
                confirm = True
                print(f'Response')
                break
            print(f'Building Response: {response}')
        print(f'Checking listed Tasks > 0: {tasks_listed}')
        if tasks_listed > 0:
            print('Adding another/(and) to response')
            if len(tasks) - 1 == tasks_listed or (tasks_listed == 2 and not list_all):
                print('Adding and to response')
                response += 'and '
            response += f'another {task_ref if len(task_ref.split()) == 1 else task_ref.split()[1]} '
            print(f'Building Response: {response}')
        print(f'Building Task Response')
        date = task[2]
        print(f'Date: {date}')
        time = task[3]
        print(f'Time: {time}')
        task_intent = task[4]
        print(f'Intent: {task_intent}')
        response += f'{date_to_response(date)} at {time} {intent_as_response(task_intent)}. '
        print(f'Building Response: {response}')
        tasks_listed += 1
    print(f'Built Response: {response}')
    return response, confirm

def handle_confirmation_response(tasks, task_ref, user_response):
    if user_response == 'Sorry, I didn\'t understand your request':
        y_or_n = 'no'
    else:
        y_or_n = get_y_or_n(user_response)
    if y_or_n == 'yes':
        alert_reading_remaining_tasks(True if len(tasks[3:]) > 1 else False)
        listed_tasks = list_tasks(tasks[3:], task_ref, list_all=True)[0]
        user_response = output_tasks_to_user(listed_tasks)
    else:
        respond_ending_request_chain()

def get_tasks_today():
    print('Getting Tasks Today')
    today = datetime.today()
    print(f'Today Datetime: {today}')
    month, day, year = today.month, today.day, today.year
    print(f'Month, Day, Year: {month}, {day}, {year}')
    date = f'{month}/{day}/{year}'
    print(f'Date: {date}')
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        query = 'SELECT * FROM tasks WHERE user_id = ? AND date = ?'
        user_id = get_user_id()
        print(f'user id: {user_id}')
        cursor.execute(query, (user_id, date))
        rows = cursor.fetchall()
        print(f'Rows: {rows}')
    return rows

def output_tasks_today():
    response = 'You have '
    print('Getting todays tasks')
    tasks = get_tasks_today()
    print(f'Got Tasks: {tasks}')
    num_tasks = len(tasks)
    print(f'Num Tasks: {tasks}')
    if num_tasks == 0:
        response += f'{num_tasks} tasks to complete today'
        output_tasks_to_user(response)
        return
    elif num_tasks == 1:
        response += f'{num_tasks} task to complete today. Would you like to hear what it is?'
    else:
        response += f'{num_tasks} tasks to complete today. Would you like to hear what they are?'
    print('Outputting Todays Tasks')
    user_response = output_tasks_to_user(response, True)
    y_or_n = get_y_or_n(user_response)
    if y_or_n == 'yes':
        response, confirm = list_tasks(tasks)
        user_response = output_tasks_to_user(response, confirm)
        if confirm:
            y_or_n = get_y_or_n(user_response)            
            if y_or_n == 'yes':
                response = list_tasks(tasks[3:], list_all=True)[0]
                output_tasks_to_user(response)
    else:
        return
    

def get_task_proximity(date):
    now = datetime.now()
    proximity = date - now
    print(f'Proximity: {proximity}')
    return proximity

def remind_task(tasks, when):
    init_task = tasks[0]
    print(f'Reminding task in {when}: {init_task}')
    if when == 'now':
        response = f'This is your {init_task[3]} reminder {intent_as_response(init_task[4])}. '
    else:
        response = f'This is a reminder {intent_as_response(init_task[4])} in {when}. '
    print(f'Response: {response}')
    task_date_str = init_task[2]
    task_date = datetime.strptime(task_date_str, '%m/%d/%Y')
    previous_task = init_task
    for task in tasks[1:]:
        date_str = task[2]
        date = datetime.strptime(date_str, '%m/%d/%Y')
        today = datetime.today()
        if date.month == today.month and date.day == today.day and date.year == today.year:
            proximity = date - task_date
            hours_diff, min_diff = proximity.hour, proximity.minute
            if hours_diff != 0:
                response += f'{hours_diff} hour'
                if hours_diff != 1:
                    response += 's '
                else:
                    response += ' '
            else:
                response += f'{min_diff} minute'
                if min_diff != 1:
                    response += 's '
                else:
                    response += ' '
            
            response += f'after completing your task {intent_as_response(previous_task[4])}, you have another task set {intent_as_response(task[4])}. '
            previous_task = task
    output_tasks_to_user(response)

def check_remind_on_time(tasks, proximity):
    print('Checking task is now')
    remind_on_time = False
    print(f'Proximity Seconds: {proximity.seconds}')
    if proximity.seconds <= 1:
        print('Task is occuring now')
        remind_on_time = True
        print('Reminding Task is now')
        remind_task(tasks, 'now') 
        if len(tasks) > 1:
            set_next_task_datetime(tasks[1:])
            next_three_tasks = get_next_tasks(4)[1:]
            set_next_task_list(next_three_tasks)
        else:
            set_next_task_datetime('')
            set_next_task_list('')

    return remind_on_time

def check_remind_thirty_mins(tasks, proximity):
    print(f'Checking If task within 30 minutes')
    remind_thirty_mins = False
    print(f'Proximity Seconds: {proximity.seconds}')
    if proximity.seconds <= 1800:
        print('Task within 30 minutes')
        remind_thirty_mins = True
        if proximity.seconds >= 1680:
            print('Remind task in 30 minutes')
            remind_task(tasks, '30 minutes')
    return remind_thirty_mins

def check_remind_two_hours(tasks, proximity):
    print(f'Checking If task within 2 hours')
    remind_two_hours = False
    print(f'Proximity Seconds: {proximity.seconds}')
    if proximity.seconds <= 7200:
        print('Task within 2 hours')
        remind_two_hours = True
        if proximity.seconds >= 7080:
            print('Reminding task in 2 hours')
            remind_task(tasks, '2 hours')
    print(f'Remind Two Hours: {remind_two_hours}')
    return remind_two_hours

def remind_tasks():    
    global remind_two_hours
    global remind_thirty_mins
    global remind_on_time
    date = get_next_task_datetime()
    if date != '':
        print(f'Getting Task Proximity to today, {date}')
        proximity = get_task_proximity(date)
        tasks = get_next_task_list()
        print(f'Tasks: {tasks}')
        print(f'Remind 2 Hours: {remind_two_hours}')
        print(f'Remind 30 Hours: {remind_thirty_mins}')
        print(f'Remind On Time: {remind_on_time}\n')
        if not remind_two_hours:    
            print('Checking Remind two hours')
            remind_two_hours = check_remind_two_hours(tasks, proximity)
        if not remind_thirty_mins:
            print('Checking Remind Thirty minutes')
            remind_thirty_mins = check_remind_thirty_mins(tasks, proximity)
        if not remind_on_time:
            print('Checking Remind On Time')
            remind_on_time = check_remind_on_time(tasks, proximity)
        print(f'Remind 2 Hours: {remind_two_hours}')
        print(f'Remind 30 Hours: {remind_thirty_mins}')
        print(f'Remind On Time: {remind_on_time}')
        if remind_on_time:
            remind_two_hours = False
            remind_thirty_mins = False
            remind_on_time = False
    else:
        print('Checking Tasks to remind')
        global check_tasks
        print(f'Check tasks: {check_tasks}')
        if check_tasks:
            tasks = get_next_tasks(3)
            print(f'Next 3 Tasks: {tasks}')
            if len(tasks) == 0:
                print('No Tasks Found Check Tasks False')
                check_tasks = False
            else:
                print('Tasks Found to Check')
                set_next_task_list(tasks[:3])
                date_str = tasks[0][2]
                time_str = tasks[0][3]
                print(f'Date String: {date_str}, Time String: {time_str}')
                date = datetime.strptime(' '.join([date_str, time_str]), '%m/%d/%Y %I:%M %p')
                set_next_task_datetime(date)
                remind_tasks()

def output_tasks_month(tasks, task_ref, month, req):
    # response = ''
    
    # if 'my' in req:
    #     response += f'Your next '
    # elif 'scheduled' in req:
    response = 'You scheduled '
   
    confirm = False        
    if len(tasks) == 0:
        response += f'no '
        response += f'{task_ref} ' if len(tasks) == 1 else f'{task_ref}s '
        response += f'in {month}.'
    else:
        response += f'{len(tasks)} '

    response += f'{task_ref} ' if len(tasks) == 1 else f'{task_ref}s '
    
    response += f'in {month}. '
    listed_tasks, confirm = list_tasks(tasks, task_ref)
    response += listed_tasks
    user_response = output_tasks_to_user(response, confirm)
    if confirm:
        handle_confirmation_response(tasks, task_ref, user_response)
    
def output_tasks_num(tasks, task_ref, task_num, req):
    response = ''
    if task_num == -1:
        task_num == len(tasks)
    if 'my' in req:
        response += 'Your '
        strs = [f'next {task_ref} is ' if task_num == 1 else f'next {task_num} {task_ref}s are ']
    else:
        response += 'The '
        strs = [f'next {task_ref} you have is ' if task_num == 1 else f'next {task_num} {task_ref}s you have are ']
    response += f'{strs[0]}'
    
    response += list_tasks(tasks, task_ref, list_all=True)[0]

    output_tasks_to_user(response)

def get_tasks_and_routines(tasks):
    new_tasks = []
    routines = {}
    for task in tasks:
        if len(task[5]) != 0:
            new_tasks.append(task)
        elif task not in routines.values():
            routines[task[5]] = task
    return tasks, routines

def output_tasks(tasks, req, task_month='', task_num=''):
    task_ref = 'upcoming ' if 'upcoming' in req or 'coming up' in req or 'later' in req else ''
    task_ref += 'remind' if 'remind' in req else 'task'
    # tasks, routines = get_tasks_and_routines()
    if len(tasks) == 0:
        return False
    if task_month != '':
        output_tasks_month(tasks, task_ref, task_month, req)
    elif task_num != '':
        output_tasks_num(tasks, task_ref, task_num, req)

def query_tasks(req, intent='', tf='', date='', time='', day_repeat=''):
    print('Querying for task')
    print(f'Req: {req}, Intent: {intent}, Time Frame: {tf}, date: {date}, time: {time}, Day Repeat: {day_repeat}')
    if date != '':
        print('Query Tasks Date')
        tasks = handle_get_tasks_date(date)
        print(f'Tasks Retrieved: {tasks}')
        if len(tasks) != 0:
            print('Length of Tasks Not 0')
            response = list_tasks(tasks)[0]
        else:
            print('No Tasks Were Found')
            if date != '':
                response = f'You have no tasks {date_to_response(date)}'
            elif intent != '':
                response = f'You have not tasks {intent_as_response(intent)}'
        print(f'Response: {response}')
        output_tasks_to_user(response)
    elif time != '':
        print('Query Tasks Time')
        tasks = handle_get_tasks_time(time)
        output_tasks(tasks, req, time)
    elif tf and tf['num'] != -1:
        print('Query Tasks Num')
        tasks = handle_get_tasks_num(tf['num'])
        output_tasks(tasks, req, task_num=tf['num'])
    elif tf and tf['month'] != '':
        print('Query Tasks Month')
        tasks = handle_get_tasks_month(tf['month'])
        output_tasks(tasks, req, task_month=tf['month'])
    elif intent != '':
        print('Query Tasks intent')
        task = handle_get_tasks_intent(intent)
        response = list_tasks([task])[0]
        output_tasks_to_user(response)
    else:
        print('Query Tasks else (3)')
        tasks = handle_get_tasks_num(3)
        print(f'Tasks Retrieved: {tasks}')
        response = list_tasks(tasks)[0]
        print(f'Response: {response}')
        output_tasks_to_user(response)

def handle_query_no_intent(req):
    tf = get_date_and_time_from_req(req)
    date, time, day_repeat, is_am = interpret_time(tf)
    print(f'Retrieved time information: date: {date}, time: {time}, day_repeat: {day_repeat}, is_am: {is_am}')
    query_tasks(req, tf=tf, date=date, time=time, day_repeat=day_repeat)

def handle_query_intent(req, intent):
    query_tasks(req, intent=intent)

def get_mark_or_move(req):
    mark_or_move = False
    mark_kw = ['check', 'complete', 'mark', 'done', 'finish']
    for kw in mark_kw:
        if kw in req:
            mark_or_move = True
            break
    return mark_or_move

# take in request
def process_task_req(req):
    # classify req as set, query, or update
    classification = classify_request(req)
    print(f'Classified as: {classification}')
    intent = get_intent(req)
    print(f'Intent: {intent}')
    # if req is set
    if classification == 'set':
        tf = get_date_and_time_from_req(req)
        task_date, task_time, day_repeat, is_am = interpret_time(tf)
        if task_date == '':
            task_date = datetime.today()
        task_ref = 'remind' if 'remind' in req else 'task'
        # validate time
        val_date, val_time = validate_date_and_time(task_date, task_time)

        if not val_time:
            missing_info = handle_missing_info(task_date, task_time, val_date, val_time)
            print(f'Missing Information: {missing_info}')
            if len(missing_info) == 0:
                prompt_user_to_retry()
                return ''
            if missing_info.get('date'):
                task_date = missing_info['date']
            if missing_info.get('time'):
                task_time = missing_info['time']
        if task_date == '':
            task_date = datetime.today()
        print('Setting task')
        hour, minute = set_task(intent, task_date, task_time, day_repeat, is_am)
        print('Task set')
        alert_task_set(intent, task_date, hour, minute, is_am, tf['repeat'], task_ref)
    # elif req is query
    elif classification == 'query':
        if intent != '':
            # handle non-specific query
            print('Query Intent')
            handle_query_intent(req, intent)
        else: 
            print('Query No Intent')
            # handle specific query
            handle_query_no_intent(req)
    # elif req is update
    elif classification == 'update':
        mark_or_move = get_mark_or_move(req)
        # if req is mark
        if mark_or_move:
            # handle mark req
            print('Marking task as complete')
            handle_mark(req, intent)
        # else if req is move
        else:
            # handle move req
            print('Moving a task')
            handle_move(req, intent)