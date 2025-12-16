import os
from PIL import Image

def crop_transparency(file_path):
    """Crop transparent whitespace from a single image."""
    try:
        with Image.open(file_path) as img:
            # Convert to RGBA if not already
            img = img.convert("RGBA")
            
            # Get the bounding box of non-transparent pixels
            bbox = img.getbbox()
            
            if bbox:
                # Crop the image to the bounding box
                cropped_img = img.crop(bbox)
                
                # Save the cropped image, overwriting the original
                cropped_img.save(file_path)
                print(f"Cropped: {os.path.basename(file_path)} ({img.size} -> {cropped_img.size})")
                return True
            else:
                print(f"Skipped (empty or already clean): {os.path.basename(file_path)}")
                return False
                
    except Exception as e:
        print(f"Error processing {os.path.basename(file_path)}: {e}")
        return False

def crop_ico(file_path):
    """Crop ICO file - convert to PNG, crop, convert back."""
    try:
        with Image.open(file_path) as img:
            # ICO files can have multiple sizes, we'll work with the largest
            # Convert to RGBA
            img = img.convert("RGBA")
            original_size = img.size
            
            bbox = img.getbbox()
            
            if bbox:
                cropped_img = img.crop(bbox)
                # Save back as ICO
                cropped_img.save(file_path, format='ICO')
                print(f"Cropped: {os.path.basename(file_path)} ({original_size} -> {cropped_img.size})")
                return True
            else:
                print(f"Skipped (empty or already clean): {os.path.basename(file_path)}")
                return False
                
    except Exception as e:
        print(f"Error processing {os.path.basename(file_path)}: {e}")
        return False

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    public_folder = os.path.abspath(os.path.join(script_dir, '..', 'public'))
    
    # List of files to process
    files_to_crop = [
        'logo-source.png',
        'logo192.png',
        'logo512.png',
        'apple-touch-icon.png',
        'agent-icon.png',
    ]
    
    ico_files = [
        'favicon.ico',
    ]
    
    print(f"Processing files in: {public_folder}")
    print("-" * 40)
    
    # Process PNG files
    for filename in files_to_crop:
        file_path = os.path.join(public_folder, filename)
        if os.path.exists(file_path):
            crop_transparency(file_path)
        else:
            print(f"File not found: {filename}")
    
    # Process ICO files
    for filename in ico_files:
        file_path = os.path.join(public_folder, filename)
        if os.path.exists(file_path):
            crop_ico(file_path)
        else:
            print(f"File not found: {filename}")
    
    print("-" * 40)
    print("All done!")
