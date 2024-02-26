import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import sys

class ImageEncoderDecoderApp:
    def __init__(self, master):
        self.master = master
        self.master.title("ULIF Program v0.0.3")
        self.master.geometry("1400x1000")

        
        self.master.configure(bg="#f0f0f0")
        self.font = ('Helvetica', 12)
        
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.upload_frame = tk.Frame(self.notebook, bg="#ffffff", bd=2, relief=tk.RAISED)
        self.display_frame = tk.Frame(self.notebook, bg="#ffffff", bd=2, relief=tk.RAISED)
        
        self.notebook.add(self.upload_frame, text='Upload')
        self.notebook.add(self.display_frame, text='Display')

        self.upload_label = tk.Label(self.upload_frame, text="Upload Image to Encode:", font=self.font, bg="#ffffff")
        self.upload_label.pack(pady=10)
        self.upload_button = tk.Button(self.upload_frame, text="Upload Image", command=self.upload_image, font=self.font)
        self.upload_button.pack(pady=5)
        
        self.decode_label = tk.Label(self.display_frame, text="Decoded Image:", font=self.font, bg="#ffffff")
        self.decode_label.pack(pady=10)
        self.decode_button = tk.Button(self.display_frame, text="Decode Image", command=self.decode_image, font=self.font)
        self.decode_button.pack(pady=5)

        self.uploaded_image_display = tk.Label(self.upload_frame, bg="#ffffff")
        self.uploaded_image_display.pack(pady=5)

        self.image_info_label = tk.Label(self.display_frame, text="", justify="left", font=('Helvetica', 10), bg="#ffffff")
        self.image_info_label.pack(pady=10)

        self.decoded_image_display = tk.Label(self.display_frame, bg="#ffffff")
        self.decoded_image_display.pack(pady=5)
        
        self.image = None
        if len(sys.argv) > 1:
            ulif_file = sys.argv[1]
            if ulif_file.lower().endswith('.ulif'):
                self.decode_ulif_file(ulif_file)

    def upload_image(self):
        filename = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if filename:
            try:
                self.image = Image.open(filename)
                self.upload_button.config(text="Upload Another Image")
                ulif_filename = filedialog.asksaveasfilename(defaultextension=".ulif", filetypes=[("ULIF Files", "*.ulif")])
                if ulif_filename:
                    self.encode_ulif(ulif_filename)

                    image_info = self.get_image_info(ulif_filename)
                    self.image_info_label.config(text=image_info)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to process image: {str(e)}")

    def encode_ulif(self, filename):
        if self.image:
            try:
                resized_image = self.image.resize((int(self.image.width / 1.3), int(self.image.height / 1.3)))
                rgb_image = resized_image.convert("RGB")
                width, height = rgb_image.size
                pixel_data = rgb_image.tobytes()
                mode = rgb_image.mode 

                with open(filename, 'wb') as f:
                    f.write(width.to_bytes(4, byteorder='big'))
                    f.write(height.to_bytes(4, byteorder='big'))
                    f.write(mode.encode('ascii'))  # Encode mode as ASCII
                    f.write(pixel_data)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to encode image: {str(e)}")
            
    def decode_image(self):
        filename = filedialog.askopenfilename(filetypes=[(".ULIF", "*.ulif")])
        if filename:
            self.decode_ulif_file(filename)

    def decode_ulif_file(self, filename):
        try:
            if filename.lower().endswith('.ulif'):
                with open(filename, 'rb') as f:
                    width_bytes = f.read(4)
                    height_bytes = f.read(4)

                    if len(width_bytes) != 4 or len(height_bytes) != 4:
                        messagebox.showerror("Error", "Invalid ULIF file format")
                        return

                    width = int.from_bytes(width_bytes, byteorder='big')
                    height = int.from_bytes(height_bytes, byteorder='big')

                    pixel_data = f.read()

                try:
                    decoded_image = Image.frombytes("RGB", (width, height), pixel_data)
                    decoded_image.thumbnail((width/1.25, height/1.25))  # must same as image
                    decoded_photo = ImageTk.PhotoImage(decoded_image)
                    self.decoded_image_display.config(image=decoded_photo)
                    self.decoded_image_display.image = decoded_photo

                    image_info = self.get_image_info(filename)
                    self.image_info_label.config(text=image_info)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to decode image data: {str(e)}")
            else:
                messagebox.showerror("Error", "Unsupported file format")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read ULIF file: {str(e)}")

    def get_image_info(self, filename):
        try:
            with open(filename, 'rb') as f:
                width_bytes = f.read(4)
                height_bytes = f.read(4)

                if len(width_bytes) != 4 or len(height_bytes) != 4:
                    return "Error: Invalid ULIF file format"

                width = int.from_bytes(width_bytes, byteorder='big')
                height = int.from_bytes(height_bytes, byteorder='big')

                file_size = os.path.getsize(filename)
                file_size_str = self.get_formatted_file_size(file_size)

                bit_depth = 24  # rgb go brrr

        except Exception as e:
            return f"Error: {str(e)}"

        format_info = f"Format: ULIF\n"
        mode_info = f"Mode: RGB\n"
        size_info = f"Dimensions: {width} x {height} pixels\n"
        file_size_info = f"File Size: {file_size_str}\n"
        bit_depth_info = f"Bit Depth: {bit_depth} bits"

        return format_info + mode_info + size_info + file_size_info + bit_depth_info

    def get_formatted_file_size(self, size_in_bytes):
        # Convert file size
        if size_in_bytes >= 1024 * 1024:
            return f"{size_in_bytes / (1024 * 1024):.2f} MB"
        elif size_in_bytes >= 1024:
            return f"{size_in_bytes / 1024:.2f} KB"
        else:
            return f"{size_in_bytes} bytes"

def main():
    root = tk.Tk()
    app = ImageEncoderDecoderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()


