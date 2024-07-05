# 
# Planet textures are not distributed with the HDA but can be downloaded from the internet.
# We provide this utility script to download them easily. Please make sur to respect their distribution license.
# Solar System Scope: https://www.solarsystemscope.com/textures/
# Planet Texture Maps Wiki: https://planet-texture-maps.fandom.com/wiki/Planet_Texture_Maps_Wiki
# 

import urllib.request
import os
import subprocess

# Base URLs
base_url = "https://www.solarsystemscope.com/textures/download/"
pluto_url = "https://planet-texture-maps.fandom.com/wiki/Special:FilePath/Pluto_Made.png"

# List of image files
files = [
    "mercury.jpg",
    "venus_surface.jpg",
    "venus_atmosphere.jpg",
    "mars.jpg",
    "jupiter.jpg",
    "saturn.jpg",
    "saturn_ring_alpha.png",
    "uranus.jpg",
    "neptune.jpg",
    "earth_daymap.jpg",
    "earth_nightmap.jpg",
    "earth_clouds.jpg",
    "earth_normal_map.tif",
    "earth_specular_map.tif",
    "stars_milky_way.jpg",
    "sun.jpg",
    "moon.jpg"
]

# Resolutions
resolutions = ["2k", "8k"]

# Ask the user for resolution choice
print("Select resolution to download:")
print("1. 2K")
print("2. 8K")
print("3. Both")
choice = input("Enter choice (1/2/3): ")

if choice == "1":
    selected_resolutions = ["2k"]
elif choice == "2":
    selected_resolutions = ["8k"]
elif choice == "3":
    selected_resolutions = ["2k", "8k"]
else:
    print("Invalid choice. Defaulting to both 2K and 8K.")
    selected_resolutions = ["2k", "8k"]

# Directory to save images
save_dir = 'solar_system'

# Create directory if it doesn't exist
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# Function to check if URL exists
def url_exists(url):
    try:
        with urllib.request.urlopen(url) as response:
            return response.status == 200
    except Exception as e:
        print(f"Error checking URL {url}: {e}")
        return False

# Function to download an image from a URL
def download_image(url, filename=None):
    try:
        file_name = filename if filename else os.path.basename(url)
        file_path = os.path.join(save_dir, file_name)

        urllib.request.urlretrieve(url, file_path)
        print(f'Successfully downloaded {file_name}')
        return file_path
    except Exception as e:
        print(f'Failed to download {url}: {e}')
        return None

# Function to convert an image to .rat format using iconvert
def convert_to_rat(file_path):
    try:
        rat_file_path = file_path.rsplit('.', 1)[0] + '.rat'
        subprocess.run(['iconvert', file_path, rat_file_path], check=True)
        print(f'Converted {file_path} to {rat_file_path}')
    except subprocess.CalledProcessError as e:
        print(f'Failed to convert {file_path} to .rat: {e}')

# List to store paths of downloaded files
downloaded_files = []

# Loop through each file and resolution to download images
for file in files:
    for res in selected_resolutions:
        url = f"{base_url}{res}_{file}"
        if url_exists(url):
            downloaded_file_path = download_image(url)
            if downloaded_file_path:
                downloaded_files.append(downloaded_file_path)
        else:
            print(f"URL does not exist: {url}")

# Special case for Pluto image
if url_exists(pluto_url):
    pluto_downloaded_file_path = download_image(pluto_url, "pluto.png")
    if pluto_downloaded_file_path:
        downloaded_files.append(pluto_downloaded_file_path)
else:
    print(f"URL does not exist: {pluto_url}")

# Convert downloaded files to .rat format
for file_path in downloaded_files:
    convert_to_rat(file_path)
