import datetime
import customtkinter as ctk # The modern version of Tkinter
from tkinter import messagebox, simpledialog
import numpy as np
from sklearn.linear_model import LinearRegression

  # --- SETTINGS ---
ctk.set_appearance_mode("dark") # Options: "dark", "light", "system"
ctk.set_default_color_theme("blue") # Options: "blue", "green", "dark-blue"
IRREGULAR_THRESHOLD = 30
FILE_NAME = "history.csv"

class PeriodTrackerApp:
      def __init__(self, root):
          self.root = root
          self.root.title("AI Period Tracker Pro")
          self.root.geometry("450x600")

          self.user_id = None
          self.setup_user()
          self.create_widgets()

      def setup_user(self):
          # CustomTkinter doesn't have a built-in simpledialog, so we use the standard one
          # or we could build a custom login screen. Let's keep it simple for now.
          from tkinter import simpledialog
          self.user_id = simpledialog.askstring("User Login", "Please enter your User ID or Name:")
          if not self.user_id:
              self.root.destroy()

      def create_widgets(self):
          # Main container to keep everything centered
          self.main_frame = ctk.CTkFrame(self.root, corner_radius=20)
          self.main_frame.pack(pady=30, padx=30, fill="both", expand=True)

          # 1. Header
          self.header = ctk.CTkLabel(self.main_frame, text=f"Hello, {self.user_id}!",
                                     font=("Segoe UI", 24, "bold"))
          self.header.pack(pady=(30, 10))

          self.sub_header = ctk.CTkLabel(self.main_frame, text="Your AI Health Companion",
                                         font=("Segoe UI", 12), text_color="gray")
          self.sub_header.pack(pady=(0, 20))

          # 2. Input Section
          self.input_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
          self.input_frame.pack(pady=20, padx=20)

          self.date_entry = ctk.CTkEntry(self.input_frame, placeholder_text="YYYY-MM-DD",
                                         width=150, font=("Segoe UI", 14))
          self.date_entry.pack(side=ctk.LEFT, padx=10)

          self.add_btn = ctk.CTkButton(self.input_frame, text="Save Date",
                                       command=self.save_date, width=100,
                                       font=("Segoe UI", 14, "bold"), fg_color="#D81B60", hover_color="#AD1457")
          self.add_btn.pack(side=ctk.LEFT)

          # 3. Analysis Section
          self.predict_btn = ctk.CTkButton(self.main_frame, text="Predict Next Cycle 🤖",
                                           command=self.calculate_cycle, width=250, height=50,
                                           font=("Segoe UI", 16, "bold"), fg_color="#1E88E5")
          self.predict_btn.pack(pady=20)

          # 4. Result Card
          self.result_card = ctk.CTkFrame(self.main_frame, fg_color="#2B2B2B", corner_radius=15)
          self.result_card.pack(pady=20, padx=20, fill="x")

          self.result_label = ctk.CTkLabel(self.result_card, text="Predictions will appear here...",
                                           font=("Segoe UI", 14), text_color="gray", wraplength=300)
          self.result_label.pack(pady=20, padx=20)

          # 5. Bottom Actions
          self.bottom_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
          self.bottom_frame.pack(side=ctk.BOTTOM, pady=30)

          self.delete_btn = ctk.CTkButton(self.bottom_frame, text="Delete Entry",
                                         command=self.delete_date, width=120, fg_color="transparent",
                                         border_width=2, text_color="white", border_color="gray")
          self.delete_btn.pack(side=ctk.LEFT, padx=10)

          self.switch_btn = ctk.CTkButton(self.bottom_frame, text="Switch User",
                                         command=self.switch_user, width=120, fg_color="transparent",
                                         border_width=2, text_color="white", border_color="gray")
          self.switch_btn.pack(side=ctk.LEFT, padx=10)

      # --- LOGIC METHODS (Kept the same as before) ---

      def save_date(self):
          date_str = self.date_entry.get()
          try:
              datetime.datetime.strptime(date_str, "%Y-%m-%d")
              with open(FILE_NAME, "a") as file:
                  file.write(f"{self.user_id},{date_str}\n")
              messagebox.showinfo("Success", "Date saved successfully!")
              self.date_entry.delete(0, 'end')
          except ValueError:
              messagebox.showerror("Invalid Date", "Please use the format YYYY-MM-DD")

      def delete_date(self):
          from tkinter import simpledialog
          date_to_remove = simpledialog.askstring("Delete", "Enter date to remove (YYYY-MM-DD):")
          if not date_to_remove: return
          try:
              with open(FILE_NAME, "r") as file:
                  lines = file.readlines()
              new_lines = [line for line in lines if line.strip() != f"{self.user_id},{date_to_remove}"]
              if len(lines) == len(new_lines):
                  messagebox.showwarning("Not Found", "Date not found.")
                  return
              with open(FILE_NAME, "w") as file:
                  file.writelines(new_lines)
              messagebox.showinfo("Deleted", "Date removed.")
          except FileNotFoundError:
              messagebox.showerror("Error", "No history found.")

      def calculate_cycle(self):
          try:
              with open(FILE_NAME, "r") as file:
                  lines = file.readlines()
              user_dates_str = [line.strip().split(',')[1] for line in lines if line.strip().split(',')[0] == self.user_id]
              if len(user_dates_str) < 2:
                  self.result_label.configure(text="Need at least 2 dates for AI prediction!", text_color="#FF5252")
                  return
              dates = sorted([datetime.datetime.strptime(d, "%Y-%m-%d") for d in user_dates_str])
              X, Y = [], []
              for i in range(len(dates) - 1):
                  delta = (dates[i+1] - dates[i]).days
                  if delta <= IRREGULAR_THRESHOLD:
                      X.append([i])
                      Y.append(delta)
              if len(X) < 2:
                  avg = sum([(dates[i+1]-dates[i]).days for i in range(len(dates)-1)]) / (len(dates)-1)
                  pred_days = int(avg)
                  mode = "Simple Average"
              else:
                  model = LinearRegression().fit(X, Y)
                  pred_days = int(model.predict([[len(X)]])[0])
                  mode = "AI Trend"
              next_date = dates[-1] + datetime.timedelta(days=pred_days)
              res_text = f"Mode: {mode}\nPredicted Length: {pred_days} days\nNext Date: {next_date.strftime('%Y-%m-%d')}"
              self.result_label.configure(text=res_text, text_color="#4CAF50")
          except Exception as e:
              messagebox.showerror("Error", f"Calculation error: {e}")

      def switch_user(self):
          self.root.destroy()
          main()

def main():
      root = ctk.CTk() # Use CTk instead of Tk
      app = PeriodTrackerApp(root)
      root.mainloop()

if __name__ == "__main__":
      main()
