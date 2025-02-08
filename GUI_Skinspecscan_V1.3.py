from tkinter import *
import tkinter as tk
from tkinter import ttk, filedialog
import uuid
import json
import os
from tkinter import messagebox
import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_pdf import PdfPages
from tkinter import filedialog, Canvas, Scrollbar, Frame
import csv
from PIL import Image, ImageTk
import webbrowser
import sys
#from process import ImageProcessor
'''I am trying different motions here, the ZOOM functionality is the old one'''


# Global variables for zoom control and ROI selection
zoom_factor = 1.0
image_display = None
zoomed_image = None
scaled_image = None
mouse_wheel_delta = 0.1  # Zoom step size
roi_start = None
roi_end = None
selecting_roi = False
spectral_signatures_tivita = {}
spectral_signatures_vis3 = {}
spectral_signatures_rn2 = {}
skin_signature_tivita = None  # To store skin signature for TIVITA
skin_signature_vis3 = None 
skin_signature_rn2 = None 
mole_count_tivita = 0  # Counter for mole ROIs for TIVITA
mole_count_vis3 = 0  # Counter for mole ROIs for VIS3
mole_count_rn2 = 0
base_directory_path = ""

# Lists to store ROI coordinates and labels for TIVITA and VIS3
rois_tivita = []
roi_labels_tivita = []
rois_vis3 = []
roi_labels_vis3 = []
rois_rn2 = []
roi_labels_rn2 = []

#scale_factor_x = 1.0
#scale_factor_y = 1.0
#use_scaling = False  # Flag to indicate whether scaling is applied
DISPLAY_SCALE_PERCENT = 75
# Minimum zoom factor to avoid zero or negative dimensions
MIN_ZOOM_FACTOR = 0.1
# Minimum image dimensions to avoid invalid sizes
MIN_IMAGE_DIMENSION = 50 # Set a reasonable lower bound for image width/height


my_data_list = []
json_file = 'databaseV3.json'

def show_splash():
    # Create a splash screen window
    splash_root = tk.Tk()
    splash_root.title("Welcome")
    splash_root.geometry("600x400")  # Set the size of the splash screen
    #splash_root.overrideredirect(True)  # Optional: remove title bar and borders
    splash_root.configure(bg="white") 
     
    # Center the splash screen on the screen
    screen_width = splash_root.winfo_screenwidth()
    screen_height = splash_root.winfo_screenheight()
    x = int((screen_width / 2) - (600 / 2))
    y = int((screen_height / 2) - (400 / 2))
    splash_root.geometry(f"600x400+{x}+{y}")
    
    # Add a welcome message or instructions for the user
    label = tk.Label(splash_root, text="Welcome to SkinSpecScan!",
    font=("Helvetica", 18, "bold"), 
    #pady=10,
    fg="#2a9df4",
    #bg="#2a9df4") 
    
    bg="white") 
    label.pack(pady=10)

    info_text = """
    This application analyzes spectral images 
    with their respective reflectance values taken by spectral cameras
    by selecting a ROI (Region of Interest) on the image 
    that can be visualised against different wavelengths.
    \n The images are taken by  Hyperspectral cameras: 
    TIVITA and BLACKMOBILE with wavelengths: 500 - 1000 nm
    \n and Multispectral cameras (IMEC VIS3 and RN2).
    IMEC VIS3 wavelengths: 460 - 600 nm 
    IMEC RN2 wavelengths: 600 - 850 nm
    \n Press 'continue' to the main application.
    """
    
    text_frame = tk.Frame(splash_root, bg="white", padx=20, pady=10)
    text_frame.pack(fill="both", expand=True)
    
    text_label = tk.Label(splash_root, text=info_text,  font=("Helvetica", 12),fg="black",bg="white",justify="center", wraplength=500)
    #text_label.pack(pady=20)
    text_label.pack(fill="both", expand=True)
    
    #frame = tk.Frame(splash_root, bg="white", width=350, height=2)
    #frame.pack(pady=(0, 20))
    
    # Add a 'Continue' button to close the splash screen
    continue_button = tk.Button(splash_root, text="Continue", command=splash_root.destroy, font=("Arial", 12))
    continue_button.pack(pady=20)

    # Keep the splash screen open until the user clicks 'Continue'
    splash_root.mainloop()

# Call the splash screen before running the main part of your application
show_splash()




primary = Tk()
primary.geometry("520x520")  # Updated width to fit the action buttons
primary.title('SkinSpecScan')



def open_pdf_():
    #pdf_path = r"C:\Users\user\OneDrive\Documents\Masterarbeit-doc\code\Fullcoverage\These_are_Test_images\HOW TO USE THE GUI.pdf"  # Replace with the path to your PDF file
    #webbrowser.open(pdf_path)
    if getattr(sys, 'frozen', False):
        # If running in a bundled environment, use sys._MEIPASS
        pdf_path = os.path.join(sys._MEIPASS, "assets", "HOW TO USE THE GUI.pdf")
    else:
        # If running in a development environment, use the relative path
        pdf_path = os.path.join("assets", "HOW TO USE THE GUI.pdf")
    try:
        if sys.platform == "win32":
            os.startfile(pdf_path)  # Windows
    except Exception as e:
        print(f"Failed to open PDF: {e}")
               
def load_data(directory_path="none"):
    global my_data_list
    global base_directory_path
    
    base_directory_path = directory_path
    
    if os.path.exists(json_file):
        with open(json_file, 'r') as f:
            try:
                my_data_list = json.load(f)
            except json.JSONDecodeError:
                my_data_list = []
    
    if directory_path != "none":
        try:
            number = 0
            for item in os.listdir(directory_path):
                item_path = os.path.join(directory_path, item)
                
                # Check if the item is a folder and if it starts with 'P'
                if os.path.isdir(item_path) and item.startswith("P"):
                    #trv.insert("", "end", values=("Link",item,"View | Edit | Delete"))
                    number+=1
                    trv.insert("", "end", values=(number,item,"View | Edit | Delete"))
                    link_directory(directory_path, item)
        except FileNotFoundError:
            print(f"The directory '{directory_path}' does not exist.")
            return []
                
# Function to ask the user to select a directory path
def choose_directory():
    directory_path = filedialog.askdirectory(title="Choose a directory")
    if directory_path:  # If a path is selected
        messagebox.showinfo("Path Selected", f"Directory: {directory_path}")
        
        load_data(directory_path)
        #open_new_window(directory_path)  # Proceed to open the "New Participant" window
    else:
        messagebox.showwarning("No Path Selected", "Please select a directory.")

# Function to open the child window for adding new participant
#def open_new_window():
#    new_window = Toplevel(primary)
#    new_window.title("New Participant")
#    new_window.geometry("300x200")
    
#    Label(new_window, text="Please add name as P01...P10:").pack(pady=10)
#    entry_name = Entry(new_window)
#    entry_name.pack(pady=5)

    
#    Button(new_window, text="Submit", command=lambda: save_participant(entry_name.get(),new_window)).pack(pady=20)
   

# Function to check for duplicate participants
def check_duplicate(name):
    for participant in my_data_list:
        if participant["name"] == name:
            return True
    return False

# Function to save participant data to the JSON file
def save_participant(name, window):
    if check_duplicate(name):
        messagebox.showwarning("Duplicate Entry", "Participant with the same name already exists!")
        return

    new_participant = { "name": name}
  
    trv.insert("", "end", values=("Link", name, "View | Edit | Delete"))
    my_data_list.append(new_participant)


    with open(json_file, 'w') as f:
        json.dump(my_data_list, f, indent=4)
    
    print(f"Saved participant: {name}")
    window.destroy()

# Function to handle item click in Treeview (View/Edit/Delete action) x1, y1, x2, y2, roi_width, roi_height = get_roi_coordinates()
def on_treeview_click(event):
    selected_item = trv.identify_row(event.y)  # Get the row that was clicked
    selected_column = trv.identify_column(event.x)  # Get the column that was clicked

    if selected_item:
        item_values = trv.item(selected_item, "values")
        participant_name = item_values[1]
        
        #if selected_column =='#1':
        #    update_link_directory(participant_name)

        if selected_column == '#3':  # If the 'ACTION' column is clicked
            # Get the clicked text within the action cell
            x_coord = event.x - trv.bbox(selected_item, '#3')[0]  # X position relative to 'ACTION' column
            if 0 <= x_coord < 40:  # If within the "View" region
                view_participant(participant_name)
            elif 41 <= x_coord < 60:  # If within the "Edit" region
                #edit_participant(participant_id)
                 open_part_selection(participant_name)
            elif 61 <= x_coord < 100:  # If within the "Delete" region
                delete_participant(participant_name)

# Function to view participant data in a new window
def view_participant_(participant_name):
    for participant in my_data_list:
        if participant["name"] == participant_name:
            
            # Get all body parts available in the participant's spectral data
            body_parts = participant["spectral_data"].keys()
            num_body_parts = len(body_parts)

            # Create a Matplotlib figure for the plot with multiple rows and columns
            num_spectral_types = 3  # We have 3 types: tivita, vis3, rn2
            fig, axes = plt.subplots(num_body_parts, num_spectral_types, figsize=(15, 5 * num_body_parts))

            if num_body_parts == 1:
                axes = [axes]  # Ensure axes are iterable even if there's only one body part

            # Spectral data types and their corresponding colors for the plots
            spectral_types = ["tivita", "vis3", "rn2"]
            titles = ["Tivita Spectral Data", "VIS3 Spectral Data", "RN2 Spectral Data"]
            #colors = ['r', 'g', 'b']  # Colors for each spectral type

             # Loop through each body part and plot the spectral data
            for row_idx, body_part in enumerate(body_parts):
                for col_idx, spectral_type in enumerate(spectral_types):
                    if spectral_type in participant["spectral_data"][body_part]:
                        spectral_info = participant["spectral_data"][body_part][spectral_type]

                        # Plot Skin Signature Data
                        if "skin_signature" in spectral_info:
                            skin_signature_data = spectral_info["skin_signature"][0].get("Data", None)
                            if skin_signature_data:
                                axes[row_idx, col_idx].plot(skin_signature_data, color='g', label="Skin Signature")
                            else:
                                print(f"No skin signature data found for {body_part} - {spectral_type}")

                        # Plot Mole Signature Data
                        mole_signatures = [key for key in spectral_info.keys() if key.startswith("mole_signature")]
                        for mole_key in mole_signatures:
                            mole_signature_data = spectral_info[mole_key][0].get("Data", None)
                            if mole_signature_data:
                                axes[row_idx, col_idx].plot(mole_signature_data, label=mole_key)
                            else:
                                print(f"No mole signature data found for {body_part} - {spectral_type} - {mole_key}")

                        # Set plot labels and titles
                        axes[row_idx, col_idx].set_title(f"{body_part} - {titles[col_idx]}")
                        axes[row_idx, col_idx].set_xlabel("Spectral Band")
                        axes[row_idx, col_idx].set_ylabel("Mean Reflectance")

                        # Ensure that the legend is only added if there are labels
                        handles, labels = axes[row_idx, col_idx].get_legend_handles_labels()
                        if labels:  # Only add legend if there are any labels
                            axes[row_idx, col_idx].legend()

                    else:
                        print(f"No data found for {body_part} - {spectral_type}")
                        axes[row_idx, col_idx].set_title(f"{body_part} - {titles[col_idx]}")
                        axes[row_idx, col_idx].text(0.5, 0.5, "No Data", horizontalalignment='center', verticalalignment='center')
                        axes[row_idx, col_idx].set_xticks([])
                        axes[row_idx, col_idx].set_yticks([])

            # Adjust layout to ensure proper spacing
            plt.tight_layout(rect=[0, 0.05, 1, 0.95])
            plt.show()

            break

