from pynput.keyboard import Key, Controller, Listener
import time
import pyperclip
import keyboard
import threading

controller = Controller()
recursive = False

def wait():
	time.sleep(0.1)

def unset_recursive():
	wait()
	global recursive
	recursive = False

# TODO: vararg?
def press_keys(k1 = None, k2 = None):
	if k1 is not None: controller.press(k1)
	if k2 is not None: controller.press(k2)
	if k2 is not None: controller.release(k2)
	if k1 is not None: controller.release(k1)

def get_highlighted_text():
	original_clipboard = pyperclip.paste()

	pyperclip.copy("")
	wait()
	press_keys(Key.ctrl, 'c')
	wait()
	highlighted_text = pyperclip.paste()
	pyperclip.copy(original_clipboard)

	return highlighted_text

# kirkification algorithm
def set_char(text, i, c):
	return text[:i] + c + text[(i + 1):]

noun_keywords = {}
noun_keywords["a"] = True
noun_keywords["an"] = True
noun_keywords["is"] = True
noun_keywords["im"] = True
noun_keywords["the"] = True
noun_keywords["its"] = True

postfixes = [
	"ing",
	"s",
	"ed",
	"er",
	"nt",
	"ification",
	"illion",
]

def kirkify_word(word, harsh = False):
	kirk = "kirk"

	# postfix detection
	kirk_postfix = ""
	if word.lower() not in noun_keywords:
		for postfix in postfixes:
			word_postfix = word[(len(word) - len(postfix)):]
			has_postfix = word_postfix.lower() == postfix
			if has_postfix:
				word = word[:(len(word) - len(postfix))]
				kirk_postfix = word_postfix
				break

	if not harsh and kirk_postfix == "":
		return word

	# figure out which letters should be capitalized
	word_len = len(word) - 1
	if word_len < 0:
		return kirk_postfix

	for k in range(len(kirk)):
		is_lower = word[min(k, word_len)].islower()
		if not is_lower:
			kirk = set_char(kirk, k, kirk[k].upper())

	return kirk + kirk_postfix

def kirkify(text):
	split_text = text.split()
	new_text = ""
	for i in range(len(split_text)):
		word = split_text[i]
		harsh = False
		if i > 0:
			new_text += " "
			prev_word = split_text[i - 1]
			if prev_word.lower() in noun_keywords and word.lower() not in noun_keywords:
				harsh = True

		new_text += kirkify_word(word, harsh)

	return new_text

def on_press(key):
	global recursive
	if recursive or key != Key.enter:
		return True

	recursive = True
	press_keys(Key.shift, Key.home) # highlight
	prompt = get_highlighted_text()
	if prompt != "":
		print("Kirkifying", prompt)
		prompt = kirkify(prompt)
		controller.type(prompt)

	global enter_block
	keyboard.unblock_key(enter_block)
	press_keys(Key.enter)
	enter_block = keyboard.block_key("enter")

	t = threading.Thread(target = unset_recursive)
	t.start()
	return True

enter_block = keyboard.block_key("enter")
with Listener(on_press = on_press) as listener:
	listener.join()
