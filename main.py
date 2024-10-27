import sys
import csv
import tkinter as tk
import random
import time

# Global variables
NUM_TRIALS = 10
MAX_KEY_COMBO = 3  # Maximum number of keys in a combination
KEY_RESET_DELAY = 500  # Buffer time between trials in milliseconds

# Read in arguments from the command line
if len(sys.argv) < 3:
	print("Usage: python script.py <participant_id> <trial_number>")
	sys.exit(1)

participant_id = sys.argv[1]
trial_number = sys.argv[2]

# Open CSV file in append mode
with open('data.csv', 'a', newline='') as csvfile:
	writer = csv.writer(csvfile)

	# Track overall stats
	correct_responses = 0
	total_time = 0
	trials_completed = 0

	# Track stats for individual key counts
	key_stats = {i: {'correct': 0, 'total_time': 0, 'trials': 0} for i in range(1, MAX_KEY_COMBO + 1)}
	
	pressed_keys = set()  # Track keys currently pressed
	target_keys = []

	def start_experiment():
		instructions = "Press the shown keys as quickly and accurately as possible"
		start_button.config(text=instructions)
		start_button.pack_forget()  # Hide the start button
		prompt_next_key(1)  # Start with single-key prompts

	def prompt_next_key(num_keys):
		global target_keys, start_time, pressed_keys

		# Clear pressed keys and target keys for the new trial
		pressed_keys.clear()
		target_keys.clear()

		# Generate target keys based on the current level
		if num_keys == 1:
			target_keys.append(random.choice("abcdefghijklmnopqrstuvwxyz"))
		else:
			# Add modifier keys and alphabet combinations for 2+ key prompts
			modifiers = ['Shift', 'Control']
			target_keys = [random.choice(modifiers)] + \
						[random.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(num_keys - 1)]

		start_time = time.time()  # Start timer

		# Display target keys prompt
		keys_text = ' + '.join(target_keys)
		prompt_label.config(text=f"Press the keys: {keys_text}")
		prompt_label.pack()

	def on_key_press(event):
		# Track the currently pressed keys
		pressed_keys.add(event.keysym)

		# Check if the number of pressed keys matches the target
		if len(pressed_keys) == len(target_keys):
			response_time = time.time() - start_time
			log_response(pressed_keys, response_time)

	def on_key_release(event):
		# Remove released key from the set
		pressed_keys.discard(event.keysym)

	def log_response(pressed, response_time):
		global correct_responses, total_time, trials_completed

		num_keys = len(target_keys)
		correct_count = sum(1 for key in pressed if key in target_keys)
		correctness_rate = correct_count / num_keys  # Calculate correctness percentage

		# Update stats for the current key count
		key_stats[num_keys]['correct'] += correctness_rate
		key_stats[num_keys]['total_time'] += response_time
		key_stats[num_keys]['trials'] += 1

		correct_responses += correct_count  # Total correct across all trials
		total_time += response_time
		trials_completed += 1

		# Progress to the next trial or end the experiment
		if trials_completed >= NUM_TRIALS:
			report_results()
		else:
			prompt_label.after(KEY_RESET_DELAY, reset_after_trial)

	def reset_after_trial():
		# Reset for the next prompt
		next_key_count = min(1 + trials_completed // (NUM_TRIALS // 3), MAX_KEY_COMBO)
		prompt_next_key(next_key_count)

	def report_results():
		# Report overall results
		avg_time_overall = total_time / NUM_TRIALS
		accuracy_overall = correct_responses / (trials_completed * len(target_keys))  # Overall accuracy based on total key presses
		writer.writerow([participant_id, trial_number, avg_time_overall, accuracy_overall, 'Overall'])

		# Report individual key count results
		for num_keys in range(1, MAX_KEY_COMBO + 1):
			if key_stats[num_keys]['trials'] > 0:
				avg_time = key_stats[num_keys]['total_time'] / key_stats[num_keys]['trials']
				accuracy = key_stats[num_keys]['correct'] / key_stats[num_keys]['trials']  # Average correctness for key count
				writer.writerow([participant_id, trial_number, avg_time, accuracy, num_keys])

		prompt_label.config(text="Experiment complete. Thank you!")
		root.after(2000, root.destroy)  # Close window after 2 seconds

	# Set up the GUI window
	root = tk.Tk()
	root.title("Reaction Time Experiment")
	root.attributes('-fullscreen', True)  # Make the window fullscreen

	# Add start button with instructions
	start_button = tk.Button(root, text="Start", command=start_experiment, font=("Helvetica", 16), width=15, height=3)
	start_button.pack(pady=20)

	# Label to display key prompts
	prompt_label = tk.Label(root, font=("Helvetica", 24))
	prompt_label.pack()

	# Bind key press and release events, and exit on ESC
	root.bind('<KeyPress>', on_key_press)
	root.bind('<KeyRelease>', on_key_release)
	root.bind('<Escape>', lambda e: root.destroy())  # Allow exit with ESC

	# Run the GUI
	root.mainloop()
