import os
import time
import threading
import subprocess
import numpy as np
import tkinter as tk
import tkinter.font as tkFont
import matplotlib.pyplot as plt
from tkinter import PhotoImage, ttk
from PIL import Image, ImageTk, ImageFilter

zombie_output = ""
rawhammer_output = ""

def main():
    def on_agree():
        if agree_var.get():
            continue_button.config(state=tk.NORMAL)
        else:
            continue_button.config(state=tk.DISABLED)

    def on_continue():
        # Clear previous UI
        for widget in app.winfo_children():
            widget.destroy()

        # Display attack list
        tk.Label(app, text="Select attacks to execute:", font=("Times", 14)).pack(pady=10)

        attack_frame = tk.Frame(app, relief=tk.GROOVE, bd=3, bg="#f0f0f0")
        attack_frame.pack(pady=10, padx=20, fill="x")

        attacks = ["Spectre Analysis v1", "Spectre Analysis v2", "Meltdown Analysis", "Rawhammer Analysis", "ZombieLoad Analysis", "Prime+Probe Cache Side-Channel Analysis", "Spoiler Analysis"]
        attack_vars = {}

        for attack in attacks:
            var = tk.BooleanVar()
            chk = tk.Checkbutton(attack_frame, text=attack, variable=var, font=("Times", 12), bg="#f0f0f0")
            chk.pack(anchor="w", pady=2)
            attack_vars[attack] = var

        tk.Button(app, text="Execute Selected Attacks", font=("Times", 12), command=lambda: run_attacks(attacks, attack_vars)).pack(pady=20)

        def run_attacks(attacks, attack_vars):
            if not any(attack_vars[attack].get() for attack in attacks):
                return
            else:
                selected = [attack for attack in attacks if attack_vars[attack].get()]

                progress_window = tk.Toplevel(app)
                progress_window.title("Running Attacks")
                progress_window.geometry("400x100")
                progress_window.iconphoto(False, tk.PhotoImage(file="./imgs/hsatIcon.png"))
                tk.Label(progress_window, text="Executing attacks...").pack(pady=10)
                progress = ttk.Progressbar(progress_window, orient=tk.HORIZONTAL, length=300, mode='determinate')
                progress.pack(pady=10)
                progress['maximum'] = len(selected)
                progress['value'] = 0

            def execute():
                for attack in selected:
                    if attack == "Spectre Analysis v1":
                        spectre_attack_v1()
                    elif attack == "Spectre Analysis v2":
                        spectre_attack_v2()
                    elif attack == "Meltdown Analysis":
                        meltdown_attack()
                    elif attack == "Rawhammer Analysis":
                        rawhammer_attack()
                    elif attack == "ZombieLoad Analysis":
                        zombieload_attack()
                    elif attack == "Prime+Probe Cache Side-Channel Analysis":
                        cache_side_channel_attack()
                    elif attack == "Spoiler Analysis":
                        spoiler_attack()
                    progress['value'] += 1
                progress_window.destroy()
                show_results(selected)

            threading.Thread(target=execute).start()

        def show_results(selected_attacks):
            for widget in app.winfo_children():
                widget.destroy()

            result_frame = tk.Frame(app, bg="white")
            result_frame.pack(pady=20, padx=20, fill="both", expand=True)

            tk.Label(result_frame, text="Attack Results", font=("Times", 16, "bold"), bg="white").pack(pady=10)

            for attack in selected_attacks:
                frame = tk.Frame(result_frame, bg="white")
                frame.pack(fill="x", pady=5, padx=10)

                tk.Label(frame, text=(attack + ":"), font=("Times", 12, "bold"), bg="white").pack(side="left")
                is_vulnerable = check_vulnerability(attack)

                if not is_vulnerable:
                    tk.Label(frame, text="✔", font=("Times", 12), fg="green", bg="white").pack(side="right")
                else:
                    details_label = tk.Label(frame, text="✖", font=("Times", 12), fg="red", bg="white")
                    details_label.pack(side="right")

                    if attack == "Prime+Probe Cache Side-Channel Analysis" or attack == "Spoiler Analysis":
                        details_button = tk.Button(frame, text="▼", font=("Times", 12), fg="black", bg="white", command=lambda atk=attack: show_attack_output(atk))
                        details_button.pack(side="right")

        def show_attack_output(attack):
            output_window = tk.Toplevel(app)
            output_window.title(f"{attack} Output")
            output_window.geometry("500x400")

            try:
                if attack == "Prime+Probe Cache Side-Channel Analysis":
                    image_path = "../../CacheSC/attack_plot.png"
                elif attack == "Spoiler Analysis":
                    image_path = "../../SPOILER/t2.png"
                img = Image.open(image_path)
                img = img.resize((480, 380), Image.ANTIALIAS)
                photo = ImageTk.PhotoImage(img)

                image_label = tk.Label(output_window, image=photo)
                image_label.image = photo
                image_label.pack(expand=True, fill="both")
            except Exception as e:
                tk.Label(output_window, text="Failed to load image.", fg="red").pack(pady=20)

        def check_vulnerability(attack):
            if attack == "Spectre Analysis v1":
                with open("../../spectre-attack/spectre_out.txt") as f:
                    output = f.read()

                    if "Success" in output:
                        return True
                    else:
                        return False
            elif attack == "Spectre Analysis v2":
                with open("../../spectrev2-poc/spectrev2_out.txt") as f:
                    output = f.read()

                    if "Success" in output:
                        return True
                    else:
                        return False
            elif attack == "Meltdown Analysis":
                with open("../../Meltdown-Attack/meltdown_out.txt") as f:
                    output = f.read()

                    if "Memory access violation!" in output:
                        return True
                    else:
                        return False
            elif attack == "Rawhammer Analysis":
                if "error" in rawhammer_output:
                    return True
                else:
                    return False
            elif attack == "ZombieLoad Analysis":
                if zombie_output[-2][5] != "0":
                    return True
                else:
                    return False
            elif attack == "Prime+Probe Cache Side-Channel Analysis":
                with open("../../CacheSC/demo/attack.log") as f:
                    output = f.read().split("\n")

                    for i in range (0, len(output)):
                        if "#### Sample number" in output[i]:
                            check = output[i+1].split(" ")
                            for j in range(0, len(check)):
                                if check[j] != '' and int(check[j]) >= 100:
                                    return True
                    return False
            elif attack == "Spoiler Analysis":
                with open("../../SPOILER/t2.txt") as f:
                    output = f.read().split("\n")

                    for i in range(1, len(output)):
                        if int(output[i]) >= int(output[i - 1]) + 600:
                            return True
                return False

    # Create main application window
    app = tk.Tk()
    app.title("Hardware Static Analysis Tool")

    window_width, window_height = 800, 800
    screen_width = app.winfo_screenwidth()
    screen_height = app.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    app.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # Set the application icon
    try:
        app.iconphoto(False, tk.PhotoImage(file="./imgs/hsatIcon.png"))
    except Exception as e:
        print(f"Error setting icon: {e}")

    # Load background image
    try:
        bg_image = Image.open("./imgs/hsat.png")
        bg_image = bg_image.resize((window_width, window_height))
        bg_photo = ImageTk.PhotoImage(bg_image)
    except Exception as e:
        print(f"Error loading background: {e}")
        return

    bg_label = tk.Label(app, image=bg_photo)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    names = tk.Label(app, text="Christos Karagiannis, Emmanouil-Angelos Tsigkas", font=("Times", 24, "bold"), bg="white").pack(pady=300)
    # "Let's Begin" button
    begin_button = tk.Button(app, text="Let's Begin", font=("Times", 14), bg="green", fg="white",
                              command=lambda: show_terms(app, bg_label))
    begin_button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    bg_label.image = bg_photo

    def show_terms(parent, bg):
        # Blur background
        bg.config(image=None)
        bg_blur = bg_image.filter(ImageFilter.BLUR)
        bg_blur_photo = ImageTk.PhotoImage(bg_blur)
        bg.config(image=bg_blur_photo)
        bg.image = bg_blur_photo

        # Terms and agreement UI
        terms_frame = tk.Frame(parent, bg="white", relief=tk.RAISED, bd=2)
        terms_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        tk.Label(terms_frame, text="Terms of Agreement", font=("Times", 14, "bold"), bg="white").pack(pady=10)
        terms_text = "By proceeding, you agree to execute the selected tests responsibly and ensure " \
                     "they align with ethical standards."
        tk.Label(terms_frame, text=terms_text, font=("Times", 12), bg="white", wraplength=400).pack(pady=10)

        global agree_var
        agree_var = tk.BooleanVar()
        agree_check = tk.Checkbutton(terms_frame, text="I agree with the above Terms", font=("Times", 12),
                                     variable=agree_var, command=on_agree, bg="white")
        agree_check.pack(pady=10)

        global continue_button
        continue_button = tk.Button(terms_frame, text="Continue", font=("Times", 12), state=tk.DISABLED, command=on_continue)
        continue_button.pack(pady=10)

    app.mainloop()

