import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List

"""
File-based storage system using JSON files.
Replaces MongoDB with simple file storage for user data.
"""

class FileStorage:
    """Simple file-based storage system for user data"""
    
    def __init__(self, data_dir: str = "data"):
        """Initialize file storage"""
        self.data_dir = data_dir
        self._ensure_dir_exists()
        self._load_all_data()
    
    def _ensure_dir_exists(self):
        """Ensure data directory exists"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def _load_all_data(self):
        """Load all user data from files"""
        self._users = {}
        self._tasks = {}
        self._habits = {}
        self._expenses = {}
        
        # Load users
        users_file = os.path.join(self.data_dir, "users.json")
        if os.path.exists(users_file):
            try:
                with open(users_file, 'r', encoding='utf-8') as f:
                    self._users = json.load(f)
            except Exception as e:
                print(f"Error loading users: {e}")
        
        # Load tasks
        tasks_file = os.path.join(self.data_dir, "tasks.json")
        if os.path.exists(tasks_file):
            try:
                with open(tasks_file, 'r', encoding='utf-8') as f:
                    self._tasks = json.load(f)
            except Exception as e:
                print(f"Error loading tasks: {e}")
        
        # Load habits
        habits_file = os.path.join(self.data_dir, "habits.json")
        if os.path.exists(habits_file):
            try:
                with open(habits_file, 'r', encoding='utf-8') as f:
                    self._habits = json.load(f)
            except Exception as e:
                print(f"Error loading habits: {e}")
        
        # Load expenses
        expenses_file = os.path.join(self.data_dir, "expenses.json")
        if os.path.exists(expenses_file):
            try:
                with open(expenses_file, 'r', encoding='utf-8') as f:
                    self._expenses = json.load(f)
            except Exception as e:
                print(f"Error loading expenses: {e}")
    
    def _save_all_data(self):
        """Save all data to files"""
        try:
            # Save users
            users_file = os.path.join(self.data_dir, "users.json")
            with open(users_file, 'w', encoding='utf-8') as f:
                json.dump(self._users, f, indent=2, ensure_ascii=False, default=str)
            
            # Save tasks
            tasks_file = os.path.join(self.data_dir, "tasks.json")
            with open(tasks_file, 'w', encoding='utf-8') as f:
                json.dump(self._tasks, f, indent=2, ensure_ascii=False, default=str)
            
            # Save habits
            habits_file = os.path.join(self.data_dir, "habits.json")
            with open(habits_file, 'w', encoding='utf-8') as f:
                json.dump(self._habits, f, indent=2, ensure_ascii=False, default=str)
            
            # Save expenses
            expenses_file = os.path.join(self.data_dir, "expenses.json")
            with open(expenses_file, 'w', encoding='utf-8') as f:
                json.dump(self._expenses, f, indent=2, ensure_ascii=False, default=str)
            
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False
    
    # User management
    def save_user(self, user_id: int, username: str, first_name: str, last_name: str = None, chat_id: int = None):
        """Save user information"""
        if user_id not in self._users:
            self._users[user_id] = {
                'user_id': user_id,
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'chat_id': chat_id,
                'created_at': str(datetime.now()),
                'last_interaction': str(datetime.now()),
                'xp': 0,
                'level': 1,
                'discipline_score': 0,
                'voice_on': False
            }
        else:
            self._users[user_id]['username'] = username
            self._users[user_id]['first_name'] = first_name
            self._users[user_id]['last_name'] = last_name
            self._users[user_id]['chat_id'] = chat_id
            self._users[user_id]['last_interaction'] = str(datetime.now())
        
        return self._save_all_data()
    
    def get_user(self, user_id: int):
        """Get user information"""
        return self._users.get(user_id, None)
    
    # Task management
    def add_task(self, user_id: int, text: str, date: str, time: str = None, completed: bool = False):
        """Add a new task"""
        if user_id not in self._tasks:
            self._tasks[user_id] = []
        
        task = {
            'text': text,
            'date': date,
            'time': time,
            'completed': completed,
            'created_at': str(datetime.now())
        }
        
        self._tasks[user_id].append(task)
        return self._save_all_data()
    
    def get_user_tasks(self, user_id: int):
        """Get all tasks for a user"""
        return self._tasks.get(user_id, [])
    
    def get_today_tasks(self, user_id: int, today_str: str):
        """Get tasks for today"""
        tasks = self.get_user_tasks(user_id)
        return [task for task in tasks if task['date'] == today_str]
    
    def mark_task_completed(self, user_id: int, task_index: int, completed: bool = True):
        """Mark a task as completed"""
        if user_id in self._tasks and 0 <= task_index < len(self._tasks[user_id]):
            self._tasks[user_id][task_index]['completed'] = completed
            return self._save_all_data()
        return False
    
    def delete_task(self, user_id: int, task_index: int):
        """Delete a task"""
        if user_id in self._tasks and 0 <= task_index < len(self._tasks[user_id]):
            del self._tasks[user_id][task_index]
            return self._save_all_data()
        return False
    
    def clear_all_tasks(self, user_id: int):
        """Clear all tasks for a user"""
        if user_id in self._tasks:
            self._tasks[user_id] = []
            return self._save_all_data()
        return False
    
    # Habit management
    def add_habit(self, user_id: int, name: str, description: str = None):
        """Add a new habit"""
        if user_id not in self._habits:
            self._habits[user_id] = []
        
        habit = {
            'name': name,
            'description': description,
            'created_at': str(datetime.now()),
            'streak': 0,
            'last_done': None
        }
        
        self._habits[user_id].append(habit)
        return self._save_all_data()
    
    def get_user_habits(self, user_id: int):
        """Get all habits for a user"""
        return self._habits.get(user_id, [])
    
    def mark_habit_done(self, user_id: int, habit_index: int, date_str: str):
        """Mark habit as done for a specific date"""
        if user_id in self._habits and 0 <= habit_index < len(self._habits[user_id]):
            habit = self._habits[user_id][habit_index]
            
            # Calculate streak
            if habit['last_done'] == date_str:
                return True  # Already marked as done
            
            # Calculate streak increase
            if habit['last_done']:
                last_date = datetime.strptime(habit['last_done'], '%Y-%m-%d')
                current_date = datetime.strptime(date_str, '%Y-%m-%d')
                if (current_date - last_date).days == 1:
                    habit['streak'] += 1
                else:
                    habit['streak'] = 1
            else:
                habit['streak'] = 1
            
            habit['last_done'] = date_str
            return self._save_all_data()
        
        return False
    
    # Expense management
    def add_expense(self, user_id: int, amount: float, category: str, description: str = None, date: str = None):
        """Add a new expense"""
        if user_id not in self._expenses:
            self._expenses[user_id] = []
        
        expense = {
            'amount': amount,
            'category': category,
            'description': description,
            'date': date or str(datetime.now().date()),
            'created_at': str(datetime.now())
        }
        
        self._expenses[user_id].append(expense)
        return self._save_all_data()
    
    def get_user_expenses(self, user_id: int):
        """Get all expenses for a user"""
        return self._expenses.get(user_id, [])
    
    def get_today_expenses(self, user_id: int, today_str: str):
        """Get today's expenses"""
        expenses = self.get_user_expenses(user_id)
        return [exp for exp in expenses if exp['date'] == today_str]
    
    def get_week_expenses(self, user_id: int, week_start: str, week_end: str):
        """Get expenses for a week"""
        expenses = self.get_user_expenses(user_id)
        return [exp for exp in expenses if week_start <= exp['date'] <= week_end]
    
    def get_month_expenses(self, user_id: int, month_str: str):
        """Get expenses for a specific month"""
        expenses = self.get_user_expenses(user_id)
        return [exp for exp in expenses if exp['date'].startswith(month_str)]
    
    # User stats
    def update_user_stats(self, user_id: int):
        """Update user statistics"""
        if user_id not in self._users:
            return False
        
        # Calculate task completion rate
        tasks = self.get_user_tasks(user_id)
        completed_tasks = sum(1 for task in tasks if task['completed'])
        task_completion_rate = (completed_tasks / len(tasks) * 100) if tasks else 0
        
        # Calculate habit streak
        habits = self.get_user_habits(user_id)
        current_streak = max((habit['streak'] for habit in habits), default=0)
        
        # Calculate total expenses
        expenses = self.get_user_expenses(user_id)
        total_expense = sum(exp['amount'] for exp in expenses)
        
        # Calculate discipline score
        discipline_score = int(task_completion_rate * 0.6 + current_streak * 0.4)
        
        # Update user info
        self._users[user_id]['discipline_score'] = discipline_score
        
        return self._save_all_data()
    
    def add_xp(self, user_id: int, xp_points: int):
        """Add XP points to user"""
        if user_id in self._users:
            self._users[user_id]['xp'] += xp_points
            
            # Calculate level (each level requires 100 XP)
            self._users[user_id]['level'] = 1 + (self._users[user_id]['xp'] // 100)
            
            return self._save_all_data()
        return False
    
    # Data export
    def export_user_data(self, user_id: int):
        """Export user data as JSON"""
        user_data = {
            'user': self.get_user(user_id),
            'tasks': self.get_user_tasks(user_id),
            'habits': self.get_user_habits(user_id),
            'expenses': self.get_user_expenses(user_id)
        }
        
        return json.dumps(user_data, ensure_ascii=False, indent=2, default=str)
    
    # Cleanup
    def cleanup_old_data(self, days: int = 30):
        """Cleanup data older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff_date.strftime('%Y-%m-%d')
        
        # Cleanup old tasks
        for user_id in self._tasks:
            self._tasks[user_id] = [
                task for task in self._tasks[user_id] 
                if task['date'] >= cutoff_str
            ]
        
        # Cleanup old expenses
        for user_id in self._expenses:
            self._expenses[user_id] = [
                exp for exp in self._expenses[user_id]
                if exp['date'] >= cutoff_str
            ]
        
        return self._save_all_data()
    
    # Helper methods
    def _today_str(self) -> str:
        """Get today's date as string"""
        return datetime.now().strftime('%Y-%m-%d')
    
    def _tomorrow_str(self) -> str:
        """Get tomorrow's date as string"""
        return (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    def get_task_by_text(self, user_id: int, text: str):
        """Find task by text (case-insensitive)"""
        tasks = self.get_user_tasks(user_id)
        for index, task in enumerate(tasks):
            if task['text'].lower() == text.lower():
                return index
        return None
    
    def get_habit_by_name(self, user_id: int, name: str):
        """Find habit by name (case-insensitive)"""
        habits = self.get_user_habits(user_id)
        for index, habit in enumerate(habits):
            if habit['name'].lower() == name.lower():
                return index
        return None

# Singleton instance
file_storage = None

def get_file_storage() -> FileStorage:
    """Get singleton instance of FileStorage"""
    global file_storage
    if file_storage is None:
        file_storage = FileStorage()
    return file_storage

# Initialize on module load
get_file_storage()
