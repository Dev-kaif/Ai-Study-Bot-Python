import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox, StringVar
from tkinter.scrolledtext import ScrolledText
from utils.ai_utils import generate_summary, generate_flashcards, generate_quiz
from utils.youtube_utils import get_youtube_transcript
from utils.input_utils import extract_text_from_pdf, extract_text_from_txt
import threading


# === Root Setup ===
root = ttkb.Window(themename="flatly")
root.title("StudyBot - AI Study Assistant")
root.geometry("1024x768")
root.resizable(True, True)

# === Header Section ===
header = ttkb.Frame(root, padding=20)
header.pack(fill=X)
ttkb.Label(header, text="📚 StudyBot", font=("Segoe UI", 28, "bold"), bootstyle="primary").pack(anchor=W)
ttkb.Label(header, text="AI-Powered Study Assistant — Summary • Flashcards • Quiz Generator", font=("Segoe UI", 12), foreground="#555").pack(anchor=W, pady=5)

# === Input Section ===
input_section = ttkb.Labelframe(root, text="📥 Input Material", padding=15, bootstyle="info")
input_section.pack(fill=X, padx=20, pady=10)
input_text = ScrolledText(input_section, height=10, font=("Segoe UI", 11), wrap="word")
input_text.pack(fill=BOTH, expand=True)

# === Input Buttons Section ===
input_buttons = ttkb.Frame(root)
input_buttons.pack(fill=X, padx=20)

def create_button(text, command, style="primary-outline"):
    ttkb.Button(input_buttons, text=text, command=command, bootstyle=style).pack(side=LEFT, padx=6, pady=10)

create_button("📄 PDF", lambda: load_pdf(), "info-outline")
create_button("📜 TXT", lambda: load_txt(), "info-outline")
create_button("📺 YouTube Transcript", lambda: load_youtube(), "info-outline")
create_button("🧹 Clear Input", lambda: input_text.delete("1.0", "end"), "danger-outline")

# === Generation Buttons Section ===
gen_buttons = ttkb.Frame(root)
gen_buttons.pack(fill=X, padx=20, pady=(0, 10))
create_button("Summary", lambda: threaded_task(generate_summary), "success")
create_button("Flashcards", lambda: threaded_task(generate_flashcards), "success")

create_button("Quiz", lambda: threaded_task(generate_quiz), "success")
create_button("Clear Output", lambda: clear_output(), "danger-outline")

# === Output Section ===
output_section = ttkb.Labelframe(root, text="📤 AI Output", padding=15, bootstyle="secondary")
output_section.pack(fill=BOTH, expand=True, padx=20, pady=(5,15))
canvas = ttkb.Canvas(output_section, borderwidth=0)
scrollbar = ttkb.Scrollbar(output_section, orient=VERTICAL, command=canvas.yview)
scrollable_frame = ttkb.Frame(canvas, bootstyle="default")
scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)
canvas.pack(side=LEFT, fill=BOTH, expand=True)
scrollbar.pack(side=RIGHT, fill=Y)

# === Enable Mousepad (Touchpad) Scrolling for Canvas ===
def _on_mousewheel(event):
    canvas.yview_scroll(-1 * int(event.delta / 120), "units")
canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
canvas.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
canvas.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

# === Output Utility Functions ===
def clear_output():
    global quiz_blocks
    quiz_blocks = []
    for widget in scrollable_frame.winfo_children():
        widget.destroy()

def threaded_task(generator_fn):
    def worker():
        text = input_text.get("1.0", "end").strip()
        clear_output()
        if not text:
            add_message("⚠️ Please enter some content first.")
            return
        add_message(f"⏳ Generating {generator_fn.__name__.split('_')[-1].capitalize()}...")
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
    ttkb.Label(scrollable_frame, text=msg, font=("Segoe UI", 12), wraplength=900, justify=LEFT).pack(anchor="w", pady=5)

# === Flashcards Renderer ===
def format_flashcards(raw):
    cards = raw.strip().split("\n")
    q, a = "", ""
    for line in cards:
        line = line.strip()
        if not line:
            continue
        if line.lower().startswith("q"):
            q = line.split(":", 1)[-1].strip()
        elif line.lower().startswith("a"):
            a = line.split(":", 1)[-1].strip()
        if q and a:
            create_flashcard(q, a)
            q, a = "", ""

def create_flashcard(question, answer):
    card = ttkb.Frame(scrollable_frame, padding=10, relief="ridge", bootstyle="light")
    card.pack(fill=X, padx=5, pady=8)
    ttkb.Label(card, text=f"❓ Q: {question}", font=("Segoe UI", 11, "bold"), wraplength=850).pack(anchor="w")
    ttkb.Label(card, text=f"✅ A: {answer}", font=("Segoe UI", 11), wraplength=850).pack(anchor="w", pady=(5, 0))

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
    ttkb.Button(scrollable_frame, text="✅ Submit Quiz", command=evaluate_quiz, bootstyle="success").pack(pady=10)

def create_quiz_block(num, question, options):
    block = ttkb.Frame(scrollable_frame, padding=12, relief="ridge", bootstyle="light")
    block.pack(fill=X, padx=10, pady=10)
    ttkb.Label(block, text=f"📝 Question {num}: {question}", font=("Segoe UI", 11, "bold"), wraplength=850).pack(anchor="w", pady=5)
    selected = StringVar()
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
        btn = ttkb.Radiobutton(block, text=opt, variable=selected, value=opt)
        btn.pack(anchor="w", padx=15, pady=2)
        buttons.append(btn)
    feedback = ttkb.Label(block, text="", font=("Segoe UI", 11))
    feedback.pack(anchor="w", padx=10, pady=5)
    quiz_blocks.append({
        "question": question,
        "correct": correct_option,
        "selected_var": selected,
        "feedback_label": feedback,
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
            label.config(text="✅ Correct", foreground="green")
        else:
            label.config(text=f"❌ Incorrect — Correct: {correct}", foreground="red")
    messagebox.showinfo("Quiz Result", f"You got {score} out of {total} correct!")

# === File Loaders ===
def load_pdf():
    path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if path:
        text = extract_text_from_pdf(path)
        input_text.delete("1.0", "end")
        input_text.insert("end", text)

def load_txt():
    path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if path:
        text = extract_text_from_txt(path)
        input_text.delete("1.0", "end")
        input_text.insert("end", text)

def load_youtube():
    def fetch():
        url = entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL.")
            return
        try:
            text = get_youtube_transcript(url)
            input_text.delete("1.0", "end")
            input_text.insert("end", text)
            popup.destroy()
        except Exception as e:
            messagebox.showerror("Failed", f"Could not fetch transcript:\n{e}")
    popup = ttkb.Toplevel(root)
    popup.title("🎥 YouTube Transcript")
    popup.geometry("420x150")
    ttkb.Label(popup, text="Enter YouTube Video URL:").pack(pady=10)
    entry = ttkb.Entry(popup, width=55)
    entry.pack(pady=5)
    ttkb.Button(popup, text="Fetch Transcript", command=fetch, bootstyle="primary").pack(pady=10)

# === Run App ===
root.mainloop()