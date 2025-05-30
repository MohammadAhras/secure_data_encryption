def main():
    print("Hello from secure-data-encryption!")


if __name__ == "__main__":
    main()
import streamlit as st
import sqlite3
import hashlib
import os
from cryptography.fernet import Fernet

KEY_FILE = "Simple_Secure.key"

def load_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
    else:
        with open(KEY_FILE, "rb") as f:
            key = f.read()
    return key

cipher = Fernet(load_key())

def init_db():
    conn = sqlite3.connect("Simple_data.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS Vault (
            label TEXT PRIMARY KEY,
            encrypted_text TEXT,
            passkey TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

def hash_passkey(passkey):
    return hashlib.sha256(passkey.encode()).hexdigest()

def encrypt(text):
    return cipher.encrypt(text.encode()).decode()

def decrypt(encrypted_text):
    return cipher.decrypt(encrypted_text.encode()).decode()

st.title("SECURE DATA ENCRYPTION WEB")
menu = ["Store Secret", "Retrieve Secret"]
choice = st.sidebar.selectbox("Choose Option", menu)

if choice == "Store Secret":
    st.header("Store a New Secret")

    label = st.text_input("Label (Unique id): ")
    secret = st.text_area('Your Secret')
    passkey = st.text_input("Passkey (to Protect it):", type="password")

    if st.button("Encrypt and Save"):
        if label and secret and passkey:
            conn = sqlite3.connect("Simple_data.db")
            c = conn.cursor()

            encrypted = encrypt(secret)
            hashed_passkey = hash_passkey(passkey)

            try:
                c.execute("INSERT INTO Vault (label, encrypted_text, passkey) VALUES (?, ?, ?)",
                         (label, encrypted, hashed_passkey))  # Fixed: using hashed_passkey instead of plain passkey
                conn.commit()
                st.success("Secret Saved Successfully!")
            except sqlite3.IntegrityError:
                st.error("Label already exists!")
            finally:
                conn.close()
        else:
            st.warning("Please fill all fields")

elif choice == "Retrieve Secret":
    st.header("Retrieve your Secret")

    label = st.text_input("Enter Label:")
    passkey = st.text_input("Enter Passkey: ", type="password")

    if st.button("Decrypt"):
        conn = sqlite3.connect("Simple_data.db")  # Fixed typo in database name
        c = conn.cursor()
        c.execute("SELECT encrypted_text, passkey FROM Vault WHERE label=?", (label,))
        result = c.fetchone()
        conn.close()

        if result:
            encrypted_text, stored_hash = result
            if hash_passkey(passkey) == stored_hash:  # Compare hashes
                try:
                    decrypted = decrypt(encrypted_text)
                    st.success("Here is your Secret")
                    st.code(decrypted)
                except:
                    st.error("Decryption failed - possible data corruption")
            else:
                st.error("Incorrect Passkey")
        else:
            st.warning("No such label found")