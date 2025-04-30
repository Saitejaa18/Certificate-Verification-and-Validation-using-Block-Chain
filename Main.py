from tkinter import messagebox
from tkinter import *
from tkinter import simpledialog
import tkinter
from tkinter import filedialog
from tkinter.filedialog import askopenfilename
from Block import *
from Blockchain import *
from hashlib import sha256
import os
from tkinter import ttk
from PIL import Image, ImageTk

main = Tk()
main.title("Blockchain Based Certificate Validation")
main.geometry("1300x1200")
main.configure(bg='#f0f0f0')

# Modern color scheme
COLORS = {
    'primary': '#2c3e50',
    'secondary': '#3498db',
    'success': '#2ecc71',
    'danger': '#e74c3c',
    'background': '#f0f0f0',
    'text': '#2c3e50'
}

global filename
global status_label

blockchain = Blockchain()
if os.path.exists('blockchain_contract.txt'):
    try:
        with open('blockchain_contract.txt', 'rb') as fileinput:
            blockchain = pickle.load(fileinput)
        fileinput.close()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load blockchain data: {str(e)}")

def clear_fields():
    tf1.delete(0, END)
    tf2.delete(0, END)
    tf3.delete(0, END)
    text.delete('1.0', END)
    update_status("Fields cleared", "info")

def update_status(message, type="info"):
    status_label.config(text=message)
    if type == "success":
        status_label.config(fg=COLORS['success'])
    elif type == "error":
        status_label.config(fg=COLORS['danger'])
    else:
        status_label.config(fg=COLORS['text'])

def saveCertificate():
    global filename
    text.delete('1.0', END)
    
    try:
        filename = askopenfilename(
            initialdir="certificate_templates",
            title="Select Certificate",
            filetypes=(("PDF files", "*.pdf"), ("All files", "*.*"))
        )
        
        if not filename:
            update_status("No file selected", "error")
            return
            
        with open(filename, "rb") as f:
            bytes = f.read()
        f.close()
        
        roll_no = tf1.get().strip()
        name = tf2.get().strip()
        contact = tf3.get().strip()
        
        if not all([roll_no, name, contact]):
            update_status("Please fill in all fields", "error")
            return
            
        if not contact.isdigit() or len(contact) < 10:
            update_status("Please enter a valid contact number", "error")
            return
            
        digital_signature = sha256(bytes).hexdigest()
        data = f"{roll_no}#{name}#{contact}#{digital_signature}"
        
        blockchain.add_new_transaction(data)
        hash = blockchain.mine()
        b = blockchain.chain[len(blockchain.chain)-1]
        
        text.insert(END, "Certificate Successfully Added to Blockchain\n\n")
        text.insert(END, f"Blockchain Previous Hash: {b.previous_hash}\n")
        text.insert(END, f"Block No: {b.index}\n")
        text.insert(END, f"Current Hash: {b.hash}\n")
        text.insert(END, f"Certificate Digital Signature: {digital_signature}\n\n")
        
        try:
            blockchain.save_object(blockchain, 'blockchain_contract.txt')
            update_status("Certificate saved successfully", "success")
        except Exception as e:
            update_status(f"Error saving blockchain: {str(e)}", "error")
            
    except Exception as e:
        update_status(f"Error: {str(e)}", "error")

