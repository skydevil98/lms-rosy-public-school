import tkinter as tk
from tkinter import messagebox

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("My Tasks")
        self.root.geometry("450x650")
        self.root.configure(bg="#f5f5f5")
        
        # Data Handling - Store tasks only in memory (Python list)
        self.tasks = []
        
        # Design Style & Typography
        self.font_title = ("Helvetica", 24, "bold")
        self.font_normal = ("Helvetica", 14)
        self.font_btn = ("Helvetica", 13, "bold")
        
        self.color_bg = "#f5f5f5"         # Light gray background
        self.color_card = "#ffffff"       # White "card-like" sections
        self.color_text = "#333333"       # Dark text
        self.color_border = "#e0e0e0"     # Light gray border
        self.color_primary = "#007aff"    # Modern blue for selection highlight
        
        # Setup Layout
        self._build_ui()
        self._update_ui_state()

    def _build_ui(self):
        # Header Section
        title_label = tk.Label(self.root, text="My Tasks", font=self.font_title, bg=self.color_bg, fg=self.color_text)
        title_label.pack(pady=(30, 20))

        # Main Card Layout inside the root window
        card_frame = tk.Frame(self.root, bg=self.color_card, highlightbackground=self.color_border, highlightthickness=1)
        card_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=(0, 25))

        # --- Input Section ---
        input_frame = tk.Frame(card_frame, bg=self.color_card)
        input_frame.pack(fill=tk.X, padx=20, pady=(25, 15))

        # Simulate a cleaner, flat border for the entry widget
        entry_border = tk.Frame(input_frame, bg=self.color_border, padx=1, pady=1)
        entry_border.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.task_entry = tk.Entry(entry_border, font=self.font_normal, borderwidth=0, relief="flat", highlightthickness=0, bg="#fafafa")
        self.task_entry.pack(fill=tk.X, expand=True, ipady=8, padx=8)
        self.task_entry.bind("<Return>", lambda event: self.add_task())

        # Add Button Layout
        self.add_btn = tk.Button(input_frame, text="Add", font=self.font_btn, command=self.add_task, relief="flat", borderwidth=0, cursor="hand2")
        self.add_btn.pack(side=tk.RIGHT, ipady=4, ipadx=10)
        self._add_hover_effect(self.add_btn)

        # --- List Area Section ---
        list_frame = tk.Frame(card_frame, bg=self.color_card)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20)

        list_border = tk.Frame(list_frame, bg=self.color_border, padx=1, pady=1)
        list_border.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.listbox = tk.Listbox(
            list_border, 
            font=self.font_normal, 
            selectbackground=self.color_primary, 
            selectforeground="#ffffff", 
            borderwidth=0, 
            relief="flat", 
            highlightthickness=0, 
            activestyle="none",
            bg="#ffffff",
            fg=self.color_text
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2, pady=2)
        self.listbox.bind("<<ListboxSelect>>", self._on_select)

        # Scrollbar for Listbox
        scrollbar = tk.Scrollbar(list_border, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)

        # --- Footer Actions Area ---
        actions_frame = tk.Frame(card_frame, bg=self.color_card)
        actions_frame.pack(fill=tk.X, padx=20, pady=25)

        self.edit_btn = tk.Button(actions_frame, text="Edit", font=self.font_btn, command=self.edit_task, relief="flat", borderwidth=0, cursor="hand2")
        self.edit_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5), ipady=5)
        self._add_hover_effect(self.edit_btn)

        self.delete_btn = tk.Button(actions_frame, text="Delete", font=self.font_btn, command=self.delete_task, relief="flat", borderwidth=0, cursor="hand2")
        self.delete_btn.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(5, 0), ipady=5)
        self._add_hover_effect(self.delete_btn)

    def _add_hover_effect(self, btn):
        """Add a subtle hover effect to a button if not disabled."""
        orig_color = btn.cget("background")
        
        def on_enter(e):
            if btn['state'] == tk.NORMAL:
                btn['background'] = "#e5e5ea"
                
        def on_leave(e):
            if btn['state'] == tk.NORMAL:
                btn['background'] = orig_color
                
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    def _on_select(self, event):
        """Handle listbox selection changes"""
        self._update_ui_state()

    def _update_ui_state(self):
        """UX Behavior: Enable or disable Edit/Delete buttons if a task is selected."""
        if self.listbox.curselection():
            self.edit_btn.config(state=tk.NORMAL)
            self.delete_btn.config(state=tk.NORMAL)
        else:
            self.edit_btn.config(state=tk.DISABLED)
            self.delete_btn.config(state=tk.DISABLED)

    def add_task(self):
        """Add a new task to the list and memory."""
        task_text = self.task_entry.get().strip()
        if task_text:
            self.tasks.append(task_text)
            self.listbox.insert(tk.END, task_text)
            # UX Behavior: Clear input field after adding a task
            self.task_entry.delete(0, tk.END)
            self._update_ui_state()
        else:
            messagebox.showwarning("Warning", "Task cannot be empty!")

    def edit_task(self):
        """Open a popup to edit the selected task."""
        selected_index = self.listbox.curselection()
        if not selected_index:
            return
            
        index = selected_index[0]
        current_task = self.tasks[index]

        # Standard Tkinter pop-up for editing
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Task")
        edit_window.geometry("350x200")
        edit_window.configure(bg=self.color_bg)
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        # Center the edit window relative to the main window
        edit_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 175
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 100
        edit_window.geometry(f"+{x}+{y}")

        title_label = tk.Label(edit_window, text="Update Task:", font=self.font_normal, bg=self.color_bg, fg=self.color_text)
        title_label.pack(pady=(25, 10))

        # Entry outline style
        entry_border = tk.Frame(edit_window, bg=self.color_border, padx=1, pady=1)
        entry_border.pack(fill=tk.X, padx=30)
        
        edit_entry = tk.Entry(entry_border, font=self.font_normal, borderwidth=0, relief="flat", highlightthickness=0, bg="#ffffff")
        edit_entry.pack(fill=tk.X, expand=True, ipady=8, padx=8)
        edit_entry.insert(0, current_task)
        edit_entry.focus()

        def save_edit(event=None):
            new_task = edit_entry.get().strip()
            if new_task:
                # Update in memory
                self.tasks[index] = new_task
                # Update UI list
                self.listbox.delete(index)
                self.listbox.insert(index, new_task)
                self.listbox.selection_set(index)
                edit_window.destroy()
            else:
                messagebox.showwarning("Warning", "Task cannot be empty!", parent=edit_window)

        edit_entry.bind("<Return>", save_edit)

        save_btn = tk.Button(edit_window, text="Save Task", font=self.font_btn, command=save_edit, relief="flat", borderwidth=0, cursor="hand2")
        save_btn.pack(pady=20, ipady=4, ipadx=10)
        self._add_hover_effect(save_btn)

    def delete_task(self):
        """Delete the selected task from memory and the listbox."""
        selected_index = self.listbox.curselection()
        if not selected_index:
            return
            
        index = selected_index[0]
        # Delete from memory
        del self.tasks[index]
        # Delete from UI listbox
        self.listbox.delete(index)
        self._update_ui_state()

if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()
