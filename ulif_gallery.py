import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageWin
import os
import subprocess

class ImageGalleryApp:
    def __init__(self, master):
        self.master = master
        self.master.title("ULIF Photo App")
        self.master.geometry("1400x1000")
        self.master.configure(bg="#f0f0f0")
        self.font = ('Helvetica', 12)

        self.images = []
        self.current_index = 0

        self.nav_frame = tk.Frame(self.master, bg="#ffffff")
        self.nav_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        self.prev_button = tk.Button(self.nav_frame, text="Previous", command=self.show_previous_image, font=self.font)
        self.prev_button.pack(side=tk.LEFT, padx=5)

        self.next_button = tk.Button(self.nav_frame, text="Next", command=self.show_next_image, font=self.font)
        self.next_button.pack(side=tk.RIGHT, padx=5)

        self.info_text = tk.Text(self.master, wrap=tk.WORD, height=5)
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.main_frame = tk.Frame(self.master, bg="#ffffff")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.image_label = tk.Label(self.main_frame, bg="#ffffff")
        self.image_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.load_images()

    def load_images(self):
        directory = filedialog.askdirectory(title="Select Directory")
        if directory:
            ulif_files = [os.path.join(directory, filename) for filename in os.listdir(directory) if filename.lower().endswith('.ulif')]
            if ulif_files:
                self.images = ulif_files
                self.show_image(0)
            else:
                messagebox.showinfo("Info", "No ULIF files found in selected directory.")

    def show_image(self, index):
        try:
            image_path = self.images[index]
            image = self.decode_ulif_file(image_path)
            self.current_image = image  # Store current image for cropping and printing
            resized_image = self.resize_image(image)
            photo = ImageTk.PhotoImage(resized_image)

            self.image_label.config(image=photo)
            self.image_label.image = photo

            self.current_index = index
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open image: {str(e)}")

    def decode_ulif_file(self, filename):
        try:
            with open(filename, 'rb') as f:
                width_bytes = f.read(4)
                height_bytes = f.read(4)

                if len(width_bytes) != 4 or len(height_bytes) != 4:
                    raise ValueError("Invalid ULIF file format")

                width = int.from_bytes(width_bytes, byteorder='big')
                height = int.from_bytes(height_bytes, byteorder='big')

                pixel_data = f.read()

            decoded_image = Image.frombytes("RGBA", (width, height), pixel_data)
            return decoded_image
        except Exception as e:
            raise ValueError(f"Failed to decode ULIF image: {str(e)}")

    def resize_image(self, image):
        max_width = 1380
        max_height = 920
        width, height = image.size
        if width > max_width or height > max_height:
            aspect_ratio = min(max_width / width, max_height / height)
            new_width = int(width * aspect_ratio)
            new_height = int(height * aspect_ratio)
            return image.resize((new_width, new_height))
        return image

    def show_previous_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.show_image(self.current_index)
            self.show_image_info()

    def show_next_image(self):
        if self.current_index < len(self.images) - 1:
            self.current_index += 1
            self.show_image(self.current_index)
            self.show_image_info()

    def show_image_info(self):
        image_path = self.images[self.current_index]
        image = self.decode_ulif_file(image_path)

        image_info = f"Image Path: {image_path}\n"
        image_info += f"Dimensions: {image.width} x {image.height}\n"
        image_info += f"Resolution: {self.calculate_megapixels(image.width, image.height):.2f} MP\n"
        image_info += f"Color Mode: {'RGBA' if image.mode == 'RGBA' else 'RGB'}\n"  # Check if RGBA mode
        image_info += f"File Size: {self.get_formatted_file_size(os.path.getsize(image_path))}"

        self.info_text.delete('1.0', tk.END)
        self.info_text.insert(tk.END, image_info)

    def calculate_megapixels(self, width, height):
        return (width * height) / (10**6)

    def get_formatted_file_size(self, size_in_bytes):
        if size_in_bytes >= 1024 * 1024:
            return f"{size_in_bytes / (1024 * 1024):.2f} MB"
        elif size_in_bytes >= 1024:
            return f"{size_in_bytes / 1024:.2f} KB"
        else:
            return f"{size_in_bytes} bytes"

def main():
    root = tk.Tk()
    app = ImageGalleryApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()







