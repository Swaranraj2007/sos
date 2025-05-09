import streamlit as st
import hashlib
import mysql.connector

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

st.set_page_config(page_title="Emergency Response App", page_icon="🚨")

# Database Connection
def create_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="emergency_response_app"
    )
    
# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None

if 'user_role' not in st.session_state:
    st.session_state['user_role'] = None

# Page Navigation
def go_to_dashboard(role):
    st.session_state["page"] = "Admin Dashboard" if role in ["master", "manager", "support"] else "User Dashboard"

if "page" not in st.session_state:
    st.session_state["page"] = "Home"

page = st.session_state["page"]
logged_in = False
user_role = None

# Home Page
if page == "Home":
    st.title("🚨 Emergency Response App")
    st.markdown("Welcome to the Emergency Assistance App. Please select an option to proceed.")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Admin Sign In"):
            st.session_state["page"] = "Admin Sign In"
            st.rerun()

    with col2:
        if st.button("User Sign In"):
            st.session_state["page"] = "User Sign In"
            st.rerun()

    with col3:
        if st.button("User Sign Up"):
            st.session_state["page"] = "Sign Up"
            st.rerun()

# Admin Sign In Page
elif page == "Admin Sign In":
    st.title("🔑 Admin Sign In")
    username = st.text_input("Admin Username")
    password = st.text_input("Password", type="password")

    if st.button("Sign In"):
        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT username, password_hash, role FROM admins WHERE username=%s AND password_hash=%s",
                       (username, hash_password(password)))
        admin_result = cursor.fetchone()
        conn.close()

        if admin_result:
            logged_in = True
            st.session_state['logged_in'] = True
            user_role = admin_result[2]
            st.session_state['user_role'] = user_role
            st.success(f"Signed in as {user_role.capitalize()} Admin!")
            go_to_dashboard(user_role)
            st.rerun()
        else:
            st.error("Invalid admin credentials.")
    
    if st.button("Forget Password"):
        st.session_state["page"] = "Forget Password"
        st.rerun()

# User Sign In Page
# User Sign In Page
elif page == "User Sign In":
    st.title("🔑 User Sign In")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Sign In"):
        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT user_id, username, password_hash FROM users WHERE username=%s AND password_hash=%s",
                       (username, hash_password(password)))
        user_result = cursor.fetchone()
        conn.close()

        if user_result:
            logged_in = True
            st.session_state['logged_in'] = True
            for user_id in range (len(user_result)):
                st.session_state['user_id'] = user_result[user_id]  # Store user ID in session state
            st.success("Signed in as User!")
            go_to_dashboard("user")
            st.rerun()
        else:
            st.error("Invalid user credentials.")


# Forget Password Page
elif page == "Forget Password":
    st.title("🔑 Reset Password")
    username = st.text_input("Username")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Update Password"):
        if new_password == confirm_password:
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET password_hash=%s WHERE username=%s",
                           (hash_password(new_password), username))
            cursor.execute("UPDATE admins SET password_hash=%s WHERE username=%s",
                           (hash_password(new_password), username))
            conn.commit()
            conn.close()
            st.success("Password updated successfully!")
            st.session_state["page"] = "Home"
            st.rerun()
        else:
            st.error("Passwords do not match.")

# Admin Dashboard
elif page == "Admin Dashboard":
    if 'logged_in' in st.session_state:
        user_role = st.session_state['user_role']
        st.title(f"📊 {user_role.capitalize()} Admin Dashboard")
        st.write(f"Welcome, {user_role} admin!")

        if user_role == "master":
            st.write("🔧 Full access to manage admins and users.")
        elif user_role == "manager":
            st.write("📋 Manage users and view reports.")
        elif user_role == "support":
            st.write("🆘 Monitor incidents and respond to SOS requests.")

        if st.button("Logout", key="logout_admin"):
            st.session_state["page"] = "Home"
            st.session_state["logged_in"] = False
            st.rerun()
    else:
        st.error("Access Denied. Please log in as an admin.")

# User Dashboard
# User Dashboard
elif page == "User Dashboard":
    if 'logged_in' in st.session_state:
        st.title("📱 User Dashboard")
        st.write("Welcome, User! Stay safe and secure with our assistance.")
        
        # Navigation to Emergency Contacts page
        if st.button("Manage Emergency Contacts"):
            st.session_state["page"] = "Emergency Contacts"
            st.rerun()

        if st.button("Logout", key="logout_user"):
            st.session_state["page"] = "Home"
            st.session_state["logged_in"] = False
            st.rerun()
    else:
        st.error("Access Denied. Please log in.")

    

