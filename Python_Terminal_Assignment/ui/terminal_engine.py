# import tkinter as tk
# from tkinter import scrolledtext
# from terminal import PythonTerminal

# class TerminalUI:
#     def __init__(self, master):
#         self.master = master
#         master.title("Python Terminal UI")
#         master.geometry("900x500")
#         master.configure(bg="black")

#         # Backend terminal
#         self.terminal = PythonTerminal()

#         # Scrollable output
#         self.output_box = scrolledtext.ScrolledText(
#             master, wrap=tk.WORD, font=("Consolas", 11),
#             bg="black", fg="white", insertbackground="white"
#         )
#         self.output_box.pack(expand=True, fill='both')
#         self.output_box.configure(state='disabled')

#         # Input box
#         self.entry = tk.Entry(master, font=("Consolas", 11), bg="black", fg="white", insertbackground="white")
#         self.entry.pack(fill='x')
#         self.entry.bind("<Return>", self.run_command)
#         self.entry.bind("<Up>", self.history_up)
#         self.entry.bind("<Down>", self.history_down)
#         self.entry.focus()

#         # Command history
#         self.history = []
#         self.history_index = -1

#         # Show initial prompt
#         self.show_prompt()

#     def show_prompt(self):
#         """Display the dynamic prompt"""
#         prompt_text = self.terminal.get_prompt()
#         if ':' in prompt_text:
#             user_host, current_dir = prompt_text.split(':', 1)
#         else:
#             user_host, current_dir = prompt_text, ""

#         self.append_output(user_host + ":", color="green", end="")
#         self.append_output(current_dir + "$ ", color="blue", end="")

#     def run_command(self, event=None):
#         command = self.entry.get().strip()
#         if not command:
#             self.show_prompt()
#             return

#         # Add to history
#         self.history.append(command)
#         self.history_index = len(self.history)

#         # Display command in output
#         self.append_output(command, color="white", end="\n")

#         # Execute the command
#         output = self.terminal.execute_command(command)

#         if output == "EXIT":
#             self.append_output("Goodbye!", color="red")
#             self.master.quit()
#         else:
#             # Color errors red
#             if "Error:" in output or "No such file" in output or "invalid" in output:
#                 self.append_output(output, color="red")
#             else:
#                 self.append_output(output, color="white")

#         self.entry.delete(0, tk.END)
#         self.show_prompt()

#     def append_output(self, text, color="white", end="\n"):
#         """Append text to the output box with color"""
#         self.output_box.configure(state='normal')
#         self.output_box.insert(tk.END, text + end)
#         self.output_box.tag_add("color", "end-1c linestart", "end-1c lineend")
#         self.output_box.tag_config("color", foreground=color)
#         self.output_box.see(tk.END)
#         self.output_box.configure(state='disabled')

#     def history_up(self, event):
#         if self.history:
#             self.history_index = max(0, self.history_index - 1)
#             self.entry.delete(0, tk.END)
#             self.entry.insert(0, self.history[self.history_index])

#     def history_down(self, event):
#         if self.history:
#             self.history_index = min(len(self.history) - 1, self.history_index + 1)
#             self.entry.delete(0, tk.END)
#             if self.history_index < len(self.history):
#                 self.entry.insert(0, self.history[self.history_index])
#             else:
#                 self.entry.insert(0, "")

# def main():
#     root = tk.Tk()
#     app = TerminalUI(root)
#     root.mainloop()

# if __name__ == "__main__":
#     main()








import tkinter as tk
from tkinter import scrolledtext
# CHANGE: The import now correctly points to the renamed engine file
from terminal_engine import PythonTerminal

# Define color themes
THEMES = {
    "dark": {
        "bg": "black",
        "fg": "white",
        "input_bg": "#1e1e1e",
        "insert_bg": "white", # Cursor color
        "sash_bg": "black",
        "green": "#4E9A06",
        "blue": "#3465A4",
        "red": "#CC0000"
    },
    "light": {
        "bg": "#f0f0f0",
        "fg": "black",
        "input_bg": "#ffffff",
        "insert_bg": "black", # Cursor color
        "sash_bg": "#f0f0f0",
        "green": "#008000",
        "blue": "#0000FF",
        "red": "#FF0000"
    }
}

