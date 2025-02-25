import json
from pprint import pprint

# Function to read the file and generate a list of dictionaries
# The list is sorted by the events timestamps 
def read_file_to_dict_list(filename):
    try:
        with open(filename, 'r') as file:
            data = file.read()
            list_of_dicts = json.loads(data)
            return sorted(list_of_dicts, key=lambda e: e["time"])
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error: The file '{filename}' does not contain valid JSON.")
        return []

# Function to get the timestamp of a specific event, along with index in searching list
# You can use notation "message:2" to skip to the second occurence of "message" 
last_i = 0  
def search_for_event_timestamp(dict_list, event_message):
    global last_i
    if len(event_message.split(":")) > 1:
        occurence = int(event_message.split(":")[1])
        event_message = event_message.split(":")[0]
    else:
        occurence = 1
    occurence_count = 0
    i = 0 
    for i, entry in enumerate(dict_list):
        if entry.get('event') == event_message:
            occurence_count += 1
            if occurence_count == occurence:
                #print(f"Event {event_message} in line {6*(last_i+i)+2}")
                last_i += i+1
                return entry.get('time'), i
    return None, len(dict_list)

def difference_between_events(event_1, event_2, events_to_time_dict):
    if events_to_time_dict[event_1] is not None and events_to_time_dict[event_2] is not None:
        return events_to_time_dict[event_2] - events_to_time_dict[event_1]
    return "Not found"

# Map each event message to its timestamp
# Once an event is found, eliminates all the previous events from the searching list
def fill_events_to_time_dict(list_of_events, list_of_events_messages_to_search):
    events_to_time_dict = dict.fromkeys(list_of_events_messages_to_search,None)
    for event in list_of_events_messages_to_search:
        events_to_time_dict[event], event_index = search_for_event_timestamp(list_of_events, event)
        list_of_events = list_of_events[event_index+1:]
    return events_to_time_dict

filename = 'events.json'
list_of_events_dicts = read_file_to_dict_list(filename)
with open(filename, 'w') as file:
    json.dump(obj=list_of_events_dicts, fp=file, indent=1, separators=(',',':'))

events_to_time_dict = fill_events_to_time_dict (
    list_of_events_dicts,
    [
    # Step 1
    'Started registering a task',                   # Enviei rpc_call pra registrar tarefa
    'Finished task creation',                       # cloud_task_manager registrou

    # Step 2
    'Started starting a task',                      # Enviei rpc_call pra iniciar tarefa
    'Finished server task initialization',          # cloud_task_manager registrou

    # Step 3
    'Started getting client stats for sending',
    'Finished updating user info',

    # Step 4
    'Started requesting task',
    'Finished requesting task',

    # Step 5
    'Started downloading task',
    'Finished downloading task',

    # Step 6
    'Started client task initialization',
    'Started client',

    # Step 7
    'Finished client',
    'Finished handling task 4fe5 finalization'
    ]
)

#print("Timestamps: ")
pprint(events_to_time_dict)

time_difference = difference_between_events(
    'Started registering a task',
    'Finished task creation',
    events_to_time_dict)
print(f"1) Time for registering a task = {time_difference} seconds")

time_difference = difference_between_events(
    'Started starting a task',
    'Finished server task initialization',
    events_to_time_dict)
print(f"2) Time for starting a task at cloud = {time_difference} seconds")

time_difference = difference_between_events(
    'Started getting client stats for sending',
    'Finished updating user info',
    events_to_time_dict)
print(f"3) Time for updating client info = {time_difference} seconds")

time_difference = difference_between_events(
    'Started requesting task',
    'Finished requesting task',
    events_to_time_dict)
print(f"4) Time for requesting a task = {time_difference} seconds")

time_difference = difference_between_events(
    'Started downloading task',
    'Finished downloading task',
    events_to_time_dict)
print(f"5) Time for downloading a task = {time_difference} seconds")

time_difference = difference_between_events(
    'Started client task initialization',
    'Started client',
    events_to_time_dict)
print(f"6) Time for starting a task at client = {time_difference} seconds")

time_difference = difference_between_events(
    'Finished client',
    'Finished handling task 4fe5 finalization',
    events_to_time_dict)
print(f"7) Time for finishing a task at client = {time_difference} seconds")
