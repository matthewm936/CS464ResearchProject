import sys
import csv
import tkinter as tk
import random
import time

NUM_TRIALS = 40
MAX_KEY_COMBO = 8

# Buffer time between trials in milliseconds
KEY_RESET_DELAY = 400

if len(sys.argv) < 3:
	print("Usage: python main.py <participant_id> <trial_number> [<seed>]")
	sys.exit(1)

	# for our experiment we will keep the seed the same for every participant, this was a later change

participant_id = sys.argv[1]
trial_number = sys.argv[2] # not sure if we will use this but the behavoir is here

seed = None
if len(sys.argv) == 4:
	seed = int(sys.argv[3])
	random.seed(seed)

with open('data.csv', 'a', newline='') as csvfile:
	writer = csv.writer(csvfile)
	writer.writerow(['Participant ID', 'Trial #', 'Avg Time (s)', 'Correctness Rate', 'Key Count'])

	correct_responses = 0
	total_time = 0
	trials_completed = 0

	key_stats = {i: {'correct': 0, 'total_time': 0, 'trials': 0} for i in range(1, MAX_KEY_COMBO + 1)}

	pressed_keys = set() # allows for us to check if the set, ie the order of keys pressed doesnt matter

	target_keys = []

	def start_experiment():
		instructions = "Press the shown keys as quickly and accurately as possible.  The order of hotkeys pressed does not matter"
		start_button.config(text=instructions)
		start_button.pack_forget()
		prompt_next_key(1)

	def prompt_next_key(num_keys):
		global target_keys, start_time, pressed_keys

		pressed_keys.clear()
		target_keys.clear()

		if num_keys == 1:
			target_keys.append(random.choice("abcdefghijklmnopqrstuvwxyz"))
		else:
			# this should allow for hotkey like combinations, instead of just purely random
			modifiers = ['Shift', 'Control']
			selected_keys = set(random.sample(modifiers, min(1, num_keys)))
			selected_keys.update(random.sample("abcdefghijklmnopqrstuvwxyz", num_keys - len(selected_keys)))
			target_keys = list(selected_keys)

		start_time = time.time()

		keys_text = ' + '.join(target_keys)
		prompt_label.config(text=f"Press the keys: {keys_text}")
		prompt_label.pack()

	def normalize_key(key):
		# left versus right ctrl and shift doesnt change things
		# also hitting shift alphabet character wont make it upper
		if key in ['Shift_L', 'Shift_R']:
			return 'Shift'
		elif key in ['Control_L', 'Control_R']:
			return 'Control'
		elif key in ['Alt_L', 'Alt_R']:
			return 'Alt'
		elif len(key) == 1 and key.isalpha():
			return key.lower()
		return key

	def on_key_press(event):
		normalized_key = normalize_key(event.keysym)
		if normalized_key == 'Shift':
			pressed_keys.add('Shift')
		else:
			if 'Shift' in pressed_keys:
				normalized_key = normalized_key.lower()
			pressed_keys.add(normalized_key)

		# testing shit
		# print(f"Keys pressed by user: {pressed_keys}")
		# print(f"Keys expected by program: {set(target_keys)}")

		if len(pressed_keys) == len(target_keys):
			response_time = time.time() - start_time
			log_response(pressed_keys, response_time)

	def on_key_release(event):
		normalized_key = normalize_key(event.keysym)
		pressed_keys.discard(normalized_key)


	def log_response(pressed, response_time):
		global correct_responses, total_time, trials_completed

		num_keys = len(target_keys)
		
		correct_count = 1 if set(pressed) == set(target_keys) else 0
		correctness_rate = correct_count

		print(f"Correctness: {'Correct' if correct_count == 1 else 'Incorrect'}")
		print(f"Response time: {response_time:.2f} seconds")

		key_stats[num_keys]['correct'] += correctness_rate
		key_stats[num_keys]['total_time'] += response_time
		key_stats[num_keys]['trials'] += 1

		correct_responses += correct_count
		total_time += response_time
		trials_completed += 1

		if trials_completed >= NUM_TRIALS:
			report_results()
		else:
			prompt_label.after(KEY_RESET_DELAY, reset_after_trial)

	def reset_after_trial():
		next_key_count = min(1 + trials_completed // (NUM_TRIALS // MAX_KEY_COMBO), MAX_KEY_COMBO)
		prompt_next_key(next_key_count)

	def report_results():
		avg_time_overall = total_time / NUM_TRIALS

		# counts any miss as a combo miss
		combo_accuracy = correct_responses / (trials_completed)
		
		 # Overall accuracy based on total key presses
		writer.writerow([participant_id, trial_number, avg_time_overall, combo_accuracy, 'Overall'])

		# Report individual key count results
		for num_keys in range(1, MAX_KEY_COMBO + 1):
			if key_stats[num_keys]['trials'] > 0:
				avg_time = key_stats[num_keys]['total_time'] / key_stats[num_keys]['trials']
				accuracy = key_stats[num_keys]['correct'] / key_stats[num_keys]['trials']  # Average correctness for key count
				writer.writerow([participant_id, trial_number, avg_time, accuracy, num_keys])

		prompt_label.config(text=f"Experiment complete.")
		root.after(3000, root.destroy)

	root = tk.Tk()
	root.title("Reaction Time Experiment")
	root.attributes('-fullscreen', True)

	start_button = tk.Button(root, text="Start", command=start_experiment, font=("Helvetica", 16), width=15, height=3)
	start_button.pack(pady=20)

	prompt_label = tk.Label(root, font=("Helvetica", 24))
	prompt_label.pack()

	root.bind('<KeyPress>', on_key_press)
	root.bind('<KeyRelease>', on_key_release)
	root.bind('<Escape>', lambda e: root.destroy())

	root.mainloop()