class TerminalUI:
    def __init__(self, master):
        self.master = master
        master.title("Python Terminal UI")
        master.geometry("900x500")

        self.terminal = PythonTerminal()
        self.current_theme = "dark"

        self.paned_window = tk.PanedWindow(
            master, orient=tk.VERTICAL, sashrelief=tk.RAISED, sashwidth=5
        )
        self.paned_window.pack(expand=True, fill='both')

        self.output_box = scrolledtext.ScrolledText(
            self.paned_window, wrap=tk.WORD, font=("Consolas", 11),
            relief="flat", borderwidth=0
        )
        self.output_box.configure(state='disabled')
        self.paned_window.add(self.output_box, minsize=100)

        input_frame = tk.Frame(self.paned_window)
        
        self.input_box = tk.Text(
            input_frame,
            height=1, # Set initial height to 1 line
            font=("Consolas", 11),
            relief="flat",
            wrap=tk.WORD
        )
        self.input_box.pack(expand=True, fill="both", pady=(5, 8), padx=8)
        self.input_box.bind("<Return>", self.run_command_handler)
        self.input_box.bind("<Shift-Return>", self.insert_newline)
        self.input_box.bind("<Up>", self.history_up)
        self.input_box.bind("<Down>", self.history_down)
        self.input_box.bind("<KeyRelease>", self.adjust_input_height)
        self.input_box.focus()

        self.paned_window.add(input_frame, minsize=45, stretch="never")
        
        self.history = []
        self.history_index = -1

        self.apply_theme(self.current_theme)
        self.show_prompt()

    def apply_theme(self, theme_name):
        """Applies the selected color theme to all UI elements."""
        theme = THEMES[theme_name]
        self.master.config(bg=theme["bg"])
        self.paned_window.config(bg=theme["sash_bg"])
        
        self.output_box.config(
            bg=theme["bg"], fg=theme["fg"], insertbackground=theme["insert_bg"]
        )
        self.output_box.tag_config("green", foreground=theme["green"])
        self.output_box.tag_config("blue", foreground=theme["blue"])
        self.output_box.tag_config("red", foreground=theme["red"])
        self.output_box.tag_config("white", foreground=theme["fg"])
        
        self.input_box.master.config(bg=theme["bg"])
        self.input_box.config(
            bg=theme["input_bg"], fg=theme["fg"], insertbackground=theme["insert_bg"]
        )

    def toggle_theme(self):
        """Switches between dark and light themes."""
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.apply_theme(self.current_theme)
        return f"Theme changed to {self.current_theme} mode."

    def adjust_input_height(self, event=None):
        """Auto-adjusts the input box height based on the number of lines."""
        current_lines = int(self.input_box.index('end-1c').split('.')[0])
        new_height = max(1, min(current_lines, 10))
        
        if self.input_box.cget("height") != new_height:
            self.input_box.config(height=new_height)

    def show_prompt(self):
        """Display the dynamic prompt based on the current mode."""
        prompt_text = self.terminal.get_prompt()
        
        # Handle Python REPL prompt
        if self.terminal.mode == 'python':
            self.append_output(prompt_text, tag="white", end="")
            return

        # Handle shell prompt
        if ':' in prompt_text:
            user_host, current_dir = prompt_text.split(':', 1)
        else:
            user_host, current_dir = prompt_text, ""
        self.append_output(user_host + ":", tag="green", end="")
        self.append_output(current_dir, tag="blue", end="")

    def run_command_handler(self, event=None):
        self.run_command()
        return "break"

    def insert_newline(self, event=None):
        self.input_box.insert(tk.INSERT, "\n")
        self.adjust_input_height()
        return "break"

    def run_command(self, event=None):
        command = self.input_box.get("1.0", "end-1c").strip()
        
        # Don't add empty commands from Python REPL to history
        if self.terminal.mode != 'python':
             self.append_output(command + "\n", tag="white", end="")
        else:
             self.append_output("\n", tag="white", end="")


        # Special handling for UI commands that work in any mode
        if command.lower() == "theme":
            output = self.toggle_theme()
            self.append_output(output + "\n", tag="green")
            self.input_box.delete("1.0", tk.END)
            self.show_prompt()
            self.adjust_input_height()
            return
            
        if self.terminal.mode == 'shell' and not command:
            self.show_prompt()
            return

        if self.terminal.mode == 'shell':
            self.history.append(command)
            self.history_index = len(self.history)

        output = self.terminal.execute_command(command)

        if output == "EXIT":
            self.append_output("Goodbye!", tag="red")
            self.master.after(500, self.master.quit)
            return
        
        if output: # Only print if there is output
            tag = "red" if any(err in output for err in ["Error:", "No such file", "invalid"]) else "white"
            self.append_output(output + "\n", tag=tag)

        self.input_box.delete("1.0", tk.END)
        self.show_prompt()
        self.adjust_input_height()

    def append_output(self, text, tag="white", end="\n"):
        self.output_box.configure(state='normal')
        start_index = self.output_box.index(tk.END + "-1c")
        self.output_box.insert(tk.END, text + end)
        end_index = self.output_box.index(tk.END + "-1c")
        if start_index != end_index: # Only add tag if text was actually inserted
            self.output_box.tag_add(tag, start_index, end_index)
        self.output_box.see(tk.END)
        self.output_box.configure(state='disabled')

    def history_up(self, event):
        if self.terminal.mode == 'shell' and self.history:
            self.history_index = max(0, self.history_index - 1)
            self.input_box.delete("1.0", tk.END)
            self.input_box.insert("1.0", self.history[self.history_index])
            self.adjust_input_height()
        return "break"

    def history_down(self, event):
        if self.terminal.mode == 'shell' and self.history:
            if self.history_index < len(self.history) - 1:
                self.history_index += 1
                self.input_box.delete("1.0", tk.END)
                self.input_box.insert("1.0", self.history[self.history_index])
            else:
                self.history_index = len(self.history)
                self.input_box.delete("1.0", tk.END)
            self.adjust_input_height()
        return "break"

def main():
    root = tk.Tk()
    app = TerminalUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
