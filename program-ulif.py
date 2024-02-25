import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os

class ImageEncoderDecoderApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Image Encoder/Decoder")
        self.master.geometry("1000x600")
        self.upload_frame = tk.Frame(self.master, bd=2, relief=tk.RIDGE)
        self.upload_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10, side=tk.LEFT)
        self.display_frame = tk.Frame(self.master, bd=2, relief=tk.RIDGE)
        self.display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10, side=tk.RIGHT)
        self.upload_label = tk.Label(self.upload_frame, text="Upload Image to Encode:", font=('Helvetica', 12))
        self.upload_label.pack(pady=10)
        self.upload_button = tk.Button(self.upload_frame, text="Upload", command=self.upload_image, font=('Helvetica', 10))
        self.upload_button.pack(pady=5)
        self.decode_label = tk.Label(self.display_frame, text="Decoded Image:", font=('Helvetica', 12))
        self.decode_label.pack(pady=10)
        self.decode_button = tk.Button(self.display_frame, text="Decode", command=self.decode_image, font=('Helvetica', 10))
        self.decode_button.pack(pady=5)
        self.decoded_image_label = tk.Label(self.display_frame)
        self.decoded_image_label.pack(pady=10)
        self.image_info_label = tk.Label(self.display_frame, text="", justify="left", font=('Helvetica', 10))
        self.image_info_label.pack(pady=10)
        self.image = None

    def upload_image(self):
        filename = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if filename:
            self.image = Image.open(filename)
            self.image.thumbnail((400, 300))
            self.photo = ImageTk.PhotoImage(self.image)
            self.upload_button.config(text="Upload Another Image")

            ulif_filename = filedialog.asksaveasfilename(defaultextension=".ulif", filetypes=[("ULIF Files", "*.ulif")])
            if ulif_filename:
                self.encode_ulif(ulif_filename)

                image_info = self.get_image_info(ulif_filename)
                self.image_info_label.config(text=image_info)

    def encode_ulif(self, filename):
        if self.image:
            width, height = self.image.size
            pixel_data = self.image.tobytes()
            mode = self.image.mode  # Get image mode (e.g., "RGB", "RGBA", "P", etc.)

            with open(filename, 'wb') as f:
                f.write(width.to_bytes(4, byteorder='big'))
                f.write(height.to_bytes(4, byteorder='big'))
                f.write(mode.encode('ascii'))  # Encode mode as ASCII bytes
                f.write(pixel_data)

    def decode_image(self):
        filename = filedialog.askopenfilename(filetypes=[("ULIF Files", "*.ulif")])
        if filename:
            try:
                with open(filename, 'rb') as f:
                    width_bytes = f.read(4)
                    height_bytes = f.read(4)
                    mode_bytes = f.read(4)

                    if len(width_bytes) != 4 or len(height_bytes) != 4 or len(mode_bytes) != 4:
                        messagebox.showerror("Error", "Invalid ULIF file format")
                        return

                    width = int.from_bytes(width_bytes, byteorder='big')
                    height = int.from_bytes(height_bytes, byteorder='big')
                    mode = mode_bytes.decode('ascii', errors='replace')

                    pixel_data = f.read()

                decoded_image = Image.frombytes(mode, (width, height), pixel_data)
                decoded_image.thumbnail((400, 300))  # Resize image to fit in label
                decoded_photo = ImageTk.PhotoImage(decoded_image)
                self.decoded_image_label.configure(image=decoded_photo)
                self.decoded_image_label.image = decoded_photo

                image_info = self.get_image_info(filename)
                self.image_info_label.config(text=image_info)

            except Exception as e:
                messagebox.showerror("Error", f"Failed to decode ULIF file: {str(e)}")

    def get_image_info(self, filename):
        try:
            with open(filename, 'rb') as f:
                width_bytes = f.read(4)
                height_bytes = f.read(4)
                mode_bytes = f.read(4)

                if len(width_bytes) != 4 or len(height_bytes) != 4 or len(mode_bytes) != 4:
                    return "Error: Invalid ULIF file format"

                width = int.from_bytes(width_bytes, byteorder='big')
                height = int.from_bytes(height_bytes, byteorder='big')
                mode = mode_bytes.decode('ascii', errors='replace')

            format_info = f"Format: ULIF\n"
            mode_info = f"Mode: {mode}\n"
            size_info = f"Size: {width} x {height} pixels\n"
            file_size_info = f"File Size: {os.path.getsize(filename)} bytes"
            return format_info + mode_info + size_info + file_size_info

        except Exception as e:
            return f"Error: {str(e)}"

def main():
    root = tk.Tk()
    app = ImageEncoderDecoderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
