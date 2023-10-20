import sqlite3
import datetime
from tkinter import *
from tkinter import ttk
import random

from habit import Habit
from db_operations import initialize_db

initialize_db()

class HabitTracker:
    def __init__(self, master, user_id):
        self.master = master
        self.master.title("Habit Tracker")
        self.user_id = user_id

        self.rewards = [
            "Drink Butterbeer!",
            "Eat a Chocolate Frog!",
            "Receive a box of Bertie Bott's Every Flavor Beans!",
            "Get a pack of Exploding Snap cards!",
            "Earn a Galleon!",
            "Take a ride on a Firebolt!",
            "Visit Hagrid for some rock cakes!",
            "Enjoy a day at Diagon Alley!",
            "Get a free pass to the Quidditch World Cup!",
            "Receive a Howler with a special message!",
                ]

        # SQLite Connection
        self.conn = sqlite3.connect("habits.db")
        self.cursor = self.conn.cursor()

        # Tkinter GUI
        self.label = Label(self.master, text="Habit Name")
        self.label.grid(row=0, column=0)
        self.entry = Entry(self.master)
        self.entry.grid(row=0, column=1)

        self.label2 = Label(self.master, text="Frequency")
        self.label2.grid(row=1, column=0)
        self.freq_var = StringVar()
        self.dropdown = ttk.Combobox(self.master, textvariable=self.freq_var, state='readonly')
        self.dropdown['values'] = ('daily', 'weekly', 'monthly')
        self.dropdown.grid(row=1, column=1)

        self.add_button = Button(self.master, text="Add Habit", command=self.add_habit)
        self.add_button.grid(row=2, column=0)
        self.complete_button = Button(self.master, text="Complete Habit", command=self.complete_habit)
        self.complete_button.grid(row=2, column=1)
        self.remove_button = Button(self.master, text="Remove Habit", command=self.remove_habit)
        self.remove_button.grid(row=2, column=2)
        self.analytics_button = Button(self.master, text="Show Analytics", command=self.show_habit_analytics)
        self.analytics_button.grid(row=2, column=3)

        #Listbox to show habits
        self.listbox = Listbox(self.master)
        self.listbox.grid(row=3, column=0, columnspan=4)
        self.update_habit_list()  # Initially populate the Listbox

    def update_habit_list(self):
        self.listbox.delete(0, END)  # Clear the existing list
        self.cursor.execute("SELECT * FROM habits")
        rows = self.cursor.fetchall()
        for row in rows:
            self.listbox.insert(END, f"{row[0]}: {row[2]}")

    def add_habit(self):

        print("Inside add_habit()")  # Debugging line
        habit_name = self.entry.get()
        frequency = self.freq_var.get()
        if habit_name and frequency:
            habit = Habit(habit_name, frequency)
            self.cursor.execute(
                "INSERT INTO habits (user_id, name, frequency, created_date, current_streak, longest_streak) VALUES (?, ?, ?, ?, 0, 0)",
                (self.user_id, habit.name, habit.frequency, datetime.datetime.now())
            )
            self.conn.commit()
            print(f"Great job adding a new habit, {habit_name}!")

    def get_selected_habit_id(self):
        selected = self.listbox.curselection()
        if selected:
            habit_entry = self.listbox.get(selected[0])
            habit_id = int(habit_entry.split(":")[0])
            return habit_id
        return None  # Return None if no selection is made
    
    def complete_habit(self):
        print("Inside complete_habit()")  # Debugging line
        habit_id = self.get_selected_habit_id()
        if habit_id is not None:
            self.cursor.execute("SELECT * FROM habits WHERE id=?", (habit_id,))
            habit_data = self.cursor.fetchone()

            if habit_data:
                current_date = datetime.datetime.now()
                last_completed_date = datetime.datetime.strptime(habit_data[5], "%Y-%m-%d %H:%M:%S.%f") if habit_data[5] else None
                freq = habit_data[3]

                if last_completed_date:
                    diff = self.check_diff(last_completed_date, current_date, freq)

                    if diff > 1:
                        # Update last_completed_date and reset streak
                        self.cursor.execute("UPDATE habits SET last_completed_date=?, current_streak=1 WHERE id=?", (current_date, habit_id))
                    else:
                        # Update last_completed_date and increase streak
                        self.cursor.execute("UPDATE habits SET last_completed_date=?, current_streak=current_streak+1 WHERE id=?", (current_date, habit_id))

                    if habit_data[6] + 1 > habit_data[7]:  # If current streak is greater than longest streak
                        self.cursor.execute("UPDATE habits SET longest_streak=current_streak WHERE id=?", (habit_id,))
                else:
                    # First-time completion
                    self.cursor.execute("UPDATE habits SET last_completed_date=?, current_streak=1, longest_streak=1 WHERE id=?", (current_date, habit_id))

                self.conn.commit()
                print("Great job, keep it up! ✨")

                if random.random() < 0.5:
                    reward = random.choice(self.rewards)  # Choose a random reward
                    print(f"Surprise! You get a special reward: {reward}")

            else:
                print("Habit not found. 😢")

    def remove_habit(self):
        habit_id = self.get_selected_habit_id()  # Fetch ID from the Listbox selection
        if habit_id is not None:
            self.cursor.execute("DELETE FROM habits WHERE id=?", (habit_id,))
            self.conn.commit()
            print("Habit removed. You got this! 🌟")
            self.update_habit_list()  # Update the Listbox after changes

    def show_habit_analytics(self):
        habit_id = self.get_selected_habit_id()  # Fetch ID from the Listbox selection
        if habit_id is not None:
            self.cursor.execute("SELECT * FROM habits WHERE id=?", (habit_id,))
            habit_data = self.cursor.fetchone()
            if habit_data:
                print(f"Current Streak: {habit_data[6]}")
                print(f"Longest Streak: {habit_data[7]}")
            else:
                print("Habit not found. 😢")

    def check_diff(self, d1, d2, freq):
        diff = (d2 - d1).days
        if freq == 'daily':
            return diff
        elif freq == 'weekly':
            return diff // 7
        elif freq == 'monthly':
            return diff // 30       


user_id = 1
root = Tk()
app = HabitTracker(root, user_id)
root.mainloop()