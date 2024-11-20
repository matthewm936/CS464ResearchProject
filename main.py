import sys
import csv
import tkinter as tk
import random
import time

# Global variables
NUM_TRIALS = 50
MAX_KEY_COMBO = 8  # Maximum number of keys in a combination
KEY_RESET_DELAY = 400  # Buffer time between trials in milliseconds

# Read in arguments from the command line
if len(sys.argv) < 3:
	print("Usage: python script.py <participant_id> <trial_number> [<seed>]")
	sys.exit(1)

participant_id = sys.argv[1]
trial_number = sys.argv[2]

# Optional seed for reproducibility
seed = None
if len(sys.argv) == 4:
	seed = int(sys.argv[3])
	random.seed(seed)

# Open CSV file in append mode
with open('data.csv', 'a', newline='') as csvfile:
	writer = csv.writer(csvfile)
	writer.writerow(['Participant ID', 'Trial #', 'Avg Time (s)', 'Correctness Rate', 'Key Count'])

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
			# Add modifier keys and ensure unique keys for 2+ key prompts
			modifiers = ['Shift', 'Control']
			selected_keys = set(random.sample(modifiers, 1))  # Start with one modifier key
			selected_keys.update(random.sample("abcdefghijklmnopqrstuvwxyz", num_keys - 1))  # Add unique keys
			
			target_keys = list(selected_keys)

		start_time = time.time()  # Start timer

		# Display target keys prompt
		keys_text = ' + '.join(target_keys)
		prompt_label.config(text=f"Press the keys: {keys_text}")
		prompt_label.pack()

	def normalize_key(key):
		"""Normalize keys to handle left/right variants and shift behavior."""
		if key in ['Shift_L', 'Shift_R']:
			return 'Shift'
		elif key in ['Control_L', 'Control_R']:
			return 'Control'
		elif key in ['Alt_L', 'Alt_R']:
			return 'Alt'
		elif len(key) == 1 and key.isalpha():  # For letters, normalize to lowercase
			return key.lower()
		return key

	def on_key_press(event):
		# Track the currently pressed keys
		normalized_key = normalize_key(event.keysym)
		if normalized_key == 'Shift':
			pressed_keys.add('Shift')  # Explicitly add Shift
		else:
			# Normalize letters to lowercase if Shift is pressed
			if 'Shift' in pressed_keys:
				normalized_key = normalized_key.lower()
			pressed_keys.add(normalized_key)

		# Print the keys pressed and the expected keys
		print(f"Keys pressed by user: {pressed_keys}")
		print(f"Keys expected by program: {set(target_keys)}")

		# Check if the number of pressed keys matches the target
		if len(pressed_keys) == len(target_keys):
			response_time = time.time() - start_time
			log_response(pressed_keys, response_time)

	def on_key_release(event):
		# Remove released key from the set
		normalized_key = normalize_key(event.keysym)
		pressed_keys.discard(normalized_key)


	def log_response(pressed, response_time):
		global correct_responses, total_time, trials_completed

		num_keys = len(target_keys)
		
		# Calculate correctness by ensuring both sets have the same keys (order doesn't matter)
		correct_count = 1 if set(pressed) == set(target_keys) else 0
		correctness_rate = correct_count  # 1 if all keys match, 0 otherwise

		# Print result of comparison
		print(f"Correctness: {'Correct' if correct_count == 1 else 'Incorrect'}")
		print(f"Response time: {response_time:.2f} seconds")

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

		# counts any miss as a combo miss
		combo_accuracy = correct_responses / (trials_completed)  # Overall accuracy based on total key presses
		writer.writerow([participant_id, trial_number, avg_time_overall, combo_accuracy, 'Overall'])

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