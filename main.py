import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk, filedialog
import threading
from utils.ai_utils import generate_summary, generate_flashcards, generate_quiz
from utils.youtube_utils import get_youtube_transcript
from utils.input_utils import extract_text_from_pdf, extract_text_from_txt



# === Theme Setup ===
BG_COLOR = "#f1f3f5"
HEADER_BG = "#343a40"
HEADER_FG = "#ffffff"
TEXT_COLOR = "#212529"
BUTTON_BG = "#007bff"
BUTTON_FG = "#ffffff"
FONT_FAMILY = "Segoe UI"
FLASHCARD_BG = "#ffffff"
FLASHCARD_BORDER = "#ced4da"

# === Root Setup ===
root = tk.Tk()
root.title("StudyBot - AI Study Assistant")
root.geometry("850x700")
root.configure(bg=BG_COLOR)

# === Header ===
header = tk.Frame(root, bg=HEADER_BG, height=60)
header.pack(fill="x")
title_label = tk.Label(
    header,
    text="StudyBot - Your AI Study Assistant",
    font=(FONT_FAMILY, 20, "bold"),
    bg=HEADER_BG,
    fg=HEADER_FG,
    pady=10
)
title_label.pack()

# === Input Label ===
input_label = tk.Label(
    root,
    text="Enter your study material:",
    font=(FONT_FAMILY, 12, "bold"),
    bg=BG_COLOR,
    fg=TEXT_COLOR
)
input_label.pack(anchor="w", padx=20, pady=(20, 5))

# === Input Area ===
input_text = scrolledtext.ScrolledText(root, height=10, wrap=tk.WORD, font=(FONT_FAMILY, 12))
input_text.pack(fill="both", expand=False, padx=20, pady=(0, 10))

# === Button Frame ===
button_frame = tk.Frame(root, bg=BG_COLOR)
button_frame.pack(pady=10)

def create_styled_button(text, command, col, row=0):
    return tk.Button(
        button_frame,
        text=text,
        command=command,
        font=(FONT_FAMILY, 11, "bold"),
        bg=BUTTON_BG,
        fg=BUTTON_FG,
        width=20,
        activebackground="#0056b3",
        relief="raised",
        bd=2
    ).grid(row=row, column=col, padx=12, pady=5)

create_styled_button("Generate Summary", lambda: threaded_task(generate_summary), 0)
create_styled_button("Generate Flashcards", lambda: threaded_task(generate_flashcards), 1)
create_styled_button("Generate Quiz", lambda: threaded_task(generate_quiz), 2)
create_styled_button("Clear Input", lambda: input_text.delete("1.0", tk.END), 0, row=1)
create_styled_button("Clear Output", lambda: clear_output(), 1, row=1)
create_styled_button("Import PDF", lambda: load_pdf(), 0, row=2)
create_styled_button("Import TXT", lambda: load_txt(), 1, row=2)
create_styled_button("Import YouTube", lambda: load_youtube(), 2, row=2)

# === Output Label ===
output_label = tk.Label(
    root,
    text="Output:",
    font=(FONT_FAMILY, 12, "bold"),
    bg=BG_COLOR,
    fg=TEXT_COLOR
)
output_label.pack(anchor="w", padx=20, pady=(20, 5))

# === Output Frame for Scrollable Results ===
output_frame = tk.Frame(root, bg=BG_COLOR)
output_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

canvas = tk.Canvas(output_frame, bg=BG_COLOR, highlightthickness=0)
scrollbar = ttk.Scrollbar(output_frame, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas, bg=BG_COLOR)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

def enable_touchpad_scroll(widget):
    widget.bind_all("<MouseWheel>", lambda e: widget.yview_scroll(int(-1*(e.delta/120)), "units"))
    widget.bind_all("<Button-4>", lambda e: widget.yview_scroll(-1, "units"))  # Linux scroll up
    widget.bind_all("<Button-5>", lambda e: widget.yview_scroll(1, "units"))   # Linux scroll down

enable_touchpad_scroll(input_text)
enable_touchpad_scroll(canvas)

def clear_output():
    global quiz_blocks
    quiz_blocks = []
    for widget in scrollable_frame.winfo_children():
        widget.destroy()

def threaded_task(generator_fn):
    def worker():
        text = input_text.get("1.0", tk.END).strip()
        clear_output()

        if not text:
            add_message("⚠️ Please enter some content first.")
            return

        if generator_fn == generate_summary:
            add_message("⏳ Generating summary...")
        elif generator_fn == generate_flashcards:
            add_message("⏳ Generating flashcards...")
        elif generator_fn == generate_quiz:
            add_message("⏳ Generating quiz...")

        raw_output = generator_fn(text)
        clear_output()

        if generator_fn == generate_flashcards:
            format_flashcards(raw_output)
        elif generator_fn == generate_quiz:
            format_quiz(raw_output)
        else:
            add_message(raw_output)

    threading.Thread(target=worker).start()

def add_message(msg):
    label = tk.Label(
        scrollable_frame,
        text=msg,
        font=(FONT_FAMILY, 12),
        bg=BG_COLOR,
        fg=TEXT_COLOR,
        wraplength=780,
        justify="left",
        anchor="w"
    )
    label.pack(anchor="w", pady=5)