# User Sign Up Page
elif page == "Sign Up":
    st.title("📝 User Sign Up")
    new_username = st.text_input("Username")
    new_email = st.text_input("Email").strip()
    new_password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    st.write(new_email)
    if st.button("Sign Up"):
        st.write([new_username, new_email, new_password, confirm_password])
        if not all([new_username, new_email, new_password, confirm_password]):
            st.error("Please fill out all fields.")
        elif new_password != confirm_password:
            st.error("Passwords do not match.")
        else:
            try:
                conn = create_connection()
                cursor = conn.cursor()

                # Check if username or email already exists
                cursor.execute("SELECT username FROM users WHERE username=%s OR email=%s", 
                               (new_username, new_email))
                result = cursor.fetchone()

                if result:
                    st.error("Username or email already exists. Please try a different one.")
                else:
                    # Insert new user into the database
                    cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                                   (new_username, new_email, hash_password(new_password)))
                    conn.commit()
                    st.success("User account created successfully!")
                    st.session_state["page"] = "Home"
                    st.rerun()

            except mysql.connector.Error as err:
                st.error(f"Database error: {err}")
            except Exception as e:
                st.error(f"An error occurred: {e}")
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()
# Update Contact Page
# Emergency Contacts Page
elif page == "Emergency Contacts":
    st.title("📇 Emergency Contacts")

    if 'logged_in' in st.session_state:
        # Fetch contacts from the database
        conn = create_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT contact_id, contact_name, contact_phone, relationship FROM emergency_contacts")
            contacts = cursor.fetchall()

            if contacts:
                for contact in contacts:
                    contact_id, contact_name, contact_phone, relationship = contact

                    # Display each contact in a card-like format
                    st.markdown(f"**Name:** {contact_name}")
                    st.markdown(f"**Phone:** {contact_phone}")
                    st.markdown(f"**Relationship:** {relationship}")

                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col1:
                        if st.button("✏️ Update", key=f"update_{contact_id}"):
                            st.session_state["page"] = "Update Contact"
                            st.session_state["contact_id"] = contact_id
                            st.rerun()

                    with col2:
                        if st.button("🗑️ Delete", key=f"delete_{contact_id}"):
                            try:
                                delete_conn = create_connection()
                                delete_cursor = delete_conn.cursor()
                                delete_cursor.execute("DELETE FROM emergency_contacts WHERE contact_id=%s", (contact_id,))
                                delete_conn.commit()
                                delete_conn.close()
                                st.success(f"✅ Contact '{contact_name}' deleted successfully!")
                                st.rerun()
                            except mysql.connector.Error as err:
                                st.error(f"❌ Database error: {err}")
                            finally:
                                delete_cursor.close()

                    with col3:
                        if st.button("🔙 Back to Dashboard", key=f"back_{contact_id}"):
                            go_to_dashboard(st.session_state['user_role'])
                            st.rerun()

                    st.markdown("---")

            else:
                st.warning("🚫 No emergency contacts found.")

            # Add new contact button
            if st.button("➕ Add New Contact"):
                st.session_state["page"] = "Add Contact"
                st.rerun()

        except mysql.connector.Error as err:
            st.error(f"❌ Database error: {err}")
        finally:
            cursor.close()
            conn.close()

    else:
        st.error("⚠️ Please log in to view emergency contacts.")

    st.title("✏️ Update Emergency Contact")
    
    if 'logged_in' in st.session_state:
        contact_id = st.session_state.get("contact_id")

        # Fetch existing contact details
        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT contact_name, contact_phone, relationship FROM emergency_contacts WHERE contact_id=%s", (contact_id,))
        contact = cursor.fetchone()

        if contact:
            contact_name = st.text_input("Contact Name", value=contact[0])
            contact_phone = st.text_input("Contact Phone", value=contact[1])
            relationship = st.text_input("Relationship", value=contact[2])

            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Update Contact"):
                    try:
                        cursor.execute(
                            "UPDATE emergency_contacts SET contact_name=%s, contact_phone=%s, relationship=%s WHERE contact_id=%s",
                            (contact_name, contact_phone, relationship, contact_id)
                        )
                        conn.commit()
                        st.success("✅ Contact updated successfully!")
                        st.session_state["page"] = "Emergency Contacts"
                        st.rerun()
                    except mysql.connector.Error as err:
                        st.error(f"❌ Database error: {err}")
                    finally:
                        cursor.close()
                        conn.close()
            with col2:
                if st.button("🔙 Back to Emergency Contacts"):
                    st.session_state["page"] = "Emergency Contacts"
                    st.rerun()
        else:
            st.error("❗ Contact not found.")
    else:
        st.error("⚠️ Please log in to update contacts.")
