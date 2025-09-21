import tkinter as tk
from tkinter import scrolledtext
from terminal import PythonTerminal

class TerminalUI:
    def __init__(self, master):
        self.master = master
        master.title("Python Terminal UI")
        master.geometry("900x500")
        master.configure(bg="black")

        # Backend terminal
        self.terminal = PythonTerminal()

        # Scrollable output
        self.output_box = scrolledtext.ScrolledText(
            master, wrap=tk.WORD, font=("Consolas", 11),
            bg="black", fg="white", insertbackground="white"
        )
        self.output_box.pack(expand=True, fill='both')
        self.output_box.configure(state='disabled')

        # Input box
        self.entry = tk.Entry(master, font=("Consolas", 11), bg="black", fg="white", insertbackground="white")
        self.entry.pack(fill='x')
        self.entry.bind("<Return>", self.run_command)
        self.entry.bind("<Up>", self.history_up)
        self.entry.bind("<Down>", self.history_down)
        self.entry.focus()

        # Command history
        self.history = []
        self.history_index = -1

        # Show initial prompt
        self.show_prompt()

    def show_prompt(self):
        """Display the dynamic prompt"""
        prompt_text = self.terminal.get_prompt()
        if ':' in prompt_text:
            user_host, current_dir = prompt_text.split(':', 1)
        else:
            user_host, current_dir = prompt_text, ""

        self.append_output(user_host + ":", color="green", end="")
        self.append_output(current_dir + "$ ", color="blue", end="")

    def run_command(self, event=None):
        command = self.entry.get().strip()
        if not command:
            self.show_prompt()
            return

        # Add to history
        self.history.append(command)
        self.history_index = len(self.history)

        # Display command in output
        self.append_output(command, color="white", end="\n")

        # Execute the command
        output = self.terminal.execute_command(command)

        if output == "EXIT":
            self.append_output("Goodbye!", color="red")
            self.master.quit()
        else:
            # Color errors red
            if "Error:" in output or "No such file" in output or "invalid" in output:
                self.append_output(output, color="red")
            else:
                self.append_output(output, color="white")

        self.entry.delete(0, tk.END)
        self.show_prompt()

    def append_output(self, text, color="white", end="\n"):
        """Append text to the output box with color"""
        self.output_box.configure(state='normal')
        self.output_box.insert(tk.END, text + end)
        self.output_box.tag_add("color", "end-1c linestart", "end-1c lineend")
        self.output_box.tag_config("color", foreground=color)
        self.output_box.see(tk.END)
        self.output_box.configure(state='disabled')

    def history_up(self, event):
        if self.history:
            self.history_index = max(0, self.history_index - 1)
            self.entry.delete(0, tk.END)
            self.entry.insert(0, self.history[self.history_index])

    def history_down(self, event):
        if self.history:
            self.history_index = min(len(self.history) - 1, self.history_index + 1)
            self.entry.delete(0, tk.END)
            if self.history_index < len(self.history):
                self.entry.insert(0, self.history[self.history_index])
            else:
                self.entry.insert(0, "")

def main():
    root = tk.Tk()
    app = TerminalUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
