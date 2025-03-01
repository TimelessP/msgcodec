import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
import platform
import subprocess

# For Windows registry access.
if platform.system() == "Windows":
    try:
        import winreg
    except ImportError:
        winreg = None

def message_encode(text: str) -> str:
    return text[::-1]  # Example: Reverse the text

def message_decode(text: str) -> str:
    return text[::-1]  # Example: Reverse back the text

def get_system_theme() -> str:
    """Returns 'dark' or 'light' based on the OS settings."""
    system = platform.system()
    try:
        if system == "Windows" and winreg:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize") as key:
                apps_use_light = winreg.QueryValueEx(key, "AppsUseLightTheme")[0]
                return "light" if apps_use_light == 1 else "dark"
        elif system == "Darwin":
            result = subprocess.run(["defaults", "read", "-g", "AppleInterfaceStyle"],
                                    capture_output=True, text=True)
            if "Dark" in result.stdout:
                return "dark"
            else:
                return "light"
        else:
            return "light"
    except Exception:
        return "light"

class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.inner_frame = tk.Frame(self.canvas)
        self.inner_frame.bind("<Configure>", 
                              lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
    
    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)
    
    def _on_mousewheel(self, event):
        if event.delta:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        elif event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")
    
    def _bind_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)
    
    def _unbind_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

class EncoderDecoderApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Encoder & Decoder App")
        self.root.geometry("600x400")
        self.message_lines = []
        self.default_font = tkFont.nametofont("TkDefaultFont")
        system = platform.system()
        if system == "Windows":
            candidates = ["Consolas", "Courier New", "Lucida Console"]
        elif system == "Darwin":
            candidates = ["Menlo", "Monaco", "Courier"]
        else:
            candidates = ["DejaVu Sans Mono", "Liberation Mono", "Courier New", "Courier"]
        available = next((f for f in candidates if f in tkFont.families()), "TkFixedFont")
        self.input_font = tkFont.Font(family=available, size=self.default_font.cget("size") * 2)
        button_texts = ["Encode", "Decode", "Delete"]
        self.global_button_pixel_width = max(self.default_font.measure(text) for text in button_texts)
        avg_char_width = self.default_font.measure("0")
        self.global_button_text_units = max(1, int(self.global_button_pixel_width / avg_char_width) + 2)
        self.scroll_frame = ScrollableFrame(self.root)
        self.scroll_frame.pack(fill="both", expand=True)
        self.theme_mode = get_system_theme()
        self.update_theme_colors()
        self.root.after(2000, self.check_theme)
        self.add_message_line()
    
    def update_theme_colors(self):
        if self.theme_mode == "light":
            self.unfocused_bg = "#ffffff"
            self.focused_bg = "#e0e0e0"
        else:
            self.unfocused_bg = "#303030"
            self.focused_bg = "#505050"
    
    def check_theme(self):
        new_theme = get_system_theme()
        if new_theme != self.theme_mode:
            self.theme_mode = new_theme
            self.update_theme_colors()
            for line in self.message_lines:
                line.update_background(line.focused)
        self.root.after(2000, self.check_theme)
    
    def add_message_line(self, text: str = "", after: "MessageLine" = None):
        new_line = MessageLine(self, self.scroll_frame.inner_frame, text, self.input_font)
        new_line.set_background(self.unfocused_bg)
        if after is None:
            new_line.container.pack(fill="x", padx=5, pady=5)
            self.message_lines.append(new_line)
        else:
            index = self.message_lines.index(after)
            self.message_lines.insert(index + 1, new_line)
            if index + 2 < len(self.message_lines):
                next_line = self.message_lines[index + 2]
                new_line.container.pack(fill="x", padx=5, pady=5, before=next_line.container)
            else:
                new_line.container.pack(fill="x", padx=5, pady=5)
        new_line.set_buttons_width(self.global_button_text_units)
        self.root.after(100, lambda: self.scroll_to_widget(new_line.container))
        new_line.focus_text()
    
    def remove_message_line(self, line: "MessageLine"):
        if line in self.message_lines:
            index = self.message_lines.index(line)
            line.destroy()
            del self.message_lines[index]
            if self.message_lines:
                new_focus = self.message_lines[index - 1] if index > 0 else self.message_lines[0]
                new_focus.focus_text()
            else:
                self.add_message_line()
            self.root.after(100, self.scroll_to_bottom)
    
    def scroll_to_bottom(self):
        self.root.update_idletasks()
        self.scroll_frame.canvas.yview_moveto(1)
    
    def scroll_to_widget(self, widget):
        self.root.update_idletasks()
        canvas = self.scroll_frame.canvas
        inner = self.scroll_frame.inner_frame
        widget_bottom = widget.winfo_y() + widget.winfo_height()
        canvas_height = canvas.winfo_height()
        total_height = inner.winfo_height()
        max_scroll = total_height - canvas_height
        if max_scroll <= 0:
            return
        desired_offset = widget_bottom - canvas_height - 4
        if desired_offset < 0:
            desired_offset = 0
        fraction = desired_offset / max_scroll
        fraction = min(max(fraction, 0.0), 1.0)
        canvas.yview_moveto(fraction)
    
    def get_focus_order(self):
        order = []
        for line in self.message_lines:
            order.extend(line.focus_order)
        return order