# elif page == "Add Contact":
#     st.title("Add Emergency Contact")
#     contact_name = st.text_input("Contact Name:")
#     contact_phone = st.text_input("Phone Number:")
#     relationship = st.text_input("Relationship:")

#     if st.button("Add Contact"):
#         if contact_name and contact_phone:
#             try:
#                 conn = create_connection()  # Fixed the function name
#                 cursor = conn.cursor()

#                 # Get the current user's ID (assuming it's stored in the session state after login)
#                 user_id = st.session_state.get("user_id", None)

#                 if user_id:
#                     query = ("INSERT INTO emergency_contacts (user_id, contact_name, contact_phone, relationship) "
#                              "VALUES (%s, %s, %s, %s)")
#                     cursor.execute(query, (user_id, contact_name, contact_phone, relationship))
#                     conn.commit()
#                     st.success("Contact added successfully!")
#                     st.session_state["page"] = "Emergency Contacts"  # Go back to the contacts page
#                     st.rerun()
#                 else:
#                     st.error("User ID not found. Please log in again.")
#             except Exception as e:
#                 st.error(f"Error: {e}")
#             finally:
#                 cursor.close()
#                 conn.close()
#         else:
#             st.warning("Please fill in all required fields.")

#     if st.button("Go Back"):
#         st.session_state["page"] = "Emergency Contacts"
#         st.rerun()

#         st.title("Add Emergency Contact")
#         contact_name = st.text_input("Contact Name:")
#         contact_phone = st.text_input("Phone Number:")
#         relationship = st.text_input("Relationship:")

#         if st.button("Add Contact"):
#             if contact_name and contact_phone:
#                 try:
#                     conn = get_db_connection()
#                     cursor = conn.cursor()
#                     query = ("INSERT INTO emergency_contacts (user_id, contact_name, contact_phone, relationship) "
#                             "VALUES (%s, %s, %s, %s)")
#                     cursor.execute(query, (user_id, contact_name, contact_phone, relationship))
#                     conn.commit()
#                     st.success("Contact added successfully!")
#                     st.experimental_rerun()  # Refresh page after adding contact
#                 except Exception as e:
#                     st.error(f"Error: {e}")
#                 finally:
#                     cursor.close()
#                     conn.close()
#             else:
#                 st.warning("Please fill in all required fields.")

#         if st.button("Go Back"):
#             st.experimental_rerun()
elif page == "Add Contact":
    st.title("Add Emergency Contact")
    contact_name = st.text_input("Contact Name:")
    contact_phone = st.text_input("Phone Number:")
    relationship = st.text_input("Relationship:")

    if st.button("Add Contact"):
        if contact_name or contact_phone:
            try:
                conn = create_connection()  # Or get_db_connection(), make sure the function is correctly defined
                cursor = conn.cursor()

                # Get the current user's ID (assuming it's stored in the session state after login)
                user_id = st.session_state.get("user_id", None)
                st.write(user_id)
                if user_id:
                    query = ("INSERT INTO emergency_contacts (user_id, contact_name, contact_phone, relationship) "
                             "VALUES (%s, %s, %s, %s)")
                    cursor.execute(query, (user_id, contact_name, contact_phone, relationship))
                    conn.commit()
                    st.success("Contact added successfully!")
                    st.session_state["page"] = "Emergency Contacts"  # Go back to the contacts page
                    st.rerun()
                else:
                    st.error("User ID not found. Please log in again.")
            except Exception as e:
                st.error(f"Error: {e}")
            finally:
                if 'cursor' in locals() and cursor is not None:
                    cursor.close()
                if 'conn' in locals() and conn is not None:
                    conn.close()
        else:
            st.warning("Please fill in all required fields.")

    if st.button("Go Back"):
        st.session_state["page"] = "Emergency Contacts"
        st.rerun()