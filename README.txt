# HOME LIBRARY MANAGEMENT GUIDE

This guide explains how to install, configure, use, and compile the software for managing your home library.
ATTENTION: THE USER INTERFACE IS IN ITALIAN. 
---

## 1. PRE-REQUISITES (If not using the EXE)

To run the scripts directly (without using the .exe file), you must have the following installed on your computer:

1.  **Python**: Downloadable from python.org (version 3.10 or higher recommended).
2.  **Required Libraries**: Once Python is installed, open the terminal (or Command Prompt) and type:
    ```bash
    pip install pandas openpyxl customtkinter Pillow pyinstaller
    ```

---

## 2. HOW TO IMPORT AN EXCEL FILE (import_script.py)

If you have a new list of books in Excel and want to create or update the database:

1.  **Prepare the Excel**: The file should have columns with these names (or similar):
    - `Titolo` (Title)
    - `Autore` (Author)
    - `Genere` (Genre)
    - `Anno` (Year)
    - `Editore` (Publisher)
    - `Posizione` (Location/Shelf)
2.  **Configure the Script**:
    - Open the file `import_script.py` with a text editor (e.g., Notepad or VS Code).
    - At line 6, change the `EXCEL_FILE` value to the exact name of your file (e.g., `EXCEL_FILE = "my_books.xlsx"`).
3.  **Run the Import**:
    - In the terminal, inside the project folder, type:
      ```bash
      python import_script.py
      ```
    - The script will automatically create or update the `library.db` file.

---

## 3. HOW TO RUN THE PROGRAM (main.py)

The program is divided into two logical parts:
- `database.py`: Handles saving and searching in the .db file.
- `main.py`: Handles the graphical user interface (GUI) you see on screen.

To start the app without the executable:
1. Open the terminal in the project folder.
2. Type:
   ```bash
   python main.py
   ```

---

## 4. HOW TO CREATE A NEW .EXE FILE (PyInstaller)

If you want to regenerate the `GestoreBiblioteca.exe` file (to use it on other PCs):

1. Ensure the `app_icon.png` file is in the folder (used for the icon and the internal logo).
2. In the terminal, type this command:
   ```bash
   pyinstaller --noconsole --onefile --collect-all customtkinter --add-data "app_icon.png;." --name "GestoreBiblioteca" main.py
   ```
   *Parameters explanation:*
   - `--noconsole`: Prevents the black terminal window from opening when you start the app.
   - `--onefile`: Creates a single .exe file instead of a folder.
   - `--add-data "app_icon.png;."`: Embeds the image inside the executable.

3. Once finished, you will find the file inside the `dist` folder. You can move it to the main project folder and delete the temporary `build` and `dist` folders.

---

## 5. PORTABILITY

Remember: to use the program on another computer, you only need TWO files in the same folder:
1. `GestoreBiblioteca.exe`
2. `library.db`

You do NOT need to install Python or anything else on the computers where you will use the executable!