def format_flashcards(raw):
    cards = raw.strip().split("\n")
    q, a = "", ""
    for line in cards:
        line = line.strip()
        if not line:
            continue
        if line.lower().startswith("q") or line.lower().startswith("question"):
            q = line.split(":", 1)[-1].strip()
        elif line.lower().startswith("a") or line.lower().startswith("answer"):
            a = line.split(":", 1)[-1].strip()
        if q and a:
            create_flashcard(q, a)
            q, a = "", ""

def create_flashcard(question, answer):
    card = tk.Frame(scrollable_frame, bg=FLASHCARD_BG, bd=2, relief="groove")
    card.pack(fill="x", padx=10, pady=10, anchor="w")
    tk.Label(card, text="Q: " + question, font=(FONT_FAMILY, 11, "bold"), bg=FLASHCARD_BG, wraplength=750, justify="left").pack(anchor="w", pady=(5, 2), padx=10)
    tk.Label(card, text="A: " + answer, font=(FONT_FAMILY, 11), bg=FLASHCARD_BG, wraplength=750, justify="left").pack(anchor="w", pady=(0, 5), padx=10)

# === Quiz System ===
quiz_blocks = []

def format_quiz(raw):
    global quiz_blocks
    quiz_blocks.clear()
    lines = raw.strip().split("\n")
    q = ""
    options = []
    count = 1

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line[0].isdigit() and "." in line:
            if q:
                create_quiz_block(count, q, options)
                count += 1
                options = []
            q = line.split(".", 1)[1].strip()
        elif any(line.lower().startswith(o) for o in ["a)", "b)", "c)", "d)"]):
            options.append(line)
    if q:
        create_quiz_block(count, q, options)

    tk.Button(
        scrollable_frame,
        text="Submit Quiz",
        command=evaluate_quiz,
        bg=BUTTON_BG,
        fg="#ffffff",
        font=(FONT_FAMILY, 12, "bold"),
        relief="raised"
    ).pack(pady=10)

def create_quiz_block(num, question, options):
    block = tk.Frame(scrollable_frame, bg="#ffffff", bd=2, relief="groove")
    block.pack(fill="x", padx=10, pady=10, anchor="w")

    tk.Label(
        block,
        text=f"Question {num}: {question}",
        font=(FONT_FAMILY, 11, "bold"),
        bg="#ffffff",
        wraplength=750,
        justify="left"
    ).pack(anchor="w", padx=10, pady=5)

    selected = tk.StringVar()
    buttons = []

    correct_option = None
    cleaned_options = []
    for opt in options:
        if "*" in opt:
            correct_option = opt.replace("*", "").strip()
            cleaned_options.append(correct_option)
        else:
            cleaned_options.append(opt)

    if not correct_option and cleaned_options:
        correct_option = cleaned_options[0]

    for opt in cleaned_options:
        btn = tk.Radiobutton(
            block,
            text=opt,
            variable=selected,
            value=opt,
            font=(FONT_FAMILY, 11),
            bg="#ffffff",
            anchor="w",
            wraplength=750,
            justify="left"
        )
        btn.pack(anchor="w", padx=25, pady=2)
        buttons.append(btn)

    feedback_label = tk.Label(block, text="", font=(FONT_FAMILY, 11), bg="#ffffff")
    feedback_label.pack(anchor="w", padx=10, pady=5)

    quiz_blocks.append({
        "question": question,
        "correct": correct_option,
        "selected_var": selected,
        "feedback_label": feedback_label,
        "radio_buttons": buttons
    })

def evaluate_quiz():
    score = 0
    total = len(quiz_blocks)
    for q in quiz_blocks:
        selected = q["selected_var"].get()
        correct = q["correct"]
        label = q["feedback_label"]

        for btn in q["radio_buttons"]:
            btn.config(state="disabled")

        if selected == correct:
            score += 1
            label.config(text="✅ Correct", fg="green")
        else:
            correct_display = correct if correct else "Unknown (not marked)"
            label.config(text=f"❌ Incorrect. Correct Answer: {correct_display}", fg="red")

    messagebox.showinfo("Quiz Result", f"You got {score} out of {total} correct!")

# === Input Loaders ===
def load_pdf():
    path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if path:
        text = extract_text_from_pdf(path)
        input_text.delete("1.0", tk.END)
        input_text.insert(tk.END, text)

def load_txt():
    path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if path:
        text = extract_text_from_txt(path)
        input_text.delete("1.0", tk.END)
        input_text.insert(tk.END, text)


def load_youtube():
    def fetch():
        url = yt_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL.")
            return
        try:
            text = get_youtube_transcript(url)
            input_text.delete("1.0", tk.END)
            input_text.insert(tk.END, text)
            yt_popup.destroy()
        except Exception as e:
            messagebox.showerror("Failed", f"Could not fetch transcript:\n{e}")

    yt_popup = tk.Toplevel(root)
    yt_popup.title("YouTube Transcript")
    yt_popup.geometry("400x150")
    tk.Label(yt_popup, text="Enter YouTube Video URL:").pack(pady=10)
    yt_entry = tk.Entry(yt_popup, width=50)
    yt_entry.pack(pady=5)
    tk.Button(yt_popup, text="Fetch Transcript", command=fetch).pack(pady=10)



# === Run App ===
root.mainloop()