# Define wavelength arrays for each modality
wavelengths_vis3 = [460.677376, 464.948464, 474.516065, 482.196347, 492.098648, 503.628412, 510.276276,
                    521.719879, 532.161709, 540.998523, 548.853675, 559.660970, 566.658505, 578.491654,
                    583.940412, 591.291963]
wavelengths_rn2 = [613.017069, 628.340847, 649.749287, 668.119267, 686.214169, 702.078574, 721.038983,
                   739.002701, 757.077485, 772.812665, 789.442170, 805.065490, 820.896383, 836.600471,
                   849.059844]
wavelengths_tivita = np.linspace(500, 1000, 100)  # Creates an array from 500 to 1000 with a step of 5

def interpolate_data_to_tivita(wavelengths, data, target_wavelengths):
    """Interpolates data to match the target wavelengths."""
    return np.interp(target_wavelengths, wavelengths, data)

def view_participant(participant_name):
    for participant in my_data_list:
        if participant["name"] == participant_name:
            
            # Get all body parts available in the participant's spectral data
            body_parts = list(participant["spectral_data"].keys())

            # Spectral data types and their corresponding titles for the plots
            spectral_types = ["tivita", "vis3", "rn2"]
            titles = ["Tivita Spectral Data", "VIS3 Spectral Data", "RN2 Spectral Data"]
            
            # Loop through each body part and create a figure for each with 3 subplots for Tivita, VIS3, and RN2
            for body_part in body_parts:
                print(f"\nInspecting body part: {body_part}")  # Debug
                fig, axes = plt.subplots(1, 3, figsize=(18, 6))  # One row, 3 columns for the 3 modalities

                for col_idx, (spectral_type, title) in enumerate(zip(spectral_types, titles)):
                    ax = axes[col_idx]  # Get the corresponding subplot axis

                    # Initialize overlay_info for vis3 and rn2
                    overlay_info = participant["spectral_data"][body_part].get("overlay", {})
                    spectral_info = participant["spectral_data"][body_part].get(spectral_type, {})

                    # Access the specific skin signature data for each spectral type
                    if spectral_type == "tivita":
                        skin_signature_data = np.array(spectral_info.get("skin_signature_tivita", [{}])[0].get("Data", []))
                        mole_signature_keys = [key for key in spectral_info.keys() if key.startswith("mole_signature_tivita")]
                        x_data = wavelengths_tivita
                    elif spectral_type == "vis3":
                        skin_signature_data = np.array(overlay_info.get("skin_signature_vis3", [{}])[0].get("Data", []))
                        mole_signature_keys = [key for key in overlay_info.keys() if key.startswith("mole_signature_vis3")]
                        x_data = wavelengths_vis3
                    elif spectral_type == "rn2":
                        skin_signature_data = np.array(overlay_info.get("skin_signature_rn2", [{}])[0].get("Data", []))
                        mole_signature_keys = [key for key in overlay_info.keys() if key.startswith("mole_signature_rn2")]
                        x_data = wavelengths_rn2

                    # Debug: Print keys to understand what's available
                    print(f"  Spectral info keys for {spectral_type}: {list(spectral_info.keys())}")
                    print(f"  Overlay info keys: {list(overlay_info.keys())}")

                    # Plot skin signature data if available
                    if len(skin_signature_data) > 0:
                        ax.plot(x_data, skin_signature_data, label=f"Skin Signature {spectral_type.capitalize()}", color='g')
                    else:
                        print(f"  No skin signature data found for {body_part} - {spectral_type}")

                    # Plot each mole signature key for the current spectral type
                    if mole_signature_keys:
                        for mole_key in mole_signature_keys:
                            mole_signature_data = (
                                np.array(spectral_info[mole_key][0].get("Data", [])) if spectral_type == "tivita"
                                else np.array(overlay_info[mole_key][0].get("Data", []))
                            )
                            if len(mole_signature_data) > 0:
                                ax.plot(x_data, mole_signature_data, label=mole_key, linestyle='--')
                            else:
                                print(f"  No data for mole signature {mole_key} in {body_part} - {spectral_type}")
                    else:
                        print(f"  No mole signature keys found for {spectral_type} in {body_part}")

                    # Set plot labels and titles for each modality of each body part
                    ax.set_title(f"{title} - {body_part}")
                    ax.set_xlabel("Wavelength (nm)")
                    ax.set_ylabel("Mean Reflectance")
                    ax.set_xlim(x_data[0], x_data[-1])
                    ax.set_ylim(0, 1)  # Set y-axis limits to a maximum of 1
                    # Ensure that the legend is added only if there are labels
                    handles, labels = ax.get_legend_handles_labels()
                    if labels:  # Only add legend if there are any labels
                        ax.legend()

                # Adjust layout and display the figure for this body part
                plt.tight_layout(rect=[0, 0.05, 1, 0.95])
                plt.show()

# Function to edit participant data
def edit_participant(participant_name):
    for participant in my_data_list:
        if participant["name"] == participant_name:
            new_window = Toplevel(primary)
            new_window.title("Edit Participant")
            new_window.geometry("300x200")

            Label(new_window, text="Name:").pack(pady=10)
            entry_name = Entry(new_window)
            entry_name.insert(0, participant["name"])
            entry_name.pack(pady=5)

            Button(new_window, text="Update", command=lambda: update_participant(participant_name, entry_name.get(), new_window)).pack(pady=20)
            break

# Function to update participant in Treeview and JSON file
def update_participant(participant_name, name,window):
    for i, participant in enumerate(my_data_list):
        if participant["name"] == participant_name:
            # Update participant details in memory
            my_data_list[i]["name"] = name
            

            # Update the Treeview
            for item in trv.get_children():
                if trv.item(item, "values")[1] == participant_name:
                    trv.item(item, values=("Link",participant_name, name, "View | Edit | Delete"))
                    break

            # Save updated data to the JSON file
            with open(json_file, 'w') as f:
                json.dump(my_data_list, f, indent=4)
            
            window.destroy()
            break

# Function to delete participant from Treeview and JSON file
def delete_participant(participant_name):
    confirm = messagebox.askyesno("Delete Participant", "Are you sure you want to delete this participant?")
    if confirm:
        for i, participant in enumerate(my_data_list):
            if participant["name"] == participant_name:
                # Remove from the list
                del my_data_list[i]

                # Remove from the Treeview
                for item in trv.get_children():
                    if trv.item(item, "values")[0] == participant_name:
                        trv.delete(item)
                        break

                # Save the updated list to the JSON file
                with open(json_file, 'w') as f:
                    json.dump(my_data_list, f, indent=4)

                print(f"Deleted participant with ID: {participant_name}")
                break

# function to link tge file Directory
def update_link_directory(participant_name):
    directory = filedialog.askdirectory()
    #base_directory_path = filedialog.askdirectory()
    for  participant in my_data_list:
        if participant["name"] == participant_name:
                    
            # create an ImagePath
            participant["folder_Path"] = directory
            #participant["folder_Path"] = base_directory_path
            
            # Save updated data to the JSON file
            with open(json_file, 'w') as f:
                json.dump(my_data_list, f, indent=4)
                
            
            print(f"Updated path: {directory}")
            #print(f"Updated path: {base_directory_path}")
            
def link_directory_(base_directory, participant_name):
    #directory = filedialog.askdirectory()
    directory = os.path.join(base_directory, participant_name)
    for  participant in my_data_list:
        if participant["name"] == participant_name:
                    
            # create an ImagePath
            participant["folder_Path"] = directory 
            
            # Save updated data to the JSON file
            with open(json_file, 'w') as f:
                json.dump(my_data_list, f, indent=4)
                
            print(f"Updated path: {directory}")

def link_directory(base_directory, participant_name):
    # Construct the directory path for the participant
    directory = os.path.join(base_directory, participant_name)
    
    # Check if the participant already exists in my_data_list
    participant_exists = False
    for participant in my_data_list:
        if participant["name"] == participant_name:
            participant_exists = True
            # Update the folder path for the existing participant
            participant["folder_Path"] = directory
            break

    # If the participant is not found, add a new entry
    if not participant_exists:
        new_participant = {
            "name": participant_name,
            "folder_Path": directory,
            "spectral_data": {}  # Assuming we start with an empty data structure for spectral_data
        }
        my_data_list.append(new_participant)

    # Save the updated participant data to the JSON file
    with open(json_file, 'w') as f:
        json.dump(my_data_list, f, indent=4)

    print(f"Updated path: {directory}")
           

    
# Function to open a child window for image uploads
def open_image_upload_window(participant_name, body_part):
    upload_window = Toplevel(primary)
    upload_window.title(f"Upload Images for {body_part}")
    upload_window.geometry("400x250")

    Label(upload_window, text=f"Upload 3 images for the {body_part}", font=("Arial", 12)).pack(pady=10)

    # Function to disable the button after clicking
    def disable_button(btn):
        btn.config(state="disabled")

    btn_image1 = Button(upload_window, text="TIVITA", command=lambda: [upload_image(1, participant_name, body_part), disable_button(btn_image1)])
    btn_image1.pack(pady=5)

    btn_image2 = Button(upload_window, text="Overlay (VIS3+RN2)", command=lambda: [upload_image(2, participant_name, body_part), disable_button(btn_image2)])
    btn_image2.pack(pady=5)

    Button(upload_window, text="Close", command=upload_window.destroy).pack(pady=20)

# Function to handle the next button click and open image upload windows for each selected body part
def handle_next_click(participant_name, selected_parts):
    for body_part in selected_parts:
        open_image_upload_window(participant_name, body_part)
        
def get_participant_parts(participant_name):
    global base_directory_path
    body_parts = []
    
    try:
        for body_part in os.listdir(os.path.join(base_directory_path, participant_name)):
            body_part_path = os.path.join(base_directory_path, participant_name, body_part)
            
            # Check if the item is a folder
            if os.path.isdir(body_part_path):
                body_parts.append(body_part)
        
        return body_parts
    except FileNotFoundError:
        print(f"The directory '{os.path.join(base_directory_path, participant_name)}' does not exist.")
        return []
    

# Function to open a child window for body part selection
def open_part_selection(participant_name):
    select_window = Toplevel(primary)
    select_window.title("Body Parts")
    select_window.geometry("400x450")

    # Define the list of body parts
    #body_parts = ['UA', 'FA', 'BA', 'HA', 'UT','LT', 'AD', 'FO', 'FC', 'CH']
    body_parts = get_participant_parts(participant_name)

    # Create a list to hold the IntVar for each checkbox
    vars_list = []

    Label(select_window, text="Select Body Part(s) \n\n mXX: Measurement number \n\n Body part (right or left) example: HA_r for Right Hand \n\n PXX: Participant Number", font=("Arial", 12)).pack(pady=10)

    # Dynamically create checkboxes based on the body_parts array
    for part in body_parts:
        var = IntVar()  # Create an IntVar for each checkbox
        vars_list.append(var)  # Add it to the vars_list
        c = Checkbutton(select_window, text=part, variable=var, onvalue=1, offvalue=0)
        c.pack()

    def collect_selected_parts():
        selected_parts = [body_parts[i] for i, var in enumerate(vars_list) if var.get() == 1]
        return selected_parts

    # "Next" button to move to the next step
    Button(select_window, text="Next", command=lambda: [select_window.destroy(), handle_next_click(participant_name, collect_selected_parts())]).pack(pady=20)