def verifyCertificate():
    text.delete('1.0', END)
    
    try:
        filename = askopenfilename(
            initialdir="certificate_templates",
            title="Select Certificate to Verify",
            filetypes=(("PDF files", "*.pdf"), ("All files", "*.*"))
        )
        
        if not filename:
            update_status("No file selected", "error")
            return
            
        with open(filename, "rb") as f:
            bytes = f.read()
        f.close()
        
        digital_signature = sha256(bytes).hexdigest()
        flag = True
        
        # Get the current certificate's details
        current_roll_no = tf1.get().strip()
        current_name = tf2.get().strip()
        current_contact = tf3.get().strip()
        
        if not all([current_roll_no, current_name, current_contact]):
            update_status("Please enter certificate details to verify", "error")
            return
        
        for i in range(len(blockchain.chain)):
            if i > 0:
                b = blockchain.chain[i]
                data = b.transactions[0]
                arr = data.split("#")
                
                # Check if both the digital signature AND the details match
                if arr[3] == digital_signature and \
                   arr[0] == current_roll_no and \
                   arr[1] == current_name and \
                   arr[2] == current_contact:
                    text.insert(END, "Certificate Validation Successful!\n\n")
                    text.insert(END, "Details extracted from Blockchain:\n\n")
                    text.insert(END, f"Roll No: {arr[0]}\n")
                    text.insert(END, f"Student Name: {arr[1]}\n")
                    text.insert(END, f"Contact No: {arr[2]}\n")
                    text.insert(END, f"Digital Signature: {arr[3]}\n")
                    update_status("Certificate verified successfully", "success")
                    flag = False
                    break
                    
        if flag:
            text.insert(END, "Verification failed: Certificate details do not match or certificate has been modified")
            update_status("Verification failed", "error")
            
    except Exception as e:
        update_status(f"Error: {str(e)}", "error")

# Modern title
title_frame = Frame(main, bg=COLORS['primary'])
title_frame.pack(fill=X, padx=10, pady=10)

title = Label(title_frame, text='Blockchain Based Certificate Validation',
             bg=COLORS['primary'], fg='white', font=('Helvetica', 16, 'bold'))
title.pack(pady=10)

# Input frame
input_frame = Frame(main, bg=COLORS['background'])
input_frame.pack(padx=20, pady=20)

# Style configuration
style = ttk.Style()
style.configure('TButton', font=('Helvetica', 10))
style.configure('TLabel', font=('Helvetica', 10))

# Input fields
fields = [
    ('Roll No:', tf1 := Entry(input_frame, width=30, font=('Helvetica', 10))),
    ('Student Name:', tf2 := Entry(input_frame, width=30, font=('Helvetica', 10))),
    ('Contact No:', tf3 := Entry(input_frame, width=30, font=('Helvetica', 10)))
]

for i, (label_text, entry) in enumerate(fields):
    label = Label(input_frame, text=label_text, bg=COLORS['background'], 
                 fg=COLORS['text'], font=('Helvetica', 10))
    label.grid(row=i, column=0, padx=10, pady=5, sticky='w')
    entry.grid(row=i, column=1, padx=10, pady=5)

# Button frame
button_frame = Frame(main, bg=COLORS['background'])
button_frame.pack(pady=10)

saveButton = Button(button_frame, text="Save Certificate", 
                   command=saveCertificate, bg=COLORS['secondary'],
                   fg='white', font=('Helvetica', 10, 'bold'))
saveButton.pack(side=LEFT, padx=5)

verifyButton = Button(button_frame, text="Verify Certificate", 
                     command=verifyCertificate, bg=COLORS['success'],
                     fg='white', font=('Helvetica', 10, 'bold'))
verifyButton.pack(side=LEFT, padx=5)

clearButton = Button(button_frame, text="Clear Fields", 
                    command=clear_fields, bg=COLORS['danger'],
                    fg='white', font=('Helvetica', 10, 'bold'))
clearButton.pack(side=LEFT, padx=5)

# Status label
status_frame = Frame(main, bg=COLORS['background'])
status_frame.pack(pady=5)
status_label = Label(status_frame, text="Ready", bg=COLORS['background'],
                    fg=COLORS['text'], font=('Helvetica', 10))
status_label.pack()

# Text area with scrollbar
text_frame = Frame(main, bg=COLORS['background'])
text_frame.pack(padx=20, pady=10, fill=BOTH, expand=True)

text = Text(text_frame, height=15, width=120, font=('Helvetica', 10))
scroll = Scrollbar(text_frame, command=text.yview)
text.configure(yscrollcommand=scroll.set)

text.pack(side=LEFT, fill=BOTH, expand=True)
scroll.pack(side=RIGHT, fill=Y)

# Initialize status
update_status("System ready", "info")

main.mainloop()
