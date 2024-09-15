import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import os

def convert_png_to_jpeg(image_path):
    img = Image.open(image_path)
    if img.format != 'PNG':
        messagebox.showerror("Conversion Error", "The selected file is not a PNG image.")
        return
    
    img = img.convert('RGB')  # Convert to RGB mode
    output_path = os.path.splitext(image_path)[0] + '.jpg'
    img.save(output_path, 'JPEG')
    return output_path

def optimize_image(image_path, target_size_kb, keep_format=False):
    img = Image.open(image_path)
    img_format = img.format
    
    if not keep_format:
        # Convert PNG to JPG if transparency is not required
        if img_format == 'PNG' and img.mode != 'RGBA':
            img = img.convert('RGB')
            img_format = 'JPEG'
            image_path = os.path.splitext(image_path)[0] + '.jpg'  # Adjust path for JPEG

    target_size_bytes = target_size_kb * 1024
    quality = 85  # Start with high quality for JPEG
    quality_step = 5  # Quality adjustment step

    temp_path = "temp_image." + img_format.lower()
    img_copy = img.copy()

    # Reduce quality iteratively
    while quality > 10:
        img_copy.save(temp_path, format=img_format, quality=quality)
        temp_size = os.path.getsize(temp_path)
        if temp_size <= target_size_bytes:
            break
        quality -= quality_step

    # If the image is still too large, resize it
    if temp_size > target_size_bytes:
        resize_factor = 0.9
        img_copy = img.copy()  # Restart with original image for resizing
        while temp_size > target_size_bytes and min(img_copy.size) > 100:
            new_size = (int(img_copy.size[0] * resize_factor), int(img_copy.size[1] * resize_factor))
            img_copy = img_copy.resize(new_size, Image.LANCZOS)
            img_copy.save(temp_path, format=img_format, quality=quality)
            temp_size = os.path.getsize(temp_path)
            resize_factor *= 0.9

    # Final save of the optimized image
    output_path = os.path.join(os.path.dirname(image_path), "optimized_" + os.path.basename(image_path))
    img_copy.save(output_path, format=img_format, quality=quality if img_format == 'JPEG' else None)
    
    # Remove the temporary file
    os.remove(temp_path)
    
    return output_path, os.path.getsize(image_path) / 1024, temp_size / 1024

def upload_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
    if file_path:
        entry_image_path.delete(0, tk.END)
        entry_image_path.insert(0, file_path)

def optimize():
    image_path = entry_image_path.get()
    try:
        target_size_kb = int(entry_target_size.get())
    except ValueError:
        messagebox.showerror("Input Error", "Please enter a valid number for the target size.")
        return
    
    if not image_path or not os.path.isfile(image_path):
        messagebox.showerror("File Error", "Please select a valid image file.")
        return
    
    try:
        # If the image is PNG, first convert to JPEG
        if image_path.lower().endswith('.png'):
            image_path = convert_png_to_jpeg(image_path)
        optimized_path, original_size, optimized_size = optimize_image(image_path, target_size_kb)
        messagebox.showinfo("Success", f"Original size: {original_size:.2f}KB\nOptimized size: {optimized_size:.2f}KB\nOptimized image saved as: {optimized_path}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def convert_png():
    image_path = entry_image_path.get()
    if not image_path or not os.path.isfile(image_path):
        messagebox.showerror("File Error", "Please select a valid PNG file.")
        return
    
    try:
        convert_png_to_jpeg(image_path)
        messagebox.showinfo("Success", "Image converted successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def optimize_png():
    image_path = entry_image_path.get()
    try:
        target_size_kb = int(entry_target_size.get())
    except ValueError:
        messagebox.showerror("Input Error", "Please enter a valid number for the target size.")
        return
    
    if not image_path or not os.path.isfile(image_path):
        messagebox.showerror("File Error", "Please select a valid PNG file.")
        return
    
    try:
        optimized_path, original_size, optimized_size = optimize_image(image_path, target_size_kb, keep_format=True)
        messagebox.showinfo("Success", f"Original size: {original_size:.2f}KB\nOptimized size: {optimized_size:.2f}KB\nOptimized image saved as: {optimized_path}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Create the main window
root = tk.Tk()
root.title("Image Optimizer")

# Create and place widgets
tk.Label(root, text="Image Path:").grid(row=0, column=0, padx=10, pady=10)
entry_image_path = tk.Entry(root, width=50)
entry_image_path.grid(row=0, column=1, padx=10, pady=10)
tk.Button(root, text="Browse", command=upload_image).grid(row=0, column=2, padx=10, pady=10)

tk.Label(root, text="Target Size (KB):").grid(row=1, column=0, padx=10, pady=10)
entry_target_size = tk.Entry(root, width=10)
entry_target_size.grid(row=1, column=1, padx=10, pady=10)

tk.Button(root, text="Optimize, this will first convert png to jpg", command=optimize).grid(row=2, column=0, columnspan=3, pady=10)

tk.Button(root, text="Convert PNG to JPEG", command=convert_png).grid(row=3, column=0, columnspan=3, pady=10)

tk.Button(root, text="Optimize PNG Only", command=optimize_png).grid(row=4, column=0, columnspan=3, pady=10)

# Start the Tkinter event loop
root.mainloop()
