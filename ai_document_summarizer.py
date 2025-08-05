import tkinter as tk
from tkinter import filedialog, messagebox
import os
from dotenv import load_dotenv
from docx import Document
from openai import OpenAI
from PyPDF2 import PdfReader
import textwrap

load_dotenv()  # Load variables from .env
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def load_text_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if not file_path:
        return
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        input_text.delete("1.0", tk.END)
        input_text.insert(tk.END, content)

def load_docx_file():
    file_path = filedialog.askopenfilename(filetypes=[("Word files", "*.docx")])
    if not file_path:
        return
    doc = Document(file_path)
    content = '\n'.join([para.text for para in doc.paragraphs])
    input_text.delete("1.0", tk.END)
    input_text.insert(tk.END, content)

def load_pdf_file():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if not file_path:
        return
    try:
        reader = PdfReader(file_path)
        full_text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                full_text += page_text + "\n"
        input_text.delete("1.0", tk.END)
        input_text.insert(tk.END, full_text.strip())
    except Exception as e:
        messagebox.showerror("PDF Error", f"Failed to load PDF:\n{e}")

def summarize_text():
    text = input_text.get("1.0", tk.END).strip()
    if not text:
        messagebox.showwarning("No Input", "Please load or enter some text to summarize.")
        return

    chunk_size = 12000  # approx 3000 tokens
    chunks = textwrap.wrap(text, width=chunk_size)
    final_summary = ""

    for chunk in chunks:
        prompt = f"Please summarize the following text:\n\n{chunk}\n\nSummary:"
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes text."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=500
            )
            summary = response.choices[0].message.content.strip()
            final_summary += summary + "\n\n"
        except Exception as e:
            messagebox.showerror("API Error", f"An error occurred during summarization:\n{e}")
            return

    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, final_summary.strip())

def clear_text():
    input_text.delete("1.0", tk.END)
    output_text.delete("1.0", tk.END)

def save_summary():
    summary = output_text.get("1.0", tk.END).strip()
    if not summary:
        messagebox.showwarning("No Summary", "No summary available to save.")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if not file_path:
        return
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(summary)
    messagebox.showinfo("Saved", f"Summary saved to:\n{file_path}")

# GUI setup
root = tk.Tk()
root.title("📄 Text & PDF Summarizer with ChatGPT")
root.geometry("900x700")

# Input frame
input_frame = tk.Frame(root)
input_frame.pack(pady=10)

input_label = tk.Label(input_frame, text="📥 Input Text:")
input_label.pack()

input_text = tk.Text(input_frame, height=15, width=100, wrap=tk.WORD)
input_text.pack()

# Output frame
output_frame = tk.Frame(root)
output_frame.pack(pady=10)

output_label = tk.Label(output_frame, text="🧾 Summary:")
output_label.pack()

output_text = tk.Text(output_frame, height=15, width=100, wrap=tk.WORD)
output_text.pack()

# Button frame
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

tk.Button(button_frame, text="📂 Load .txt", command=load_text_file).grid(row=0, column=0, padx=5)
tk.Button(button_frame, text="📄 Load .docx", command=load_docx_file).grid(row=0, column=1, padx=5)
tk.Button(button_frame, text="📕 Load .pdf", command=load_pdf_file).grid(row=0, column=2, padx=5)
tk.Button(button_frame, text="🧠 Summarize with GPT", command=summarize_text).grid(row=0, column=3, padx=5)
tk.Button(button_frame, text="🧹 Clear", command=clear_text).grid(row=0, column=4, padx=5)
tk.Button(button_frame, text="💾 Save Summary", command=save_summary).grid(row=0, column=5, padx=5)

root.mainloop()