def spectre_attack_v1():
    os.system("cd ../../spectre-attack && make")
    st = time.time()
    os.system("cd ../../spectre-attack && ./spectre > spectre_out.txt")
    et = time.time() - st
    print(f"Spectre v1 time: {et}")

def spectre_attack_v2():
    os.system("cd ../../spectrev2-poc && make")
    st = time.time()
    os.system("cd ../../spectrev2-poc && ./spectrev2 > spectrev2_out.txt")
    et = time.time() - st
    print(f"Spectre v2 time: {et}")

def meltdown_attack():
    os.system("cd ../../Meltdown-Attack && make")
    st = time.time()
    os.system("cd ../../Meltdown-Attack && ./MeltdownAttack1 > meltdown_out.txt")
    et = time.time() - st
    print(f"Meltdown time: {et}")

def rawhammer_attack():
    global rawhammer_output
    os.system("cd ../../rowhammer-test && ./make.sh")
    try:
        st = time.time()
        p = subprocess.Popen(["../../rowhammer-test/rowhammer_test"], stdout=subprocess.PIPE, text=True)

        time.sleep(490)

        rawhammer_output = p.stdout.read().split("\n")
    except subprocess.TimeoutExpired:
        p.kill()
        print("rowhammer_test exceeded time limit and was terminated.")

    et = time.time() - st
    print(f"rowhammer time: {et}")

