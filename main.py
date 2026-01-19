"""
Universal File Format Converter
Main application with GUI
"""
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

# Import converters and utilities
from utils.file_detector import FileDetector
from converters.image_converter import ImageConverter
from converters.document_converter import DocumentConverter


class FileConverterApp:
    """Main application class for file converter"""
    
    def __init__(self, root):
        """Initialize the application"""
        self.root = root
        self.root.title("Universal File Converter")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Initialize converters
        self.file_detector = FileDetector()
        self.image_converter = ImageConverter()
        self.document_converter = DocumentConverter()
        
        # Variables
        self.selected_files = []
        self.detected_format_type = None
        self.detected_format = None
        
        # Setup UI
        self.setup_ui()
        
        # Center window
        self.center_window()
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_ui(self):
        """Setup the user interface"""
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="Universal File Format Converter",
            font=('Arial', 20, 'bold')
        )
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # File selection frame
        file_frame = ttk.LabelFrame(main_frame, text="Step 1: Select Files", padding="10")
        file_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(0, weight=1)
        
        # File selection button
        self.select_btn = ttk.Button(
            file_frame,
            text="📁 Browse Files",
            command=self.select_files,
            width=20
        )
        self.select_btn.grid(row=0, column=0, pady=5)
        
        # Selected files listbox
        list_frame = ttk.Frame(file_frame)
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        list_frame.columnconfigure(0, weight=1)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.files_listbox = tk.Listbox(
            list_frame,
            height=6,
            yscrollcommand=scrollbar.set,
            selectmode=tk.EXTENDED
        )
        self.files_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E))
        scrollbar.config(command=self.files_listbox.yview)
        
        # Remove button
        self.remove_btn = ttk.Button(
            file_frame,
            text="❌ Remove Selected",
            command=self.remove_selected_files,
            state=tk.DISABLED
        )
        self.remove_btn.grid(row=2, column=0, pady=5)
        
        # Format detection frame
        detect_frame = ttk.LabelFrame(main_frame, text="Detected Format", padding="10")
        detect_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.format_label = ttk.Label(
            detect_frame,
            text="No files selected",
            font=('Arial', 11)
        )
        self.format_label.grid(row=0, column=0, pady=5)
        
        # Conversion options frame
        convert_frame = ttk.LabelFrame(main_frame, text="Step 2: Select Target Format", padding="10")
        convert_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        convert_frame.columnconfigure(0, weight=1)
        
        # Target format dropdown
        self.target_var = tk.StringVar()
        self.target_combo = ttk.Combobox(
            convert_frame,
            textvariable=self.target_var,
            state='readonly',
            width=30
        )
        self.target_combo.grid(row=0, column=0, pady=5)
        self.target_combo['values'] = ()
        
        # Output directory selection
        output_dir_frame = ttk.Frame(convert_frame)
        output_dir_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        output_dir_frame.columnconfigure(1, weight=1)
        
        ttk.Label(output_dir_frame, text="Output Folder:").grid(row=0, column=0, padx=(0, 10))
        
        self.output_dir_var = tk.StringVar(value=str(Path.home() / "Downloads"))
        self.output_entry = ttk.Entry(
            output_dir_frame,
            textvariable=self.output_dir_var,
            state='readonly'
        )
        self.output_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.browse_output_btn = ttk.Button(
            output_dir_frame,
            text="Browse",
            command=self.select_output_directory,
            width=10
        )
        self.browse_output_btn.grid(row=0, column=2)
        
        # Convert button
        self.convert_btn = ttk.Button(
            convert_frame,
            text="🔄 Convert Files",
            command=self.convert_files,
            state=tk.DISABLED,
            width=20
        )
        self.convert_btn.grid(row=2, column=0, pady=10)
        
        # Progress frame
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100
        )
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.status_label = ttk.Label(
            progress_frame,
            text="Ready",
            font=('Arial', 9)
        )
        self.status_label.grid(row=1, column=0, pady=(5, 0))
    
    def select_files(self):
        """Open file dialog to select files"""
        files = filedialog.askopenfilenames(
            title="Select files to convert",
            filetypes=[
                ("All Supported Files", "*.pdf *.docx *.doc *.xlsx *.xls *.png *.jpg *.jpeg *.bmp *.tiff *.gif *.webp *.ico"),
                ("PDF Files", "*.pdf"),
                ("Word Documents", "*.docx *.doc"),
                ("Excel Files", "*.xlsx *.xls"),
                ("Image Files", "*.png *.jpg *.jpeg *.bmp *.tiff *.gif *.webp *.ico"),
                ("All Files", "*.*")
            ]
        )
        
        if files:
            self.add_files(list(files))
    
    def add_files(self, file_paths):
        """Add files to the list"""
        for file_path in file_paths:
            if file_path not in self.selected_files:
                self.selected_files.append(file_path)
                self.files_listbox.insert(tk.END, os.path.basename(file_path))
        
        # Detect format of first file
        if self.selected_files:
            self.detect_format()
            self.remove_btn['state'] = tk.NORMAL
    
    def remove_selected_files(self):
        """Remove selected files from list"""
        selected_indices = self.files_listbox.curselection()
        
        # Remove in reverse order to maintain indices
        for index in reversed(selected_indices):
            self.files_listbox.delete(index)
            del self.selected_files[index]
        
        if not self.selected_files:
            self.remove_btn['state'] = tk.DISABLED
            self.convert_btn['state'] = tk.DISABLED
            self.format_label['text'] = "No files selected"
            self.target_combo['values'] = ()
            self.detected_format_type = None
            self.detected_format = None
        else:
            self.detect_format()
    
    def detect_format(self):
        """Detect format of selected files"""
        if not self.selected_files:
            return
        
        try:
            # Detect format of first file
            format_type, file_format = self.file_detector.detect_format(self.selected_files[0])
            
            self.detected_format_type = format_type
            self.detected_format = file_format
            
            # Update label
            format_display = file_format.upper()
            type_display = format_type.capitalize()
            self.format_label['text'] = f"Detected: {format_display} ({type_display})"
            
            # Get available target formats
            target_formats = self.file_detector.get_conversion_targets(format_type)
            
            # Update combo box
            self.target_combo['values'] = [fmt.upper() for fmt in target_formats]
            if target_formats:
                self.target_combo.current(0)
                self.convert_btn['state'] = tk.NORMAL
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to detect file format:\n{str(e)}")
            self.format_label['text'] = "Format detection failed"
    
    def select_output_directory(self):
        """Select output directory"""
        directory = filedialog.askdirectory(
            title="Select output directory",
            initialdir=self.output_dir_var.get()
        )
        
        if directory:
            self.output_dir_var.set(directory)
    
    def convert_files(self):
        """Convert selected files"""
        if not self.selected_files:
            messagebox.showwarning("No Files", "Please select files to convert.")
            return
        
        if not self.target_var.get():
            messagebox.showwarning("No Target Format", "Please select a target format.")
            return
        
        target_format = self.target_var.get().lower()
        output_dir = self.output_dir_var.get()
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Disable buttons during conversion
        self.convert_btn['state'] = tk.DISABLED
        self.select_btn['state'] = tk.DISABLED
        
        # Reset progress
        self.progress_var.set(0)
        self.root.update()
        
        # Convert files
        total_files = len(self.selected_files)
        successful = 0
        failed = 0
        errors = []
        
        for i, input_path in enumerate(self.selected_files):
            try:
                # Update status
                filename = os.path.basename(input_path)
                self.status_label['text'] = f"Converting: {filename}"
                self.root.update()
                
                # Generate output path
                base_name = os.path.splitext(filename)[0]
                output_path = os.path.join(output_dir, f"{base_name}.{target_format}")
                
                # Select appropriate converter
                if self.detected_format_type == 'image':
                    self.image_converter.convert(input_path, output_path, target_format)
                elif self.detected_format_type == 'document':
                    self.document_converter.convert(input_path, output_path, target_format)
                else:
                    raise ValueError(f"Unknown format type: {self.detected_format_type}")
                
                successful += 1
                
            except Exception as e:
                failed += 1
                errors.append(f"{filename}: {str(e)}")
            
            # Update progress
            progress = ((i + 1) / total_files) * 100
            self.progress_var.set(progress)
            self.root.update()
        
        # Show results
        result_msg = f"Conversion Complete!\n\n"
        result_msg += f"✅ Successful: {successful}\n"
        result_msg += f"❌ Failed: {failed}\n\n"
        result_msg += f"Output folder: {output_dir}"
        
        if errors:
            result_msg += "\n\nErrors:\n" + "\n".join(errors[:5])
            if len(errors) > 5:
                result_msg += f"\n... and {len(errors) - 5} more errors"
        
        if failed > 0:
            messagebox.showwarning("Conversion Complete", result_msg)
        else:
            messagebox.showinfo("Success", result_msg)
        
        # Update status
        self.status_label['text'] = f"Complete: {successful} successful, {failed} failed"
        
        # Re-enable buttons
        self.convert_btn['state'] = tk.NORMAL
        self.select_btn['state'] = tk.NORMAL


def main():
    """Main entry point"""
    root = tk.Tk()
    app = FileConverterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
