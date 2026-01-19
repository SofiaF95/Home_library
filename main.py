import os
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import database
import pandas as pd
from tkinter import filedialog
from PIL import Image
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Biblioteca v4.9")
        self.geometry("800x600")

        # Set Icon
        self.set_app_icon()

        # Layout configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Header (Search & New) ---
        self.header_frame = ctk.CTkFrame(self)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        self.header_frame.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(self.header_frame, placeholder_text="Cerca per titolo, autore, editore...", height=40, font=("Arial", 16))
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(20, 10), pady=10)
        self.search_entry.bind("<KeyRelease>", self.on_search)

        main_btn_style = {
            "width": 40, "height": 40, "font": ("Arial", 20),
            "fg_color": "transparent", "border_width": 1, "border_color": "white",
            "text_color": "white", "anchor": "center", "border_spacing": 0
        }

        self.btn_show_all = ctk.CTkButton(self.header_frame, text="👁️", command=lambda: self.load_books(show_all=True), **main_btn_style)
        self.btn_show_all.grid(row=0, column=1, padx=5, pady=10)

        self.btn_new = ctk.CTkButton(self.header_frame, text="+", command=self.open_new_book, **main_btn_style)
        self.btn_new.grid(row=0, column=2, padx=5, pady=10)

        self.btn_export = ctk.CTkButton(self.header_frame, text="📊", command=self.export_to_excel, **main_btn_style)
        self.btn_export.grid(row=0, column=3, padx=(5, 20), pady=10)

        # --- Content Area ---
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        # Book List - Removed label for a cleaner look
        self.scrollable_list = ctk.CTkScrollableFrame(self.content_frame)
        self.scrollable_list.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.scrollable_list.grid_columnconfigure(0, weight=1)

        # Pagination State
        self.current_query = ""
        self.current_offset = 0
        self.is_show_all = False
        self.items_per_page = 50
        self.load_more_btn = None
        self.detail_frame = None

        self.show_welcome()

    def set_app_icon(self, window=None):
        if window is None: window = self
        try:
            path = resource_path("app_icon.png")
            if os.path.exists(path):
                icon_img = tk.PhotoImage(file=path)
                window.iconphoto(False, icon_img)
                window._icon_ref = icon_img
        except:
            pass

    def show_welcome(self):
        for widget in self.scrollable_list.winfo_children():
            widget.destroy()
        
        try:
            path = resource_path("app_icon.png")
            if os.path.exists(path):
                # Use CTkImage for better compatibility and scaling
                pil_img = Image.open(path)
                # Adjusted logo to 350x350 for an even more refined look
                self.welcome_logo = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(300, 300))
                lbl_logo = ctk.CTkLabel(self.scrollable_list, image=self.welcome_logo, text="")
                lbl_logo.pack(pady=70) # Adjusted padding
        except Exception as e:
            print(f"Logo error: {e}")

    def load_books(self, query="", show_all=False, append=False):
        if not append:
            for widget in self.scrollable_list.winfo_children():
                widget.destroy()
            self.current_offset = 0
            self.current_query = query
            self.is_show_all = show_all
            if self.load_more_btn:
                self.load_more_btn.destroy()
                self.load_more_btn = None

        if self.current_query:
            books = database.search_books(self.current_query, limit=self.items_per_page, offset=self.current_offset)
        elif self.is_show_all:
            books = database.get_all_books(limit=self.items_per_page, offset=self.current_offset)
        else:
            return

        if not books and not append:
            lbl = ctk.CTkLabel(self.scrollable_list, text="Nessun libro trovato.", font=("Arial", 14))
            lbl.pack(pady=20)
            return

        for book in books:
            self.create_book_card(book)
        
        if len(books) == self.items_per_page:
             self.items_per_page = 10
             if self.load_more_btn: self.load_more_btn.destroy()
             self.load_more_btn = ctk.CTkButton(self.scrollable_list, text="Carica Altri (+10)", 
                                              command=self.load_more, fg_color="gray30")
             self.load_more_btn.pack(pady=20)
        else:
             if self.load_more_btn: self.load_more_btn.destroy()

    def create_book_card(self, book):
        card = ctk.CTkFrame(self.scrollable_list, fg_color=("gray90", "gray20"))
        card.pack(fill="x", pady=5, padx=5)
        
        # Text container for vertical stacking
        text_frame = ctk.CTkFrame(card, fg_color="transparent")
        text_frame.pack(side="left", padx=10, pady=10, fill="both", expand=True)

        title_val = book['title'] if book['title'] else "Senza Titolo"
        year_val = f" ({book['year']})" if book['year'] else ""
        lbl_title = ctk.CTkLabel(text_frame, text=f"{title_val}{year_val}", font=("Arial", 16, "bold"), anchor="w")
        lbl_title.pack(side="top", anchor="w")
        
        author_val = book['author'] if book['author'] else "Autore sconosciuto"
        lbl_author = ctk.CTkLabel(text_frame, text=author_val, font=("Arial", 12, "italic"), text_color="gray", anchor="w")
        lbl_author.pack(side="top", anchor="w")
        
        # Minimalist View Button
        btn_view = ctk.CTkButton(card, text="📖", width=40, height=40, font=("Arial", 20),
                                fg_color="transparent", border_width=1, border_color="white",
                                command=lambda b=book: self.open_detail(b))
        btn_view.pack(side="right", padx=10, pady=10)

    def load_more(self):
        self.current_offset += 50 if self.current_offset == 0 else 10
        self.load_books(append=True)

    def on_search(self, event):
        query = self.search_entry.get()
        if not query:
            self.show_welcome()
            self.focus() # Remove focus from entry to hide cursor
            return

        if len(query) > 2:
            self.items_per_page = 50
            self.load_books(query)
        elif len(query) == 0:
            self.show_welcome()

    def open_detail(self, book):
        if self.detail_frame: self.detail_frame.destroy()
        self.header_frame.grid_forget()
        self.scrollable_list.grid_forget()
        self.detail_frame = BookDetailFrame(self.content_frame, book, self.back_to_list, delete_callback=self.on_book_deleted)
        self.detail_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    def open_new_book(self):
        if self.detail_frame: self.detail_frame.destroy()
        self.header_frame.grid_forget()
        self.scrollable_list.grid_forget()
        self.detail_frame = BookDetailFrame(self.content_frame, None, self.back_to_list, is_new=True, delete_callback=self.on_book_deleted)
        self.detail_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    def on_book_deleted(self):
        self.back_to_list()
        self.load_books(self.search_entry.get())

    def back_to_list(self):
        if self.detail_frame:
            self.detail_frame.destroy()
            self.detail_frame = None
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        self.scrollable_list.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    def export_to_excel(self):
        try:
            books_dict = database.get_all_books_sorted()
            if not books_dict:
                messagebox.showwarning("Esportazione", "Il database è vuoto.")
                return

            df = pd.DataFrame(books_dict)
            
            # Map columns to user-friendly names
            columns_map = {
                'title': 'Titolo',
                'author': 'Autore',
                'genre': 'Genere',
                'year': 'Anno',
                'publisher': 'Editore',
                'location': 'Posizione',
                'language': 'Lingua',
                'is_loaned': 'In Prestito',
                'loaned_to': 'Prestato a'
            }
            
            # Reorder and filter if needed (removing 'id')
            df_export = df[[c for c in columns_map.keys() if c in df.columns]].rename(columns=columns_map)
            
            # Convert Boolean/Int to friendly string
            if 'In Prestito' in df_export.columns:
                df_export['In Prestito'] = df_export['In Prestito'].apply(lambda x: 'Sì' if x == 1 else 'No')

            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                title="Salva Esportazione Biblioteca",
                initialfile="Esportazione_Biblioteca.xlsx"
            )

            if file_path:
                df_export.to_excel(file_path, index=False, engine='openpyxl')
                messagebox.showinfo("Successo", f"Database esportato correttamente in:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Errore Esportazione", str(e))