class MessageLine:
    def __init__(self, app: EncoderDecoderApp, parent, text: str = "", input_font=None):
        self.app = app
        self.focused = False
        self.container = tk.Frame(parent, bg=self.app.unfocused_bg)
        self.container.grid_columnconfigure(0, weight=1)
        self.text_widget = tk.Text(self.container, wrap="word", height=1, font=input_font, takefocus=True, relief="flat")
        self.text_widget.insert("1.0", text)
        self.text_widget.after(100, self.adjust_height)
        self.text_widget.grid(row=0, column=0, sticky="nsew", padx=(5,2), pady=5)
        self.text_widget.bind("<KeyRelease>", self.adjust_height)
        self.text_widget.bind("<ButtonRelease-1>", lambda e: self.app.scroll_to_widget(self.container))
        self.text_widget.bind("<FocusIn>", lambda e: self.text_widget.after(150, self.on_focus_in))
        self.text_widget.bind("<FocusOut>", lambda e: self.text_widget.after(150, self.on_focus_out))
        
        self.button_container = tk.Frame(self.container, bg=self.app.unfocused_bg)
        self.button_container.grid(row=0, column=1, sticky="ne", padx=(2,5), pady=5)
        self.encode_button = tk.Button(self.button_container, text="Encode", takefocus=True, command=self.on_encode, bg=self.app.unfocused_bg, relief="flat")
        self.decode_button = tk.Button(self.button_container, text="Decode", takefocus=True, command=self.on_decode, bg=self.app.unfocused_bg, relief="flat")
        self.delete_button = tk.Button(self.button_container, text="Delete", takefocus=True, command=self.on_delete, bg=self.app.unfocused_bg, relief="flat")
        self.encode_button.pack(side="top", fill="x", pady=1)
        self.decode_button.pack(side="top", fill="x", pady=1)
        self.delete_button.pack(side="top", fill="x", pady=1)
        
        self.focus_order = [self.text_widget, self.encode_button, self.decode_button, self.delete_button]
        for widget in self.focus_order:
            widget.bind("<Tab>", self.on_tab_forward)
            widget.bind("<Shift-Tab>", self.on_tab_backward)
            widget.bind("<FocusIn>", lambda e: self.text_widget.after(150, self.ensure_visible), add="+")
            widget.bind("<FocusOut>", lambda e: self.text_widget.after(150, self.on_focus_out), add="+")
    
    def adjust_height(self, event=None):
        self.text_widget.update_idletasks()
        try:
            display_lines = int(self.text_widget.count("1.0", "end", "displaylines")[0])
        except Exception:
            content = self.text_widget.get("1.0", "end-1c")
            display_lines = content.count("\n") + 1
        self.text_widget.configure(height=display_lines)
    
    def ensure_visible(self):
        self.app.scroll_to_widget(self.container)
    
    def on_focus_in(self, event=None):
        self.set_focused(True)
        self.ensure_visible()
    
    def on_focus_out(self, event=None):
        self.text_widget.after(150, self.check_focus)
    
    def check_focus(self):
        if not any(widget == self.app.root.focus_get() for widget in self.focus_order):
            self.set_focused(False)
    
    def set_focused(self, flag: bool):
        self.focused = flag
        bg = self.app.focused_bg if flag else self.app.unfocused_bg
        self.set_background(bg)
    
    def set_background(self, color: str):
        self.container.configure(bg=color)
        self.button_container.configure(bg=color)
        self.encode_button.configure(bg=color)
        self.decode_button.configure(bg=color)
        self.delete_button.configure(bg=color)
    
    def on_tab_forward(self, event):
        full_order = self.app.get_focus_order()
        try:
            idx = full_order.index(event.widget)
        except ValueError:
            return
        next_idx = (idx + 1) % len(full_order)
        full_order[next_idx].focus_set()
        return "break"
    
    def on_tab_backward(self, event):
        full_order = self.app.get_focus_order()
        try:
            idx = full_order.index(event.widget)
        except ValueError:
            return
        prev_idx = (idx - 1) % len(full_order)
        full_order[prev_idx].focus_set()
        return "break"
    
    def on_encode(self):
        content = self.text_widget.get("1.0", "end-1c")
        if content.strip():
            result = message_encode(content)
            self.app.add_message_line(result, after=self)
    
    def on_decode(self):
        content = self.text_widget.get("1.0", "end-1c")
        if content.strip():
            result = message_decode(content)
            self.app.add_message_line(result, after=self)
    
    def on_delete(self):
        self.app.remove_message_line(self)
    
    def focus_text(self):
        self.text_widget.focus_set()
    
    def set_buttons_width(self, width_units: int):
        self.encode_button.config(width=width_units)
        self.decode_button.config(width=width_units)
        self.delete_button.config(width=width_units)
    
    def destroy(self):
        self.container.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = EncoderDecoderApp(root)
    root.mainloop()

