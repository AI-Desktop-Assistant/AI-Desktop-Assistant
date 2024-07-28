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
    
def update_task(task_purpose, tf, date, time, day_repeat):
    rows_to_update = ''
    values = []
    if date != '':
        rows_to_update += 'date = ? AND '
        values.append(date)
    elif time != '':
        rows_to_update += 'time = ? AND '
        values.append(time)
    elif day_repeat != '':
        rows_to_update += 'repetition = ? '
        values.append(day_repeat)
    if rows_to_update.endswith('AND '):
        rows_to_update = rows_to_update[:-4]
    user_id = get_user_id()
    values.append(user_id)
    values.append(task_purpose)
    with sqlite3.connect('users.db') as conn:
        query = f'UPDATE tasks SET {rows_to_update}WHERE user_id = ? AND task = ?'
        conn.execute(query, values)
        conn.commit()

def handle_updating_task(intent, tf, date, time, day_repeat):
    task, confidence = get_task_intent(intent)
    update_task(task, tf, date, time, day_repeat)

# handle move req
def handle_move(req, intent):
    # parse updated time for task
    tf = get_date_and_time_from_req(req)
    # interpret time from user
    date, time, day_repeat = interpret_time(tf)
    # handle updating task
    handle_updating_task(intent, tf, date, time, day_repeat)

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
        intent = 'alarm'
    else:
        intent = ' '.join(predicted_tokens)

    return intent

def interpret_time(time):
    task_date = ''
    task_time = ''
    num = time['num']
    time_spec = time['time']
    day = time['day']
    repeat = time['repeat']
    day_repeat = ''
    is_am = False
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
        if time['hours']:
            task_time = get_time_now_to_x_hours(num)[1]
            print('Num, Hours')
        elif time['minutes']:
            task_time = get_time_now_to_x_minutes(num)[1]
            print('Num, Minutes')
    elif day != '':
        task_date = get_dates_by_day_name(day, next=time['next'])
        print(f'Day: {day}, Next: {time["next"]}')
        if repeat:
            day_repeat = day
            print(f'Day Repeat: {day_repeat}')
    print(f'Task Date: {task_date}')

    if time_spec != '':
        task_time, is_am = get_time_from_spec(time_spec, time['am'], time['pm'])
    
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
            tf_item[key] = True
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
    if tf_item == tf_item_copy:
        return None
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
    new_chances = chances - 1
    missing_info = {}
    if chances == 0:
        return missing_info
    response = prompt_for_missing_date_or_time(val_date, val_time)
    if response == '':
        alert_not_understood()
        handle_missing_info(task_date, task_time, val_date, val_time, chances=new_chances)
    else:
        tf = get_date_and_time_from_req(response)
        task_date, task_time, day_repeat = interpret_time(tf)
        print(f'Task Date: {task_date}, Task Time: {task_time}, Reapeating Day: {day_repeat}')
        new_val_date = new_val_time = True
        if not val_date and not val_time:
            new_val_date, new_val_time = validate_date_and_time(task_date, task_time)
            if not val_date and not val_time:
                handle_missing_info(new_val_date, new_val_time, chances=new_chances)
            else:
                missing_info['date'] = task_date
                missing_info['time'] = task_time
        elif not val_date:
            new_val_date = validate_date(task_date)
            if not new_val_date:
                handle_missing_info(new_val_date, val_time, chances=new_chances)
            else:
                missing_info['date'] = task_date
        elif not val_time:
            val_time = validate_time(task_time)
            if not new_val_time:
                handle_missing_info(val_date, new_val_time, chances=new_chances)
            else:
                missing_info['time'] = task_time
    return missing_info

def insert_new_task(intent, date_str, time_str, day_reapeat):
    with sqlite3.connect('users.db') as conn:
        query = 'INSERT INTO tasks (user_id, date, time, task, repetition) VALUES (?, ?, ?, ?, ?)'
        task = intent
        user_id = get_user_id()
        conn.execute(query, (user_id, date_str, time_str, task,  day_reapeat))
        print(f'Inserting: user_id: {user_id}, date_str: {date_str}, time_str: {time_str}, task: {task},  day_reapeat: {day_reapeat}')
        if day_reapeat != '':
            date_obj = datetime.strptime(date_str, '%m/%d/%Y')
            new_date_obj = date_obj + timedelta(weeks=1)
            new_date = f'{new_date_obj.month}/{new_date_obj.day}/{new_date_obj.year}'
            new_query = 'INSERT INTO tasks (user_id, date, time, task, repetition) VALUES (?, ?, ?, ?, ?)'
            print(f'Inserting: user_id: {user_id}, date_str: {date_str}, time_str: {time_str}, task: {task},  day_reapeat: {day_reapeat}')
            conn.execute(new_query, (user_id, new_date, time_str, task, day_reapeat))
        conn.commit()
        

def set_task(intent, date, time, day_reapeat, is_am):
    if date == '':
        date = datetime.today()
    date_str = f'{date.month}/{date.day}/{date.year}'
    if time.minute < 10:
        minute = f'0{time.minute}'
    else:
        minute = time.minute
    if is_am:
        if time.hour == 0:
            hour = 12
        else:
            hour = time.hour
        am_or_pm = ' AM'
    else:
        if time.hour > 12:
            hour = time.hour - 12
        am_or_pm = ' PM'
    
    time_str = f'{hour}:{minute} {am_or_pm}'
    insert_new_task(intent, date_str, time_str, day_reapeat)
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
    inputs = tokenizer(text, return_tensors="pt", max_length=512, truncation=True, padding='max_length')
    with torch.no_grad():
        outputs = bert_model(**inputs)
    embeddings = outputs.last_hidden_state.mean(dim=1)
    return embeddings

