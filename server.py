import tkinter as tk
from tkinter import messagebox
from autobot_backend_packages import road_small, road_big, air_single, air_multiple

#calculates delivery time based on distance
def calculate_time(distance):
    #assuming avg speed as 5 km/h
    time_in_hours=distance / 5000
    time_in_minutes=time_in_hours * 60
    return round(time_in_minutes, 2)

#handle delivery type and trigger relevant function
def handle_delivery():
    delivery_type=delivery_type_var.get()
    start_coords=[float(start_lat_var.get()), float(start_lon_var.get())]
    end_coords=[float(end_lat_var.get()), float(end_lon_var.get())]

    distance=0  #initialize distance to 0 for error handling

    #check the delivery type and call the function needed
    if delivery_type=="Road single":
        distance = road_small(start_coords, end_coords)
    elif delivery_type=="Road multiple":
        end_coords_multiple=[list(map(float, coords.split(','))) for coords in end_coords_multiple_var.get().split(';')]
        distance = road_big(start_coords, end_coords_multiple)
    elif delivery_type=="Air Single":
        distance = air_single(start_coords, end_coords)
    elif delivery_type=="Air Multiple":
        end_coords_multiple=[list(map(float, coords.split(','))) for coords in end_coords_multiple_var.get().split(';')]
        distance=air_multiple(start_coords, end_coords_multiple)
    else:
        messagebox.showerror("Invalid Delivery Type", "Please select a valid delivery type.")
        return

    if distance==0:
        messagebox.showerror("Error", "There was an issue calculating the route.")
        return

    #time for delivery
    delivery_time=calculate_time(distance)

    #shows time and open the map
    messagebox.showinfo("Estimated Delivery Time", f"The estimated delivery time is {delivery_time} minutes.")


root = tk.Tk()
root.title("Delivery Service")
root.attributes("-fullscreen", True)
def toggle_full_screen(event=None):
    current_state=root.attributes("-fullscreen")
    root.attributes("-fullscreen", not current_state)
    return "break"

root.bind("<Escape>", toggle_full_screen)

frame=tk.Frame(root)
frame.pack(expand=True)

# Delivery type options
delivery_type_var=tk.StringVar()
delivery_type_var.set("Road single")

delivery_type_label=tk.Label(frame, text="Choose Delivery Type:", font=("Helvetica", 16))
delivery_type_label.grid(row=0, column=0, pady=10)

delivery_type_menu=tk.OptionMenu(frame, delivery_type_var, "Road single", "Road multiple", "Air Single", "Air Multiple")
delivery_type_menu.config(font=("Helvetica", 14), width=20)
delivery_type_menu.grid(row=0, column=1, pady=10)

# Start coordinates input
start_lat_var=tk.StringVar()
start_lon_var=tk.StringVar()

start_coords_label=tk.Label(frame, text="Start Coordinates (lat, lon):", font=("Helvetica", 16))
start_coords_label.grid(row=1, column=0, pady=10)

start_lat_entry=tk.Entry(frame, textvariable=start_lat_var, font=("Helvetica", 14), width=20)
start_lat_entry.grid(row=1, column=1, pady=10)

start_lon_entry=tk.Entry(frame, textvariable=start_lon_var, font=("Helvetica", 14), width=20)
start_lon_entry.grid(row=1, column=2, pady=10)

# End coordinates input
end_lat_var=tk.StringVar()
end_lon_var=tk.StringVar()

end_coords_label=tk.Label(frame, text="End Coordinates (lat, lon):", font=("Helvetica", 16))
end_coords_label.grid(row=2, column=0, pady=10)

end_lat_entry=tk.Entry(frame, textvariable=end_lat_var, font=("Helvetica", 14), width=20)
end_lat_entry.grid(row=2, column=1, pady=10)

end_lon_entry=tk.Entry(frame, textvariable=end_lon_var, font=("Helvetica", 14), width=20)
end_lon_entry.grid(row=2, column=2, pady=10)

# For multiple end coordinates:for "Big Route" and "Air Route (Multiple)"
end_coords_multiple_var=tk.StringVar()

end_coords_multiple_label=tk.Label(frame, text="End Coordinates (Multiple, separated by ';' e.g. lat,lon;lat,lon):", font=("Helvetica", 16))
end_coords_multiple_label.grid(row=3, column=0, pady=10)

end_coords_multiple_entry=tk.Entry(frame, textvariable=end_coords_multiple_var, font=("Helvetica", 14), width=40)
end_coords_multiple_entry.grid(row=3, column=1, columnspan=2, pady=10)

#button to start delivery
start_button=tk.Button(frame, text="Start Delivery", command=handle_delivery, font=("Helvetica", 16), width=20)
start_button.grid(row=4, column=0, columnspan=3, pady=20)

#exit button to quit the application
exit_button=tk.Button(frame, text="Exit", command=root.quit, font=("Helvetica", 16), width=20)
exit_button.grid(row=5, column=0, columnspan=3, pady=20)

root.mainloop()