def zombieload_attack():
    global zombie_output
    os.system("cd ../../ZombieLoad/attacker/variant1_linux && make")
    os.system("cd ../../ZombieLoad/victim/userspace_linux_windows && make")

    try:
        st = time.time()
        attacker_process = subprocess.Popen(
            ["taskset", "-c", "3", "../../ZombieLoad/attacker/variant1_linux/leak"], stdout=subprocess.PIPE, text=True)
        victim_process = subprocess.Popen(
            ["taskset", "-c", "7", "../../ZombieLoad/victim/userspace_linux_windows/secret"])

        # Let the processes run for 20 seconds
        time.sleep(20)

        # Terminate both processes
        attacker_process.terminate()
        victim_process.terminate()

        # Wait for processes to terminate
        attacker_process.wait(timeout=5)
        victim_process.wait(timeout=5)

        zombie_output = attacker_process.stdout.read().split("\n")
    except subprocess.TimeoutExpired:
        attacker_process.kill()
        victim_process.kill()
        print("Processes were terminated due to timeout.")

    et = time.time() - st
    print(f"rowhammer time: {et}")

def cache_side_channel_attack():
    os.system("cd ../../CacheSC/ && make")
    os.system("cd ../../CacheSC/demo && make single-eviction")
    st = time.time()
    os.system("cd ../../CacheSC/demo && ./single-eviction 10000 > attack.log")
    et = time.time() - st
    print(f"single-eviction time: {et}")
    os.system("cd ../../CacheSC/ && ./scripts/plot-log.py -o ./ -v -t ./demo/attack.log")

def spoiler_attack():
    os.system("cd ../../SPOILER && make")
    st = time.time()
    os.system("cd ../../SPOILER && ./spoiler")
    et = time.time() - st
    print(f"spoiler time: {et}")

    # Load the single-column data
    data = np.loadtxt('../../SPOILER/t2.txt')

    # Plot using the array index for the x-axis
    plt.plot(data, linestyle='-')

    # (Optional) Label axes and give a title
    plt.xlabel('Page Number')
    plt.ylabel('Time (ns)')
    plt.title('SPOILER Attack')
    plt.savefig('../../SPOILER/t2.png')

    plt.close()

if __name__ == "__main__":
    main()