def cosine_similarity(embedding1, embedding2):
    similarity = 1 - cosine(embedding1.squeeze().numpy(), embedding2.squeeze().numpy())
    return similarity

def compare_strings(str1, str2):
    emb_1 = get_bert_embedding(str1)
    emb_2 = get_bert_embedding(str2)
    similarity = cosine_similarity(emb_1, emb_2)
    return similarity

def get_next_tasks(num=-1):
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        query = 'SELECT * FROM tasks WHERE user_id = ? ORDER BY date, time'
        user_id = get_user_id()
        cursor.execute(query, (user_id))
        rows = cursor.fetchall()
        tasks_num = 3
        if num != -1:
            tasks_num = num
        tasks = rows[:tasks_num]
    return tasks

def get_max_similarity(rows, similarities):
    max_idx = similarities.index(max(similarities))
    return rows[max_idx], similarities[max_idx]

def get_task_intent(intent):
    with sqlite3.connect('users.db') as conn:
        query = 'SELECT * FROM tasks WHERE user_id = ?'
        cursor = conn.cursor()
        user_id = get_user_id()
        cursor.execute(query, (user_id, intent))
        rows = cursor.fetchall()
    similarities = []
    for row in rows:
        task = row[4]
        similarity = compare_strings(task, intent)
        similarities.append(similarity)
    task, confidence = get_max_similarity(rows, similarities)

    return task, confidence

def handle_get_tasks_num(num, next):
    if next:
        tasks = get_next_tasks(num=num)
    else:
        tasks = get_next_tasks()
    return tasks

def handle_get_tasks_month(month):
    start, end = get_month_start_and_end_by_name(month)
    tasks = get_tasks_within_date_range(start, end)
    return tasks

def handle_get_tasks_intent(intent):
    task = get_task_intent(intent)

    return task

def date_to_response(date):
    month, day, year = date.split('/')
    months = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
    idx = int(month)-1
    month_word = months[idx]
    day_as_word = f'{day}st' if day.endswith('1') and day != '11' else f'{day}nd' if day.endswith('2') and day != '12' else f'{day}rd' if day.endswith('3') and day != '13' else f'{day}th'
    date_as_response = f'{month_word} {day_as_word}'
    return date_as_response

def task_intent_to_response(task_intent):
    first_word = task_intent.split()[0]
    if first_word.endswith('ing'):
        response = 'for '
    else:
        response = 'to '
    response += task_intent
    return response

def list_tasks(tasks, task_ref='task', list_all=False):
    response = ''
    tasks_listed = 0
    confirm = False
    for task in tasks:
        if not list_all:
            if tasks_listed == 3 and len(tasks) > 3:
                strs = ['are' if len(tasks[:3]) > 1 else 'is', f'{task_ref} ' if len(tasks[:3]) == 1 else f'{task_ref}s ', 'they are' if len(tasks[:3]) > 1 else 'it is']
                response += f'There {strs[0]} {len(tasks[:3])} other {strs[1]}, do you want to know what {strs[2]}?'
                confirm = True
        if tasks_listed > 0:
            if len(tasks) - 1 == tasks_listed or (tasks_listed == 2 and not list_all):
                response += 'and '
            response += f'another {task_ref if len(task_ref.split()) == 1 else task_ref.split()[1]} '
        date = task[2]
        time = task[3]
        task_intent = task[4]
        response += f'On {date_to_response(date)} at {time} you have a {task_ref if len(task_ref.split()) == 1 else task_ref.split()[1]} set {task_intent_to_response(task_intent)}. '

        tasks_listed += 1
    return response, confirm

def handle_confirmation_response(tasks, task_ref, user_response):
    if user_response == '':
        y_or_n = 'no'
    else:
        y_or_n = get_y_or_n(user_response)
    if y_or_n == 'yes':
        alert_reading_remaining_tasks(True if len(tasks[:3]) > 1 else False)
        listed_tasks = list_tasks(tasks[:3], task_ref, list_all=True)[0]
        user_response = output_tasks_to_user(listed_tasks)
    else:
        respond_ending_request_chain()

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
    if date != '':
        tasks = handle_get_tasks_date(date)
    elif time != '':
        tasks = handle_get_tasks_time(time)
        output_tasks(tasks, req, time)
    elif tf['num']:
        tasks = handle_get_tasks_num(tf['num'], tf['next'])
        output_tasks(tasks, req, task_num=tf['num'])
    elif tf['month']:
        tasks = handle_get_tasks_month(tf['month'])
        output_tasks(tasks, req, task_month=tf['month'])
    elif intent != '':
        task = handle_get_tasks_intent(intent)
        response = list_tasks([task])[0]
        output_tasks_to_user(response)
    else:
        tasks = handle_get_tasks_num(3)

def handle_query_no_intent(req):
    tf = get_date_and_time_from_req(req)
    date, time, day_repeat, is_am = interpret_time(tf)

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
            if len(missing_info) != 0:
                prompt_user_to_retry()
                return ''
            if missing_info.get('date'):
                task_date = missing_info['date']
            if missing_info.get('time'):
                task_time = missing_info['time']
        
        hour, minute = set_task(intent, task_date, task_time, day_repeat, is_am)
        alert_task_set(intent, task_date, hour, minute, is_am, tf['repeat'], task_ref)
    # elif req is query
    elif classification == 'query':
        if intent != 'alarm':
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
            handle_mark(req, intent)
        # else if req is move
        else:
            # handle move req
            handle_move(req, intent)