def update_spectral_data(participant_name, body_part, image_num, file_paths, skin_signatures, mole_signatures, skin_rois, mole_rois): 
    
    # Determine modality based on `image_num`
    if image_num == 1:  # TIVITA
        modality = "tivita"
        #skin_signatures_tivita = skin_signatures[0]
        #skin_signatures_tivita 
        mole_signatures_tivita = mole_signatures[0]
        #mole_signatures_tivita 
    elif image_num == 2:  # overlay of VIS3 and RN2
        modality = "overlay"
        skin_signatures_vis3 = skin_signatures[0]
        skin_signatures_rn2 = skin_signatures[1]
        mole_signatures_vis3 = mole_signatures[0]
        mole_signatures_rn2 = mole_signatures[1]
    else:
        raise ValueError("Invalid image number. Expected 1 (TIVITA) or 2 (Overlay of VIS3 and RN2).")

    # Find the participant in data
    for participant in my_data_list:
        if participant["name"] == participant_name:
            
            # Initialize 'spectral_data' if missing
            if "spectral_data" not in participant:
                participant["spectral_data"] = {}

            # Initialize body part section if missing
            if body_part not in participant["spectral_data"]:
                participant["spectral_data"][body_part] = {"tivita": {}, "overlay": {}}
                
            #if "skin_signature" not in participant["spectral_data"][body_part][modality]:
                #participant["spectral_data"][body_part][modality]["skin_signature"]= []
            
            # Store skin signatures for each modality
            if modality == "tivita":
                if "skin_signature" not in participant["spectral_data"][body_part][modality]:
                    participant["spectral_data"][body_part]["tivita"]["skin_signature_tivita"] = []
                    for i, roi in enumerate(skin_rois):
                    #for i in range(min(len(skin_signatures_tivita), len(skin_rois))):
                    #for i, roi in enumerate(skin_rois):
                        (top_left, bottom_right, roi_width, roi_height) = roi
                        x1, y1 = top_left
                        x2, y2 = bottom_right

                        modality_data_skin_tivita = {
                            "Data": skin_signatures_tivita.tolist(),
                            #"Data": skin_signatures_tivita[i].tolist(),
                            #"ROIs": {
                                #"x1": roi[0], "y1": roi[1],
                                #"x2": roi[2], "y2": roi[3],
                                #"w": roi[4], "h": roi[5],
                            "ROIs": {
                                "x1": x1, "y1": y1,  # From unpacked top-left
                                "x2": x2, "y2": y2,  # From unpacked bottom-right
                                "w": roi_width, "h": roi_height,
                            },
                        }
                        participant["spectral_data"][body_part]["tivita"]["skin_signature_tivita"].append(modality_data_skin_tivita)
                #if "mole_signature" not in participant["spectral_data"][body_part][modality]:
                   # participant["spectral_data"][body_part]["tivita"]["mole_signature"] = []
                    for i, roi in enumerate(mole_rois):
                        (top_left, bottom_right, roi_width, roi_height) = roi
                        x1, y1 = top_left
                        x2, y2 = bottom_right
                        mole_key_tivita = f"mole_signature_tivita_{i+1}"
                        
                            # Initialize the key as an empty list if it doesn't exist
                        participant["spectral_data"][body_part][modality][mole_key_tivita] = []
                        modality_data_mole_tivita = {
                            "Data": mole_signatures_tivita.tolist(),
                            #"Data":[signature.tolist() for signature in spectral_signatures_tivita[i]],
                            #"ROIs": {
                                #"x1": roi[0], "y1": roi[1],
                                #"x2": roi[2], "y2": roi[3],
                                #"w": roi[4], "h": roi[5],
                             "ROIs": {
                                "x1": x1, "y1": y1,  # From unpacked top-left
                                "x2": x2, "y2": y2,  # From unpacked bottom-right
                                "w": roi_width, "h": roi_height,
                            },
                        }
                        #participant["spectral_data"][body_part]["tivita"][mole_key_tivita] = modality_data_mole_tivita
                        participant["spectral_data"][body_part]["tivita"][mole_key_tivita].append(modality_data_mole_tivita)
            elif modality == "overlay":
                # Ensure necessary lists exist for overlay modality if not already present
                if "skin_signature_vis3" not in participant["spectral_data"][body_part]["overlay"]:
                    participant["spectral_data"][body_part]["overlay"]["skin_signature_vis3"] = []
                if "skin_signature_rn2" not in participant["spectral_data"][body_part]["overlay"]:
                    participant["spectral_data"][body_part]["overlay"]["skin_signature_rn2"] = []
                for i, roi in enumerate(skin_rois):
                    (top_left, bottom_right, roi_width, roi_height) = roi
                    x1, y1 = top_left
                    x2, y2 = bottom_right
                    modality_data_skin_vis3 = {
                        #"Data": skin_signatures_vis3[i].tolist(),
                        "Data": skin_signatures_vis3.tolist(),
                       #"ROIs": {
                           # "x1": roi[0], "y1": roi[1],
                            #"x2": roi[2], "y2": roi[3],
                            #"w": roi[4], "h": roi[5],
                        "ROIs": {
                                "x1": x1, "y1": y1,  # From unpacked top-left
                                "x2": x2, "y2": y2,  # From unpacked bottom-right
                                "w": roi_width, "h": roi_height,
                        },
                    }
                    modality_data_skin_rn2 = {
                        #"Data": skin_signatures_rn2[i].tolist(),
                        "Data": skin_signatures_rn2.tolist(),
                        #"ROIs": {
                            #x1": roi[0], "y1": roi[1],
                            #"x2": roi[2], "y2": roi[3],
                            #"w": roi[4], "h": roi[5],
                        "ROIs": {
                                "x1": x1, "y1": y1,  # From unpacked top-left
                                "x2": x2, "y2": y2,  # From unpacked bottom-right
                                "w": roi_width, "h": roi_height,
                        },
                    }
                    participant["spectral_data"][body_part]["overlay"]["skin_signature_vis3"].append(modality_data_skin_vis3)
                    participant["spectral_data"][body_part]["overlay"]["skin_signature_rn2"].append(modality_data_skin_rn2)
               
                for i, roi in enumerate(mole_rois):
                    (top_left, bottom_right, roi_width, roi_height) = roi
                    x1, y1 = top_left
                    x2, y2 = bottom_right
                    mole_key_vis3 = f"mole_signature_vis3_{i+1}"
                    mole_key_rn2 = f"mole_signature_rn2_{i+1}"
                      # Initialize the key as an empty list if it doesn't exist
                    participant["spectral_data"][body_part][modality][mole_key_vis3] = []
                      # Initialize the key as an empty list if it doesn't exist
                    participant["spectral_data"][body_part][modality][mole_key_rn2] = []
                    
                    modality_data_mole_vis3 = {
                       # "Data": mole_signatures_vis3[i].tolist(),
                        "Data": mole_signatures_vis3.tolist(),
                        #"ROIs": {
                            #"x1": roi[0], "y1": roi[1],
                            #"x2": roi[2], "y2": roi[3],
                            #"w": roi[4], "h": roi[5],
                        "ROIs": {
                                "x1": x1, "y1": y1,  # From unpacked top-left
                                "x2": x2, "y2": y2,  # From unpacked bottom-right
                                "w": roi_width, "h": roi_height,
                        },
                    }
                    modality_data_mole_rn2 = {
                        #"Data": mole_signatures_rn2[i].tolist(),
                        "Data": mole_signatures_rn2.tolist(),
                        #"ROIs": {
                            #"x1": roi[0], "y1": roi[1],
                            #"x2": roi[2], "y2": roi[3],
                            #"w": roi[4], "h": roi[5],
                        "ROIs": {
                                "x1": x1, "y1": y1,  # From unpacked top-left
                                "x2": x2, "y2": y2,  # From unpacked bottom-right
                                "w": roi_width, "h": roi_height,
                        },
                    }
                    participant["spectral_data"][body_part]["overlay"][mole_key_vis3].append(modality_data_mole_vis3)
                    participant["spectral_data"][body_part]["overlay"][mole_key_rn2].append(modality_data_mole_rn2)
                   

            # Save back to JSON
            with open(json_file, 'w') as f:
                json.dump(my_data_list, f, indent=4)

            print(f"Updated {modality} data for {body_part} of Participant ID: {participant_name}")
            return  # Exit after updating

    print(f"Participant ID {participant_name} not found.")

    
def get_first_subfolder(directory):
    try:
        # List all items in the directory
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            
            # Check if the item is a folder
            if os.path.isdir(item_path):
                return item  # Return the first subfolder found
    except FileNotFoundError:
        print(f"The directory '{directory}' does not exist.")
        return None

    return None  # If no subfolder is found

# Function to handle image upload and store the image path in JSON
def upload_image(image_num, participant_name, body_part):

    print(f"Uploading image {image_num} for {body_part} of participant {participant_name}")

    
    # Load participant data from the JSON file
    try:
        with open(json_file, 'r') as f:
            my_data_list = json.load(f)
    except FileNotFoundError:
        print("JSON file not found.")
        return
    
    # Find the participant by name
    participant = next((p for p in my_data_list if p['name'] == participant_name), None)
    
    if not participant:
        print(f"Participant '{participant_name}' not found.")
        return
    
    folder_path = participant.get('folder_Path')

    if not folder_path or not os.path.isdir(folder_path):
        print(f"Invalid folder path for participant '{participant_name}'.")
        return
    
    if image_num == 1: #tivita
        # Loads Tivita image and select ROI
        subfolder = "TIVITA"  # Name of the subdirectory you want to start in
        
        initial_directory = os.path.join(folder_path, body_part, subfolder, get_first_subfolder(os.path.join(folder_path, body_part, subfolder)))
        
        try:
            file_name = [f for f in os.listdir(initial_directory) if f.endswith(".dat")][0]
            file_path = os.path.join(initial_directory, file_name)
        except IndexError:
            print("No TIVITA file found.")
            return
        
        if not file_path:
            print("No file selected.")
            return

        if file_path:
            #skin_signature,spectral_signatures_tivita = process_tivita_file(file_path)
            skin_signatures, skin_rois, mole_signatures, mole_rois = process_tivita_file(file_path)
            #print(f"Skin signatures {skin_signatures} \n")
            #print(f"Skin roi {skin_rois} \n")
            #print(f"Mole signatures {mole_signatures} \n")
            #print(f"Mole roi {mole_rois} \n")
             # Check if processing was successful (i.e., both values are not None)
            if skin_signatures and mole_signatures:
                # Convert spectral_signatureTI to a list if it's a NumPy array
                if isinstance(skin_signatures, np.ndarray):
                    skin_signatures = skin_signature_tivita.tolist()
                if isinstance(mole_signatures, np.ndarray):
                    mole_signatures = spectral_signatures_tivita.tolist()
                    
                #x1, y1, x2, y2 = get_roi_coordinates()[:4]
                #update_spectral_data(participant_name,body_part,image_num, file_path,skin_signatures,mole_signatures, x1, y1,x2,y2)
                if skin_rois and mole_rois:
                    # Update the spectral data, passing ROI coordinates
                    update_spectral_data(participant_name, body_part, image_num, file_path, skin_signatures, mole_signatures, skin_rois, mole_rois)
                else:
                    print("Invalid ROI selection. Please select a valid ROI.")
            else:
                print("Failed to process the Tivita file. Spectral signature or ROI size is None.")
                return None
            
    if image_num == 2: 
        # Load both VIS3 and RN2 images and process as overlay
        vis3_subfolder = "VIS3"
        rn2_subfolder = "RN2"
        vis3_directory = os.path.join(folder_path, body_part, vis3_subfolder, "full_processed")
        #vis3_directory = os.path.join(folder_path, body_part, vis3_subfolder, "processed")
        rn2_directory = os.path.join(folder_path, body_part, rn2_subfolder, "full_processed")
        #rn2_directory = os.path.join(folder_path, body_part, rn2_subfolder, "processed")

        try:
            vis3_file = [f for f in os.listdir(vis3_directory) if f.endswith(".raw")][0]
            rn2_file = [f for f in os.listdir(rn2_directory) if f.endswith(".raw")][0]
            vis3_file_path = os.path.join(vis3_directory, vis3_file)
            rn2_file_path = os.path.join(rn2_directory, rn2_file)
        except IndexError:
            print("No VIS3 or RN2 file found.")
            return
        
    
        if not vis3_file_path or not rn2_file_path:
            print("No file selected.")
            return
        
        if vis3_file_path and rn2_file_path:
            result = process_and_register_vis3_rn2(vis3_file_path, rn2_file_path)
            if result is None:
                print("Failed to process and register VIS3 and RN2 file.")
                return
            #if skin_signatures and skin_rois and mole_signatures and mole_rois is not None:
            skin_signatures, skin_rois, mole_signatures, mole_rois = result
           # print(f"Skin signatures {skin_signatures} \n")
            #print(f"Skin roi {skin_rois} \n")
           #print(f"Mole signatures {mole_signatures} \n")
            #print(f"Mole roi {mole_rois} \n")
            # Check if processing was successful (i.e., both values are not None)
            if skin_signatures and mole_signatures:
                # Convert spectral_signatureTI to a list if it's a NumPy array
                if isinstance(skin_signatures, np.ndarray):
                    skin_signatures = skin_signatures.tolist()
                if isinstance(mole_signatures, np.ndarray):
                    mole_signatures = mole_signatures.tolist()
                if skin_rois and mole_rois:
                    # Update the spectral data, passing ROI coordinates
                    update_spectral_data(participant_name, body_part, image_num, [vis3_file_path, rn2_file_path], skin_signatures, mole_signatures, skin_rois, mole_rois)
                else:
                    print("Invalid ROI selection. Please select a valid ROI.")
                
            else:
                print("Failed to process VIS3 and RN2 file. Spectral signature or ROI size is None.")
                return None

    

