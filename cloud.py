import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector


def init_db():
  try:
    conn = mysql.connector.connect(
        host="localhost", user="root", password="Sonali@2826"
    )
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS cloud_tracker")
    cursor.execute("USE cloud_tracker")

    # Using a brand new table name 'user_track_progress' to avoid old cache conflicts
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_track_progress (
                username VARCHAR(255),
                cloud_track VARCHAR(100),
                task_name VARCHAR(255),
                is_completed INT,
                PRIMARY KEY (username, cloud_track, task_name)
            )
        """)

    cursor.execute("""
            CREATE TABLE IF NOT EXISTS track_info (
                cloud_track VARCHAR(100) PRIMARY KEY,
                description TEXT,
                key_services TEXT
            )
        """)

    cursor.execute("SELECT COUNT(*) FROM track_info")
    if cursor.fetchone()[0] == 0:
      sample_data = [
          (
              "AWS",
              (
                  "Amazon Web Services Cloud Practitioner & Solutions Architect"
                  " Track"
              ),
              "EC2, S3, RDS, IAM, Lambda, VPC",
          ),
          (
              "Azure",
              "Microsoft Azure Fundamentals & Administrator Track",
              "Virtual Machines, Blob Storage, Azure SQL, Active Directory",
          ),
          (
              "GCP",
              "Google Cloud Digital Leader & Associate Engineer Track",
              "Compute Engine, Cloud Storage, BigQuery, IAM",
          ),
      ]
      cursor.executemany(
          "INSERT INTO track_info (cloud_track, description, key_services)"
          " VALUES (%s, %s, %s)",
          sample_data,
      )

    conn.commit()
    cursor.close()
    conn.close()
  except mysql.connector.Error as err:
    messagebox.showerror("Database Error", f"Connection failed: {err}")


class CloudTrackerApp(tk.Tk):

  def __init__(self):
    super().__init__()
    self.title("CloudCert Tracker Project")
    self.geometry("520x580")
    self.resizable(False, False)

    self.current_user = tk.StringVar()
    self.selected_track = tk.StringVar()

    container = tk.Frame(self)
    container.pack(side="top", fill="both", expand=True)
    container.grid_rowconfigure(0, weight=1)
    container.grid_columnconfigure(0, weight=1)

    self.frames = {}
    for F in (LoginPage, DashboardPage, CompletionPage):
      frame = F(container, self)
      self.frames[F] = frame
      frame.grid(row=0, column=0, sticky="nsew")

    self.show_frame(LoginPage)

  def show_frame(self, cont):
    frame = self.frames[cont]
    if cont == DashboardPage:
      frame.load_dashboard_data()
    frame.tkraise()


# --- PAGE 1: Login Page ---
class LoginPage(tk.Frame):

  def __init__(self, parent, controller):
    super().__init__(parent, bg="#f4f6f9")
    self.controller = controller

    tk.Label(
        self,
        text="CloudCert Portal",
        font=("Arial", 20, "bold"),
        bg="#f4f6f9",
        fg="#1f2937",
    ).pack(pady=40)

    form_frame = tk.Frame(self, bg="#ffffff", padx=20, pady=20)
    form_frame.pack(pady=10, padx=40, fill="x")

    tk.Label(
        form_frame,
        text="Username:",
        font=("Arial", 11),
        bg="#ffffff",
        anchor="w",
    ).pack(fill="x", pady=5)
    self.username_entry = tk.Entry(form_frame, font=("Arial", 11))
    self.username_entry.pack(fill="x", pady=5)

    tk.Label(
        form_frame,
        text="Select Cloud Track:",
        font=("Arial", 11),
        bg="#ffffff",
        anchor="w",
    ).pack(fill="x", pady=5)
    self.track_combobox = ttk.Combobox(
        form_frame, values=["AWS", "Azure", "GCP"], state="readonly", font=("Arial", 11)
    )
    self.track_combobox.pack(fill="x", pady=5)
    self.track_combobox.set("AWS")

    tk.Button(
        self,
        text="Login & View Info",
        command=self.handle_login,
        font=("Arial", 11, "bold"),
        bg="#2563eb",
        fg="white",
        pady=8,
    ).pack(pady=30, fill="x", padx=40)

  def handle_login(self):
    username = self.username_entry.get().strip()
    track = self.track_combobox.get()

    if not username:
      messagebox.showerror("Error", "Please enter a username.")
      return

    try:
      init_db()
      self.controller.current_user.set(username)
      self.controller.selected_track.set(track)
      self.controller.show_frame(DashboardPage)
    except mysql.connector.Error as err:
      messagebox.showerror("Database Error", f"{err}")


# --- PAGE 2: Dashboard with Track-Specific Progress ---
class DashboardPage(tk.Frame):

  def __init__(self, parent, controller):
    super().__init__(parent, bg="#f4f6f9")
    self.controller = controller

    self.title_label = tk.Label(
        self, text="", font=("Arial", 18, "bold"), bg="#f4f6f9", fg="#1f2937"
    )
    self.title_label.pack(pady=10)

    self.info_card = tk.Frame(self, bg="#ffffff", padx=20, pady=15)
    self.info_card.pack(pady=5, padx=30, fill="both", expand=True)

    self.desc_label = tk.Label(
        self.info_card,
        text="",
        font=("Arial", 10),
        bg="#ffffff",
        wraplength=400,
        justify="left",
    )
    self.desc_label.pack(anchor="w", pady=5)

    tk.Label(
        self.info_card,
        text="Check off topics as you learn them:",
        font=("Arial", 10, "bold"),
        bg="#ffffff",
        fg="#1f2937",
    ).pack(anchor="w", pady=(10, 5))

    self.task_vars = []
    self.task_names = [
        "1. Understand Core Compute Services",
        "2. Learn Cloud Storage Basics",
        "3. Master Security & IAM Roles",
        "4. Review Networking & Practice Lab",
    ]

    self.checkboxes = []
    for name in self.task_names:
      var = tk.IntVar()
      cb = tk.Checkbutton(
          self.info_card,
          text=name,
          variable=var,
          command=self.update_progress,
          font=("Arial", 9),
          bg="#ffffff",
          anchor="w",
      )
      cb.pack(anchor="w", fill="x", pady=2)
      self.task_vars.append(var)
      self.checkboxes.append(cb)

    tk.Label(
        self.info_card,
        text="Overall Track Progress:",
        font=("Arial", 10, "bold"),
        bg="#ffffff",
        fg="#4b5563",
    ).pack(anchor="w", pady=(15, 2))

    self.progress_bar = ttk.Progressbar(
        self.info_card, orient="horizontal", length=400, mode="determinate"
    )
    self.progress_bar.pack(anchor="w", pady=5)

    self.progress_text = tk.Label(
        self.info_card,
        text="0% Completed",
        font=("Arial", 9, "bold"),
        bg="#ffffff",
        fg="#2563eb",
    )
    self.progress_text.pack(anchor="w", pady=(0, 5))

    btn_frame = tk.Frame(self, bg="#f4f6f9")
    btn_frame.pack(pady=10, fill="x", padx=30)

    tk.Button(
        btn_frame,
        text="← Back",
        command=lambda: controller.show_frame(LoginPage),
        font=("Arial", 10),
        padx=10,
        pady=5,
    ).pack(side="left")
    tk.Button(
        btn_frame,
        text="Go to Completion Page →",
        command=lambda: controller.show_frame(CompletionPage),
        font=("Arial", 10, "bold"),
        bg="#10b981",
        fg="white",
        padx=10,
        pady=5,
    ).pack(side="right")

  def load_dashboard_data(self):
    user = self.controller.current_user.get()
    track = self.controller.selected_track.get()
    self.title_label.config(text=f"Welcome, {user} ({track} Track)!")

    try:
      conn = mysql.connector.connect(
          host="localhost",
          user="root",
          password="Sonali@2826",
          database="cloud_tracker",
      )
      cursor = conn.cursor()
      cursor.execute(
          "SELECT description FROM track_info WHERE cloud_track = %s", (track,)
      )
      result = cursor.fetchone()
      if result:
        self.desc_label.config(text=f"Track Focus: {result[0]}")

      # Load saved checkbox states filtered by user AND track from new table
      cursor.execute(
          "SELECT task_name, is_completed FROM user_track_progress WHERE"
          " username = %s AND cloud_track = %s",
          (user, track),
      )
      saved_tasks = {row[0]: row[1] for row in cursor.fetchall()}
      cursor.close()
      conn.close()

      for i, name in enumerate(self.task_names):
        val = saved_tasks.get(name, 0)
        self.task_vars[i].set(val)

      self.calculate_bar()
    except mysql.connector.Error as err:
      print(err)

  def update_progress(self):
    self.calculate_bar()
    user = self.controller.current_user.get()
    track = self.controller.selected_track.get()

    try:
      conn = mysql.connector.connect(
          host="localhost",
          user="root",
          password="Sonali@2826",
          database="cloud_tracker",
      )
      cursor = conn.cursor()

      for name, var in zip(self.task_names, self.task_vars):
        cursor.execute(
            """
                    INSERT INTO user_track_progress (username, cloud_track, task_name, is_completed) 
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE is_completed = %s
                """,
            (user, track, name, var.get(), var.get()),
        )

      conn.commit()
      cursor.close()
      conn.close()
    except mysql.connector.Error as err:
      print(err)

  def calculate_bar(self):
    completed_count = sum(var.get() for var in self.task_vars)
    total_tasks = len(self.task_names)
    percentage = int((completed_count / total_tasks) * 100)

    self.progress_bar["value"] = percentage
    self.progress_text.config(text=f"{percentage}% Completed")


# --- PAGE 3: End / Completion Page ---
class CompletionPage(tk.Frame):

  def __init__(self, parent, controller):
    super().__init__(parent, bg="#f4f6f9")
    self.controller = controller

    tk.Label(
        self,
        text="🎉 Milestone Reached!",
        font=("Arial", 20, "bold"),
        bg="#f4f6f9",
        fg="#059669",
    ).pack(pady=40)

    card = tk.Frame(self, bg="#ffffff", padx=20, pady=30)
    card.pack(pady=10, padx=40, fill="x")

    tk.Label(
        card,
        text=(
            "Your track-specific progress is safely recorded in the database!"
        ),
        font=("Arial", 12),
        bg="#ffffff",
        wraplength=350,
        justify="center",
    ).pack(pady=10)

    tk.Button(
        self,
        text="Logout / Start Over",
        command=lambda: controller.show_frame(LoginPage),
        font=("Arial", 11, "bold"),
        bg="#dc2626",
        fg="white",
        pady=8,
    ).pack(pady=40, fill="x", padx=40)


if __name__ == "__main__":
  init_db()
  app = CloudTrackerApp()
  app.mainloop()