class AutocompleteEntry(ctk.CTkEntry):
    def __init__(self, master, suggestions_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.suggestions_callback = suggestions_callback
        self.dropdown = None
        self.bind("<KeyRelease>", self.on_key_release)
        self.bind("<FocusOut>", self.on_focus_out)
        self.bind("<FocusIn>", self.on_key_release)

    def on_key_release(self, event=None):
        val = self.get().lower()
        if not val:
            self.hide_dropdown()
            return
        
        all_suggestions = self.suggestions_callback()
        filtered = [s for s in all_suggestions if val in str(s).lower()]
        
        if filtered:
            self.show_dropdown(filtered[:5]) # Show top 5
        else:
            self.hide_dropdown()

    def show_dropdown(self, suggestions):
        if self.dropdown: self.dropdown.destroy()
        
        self.dropdown = tk.Toplevel(self)
        self.dropdown.wm_overrideredirect(True)
        
        # Position dropdown
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()
        self.dropdown.wm_geometry(f"+{x}+{y}")
        
        frame = ctk.CTkFrame(self.dropdown, border_width=1, border_color="white")
        frame.pack(fill="both", expand=True)
        
        for s in suggestions:
            btn = ctk.CTkButton(frame, text=s, fg_color="transparent", anchor="w", 
                               command=lambda val=s: self.select_suggestion(val))
            btn.pack(fill="x")

    def select_suggestion(self, value):
        self.delete(0, tk.END)
        self.insert(0, value)
        self.hide_dropdown()

    def hide_dropdown(self):
        if self.dropdown:
            self.dropdown.destroy()
            self.dropdown = None

    def on_focus_out(self, event):
        # Small delay to allow button click to register
        self.after(200, self.hide_dropdown)

class BookDetailFrame(ctk.CTkFrame):
    def __init__(self, master, book, back_callback, is_new=False, delete_callback=None):
        super().__init__(master)
        self.book = dict(book) if book else {}
        self.back_callback = back_callback
        self.delete_callback = delete_callback
        self.is_new = is_new
        self.edit_mode = is_new 

        self.grid_columnconfigure(1, weight=1)
        self.original_data = {} # To track unsaved changes

        # --- Header Row (Row 0) ---
        self.header_container = ctk.CTkFrame(self, fg_color="transparent")
        self.header_container.grid(row=0, column=0, columnspan=2, pady=(10, 20), sticky="ew", padx=10)
        self.header_container.grid_columnconfigure(0, weight=1)

        header_text = "Nuovo Libro" if is_new else "Dettaglio Libro"
        self.lbl_header = ctk.CTkLabel(self.header_container, text=header_text, font=("Arial", 22, "bold"))
        self.lbl_header.grid(row=0, column=0, sticky="w", padx=10)

        # Icon Buttons Cluster
        self.icons_frame = ctk.CTkFrame(self.header_container, fg_color="transparent")
        self.icons_frame.grid(row=0, column=1, sticky="e")

        btn_style = {
            "width": 40, "height": 40, "font": ("Arial", 20),
            "fg_color": "transparent", "border_width": 1, "border_color": "white",
            "text_color": "white"
        }

        # Back Button
        self.btn_back = ctk.CTkButton(self.icons_frame, text="⬅", command=self.on_back_click, **btn_style)
        self.btn_back.pack(side="left", padx=5)

        if not self.is_new:
            # Edit Button
            self.btn_edit = ctk.CTkButton(self.icons_frame, text="✏", command=self.toggle_edit, **btn_style)
            self.btn_edit.pack(side="left", padx=5)

            # Delete Button
            self.btn_delete = ctk.CTkButton(self.icons_frame, text="🗑", command=self.confirm_delete, **btn_style)
            self.btn_delete.pack(side="left", padx=5)
            
            # Loan Button
            loan_val = self.book.get('is_loaned', 0)
            self.btn_loan_action = ctk.CTkButton(self.icons_frame, text="🚪➔" if not loan_val else "🚪⇠", 
                                                command=self.handle_loan, **btn_style)
            self.btn_loan_action.pack(side="left", padx=5)

        # Save Button - Only in edit mode
        self.btn_save = ctk.CTkButton(self.icons_frame, text="💾", command=self.save_data, **btn_style)
        if self.edit_mode:
            self.btn_save.pack(side="left", padx=5)

        # --- Fields ---
        self.fields = [("Titolo", "title"), ("Autore", "author"), ("Genere", "genre"), ("Anno", "year"), ("Editore", "publisher"), ("Posizione", "location"), ("Lingua", "language")]
        self.entries = {}; self.labels = {}
        
        current_row = 1
        for label_text, key in self.fields:
            ctk.CTkLabel(self, text=label_text + ":", font=("Arial", 14, "bold")).grid(row=current_row, column=0, sticky="w", padx=20, pady=5)
            val = self.book.get(key, "")
            
            lbl_val = ctk.CTkLabel(self, text=str(val if val else ""), font=("Arial", 14), anchor="w")
            self.labels[key] = lbl_val
            
            # Autocomplete for metadata fields
            if key != "title" and key != "year":
                entry = AutocompleteEntry(self, suggestions_callback=lambda k=key: database.get_unique_values(k), font=("Arial", 14))
            else:
                entry = ctk.CTkEntry(self, font=("Arial", 14))
            
            entry.insert(0, str(val if val else ""))
            self.entries[key] = entry

            if self.edit_mode: entry.grid(row=current_row, column=1, sticky="ew", padx=20, pady=5)
            else: lbl_val.grid(row=current_row, column=1, sticky="ew", padx=20, pady=5)
            current_row += 1

        # Loan Status Section - Grid Aligned (Hide for new books)
        if not self.is_new:
            ctk.CTkLabel(self, text="Stato:", font=("Arial", 14, "bold")).grid(row=current_row, column=0, sticky="w", padx=20, pady=15)
            
            loan_val = self.book.get('is_loaned', 0)
            loaned_to = self.book.get('loaned_to', "")
            status_text = "Disponibile" if not loan_val else f"In Prestito ({loaned_to})"
            
            self.lbl_loan_status = ctk.CTkLabel(self, text=status_text, font=("Arial", 14), anchor="w")
            self.lbl_loan_status.grid(row=current_row, column=1, sticky="w", padx=20, pady=15)

    def on_back_click(self):
        if not self.edit_mode:
            self.back_callback()
        else:
            # Check for changes
            current_data = {k : self.entries[k].get() for _, k in self.fields}
            changed = any(str(current_data[k]) != str(self.original_data.get(k, "")) for _, k in self.fields)
            
            if changed:
                res = messagebox.askyesnocancel("Conferma", "Vuoi salvare le modifiche prima di uscire?")
                if res is True: # Yes
                    self.save_data()
                elif res is False: # No (Discard)
                    if self.is_new:
                        self.back_callback()
                    else:
                        self.toggle_edit()
                # If None (Cancel), stays in edit mode
            else:
                # No changes
                if self.is_new:
                    self.back_callback()
                else:
                    self.toggle_edit()

    def toggle_edit(self):
        if not self.edit_mode:
            # Entering edit mode: store original values
            self.original_data = {k : self.entries[k].get() for _, k in self.fields}
        self.edit_mode = not self.edit_mode
        self.refresh_ui()

    def refresh_ui(self):
        # Header text
        header_text = "Modifica Libro" if self.edit_mode else "Dettaglio Libro"
        self.lbl_header.configure(text=header_text)

        # Re-grid fields based on mode
        current_row = 1
        for _, k in self.fields:
            self.labels[k].grid_forget()
            self.entries[k].grid_forget()
            if self.edit_mode:
                 self.entries[k].grid(row=current_row, column=1, sticky="ew", padx=20, pady=5)
            else:
                 self.labels[k].grid(row=current_row, column=1, sticky="ew", padx=20, pady=5)
            current_row += 1

        # Save button toggle
        if self.edit_mode:
            self.btn_save.pack(side="left", padx=5)
            if hasattr(self, 'btn_edit'): self.btn_edit.pack_forget()
            if hasattr(self, 'btn_delete'): self.btn_delete.pack_forget()
            if hasattr(self, 'btn_loan_action'): self.btn_loan_action.pack_forget()
        else:
            self.btn_save.pack_forget()
            if hasattr(self, 'btn_edit'): self.btn_edit.pack(side="left", padx=5)
            if hasattr(self, 'btn_delete'): self.btn_delete.pack(side="left", padx=5)
            if hasattr(self, 'btn_loan_action'): self.btn_loan_action.pack(side="left", padx=5)

    def save_data(self):
        data = {k: self.entries[k].get() for _, k in self.fields}
        try:
            if self.is_new:
                database.add_book(**data)
                messagebox.showinfo("Successo", "Libro aggiunto!")
                self.back_callback()
            else:
                data['is_loaned'] = self.book['is_loaned']
                data['loaned_to'] = self.book['loaned_to']
                database.update_book(self.book['id'], **data)
                messagebox.showinfo("Successo", "Salvato!")
                self.book.update(data)
                for _, k in self.fields: self.labels[k].configure(text=str(data[k]))
                self.original_data = data.copy()
                self.toggle_edit()
        except Exception as e: messagebox.showerror("Errore", str(e))

    def confirm_delete(self):
        if messagebox.askyesno("Conferma", "Eliminare il libro?"):
            database.delete_book(self.book['id'])
            if self.delete_callback: self.delete_callback()

    def handle_loan(self):
        if not self.book['is_loaned']:
            name = ctk.CTkInputDialog(text="A chi presti il libro?", title="Prestito").get_input()
            if name:
                database.toggle_loan_status(self.book['id'], 0, name)
                self.book['is_loaned'] = 1; self.book['loaned_to'] = name
        else:
            if messagebox.askyesno("Reso", "Libro restituito?"):
                database.toggle_loan_status(self.book['id'], 1)
                self.book['is_loaned'] = 0; self.book['loaned_to'] = ""
        
        status = "Disponibile" if not self.book['is_loaned'] else f"In Prestito ({self.book['loaned_to']})"
        self.lbl_loan_status.configure(text=status)
        self.btn_loan_action.configure(text="🚪➔" if not self.book['is_loaned'] else "🚪⇠")

if __name__ == "__main__":
    app = App()
    app.mainloop()