##CSV STARTS HERE

# Function to determine the maximum number of mole signatures for dynamic header
def get_max_mole_signatures():
    max_mole_count = 0
    #row = [participant_name, body_part, modality]
    for participant in my_data_list:
        if "spectral_data" in participant:
            for body_part, modalities in participant["spectral_data"].items():
                for modality, data in modalities.items():
                    # Count the number of mole signatures (e.g., mole_signature_1, mole_signature_2, ...)
                    #mole_signatures = [key for key in data.keys() if key.startswith("mole_signature")]
                    #max_mole_count = max(max_mole_count, len(mole_signatures))
                     if isinstance(data, dict):
                        mole_signatures = [key for key in data.keys() if key.startswith("mole_signature")]
                        max_mole_count = max(max_mole_count, len(mole_signatures))
    return max_mole_count

# Function to extract Data and ROIs from the JSON structure
def extract_data_rois_(max_mole_count):
    extracted_data = []
    
    
    for participant in my_data_list:
        participant_name = participant.get("name", "Unknown")
        if "spectral_data" in participant:
            for body_part, modalities in participant["spectral_data"].items():
                for modality, data in modalities.items():
                     # Initialize an empty row
                    row = [participant_name, body_part, modality]
                    
                    # Prepare placeholders for mole signatures and skin signatures
                    mole_signatures = ["N/A"] * max_mole_count  # Placeholder for N mole signatures
                    skin_signature = "N/A"
                    
                     # Process mole signatures (e.g., mole_signature_1, mole_signature_2, ...)
                    #for key in data.keys():
                       # if key.startswith("mole_signature"):
                            #index = int(key.split("_")[-1]) - 1  # Get the index for the signature (e.g., 1 for mole_signature_1)
                            #mole_signatures[index] = ', '.join(map(str, data[key][0]["Data"]))  
                    # Process mole signatures if data is a dictionary
                    if isinstance(data, dict):
                        for key in data.keys():
                            if key.startswith("mole_signature"):
                                index = int(key.split("_")[-1]) - 1  # Get the index for the signature (e.g., 1 for mole_signature_1)
                                if index < max_mole_count and "Data" in data[key][0]:
                                    mole_signatures[index] = ', '.join(map(str, data[key][0]["Data"]))  
                        # Process skin signatures
                        if "skin_signature" in data:
                            skin_signature = ', '.join(map(str, data["skin_signature"][0]["Data"]))  # You can replace this with actual data if needed

                    # Append signatures to the row
                    row += mole_signatures + [skin_signature]
                    
                    # Add the row to the extracted data
                    extracted_data.append(row)
                    
                    
                                    
                
    return extracted_data

def extract_data_rois_(max_mole_count):
    extracted_data = []
    
    for participant in my_data_list:
        participant_name = participant.get("name", "Unknown")
        if "spectral_data" in participant:
            for body_part, modalities in participant["spectral_data"].items():
                for modality, data in modalities.items():
                    # Initialize an empty row
                    row = [participant_name, body_part, modality]
                    
                    # Prepare placeholders for mole signatures and skin signatures
                    mole_signatures = ["NaN"] * max_mole_count  # Placeholder for N mole signatures
                    #skin_signature = "NaN"
                    
                    # Ensure that data is a dictionary before accessing its keys
                    if isinstance(data, dict):
                        # Process mole signatures (e.g., mole_signature_1, mole_signature_2, ...)
                        for key in data.keys():
                            if key.startswith("mole_signature"):
                                try:
                                    # Safeguard access to data[key] and ensure the list has an entry
                                    if isinstance(data[key], list) and len(data[key]) > 0 and "Data" in data[key][0]:
                                        index = int(key.split("_")[-1]) - 1  # Get the index for the signature (e.g., 1 for mole_signature_1)
                                        if index < max_mole_count:
                                            mole_signatures[index] = ', '.join(map(str, data[key][0]["Data"]))
                                except (IndexError, KeyError, ValueError) as e:
                                    print(f"Error processing {key} for {participant_name}: {e}")
                                    continue

                       # Process skin signatures
                    skin_signatures = []
                   # Extract data from "tivita" section
                    tivita_data = data.get("tivita", {})
                    if "skin_signature_tivita" in tivita_data and "Data" in tivita_data["skin_signature_tivita"][0]:
                        skin_signatures.append(', '.join(map(str, tivita_data["skin_signature_tivita"][0]["Data"])))
                    else:
                        skin_signatures.append("N/A")
                    
                    # Extract data from "overlay" section
                    overlay_data = data.get("overlay", {})
                    if "skin_signature_vis3" in overlay_data and "Data" in overlay_data["skin_signature_vis3"][0]:
                        skin_signatures.append(', '.join(map(str, overlay_data["skin_signature_vis3"][0]["Data"])))
                    else:
                        skin_signatures.append("N/A")
                    
                    if "skin_signature_rn2" in overlay_data and "Data" in overlay_data["skin_signature_rn2"][0]:
                        skin_signatures.append(', '.join(map(str, overlay_data["skin_signature_rn2"][0]["Data"])))
                    else:
                        skin_signatures.append("N/A")
                    
                    # Append signatures to the row
                    row += mole_signatures + skin_signatures
                    # Add the row to the extracted data
                    extracted_data.append(row)
                    
    return extracted_data
def extract_data_rois(max_mole_count):
    extracted_data = []
    
    for participant in my_data_list:
        participant_name = participant.get("name", "Unknown")
        if "spectral_data" in participant:
            for body_part, modalities in participant["spectral_data"].items():
                for modality, data in modalities.items():
                    if modality == "tivita":
                        # Handle the "tivita" modality
                        row = [participant_name, body_part, "tivita"]
                        mole_signatures = ["NaN"] * max_mole_count
                        
                        # Process mole_signature_tivita
                        for key in data.keys():
                            if key.startswith("mole_signature_tivita"):
                                try:
                                    if isinstance(data[key], list) and len(data[key]) > 0 and "Data" in data[key][0]:
                                        index = int(key.split("_")[-1]) - 1  # Get the index for the signature
                                        if index < max_mole_count:
                                            mole_signatures[index] = ', '.join(map(str, data[key][0]["Data"]))
                                except (IndexError, KeyError, ValueError) as e:
                                    print(f"Error processing {key} for {participant_name}: {e}")
                                    continue

                        # Process skin_signature_tivita
                        skin_signature = "N/A"
                        if "skin_signature_tivita" in data and "Data" in data["skin_signature_tivita"][0]:
                            skin_signature = ', '.join(map(str, data["skin_signature_tivita"][0]["Data"]))

                        # Append to the row
                        row += mole_signatures + [skin_signature]
                        extracted_data.append(row)

                    elif modality == "overlay":
                        # Handle the "overlay" modality, treating "vis3" and "rn2" separately
                        for sub_modality in ["vis3", "rn2"]:
                            row = [participant_name, body_part, sub_modality]
                            mole_signatures = ["NaN"] * max_mole_count
                            
                            # Process mole_signature_vis3 or mole_signature_rn2
                            mole_key_prefix = f"mole_signature_{sub_modality}"
                            for key in data.keys():
                                if key.startswith(mole_key_prefix):
                                    try:
                                        if isinstance(data[key], list) and len(data[key]) > 0 and "Data" in data[key][0]:
                                            index = int(key.split("_")[-1]) - 1  # Get the index for the signature
                                            if index < max_mole_count:
                                                mole_signatures[index] = ', '.join(map(str, data[key][0]["Data"]))
                                    except (IndexError, KeyError, ValueError) as e:
                                        print(f"Error processing {key} for {participant_name}: {e}")
                                        continue

                            # Process skin_signature_vis3 or skin_signature_rn2
                            skin_signature_key = f"skin_signature_{sub_modality}"
                            skin_signature = "N/A"
                            if skin_signature_key in data and "Data" in data[skin_signature_key][0]:
                                skin_signature = ', '.join(map(str, data[skin_signature_key][0]["Data"]))

                            # Append to the row
                            row += mole_signatures + [skin_signature]
                            extracted_data.append(row)

    return extracted_data



# Function to save Data and ROIs as a CSV file
def save_data_rois_as_csv():
    max_mole_count = get_max_mole_signatures()  # Get the maximum number of mole signatures
    extracted_data = extract_data_rois(max_mole_count)
    
    if not extracted_data:
        messagebox.showwarning("No Data", "No Data or ROIs found in the JSON file.")
        return
    
    # Ask the user where to save the CSV file
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    
    if file_path:
        # Write the extracted data to a CSV file
        with open(file_path, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            
            # Create a dynamic header with N mole signatures
            mole_signature_headers = [f"mole_signature_{i+1}" for i in range(max_mole_count)]
            header = ['participant_name', 'body_part', 'modality'] + mole_signature_headers + ['skin_signature']
            writer.writerow(header)
            
            # Write the data rows
            writer.writerows(extracted_data)
        
        messagebox.showinfo("Success", f"Data and ROIs saved to {file_path}")
        

def mouse_callback_(event, x, y, flags, param):
    global zoom_factor, image_display, zoomed_image, roi_start, roi_end, selecting_roi
    #print(f"Mouse event: {event}, Position: ({x}, {y}), Flags: {flags}")
    # Check if the images are initialized before proceeding
    if image_display is None:
        return  # Exit if images are not initialized
    
    # Display coordinates dynamically on a temporary image copy
    #temp_image = zoomed_image.copy()
    #coordinates_text = f"Coordinates: ({x}, {y})"
    #cv2.putText(temp_image, coordinates_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    # Zoom in/out with mouse wheel
    if event == cv2.EVENT_MOUSEWHEEL:
        if flags > 0:  # Scroll up (zoom in)
            zoom_factor += mouse_wheel_delta
        else:  # Scroll down (zoom out)
            zoom_factor = max(MIN_ZOOM_FACTOR, zoom_factor - mouse_wheel_delta)

        # Resize image according to zoom factor
        new_width = int(image_display.shape[1] * zoom_factor)
        new_height = int(image_display.shape[0] * zoom_factor)
        if new_width >= MIN_IMAGE_DIMENSION and new_height >= MIN_IMAGE_DIMENSION:
            zoomed_image = cv2.resize(image_display, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
            cv2.imshow("Zoomable Image", zoomed_image)
            print(f"Resizing image to {new_width}x{new_height}") 
        else:
            print("Image too small to resize, skipping resize.")

    # ROI selection with left mouse button
    elif event == cv2.EVENT_LBUTTONDOWN:
        roi_start = (x, y)
        roi_end = (x, y)
        selecting_roi = True

    elif event == cv2.EVENT_MOUSEMOVE:
        if selecting_roi:
            roi_end = (x, y)
            temp_image = zoomed_image.copy()
            cv2.rectangle(temp_image, roi_start, roi_end, (255,0,0), 1)
            cv2.imshow("Zoomable Image", temp_image)
            

    elif event == cv2.EVENT_LBUTTONUP:
        roi_end = (x, y)
        selecting_roi = False
        cv2.rectangle(zoomed_image, roi_start, roi_end, (255,0,0), 1)
        cv2.imshow("Zoomable Image", zoomed_image)
        print(f"Coordinates after release: ({x}, {y})")
        
    #if event == cv2.EVENT_MOUSEMOVE:
        #print(f"Current Mouse Position: ({x}, {y})")                 

def mouse_callback(event, x, y, flags, param):
    global zoom_factor, x_start, y_start, image_display, zoomed_image, roi_start, roi_end, selecting_roi
    

    # Zoom in/out with mouse wheel
    if event == cv2.EVENT_MOUSEWHEEL:
        if flags > 0:  # Zoom in
            zoom_factor = min(zoom_factor * 1.1, 5)
        elif flags < 0:  # Zoom out
            zoom_factor = max(zoom_factor / 1.1, 1)
        else:
            return  # Do nothing if the event is not a valid zoom

        # Calculate new dimensions for the zoomed region
        new_width = int(image_display.shape[1] / zoom_factor)
        new_height = int(image_display.shape[0] / zoom_factor)

        # Calculate the top-left coordinates of the zoomed region centered on (x, y)
        x_start = max(0, min(image_display.shape[1] - new_width, x - new_width // 2))
        y_start = max(0, min(image_display.shape[0] - new_height, y - new_height // 2))

        # Crop and resize the zoomed region for display
        zoomed_img = image_display[y_start:y_start + new_height, x_start:x_start + new_width]
        zoomed_image = cv2.resize(zoomed_img, (image_display.shape[1], image_display.shape[0]), interpolation=cv2.INTER_LINEAR)

        # Display the updated zoomed image
        cv2.imshow('Zoomable Image', zoomed_image)

    # ROI selection with left mouse button
    elif event == cv2.EVENT_LBUTTONDOWN:
        roi_start = (x, y)
        roi_end = (x, y)
        
        selecting_roi = True
       
    elif event == cv2.EVENT_MOUSEMOVE:
        if selecting_roi:
            roi_end = (x, y)
            
            temp_image = zoomed_image.copy()
            
            cv2.rectangle(temp_image, roi_start, roi_end,  (255, 0, 0), -1)#(0, 255, 0), -1)
            cv2.imshow("Zoomable Image", temp_image)
            

    elif event == cv2.EVENT_LBUTTONUP:
        roi_end = (x, y)
        selecting_roi = False
        
        cv2.rectangle(zoomed_image, roi_start, roi_end, (255, 0, 0), -1) #(0, 255, 0), -1)
        cv2.imshow("Zoomable Image", zoomed_image)
        print(f"Coordinates after release: ({x}, {y})")
        

        # Print the ROI coordinates in the original image scale
        print(f"ROI coordinates in `image_display` scale: Start={roi_start}, End={roi_end}")
   

# Function to read ENVI header file metadata
def read_envi_header(header_path):
    metadata = {}
    with open(header_path, 'r') as file:
        for line in file:
            if '=' in line:
                key, value = line.split('=', 1)
                metadata[key.strip()] = value.strip()
    return metadata

# Function to select the ROI on the image
def get_roi_coordinates():
    global roi_start, roi_end, zoom_factor
    if roi_start and roi_end:
        x1, y1 = roi_start
        x2, y2 = roi_end

        # Normalises the coordinates to ensure proper ordering
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)

        # Adjust ROI coordinates to the original image scale
        #x1 = int(x1 / zoom_factor)
        #y1 = int(y1 / zoom_factor)
        #x2 = int(x2 / zoom_factor)
        #y2 = int(y2 / zoom_factor)
        x1 = int(x1 / zoom_factor + x_start)
        y1 = int(y1 / zoom_factor + y_start)
        x2 = int(x2 / zoom_factor + x_start)
        y2 = int(y2 / zoom_factor + y_start)
        
        
        
        
        # Calculate ROI width and height
        roi_width = x2 - x1
        roi_height = y2 - y1

        # Return the top-left and bottom-right coordinates of the ROI
        #return [x1, y1, x2, y2,  roi_width, roi_height]
    #return None, None, None, None, None, None
        if roi_width > 0 and roi_height > 0:
            print (x1, y1, x2, y2, roi_width, roi_height)
            #return [x1, y1, x2, y2, roi_width, roi_height]
            return (x1, y1), (x2, y2), roi_width, roi_height
            
        #else:
            #print("Invalid ROI dimensions (width or height is zero).")
            #return None, None, None, None, None, None
    #print("ROI start or end is not set.")
    #return None, None, None, None, None, None
        else:
            print("Invalid ROI dimensions.")
            return None
    else:
        print("ROI start or end not set.")
        return None
# Function to scale down the image for display purposes
def scale_image_for_display_(image, scale_percent=30):
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    dim = (width, height)
    return cv2.resize(image, dim, interpolation=cv2.INTER_AREA)

def select_mole_(data_cube, width, height, mole_count, file_type):
    global spectral_signatures_tivita, spectral_signatures_vis3,pectral_signatures_rn2, rois_tivita, roi_labels_tivita, rois_vis3, roi_labels_vis3, rois_rn2, roi_labels_rn2, mole_count_rn2
    #x1, y1, x2, y2  = get_roi_coordinates()[:4]
    x1, y1, x2, y2, roi_width, roi_height = get_roi_coordinates()


    if x1 is not None and y1 is not None:
        w = x2 - x1
        h = y2 - y1

        # Validate ROI dimensions
        #if x1 < 0 or y1 < 0 or x1 + w > width or y1 + h > height or w <= 0 or h <= 0:
        #    raise ValueError('Invalid ROI dimensions.')

        # Extract the ROI from the original data_cube (not the zoomed one)
        roi_image = data_cube[y1:y1+h, x1:x1+w, :]

        if roi_image.size == 0:
            raise ValueError('Selected ROI resulted in an empty slice.')

        # Calculate the spectral signature by averaging over the ROI
        spectral_signature_mole = np.mean(np.mean(roi_image, axis=0), axis=0)

        # Increment mole counter and label the ROI
        mole_count += 1
        label = f"Mole {mole_count}"
        roi_coordinates = (x1, y1, x2, y2)

        if file_type == "TIVITA":
            spectral_signatures_tivita[label] = spectral_signature_mole
            rois_tivita.append(roi_coordinates)  # Save the ROI coordinates
            roi_labels_tivita.append(label)      # Save the label
        elif file_type == "VIS3":
            spectral_signatures_vis3[label] = spectral_signature_mole
            rois_vis3.append(roi_coordinates)  # Save the ROI coordinates
            roi_labels_vis3.append(label)      # Save the label
        elif file_type == "RN2":
            spectral_signatures_rn2[label] = spectral_signature_mole
            rois_rn2.append(roi_coordinates)  # Save the ROI coordinates
            roi_labels_rn2.append(label) 
              
        messagebox.showinfo(f'{label} selected and spectral signature calculated.')
       # messagebox.showinfo('Mole selected and spectral signature calculated.')
    #return mole_count
    return spectral_signature_mole, mole_count
def select_mole(tivita_cube=None, vis3_cube=None, rn2_cube=None, aligned_vis3_display=None, warp_matrix=None, mole_count=0, file_type="TIVITA"):
    global spectral_signatures_vis3, spectral_signatures_rn2, spectral_signatures_tivita
    global rois_vis3, roi_labels_vis3, rois_rn2, roi_labels_rn2, rois_tivita, roi_labels_tivita
    
    # Retrieve coordinates for the selected ROI
    #x1, y1, x2, y2, roi_width, roi_height = get_roi_coordinates()
    #if x1 is None or y1 is None or x2 is None or y2 is None:
        #print("ROI coordinates are invalid; skipping mole selection.")
        #return None, None,mole_count
    
    result = get_roi_coordinates()
    if not result:
        print("Invalid ROI; skipping mole selection.")
        return None, mole_count

    # Unpack ROI coordinates and dimensions
    (x1, y1), (x2, y2), roi_width, roi_height = result
    w, h = x2 - x1, y2 - y1
    # Check if we are working with registered VIS3 and RN2 data
    if file_type == "overlay" and vis3_cube is not None and rn2_cube is not None:
        try:
            # Adjust ROI coordinates for VIS3 using the transformation from the warp matrix
            tx, ty = warp_matrix[0, 2], warp_matrix[1, 2]
            min_x, min_y = int(x1 - tx), int(y1 - ty)
            max_x, max_y = int(x1 + w - tx), int(y1 + h - ty)

            # Ensure coordinates are within bounds
            min_x, min_y = max(min_x, 0), max(min_y, 0)
            max_x, max_y = min(max_x, vis3_cube.shape[1] - 1), min(max_y, vis3_cube.shape[0] - 1)
            print(f"Adjusted coordinates for VIS3: min_x={min_x}, min_y={min_y}, max_x={max_x}, max_y={max_y}")

            # Extract and average ROI data for VIS3 and RN2
            roi_vis3 = vis3_cube[min_y:max_y, min_x:max_x, :]
            roi_rn2 = rn2_cube[y1:y1+h, x1:x1+w, :]
            
            #if roi_vis3.size == 0 or roi_rn2.size == 0:
                #print("Extracted ROI for VIS3 or RN2 is empty.")
                #return None, None, mole_count
            
            mole_signatures_vis3 = np.mean(roi_vis3, axis=(0, 1))
            mole_signatures_rn2 = np.mean(roi_rn2, axis=(0, 1))

            # Increment mole counter and label the ROI
            mole_count += 1
            label = f"Mole {mole_count}"
            roi_coordinates = (x1, y1, w, h)

            # Store the results
            spectral_signatures_vis3[label] = mole_signatures_vis3
            spectral_signatures_rn2[label] = mole_signatures_rn2
            rois_vis3.append(roi_coordinates)
            roi_labels_vis3.append(label)
            rois_rn2.append(roi_coordinates)
            roi_labels_rn2.append(label)

            messagebox.showinfo(f'{label} selected and spectral signatures calculated for VIS3 and RN2.')

            return mole_signatures_vis3, mole_signatures_rn2, mole_count
        except Exception as e:
            print(f"Error processing mole selection for overlay: {e}")
            return None, None, mole_count
    elif file_type == "TIVITA" and tivita_cube is not None:
        # Calculate ROI for TIVITA data
        roi_tivita = tivita_cube[y1:y1+h, x1:x1+w, :]

        # Calculate spectral signature for TIVITA
        mole_signatures_tivita = np.mean(roi_tivita, axis=(0, 1))

        # Increment mole counter and label the ROI
        mole_count += 1
        label = f"Mole {mole_count}"
        roi_coordinates = (x1, y1, w, h)

        # Store in TIVITA context
        spectral_signatures_tivita[label] = mole_signatures_tivita
        rois_tivita.append(roi_coordinates)
        roi_labels_tivita.append(label)

        messagebox.showinfo(f'{label} selected and spectral signature calculated for TIVITA.')

        return mole_signatures_tivita,mole_count

# Function to handle skin selection logic
def select_skin_(data_cube, width, height, file_type):
    global skin_signature_tivita, skin_signature_vis3,skin_signature_rn2, rois_tivita, rois_vis3, rois_rn2
    #x1, y1, x2, y2= get_roi_coordinates()[:4]
    #x1, y1, x2, y2, roi_width, roi_height = get_roi_coordinates()
    (x1, y1), (x2, y2), roi_width, roi_height = get_roi_coordinates()

    if x1 is not None and y1 is not None:
        w = x2 - x1
        h = y2 - y1

        # Validate ROI dimensions
        #print(f"w: {w}\n")
        #print(f"h: {h}\n")
        #print(f"width: {width}\n")
        #print(f"height: {height}\n")
        #print(f"x1: {x1}\n")
        #print(f"x2: {x2}\n")
        #print(f"y1: {y1}\n")
        #print(f"y2: {y2}\n")
        #if x1 < 0 or y1 < 0 or x1 + w > width or y1 + h > height or w <= 0 or h <= 0:
        #    raise ValueError('Invalid ROI dimensions.')

        # Extract the ROI from the original data_cube (not the zoomed one)
        roi_image = data_cube[y1:y1+h, x1:x1+w, :]

        if roi_image.size == 0:
            raise ValueError('Selected ROI resulted in an empty slice.')

        # Calculate the spectral signature for the skin
        skin_signature = np.mean(np.mean(roi_image, axis=0), axis=0)
        # Store the skin ROI and signature
        roi_coordinates = (x1, y1, x2, y2)  # Store the ROI coordinates
        if file_type == "TIVITA":
            skin_signature_tivita = skin_signature
            rois_tivita.append(roi_coordinates)  # Save the ROI coordinates
            roi_labels_tivita.append("Skin")     # Save the label
        elif file_type == "VIS3":
            skin_signature_vis3 = skin_signature
            rois_vis3.append(roi_coordinates)  # Save the ROI coordinates
            roi_labels_vis3.append("Skin")     # Save the label
        elif file_type == "RN2":
            skin_signature_rn2 = skin_signature
            rois_rn2.append(roi_coordinates)  # Save the ROI coordinates
            roi_labels_rn2.append("Skin")

        messagebox.showinfo('Skin region selected and spectral signature calculated.')
        
    return skin_signature
def select_skin(tivita_cube=None, vis3_cube=None, rn2_cube=None, aligned_vis3_display=None, warp_matrix=None, file_type="TIVITA"):
    global skin_signatures_vis3, skin_signatures_rn2,skin_signatures_tivita
    global rois_vis3, roi_labels_vis3, rois_rn2, roi_labels_rn2, rois_tivita, roi_labels_tivita
   
    
    result = get_roi_coordinates()
    if not result:
        print("Invalid ROI; skipping mole selection.")
        return None
    
    # Retrieve coordinates for the selected ROI
    (x1, y1), (x2, y2), roi_width, roi_height = get_roi_coordinates()
    # Validate ROI coordinates
    #if x1 is None or y1 is None or x2 is None or y2 is None:
        #print("ROI coordinates are None.")
        #return None, None
    
    #if x1 is not None and y1 is not None:
       # w = x2 - x1
        #h = y2 - y1
    w, h = x2 - x1, y2 - y1
    if file_type == "overlay" and vis3_cube is not None and rn2_cube is not None:
        # Adjust ROI coordinates for VIS3 using the warp matrix from registration
        tx, ty = warp_matrix[0, 2], warp_matrix[1, 2]
        min_x, min_y = int(x1 - tx), int(y1 - ty)
        max_x, max_y = int(x1 + w - tx), int(y1 + h - ty)

        # Ensure coordinates are within bounds for VIS3
        min_x, min_y = max(min_x, 0), max(min_y, 0)
        max_x, max_y = min(max_x, vis3_cube.shape[1] - 1), min(max_y, vis3_cube.shape[0] - 1)

        # Extract and calculate spectral signature for both VIS3 and RN2
        roi_vis3 = vis3_cube[min_y:max_y, min_x:max_x, :]
        roi_rn2 = rn2_cube[y1:y1+h, x1:x1+w, :]
        
        skin_signatures_vis3 = np.mean(roi_vis3, axis=(0, 1))
        skin_signatures_rn2 = np.mean(roi_rn2, axis=(0, 1))

        # Define label and ROI coordinates
        label = "Skin"
        roi_coordinates = (x1, y1, w, h)

        # Store results for VIS3 and RN2
        spectral_signatures_vis3[label] = skin_signatures_vis3
        spectral_signatures_rn2[label] = skin_signatures_rn2
        rois_vis3.append(roi_coordinates)
        roi_labels_vis3.append(label)
        rois_rn2.append(roi_coordinates)
        roi_labels_rn2.append(label)

        messagebox.showinfo("Skin ROI selected and spectral signatures calculated for VIS3 and RN2.")

        # Return only VIS3 spectral signature for consistency
        return skin_signatures_vis3, skin_signatures_rn2

    elif file_type == "TIVITA"and tivita_cube is not None:
        # Extract ROI from TIVITA data cube
        roi_tivita = tivita_cube[y1:y1+h, x1:x1+w, :]

        # Calculate spectral signature for TIVITA
        skin_signatures_tivita = np.mean(roi_tivita, axis=(0, 1))

        # Define label and ROI coordinates
        label = "Skin"
        roi_coordinates = (x1, y1, w, h)

        # Store results for TIVITA
        spectral_signatures_tivita[label] = skin_signatures_tivita
        rois_tivita.append(roi_coordinates)
        roi_labels_tivita.append(label)

        messagebox.showinfo("Skin ROI selected and spectral signature calculated for TIVITA.")

        return skin_signatures_tivita

# Function to process tivita files and select a ROI  
def process_tivita_file(file_path):
    global image_display, zoomed_image, zoom_factor, mole_count_tivita
    #use_scaling, scale_factor_x, scale_factor_y
    mole_count_tivita = 0
    try:
        with open(file_path, 'rb') as file:
            cube_shape = np.fromfile(file, dtype='>i', count=3)  # opens the Tivita file
            width = cube_shape[0]
            height = cube_shape[1]
            channels = cube_shape[2]
          
        data = np.fromfile(file_path, dtype='>f', offset=12)
        tivita_cube = data.reshape((width, height, channels))

        # Select ROI on the first spectral band
        first_band = tivita_cube[:, :, 3]  # Selects all rows, columns, and the first spectral band
        normalized_band = (first_band - np.min(first_band)) / (np.max(first_band) - np.min(first_band)) * 255
        image_display = normalized_band.astype(np.uint8)
        
        clahe = cv2.createCLAHE(clipLimit=5.0, tileGridSize=(8, 8))
        image_display = clahe.apply(image_display)
        
        zoomed_image = image_display.copy()
        
        # Create a window and set the mouse callback for zooming and ROI selection
        #cv2.namedWindow("Zoomable Image")
        cv2.namedWindow("Zoomable Image")
        if cv2.getWindowProperty("Zoomable Image", cv2.WND_PROP_VISIBLE) >= 1:
            print("Window 'Zoomable Image' successfully created.")
        else:
            print("Failed to create 'Zoomable Image' window.")
        cv2.setMouseCallback("Zoomable Image", mouse_callback)
        
        # Display the image and let the user control zoom and ROI selection
        #cv2.imshow("Zoomable Image", zoomed_image)
        
        #mole_count = 0  # Counter for mole ROIs
        mole_signatures = []
        mole_rois = []
        skin_signatures = []
        skin_rois = []
        while True:
            cv2.imshow("Zoomable Image", zoomed_image)
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC key to exit
                break
            elif key == ord('s'):  # 's' key for selecting normal skin
                skin_signature_tivita = select_skin(tivita_cube, file_type="TIVITA")
                #skin_rois.append(get_roi_coordinates())
                roi_data = get_roi_coordinates()
                if roi_data:
                    #(x1, y1), (x2, y2), _, _ = roi_data
                #skin_rois.append(((x1, y1), (x2, y2)))
                    (top_left, bottom_right, roi_width, roi_height) = roi_data
                    x1, y1 = top_left
                    x2, y2 = bottom_right
                # Append directly to skin_rois without reconstructing
                skin_rois.append(roi_data)
                cv2.rectangle(image_display, (x1, y1), (x2, y2), (255, 0, 0), -1)
                print(f"skin signature {skin_signature_tivita} \n")
                print(f"skin roi {roi_data} \n")
                
                if (skin_signature_tivita.any()):
                    skin_signatures.append(skin_signature_tivita)
                else:
                    print("Failed to collect mole signature for TIVITA (ROI may be invalid).")
                #print(f"skin signature {skin_signature_tivita} \n")
                #print(f"skin roi {skin_rois} \n")
                #if skin_signature_tivita is not None:
                   # skin_rois.append(get_roi_coordinates())
                    #skin_signatures.append(skin_signature_tivita)
                
                    #print(f"Skin signature collected for TIVITA: {skin_signature_tivita}")
                #else:
                    #print("Failed to collect skin signature for TIVITA (ROI may be invalid).")
                
            elif key == ord('m'):  # When user presses 'Enter', confirm mole ROI selection
                
                mole_signature_tivita, mole_count_tivita = select_mole(tivita_cube, mole_count=mole_count_tivita, file_type="TIVITA")
                #mole_rois.append(get_roi_coordinates())
                roi_data = get_roi_coordinates()
                if roi_data:
                    #(x1, y1), (x2, y2), _, _ = roi_data
                #mole_rois.append(((x1, y1), (x2, y2)))
                    (top_left, bottom_right, roi_width, roi_height) = roi_data
                    x1, y1 = top_left
                    x2, y2 = bottom_right
                # Append directly to skin_rois without reconstructing
                mole_rois.append(roi_data)
                cv2.rectangle(image_display, (x1, y1), (x2, y2), (255, 0, 0), -1) 
                print(f"mole signature {mole_signature_tivita} \n")
                print(f"mole roi {roi_data} \n")
                
                if (mole_signature_tivita.any()):
                    mole_signatures.append(mole_signature_tivita)
                    print(f"mole signature {mole_signature_tivita} \n")
                else:
                    print("Failed to collect mole signature for TIVITA (ROI may be invalid).")
                
                #break
            elif key == 27:  # Press 'Esc' to exit and display results
                break
            elif cv2.getWindowProperty('Zoomable Image', cv2.WND_PROP_VISIBLE) < 1:
                break
        cv2.destroyAllWindows()
            
        return skin_signatures, skin_rois, mole_signatures, mole_rois
    except Exception as e:
        messagebox.showerror('Processing Error', f'Failed to process the Tivita file: {e}')
        return None, None, None, None

#Function to process VIS3 files and select an ROI
def process_vis3_file_(file_path, file_type="VIS3"):
    global scaled_image, scale_factor_x, scale_factor_y, use_scaling, image_display, mole_count_vis3
    mole_count_vis3 = 0
    try:
        width, height, channels = 270, 510, 16
        data = np.fromfile(file_path, dtype=np.float32)
        data_cube = data.reshape((width, height, channels))

        # Normalize and prepare the first spectral band for display
        first_band = data_cube[:, :, 3]
        normalized_band = (first_band - np.min(first_band)) / (np.max(first_band) - np.min(first_band)) * 255
        image_display = normalized_band.astype(np.uint8)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        image_display = clahe.apply(image_display)
        
        zoomed_image = image_display.copy()
        # Set scaling behavior based on file type
        if file_type in ["VIS3", "RN2"]:
            use_scaling = True
            #Scale down the image for display
            scale_percent = 95
            #Adjust as needed for your screen
            #scaled_image = scale_image_for_display(image_display, scale_percent)
            #Compute the scale factors for translating ROI back to the original image resolution
            scale_factor_x = width / scaled_image.shape[1]
            scale_factor_y = height / scaled_image.shape[0]
            zoomed_image = scaled_image.copy()
            
        else:
            use_scaling = False
            zoomed_image = image_display.copy()

        # Create a window and set the mouse callback for zooming and ROI selection
        cv2.namedWindow("Zoomable Image")
        cv2.setMouseCallback("Zoomable Image", mouse_callback)

        # Display the image and let the user control zoom and ROI selection
        cv2.imshow("Zoomable Image", zoomed_image)
        #cv2.imshow("Zoomable Image", enhanced_image)
        #mole_count = 0 
        mole_signatures = []
        mole_rois = []
        skin_signatures = []
        skin_rois = []
        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == ord('s'):  # 's' key for selecting normal skin
                skin_signature_vis3=select_skin(data_cube, width, height, file_type="VIS3")
                skin_rois.append(get_roi_coordinates())
                print(f'skin signature {skin_signature_vis3}\n')
                if (skin_signature_vis3.any()):
                   skin_signatures.append(skin_signature_vis3)
            elif key == 13:  # When user presses 'Enter', confirm mole ROI selection
                #mole_count = select_mole(data_cube, width, height, mole_count_vis3)
                mole_signature_vis3, mole_count_vis3 = select_mole(data_cube, width, height, mole_count_vis3, file_type="VIS3")
                mole_rois.append(get_roi_coordinates())
                if (mole_signature_vis3.any()):
                    mole_signatures.append(mole_signature_vis3)
            elif key == 27:  # Press 'Esc' to exit and display results
                break
            elif cv2.getWindowProperty('Zoomable Image', cv2.WND_PROP_VISIBLE) < 1:
                break
        cv2.destroyAllWindows()
        return skin_signatures,skin_rois, mole_signatures,mole_rois
    except Exception as e:
        print(f"Failed to process the VIS3 file: {e}")
        return None

# Function to process VIS3 files and select an ROI
def process_rn2_file_(file_path, file_type="RN2"):
    global scaled_image, scale_factor_x, scale_factor_y, use_scaling, image_display, mole_count_rn2
    mole_count_rn2 = 0;
    try:
        width, height, channels = 270, 510, 15
        data = np.fromfile(file_path, dtype=np.float32)
        data_cube = data.reshape((width, height, channels))

        # Normalize and prepare the first spectral band for display
        first_band = data_cube[:, :, 3]
        normalized_band = (first_band - np.min(first_band)) / (np.max(first_band) - np.min(first_band)) * 255
        image_display = normalized_band.astype(np.uint8)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        image_display = clahe.apply(image_display)

        zoomed_image = image_display.copy()

        # Create a window and set the mouse callback for zooming and ROI selection
        cv2.namedWindow("Zoomable Image")
        cv2.setMouseCallback("Zoomable Image", mouse_callback)

        # Display the image and let the user control zoom and ROI selection
        #cv2.imshow("Zoomable Image", zoomed_image)
        #cv2.imshow("Zoomable Image", enhanced_image)
        #mole_count = 0 
        mole_signatures = []
        mole_rois = []
        skin_signatures = []
        skin_rois = []
        while True:
            cv2.imshow("Zoomable Image", zoomed_image)
            key = cv2.waitKey(1) & 0xFF# Check if the window is closed
            if key == 27:  # Press 'Esc' to exit and display results
                break
            elif key == ord('s'):  # 's' key for selecting normal skin
                skin_signature_rn2 = select_skin(data_cube, width, height, file_type="RN2")
                skin_rois.append(get_roi_coordinates())
                print(f'skin signature rn2: {skin_signature_rn2}')
                if (skin_signature_rn2.any()):
                    skin_signatures.append(skin_signature_rn2)
            elif key == 13:  # When user presses 'Enter', confirm mole ROI selection
                #mole_count = select_mole(data_cube, width, height, mole_count_vis3)
                mole_signature_rn2, mole_count_rn2 = select_mole(data_cube, width, height, mole_count_rn2, file_type="RN2")
                mole_rois.append(get_roi_coordinates())
                if (mole_signature_rn2.any()):
                    mole_signatures.append(mole_signature_rn2)

            #elif key == 27:  # Press 'Esc' to exit and display results
                #break
            elif cv2.getWindowProperty('Zoomable Image', cv2.WND_PROP_VISIBLE) < 1:
                break
        cv2.destroyAllWindows()
        return skin_signatures,skin_rois, mole_signatures, mole_rois
    except Exception as e:
        print(f"Failed to process the RN2 file: {e}")
        return None

    return data_cube, enhanced_band 
# Main function to process, overlay, and apply zoom and ROI selection for VIS3 and RN2
def process_and_register_vis3_rn2(vis3_file_path, rn2_file_path):
    global image_display, zoomed_image, mole_count, mole_signatures, skin_signatures, mole_rois, skin_rois
    #scale_factor_x, scale_factor_y,
    mole_count = 0
    try:
        
        vis3_data = np.fromfile(vis3_file_path, dtype=np.float32)
        if vis3_data.size == 0:
            print("Failed to load VIS3 file, data is empty.")
            return None
        vis3_cube = vis3_data.reshape((270, 510, 16))
        print(f"Loaded VIS3 data with shape: {vis3_cube.shape}")
        rn2_data = np.fromfile(rn2_file_path, dtype=np.float32)
        if rn2_data.size == 0:
            print("Failed to load RN2 file, data is empty.")
            return None
        rn2_cube = rn2_data.reshape((270, 510, 15))
        print(f"Loaded RN2 data with shape: {rn2_cube.shape}")

        
        vis3_display = cv2.normalize(vis3_cube[:, :, 15], None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        rn2_display = cv2.normalize(rn2_cube[:, :, 0], None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        clahe = cv2.createCLAHE(clipLimit=5.0, tileGridSize=(8, 8))
        vis3_display = clahe.apply(vis3_display)
        rn2_display = clahe.apply(rn2_display)

       
        #warp_matrix = np.eye(2, 3, dtype=np.float32)
        warp_matrix = np.eye(3, 3, dtype=np.float32) # Homography
        
        motion_type = cv2.MOTION_HOMOGRAPHY 
        #motion_type = cv2.MOTION_AFFINE
        #motion_type = cv2.MOTION_TRANSLATION
        # Sets termination criteria for ECC alignment
        #criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 500, 1e-5)
        criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 2000, 1e-7) # HOMOGRAPHY

        # Converts images to float32 for ECC
        #vis3_gray = vis3_display.astype(np.float32)
        #rn2_gray = rn2_display.astype(np.float32)

       
        try:
            cc, warp_matrix = cv2.findTransformECC(rn2_display.astype(np.float32), vis3_display.astype(np.float32), warp_matrix, motion_type, criteria)

            
            height, width = rn2_display.shape
            #aligned_vis3_display = cv2.warpAffine(vis3_display, warp_matrix, (width, height), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)
            aligned_vis3_display = cv2.warpPerspective(vis3_display, warp_matrix, (width, height), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP) #HOMOGRAPHY
            print("ECC registration with translation applied.")
            print(f'size of aligned_vis3_display: {aligned_vis3_display.shape}')
            print(f'size of rn2_display: {rn2_display.shape}')
        except cv2.error as e:
            print("ECC registration failed:", e)
            return None, None, None, None
        
      
        if aligned_vis3_display is None:
            print("Failed to align VIS3 to RN2.")
            return None
        
        #Cyan(like blue)
        vis3_color = np.zeros((aligned_vis3_display.shape[0], aligned_vis3_display.shape[1], 3), dtype=np.uint8)
        vis3_color[:, :, 0] = aligned_vis3_display
        vis3_color[:, :, 1] = aligned_vis3_display
        
         # Set RN2 to Magnenta(like pink)
        rn2_color = np.zeros((rn2_display.shape[0], rn2_display.shape[1], 3), dtype=np.uint8)
        # [:, :, 2] and [:, :, 0] for magnenta that looks like pink
        rn2_color[:, :, 2] = rn2_display  # Set green channel
        rn2_color[:, :, 0] = rn2_display
        # Make VIS3 translucent after registration
        #vis3_rgb = cv2.cvtColor(aligned_vis3_display, cv2.COLOR_GRAY2BGR)  # Convert to BGR for blending
        #rn2_rgb = cv2.cvtColor(rn2_display, cv2.COLOR_GRAY2BGR)  # Convert RN2 to BGR as well

        # Set alpha for translucency level (0.5 for 50% transparency)
        alpha = 0.5
        translucent_overlay = cv2.addWeighted(vis3_color, alpha, rn2_color, 1 - alpha, 0)

        # Set initial image display
        #image_display = aligned_vis3_display.copy()
        image_display = translucent_overlay.copy()
        zoomed_image = image_display.copy()
        
        
        
        cv2.namedWindow("Zoomable Image")
        if cv2.getWindowProperty("Zoomable Image", cv2.WND_PROP_VISIBLE) >= 1:
            print("Window 'Zoomable Image' successfully created.")
        else:
            print("Failed to create 'Zoomable Image' window.")
        cv2.setMouseCallback("Zoomable Image", mouse_callback)
        print("Mouse callback set for 'Zoomable Image'.")
        #cv2.imshow("Zoomable Image", zoomed_image)
        
        # Initialize storage for ROI data
        mole_signatures = []
        mole_rois = []
        skin_signatures = []
        skin_rois = []

        while True:
            print("Entering display loop.")
            cv2.imshow("Zoomable Image", zoomed_image)
            #key = cv2.waitKey(1) & 0xFF
            key = cv2.waitKey(0) & 0xFF  # Wait for key input for each interaction
            
            if key == 27:  # ESC key to exit
                break
            
            elif key == ord('s'):  # 's' key for selecting normal skin
                print("Attempting to select skin ROI.")
                skin_signature_vis3, skin_signature_rn2 = select_skin(None, vis3_cube, rn2_cube, aligned_vis3_display, warp_matrix, file_type="overlay")
                #skin_roi = get_roi_coordinates()
                if skin_signature_vis3 is not None and skin_signature_rn2 is not None and  skin_signature_vis3.size > 0 and skin_signature_rn2.size > 0:
                        #print("select_skin failed to collect valid data.")
                        #continue
                    skin_signatures.append(skin_signature_vis3)
                    skin_signatures.append(skin_signature_rn2)
                    #skin_rois.append(get_roi_coordinates())
                    roi_data = get_roi_coordinates()
                    if roi_data:
                        #(x1, y1), (x2, y2), _, _ = roi_data
                    #skin_rois.append(((x1, y1), (x2, y2)))
                        (top_left, bottom_right, roi_width, roi_height) = roi_data
                        x1, y1 = top_left
                        x2, y2 = bottom_right
                    # Append directly to skin_rois without reconstructing
                    skin_rois.append(roi_data)
                    cv2.rectangle(image_display, (x1, y1), (x2, y2), (255, 0, 0), -1)
                    print(f"Skin signatures collected: VIS3: {skin_signature_vis3}, RN2: {skin_signature_rn2}")
                else:
                    print("Failed to collect skin signature or ROI for VIS3 or RN2.")
            elif key == ord('m'):  # 'Enter' key for mole selection
                print("Attempting to select mole ROI.")
                mole_signature_vis3, mole_signature_rn2, mole_count = select_mole(None, vis3_cube, rn2_cube, aligned_vis3_display, warp_matrix, mole_count=mole_count, file_type="overlay")
                #mole_rois.append(get_roi_coordinates())
                #mole_roi = get_roi_coordinates()
                if mole_signature_vis3 is not None and mole_signature_rn2 is not None and mole_signature_vis3.size > 0 and mole_signature_rn2.size > 0:
                    #print("select_mole failed to collect valid data.")
                    #continue
                    mole_signatures.append(mole_signature_vis3)
                    mole_signatures.append(mole_signature_rn2)
                    #mole_rois.append(get_roi_coordinates())
                    roi_data = get_roi_coordinates()
                    if roi_data:
                        #(x1, y1), (x2, y2), _, _ = roi_data
                    #mole_rois.append(((x1, y1), (x2, y2)))
                        (top_left, bottom_right, roi_width, roi_height) = roi_data
                        x1, y1 = top_left
                        x2, y2 = bottom_right
                    # Append directly to skin_rois without reconstructing
                    mole_rois.append(roi_data)
                    cv2.rectangle(image_display, (x1, y1), (x2, y2), (255, 0, 0), -1) 
                    #mole_count += 1
                    print(f"Mole {mole_count}: VIS3: {mole_signature_vis3}, RN2: {mole_signature_rn2}")
                else:
                    print("Failed to collect mole signature or ROI for VIS3 or RN2.")
            # Close and exit on window property change or ESC key
            elif cv2.getWindowProperty("Zoomable Image", cv2.WND_PROP_VISIBLE) < 1:
                break

        cv2.destroyAllWindows()
        return skin_signatures, skin_rois, mole_signatures, mole_rois

    except Exception as e:
        print(f"Failed to process and register VIS3 and RN2 files: {e}")
        return None, None, None, None

def handle_upload_():
    # Step 1: Iterate over all participants in the data list
    for participant in my_data_list:
        participant_name = participant.get("name", "Unknown")
        spectral_data = participant.get("spectral_data", {})
        
        # Step 2: Iterate over all body parts in the spectral data for this participant
        for body_part, body_part_data in spectral_data.items():
            # Extract data for TIVITA
            tivita_data = body_part_data.get("tivita", {})
            tivita_skin_signature = []
            tivita_mole_signatures = []
            
            if "skin_signature" in tivita_data:
                tivita_skin_signature = [item["Data"] for item in tivita_data["skin_signature"]]
            
            for i in range(1, 4):  # Assuming you have mole_signature_1, mole_signature_2, etc.
                mole_signature_key = f"mole_signature_{i}"
                if mole_signature_key in tivita_data:
                    tivita_mole_signatures.append(tivita_data[mole_signature_key][0]["Data"])

            # Extract data for VIS3
            vis3_data = body_part_data.get("vis3", {})
            vis3_skin_signature = []
            vis3_mole_signatures = []
            
            if "skin_signature" in vis3_data:
                vis3_skin_signature = [item["Data"] for item in vis3_data["skin_signature"]]
            
            for i in range(1, 3):  # Assuming you have mole_signature_1, mole_signature_2, etc.
                mole_signature_key = f"mole_signature_{i}"
                if mole_signature_key in vis3_data:
                    vis3_mole_signatures.append(vis3_data[mole_signature_key][0]["Data"])

            # Extract data for RN2
            rn2_data = body_part_data.get("rn2", {})
            rn2_skin_signature = []
            rn2_mole_signatures = []
            
            if "skin_signature" in rn2_data:
                rn2_skin_signature = [item["Data"] for item in rn2_data["skin_signature"]]
            
            for i in range(1, 3):  # Assuming you have mole_signature_1, mole_signature_2, etc.
                mole_signature_key = f"mole_signature_{i}"
                if mole_signature_key in rn2_data:
                    rn2_mole_signatures.append(rn2_data[mole_signature_key][0]["Data"])

            # Step 3: Plot the extracted data for each participant and body part
            fig, (ax1, ax2, ax3) = plt.subplots(nrows=1, ncols=3, figsize=(15, 5))

            # Plot TIVITA data
            for mole_signature in tivita_mole_signatures:
                ax1.plot(mole_signature, label="TIVITA Mole Signature")
            if tivita_skin_signature:
                ax1.plot(tivita_skin_signature[0], label="TIVITA Skin Signature", linestyle="--")
            ax1.set_title(f'{participant_name} - {body_part} - TIVITA')
            ax1.set_xlabel('Spectral Band')
            ax1.set_ylabel('Mean Reflectance')
            ax1.legend()

            # Plot VIS3 data
            for mole_signature in vis3_mole_signatures:
                ax2.plot(mole_signature, label="VIS3 Mole Signature")
            if vis3_skin_signature:
                ax2.plot(vis3_skin_signature[0], label="VIS3 Skin Signature", linestyle="--")
            ax2.set_title(f'{participant_name} - {body_part} - VIS3')
            ax2.set_xlabel('Spectral Band')
            ax2.set_ylabel('Mean Reflectance')
            ax2.legend()

            # Plot RN2 data
            for mole_signature in rn2_mole_signatures:
                ax3.plot(mole_signature, label="RN2 Mole Signature")
            if rn2_skin_signature:
                ax3.plot(rn2_skin_signature[0], label="RN2 Skin Signature", linestyle="--")
            ax3.set_title(f'{participant_name} - {body_part} - RN2')
            ax3.set_xlabel('Spectral Band')
            ax3.set_ylabel('Mean Reflectance')
            ax3.legend()

            # Finalize plot layout and show
            fig.suptitle(f"Spectral Signatures for {participant_name} - {body_part}")
            plt.tight_layout(rect=[0, 0.05, 1, 0.95])
            plt.show()

# Function to get and print selected items from the Treeview
def get_selected_ids():
    selected_items = trv.selection()  # Get selected item IDs
    selected_ids = []
    spectral_names = set()  # To hold unique spectral names
    for item in selected_items:
        # Get the ID value of the selected item (first column)
        data = trv.item(item, 'values')
        selected_ids.append(data[0])  # Assuming the first column is the ID

        # Find corresponding spectral data
        for entry in my_data_list:
            if entry["id"] == data[0]:  # Match ID
                # Get the keys from spectral_data
                spectral_names.update(entry["spectral_data"].keys())

    # print("Selected IDs:", selected_ids)
    # print("Spectral Names:", spectral_names)

    # Open a child window to display radio buttons
    #open_radio_window(selected_ids, spectral_names)
    


# Function to open a child window with radio buttons
def open_radio_window_(selected_ids, spectral_names):
    radio_window = Toplevel(primary)
    radio_window.title("Select Spectral Data")

    # Variable to store the selected radio button value
    selected_option = StringVar(value=list(spectral_names)[0] if spectral_names else "No options")

    # Create and place radio buttons for each spectral name
    for name in spectral_names:
        rb = Radiobutton(radio_window, text=name, variable=selected_option, value=name)
        rb.pack(anchor="w")  # Pack the radio buttons vertically

    # Button to confirm selection and close the radio window
    #confirm_btn = Button(radio_window, text="Plot Comparison", command=lambda: plot_comparison(selected_option.get(), selected_ids))
    #confirm_btn.pack(pady=10)

   
    
    
def open_information_window():
    info_window = Toplevel(primary)
    info_window.title('Information')
    info_window.geometry('600x300')
    
    # Adding the information text for each function
    Label(info_window, text="Information", font=("Arial", 16)).pack(pady=10)
    
    Label(info_window, text="Set base directory: Choose the folder where all participants are saved.", font=("Arial", 10)).pack(pady=10)
    
    Label(info_window, text="View: Displays plot of TIVITA, VIS3, and RN2 spectral data for each body part.", font=("Arial", 10)).pack(pady=10)
    
    Label(info_window, text="Edit: Choose all body parts of a participant and select a ROI. Confirm a mole with 'm' and skin with 's'", font=("Arial", 10)).pack(pady=10)
    
    Label(info_window, text="Delete: Deletes the spectral data of a participant.", font=("Arial", 10)).pack(pady=10)
    


# Configure the main window grid layout
primary.grid_columnconfigure(0, weight=1)
primary.grid_columnconfigure(1, weight=1)
primary.grid_columnconfigure(2, weight=1)
primary.grid_columnconfigure(3, weight=0)
primary.grid_columnconfigure(4, weight=0)
primary.grid_columnconfigure(5, weight=1)
primary.grid_columnconfigure(6, weight=1)
primary.grid_columnconfigure(7, weight=1)

primary.grid_rowconfigure(0, weight=1)
primary.grid_rowconfigure(20, weight=1)


# Heading label to welcome the user
#welcome_label = Label(primary, text="Welcome to the Skin Anomalies Analysis GUI, SkinSpecScan", font=("Helvetica", 12), fg="blue")
#welcome_label.grid(row=0, column=3, columnspan=2, pady=10, sticky="nsew")

# Button to open the Information window
BtnOpeninfowindow = Button(primary, text="Information before you navigate",bg="#34d2eb", command=open_information_window)
BtnOpeninfowindow.grid(row=1, column=3, columnspan=2, pady=10, sticky="nsew")
# Button to choose a directory and then open the new participant window
BtnChooseDirectory = Button(primary, text="Set base directory", bg="#34d2eb", padx=2, pady=3, command=choose_directory)
BtnChooseDirectory.grid(row=2, column=3, columnspan=2, pady=10, sticky="nsew")

# Treeview widget
trv = ttk.Treeview(primary, columns=(1,2,3), show="headings", height="10", selectmode="extended")
trv.grid(row=3, column=3, rowspan=16, columnspan=2, pady=10, sticky="nsew")

trv.heading(1, text="NUMBER", anchor="w")
trv.heading(2, text="NAME", anchor="center")
trv.heading(3, text="ACTION", anchor="center")

trv.column('#1', anchor="w", width=100, stretch=False)
trv.column('#2', anchor="w", width=100, stretch=False)
trv.column('#3', anchor="w", width=110, stretch=False)
# Increased width for View/Edit/Delete

# Bind click events for the Treeview
trv.bind("<Button-1>", on_treeview_click)


# Button to trigger JSON file open and CSV save
btn_save_csv = Button(primary, text="Save Data as CSV", bg="#34d2eb",padx=2, pady=3, command=save_data_rois_as_csv)
btn_save_csv.grid(row=19, column=3, columnspan=2, pady=10, sticky="nsew")
#pdf_button = Button(primary, text="Open User Manual", bg="#34d2eb",padx=2, pady=3, command=open_pdf)
#pdf_button.grid(row=20, column=3, columnspan=2, pady=5, sticky="nsew")

# Adds a label inside the "Manager Participant" box as a note
##ote_label = tk.Label(primary, text="Note: 'Edit' means select body part.", font=("Arial", 9), fg="black")
##note_label.grid(row=2, column=1, padx=10, pady=(5, 0))
#note_label.grid(row=4, column=6, padx=20, pady=5, sticky="nw")


# Load existing data from JSON file when the application starts
load_data()

primary.mainloop()
