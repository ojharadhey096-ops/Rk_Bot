from pymongo import MongoClient, errors
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import json
import re

# Load environment variables
load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.client = None
        self.db = None
        self.connections = {}
        self.initialize()
    
    def initialize(self):
        """Initialize MongoDB connection"""
        try:
            # Get MongoDB connection URI from environment variables
            mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
            db_name = os.getenv('MONGODB_DB', 'radhey_ai_db')
            
            self.client = MongoClient(mongo_uri)
            self.db = self.client[db_name]
            
            # Check connection
            self.client.admin.command('ping')
            
            # Initialize collections
            self._init_collections()
            
            print("Successfully connected to MongoDB")
        except errors.ConnectionFailure as e:
            print(f"Could not connect to MongoDB: {e}")
        except Exception as e:
            print(f"Database initialization error: {e}")
    
    def _init_collections(self):
        """Initialize database collections with indexes"""
        try:
            # User profile collection
            self.users: Collection = self.db['users']
            self.users.create_index('user_id', unique=True)
            self.users.create_index('username')
            
            # Tasks collection
            self.tasks: Collection = self.db['tasks']
            self.tasks.create_index('user_id')
            self.tasks.create_index('date')
            self.tasks.create_index('completed')
            
            # Habits collection
            self.habits: Collection = self.db['habits']
            self.habits.create_index('user_id')
            self.habits.create_index('active')
            
            # Habit tracking collection
            self.habit_tracking: Collection = self.db['habit_tracking']
            self.habit_tracking.create_index('user_id')
            self.habit_tracking.create_index('habit_id')
            self.habit_tracking.create_index('date')
            
            # Expenses collection
            self.expenses: Collection = self.db['expenses']
            self.expenses.create_index('user_id')
            self.expenses.create_index('date')
            self.expenses.create_index('category')
            
            # User stats collection
            self.user_stats: Collection = self.db['user_stats']
            self.user_stats.create_index('user_id', unique=True)
            
        except Exception as e:
            print(f"Collection initialization error: {e}")
    
    # User Management
    def save_user(self, user_id, username, first_name, last_name=None, chat_id=None):
        """Save or update user information"""
        try:
            user_data = {
                'user_id': user_id,
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'chat_id': chat_id,
                'last_interaction': datetime.now(),
                'created_at': datetime.now(),
                'xp': 0,
                'level': 1,
                'discipline_score': 0
            }
            
            self.users.update_one(
                {'user_id': user_id},
                {'$set': user_data, '$setOnInsert': {'created_at': datetime.now()}},
                upsert=True
            )
            
            # Initialize user stats if not exists
            self._init_user_stats(user_id)
            
            return True
        except Exception as e:
            print(f"Error saving user: {e}")
            return False
    
    def _init_user_stats(self, user_id):
        """Initialize user statistics document"""
        try:
            stats_data = {
                'user_id': user_id,
                'total_tasks': 0,
                'completed_tasks': 0,
                'total_expenses': 0,
                'current_habit_streak': 0,
                'longest_habit_streak': 0,
                'discipline_score': 0,
                'monthly_spending': {},
                'category_spending': {}
            }
            
            self.user_stats.update_one(
                {'user_id': user_id},
                {'$set': stats_data},
                upsert=True
            )
        except Exception as e:
            print(f"Error initializing user stats: {e}")
    
    # Task Management
    def add_task(self, user_id, task_text, date, time=None, completed=False):
        """Add a new task"""
        try:
            task_data = {
                'user_id': user_id,
                'text': task_text,
                'date': date,
                'time': time,
                'completed': completed,
                'created_at': datetime.now(),
                'reminder_sent': False
            }
            
            inserted = self.tasks.insert_one(task_data)
            return str(inserted.inserted_id)
        except Exception as e:
            print(f"Error adding task: {e}")
            return None
    
    def get_user_tasks(self, user_id, date=None):
        """Get tasks for user, optionally filtered by date"""
        try:
            query = {'user_id': user_id}
            if date:
                query['date'] = date
                
            tasks = self.tasks.find(query).sort('time', 1)
            return list(tasks)
        except Exception as e:
            print(f"Error getting tasks: {e}")
            return []
    
    def mark_task_completed(self, user_id, task_id, completed=True):
        """Mark a task as completed"""
        try:
            result = self.tasks.update_one(
                {'_id': ObjectId(task_id), 'user_id': user_id},
                {'$set': {'completed': completed, 'completed_at': datetime.now()}}
            )
            
            return result.modified_count > 0
        except Exception as e:
            print(f"Error marking task completed: {e}")
            return False
    
    def delete_task(self, user_id, task_id):
        """Delete a task"""
        try:
            result = self.tasks.delete_one({'_id': ObjectId(task_id), 'user_id': user_id})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting task: {e}")
            return False
    
    def get_today_tasks(self, user_id):
        """Get today's tasks for user"""
        today = datetime.now().strftime('%Y-%m-%d')
        return self.get_user_tasks(user_id, today)
    
    # Habit Management
    def add_habit(self, user_id, habit_name, description=None):
        """Add a new habit"""
        try:
            habit_data = {
                'user_id': user_id,
                'name': habit_name,
                'description': description,
                'active': True,
                'created_at': datetime.now(),
                'last_completed': None
            }
            
            inserted = self.habits.insert_one(habit_data)
            return str(inserted.inserted_id)
        except Exception as e:
            print(f"Error adding habit: {e}")
            return None
    
    def get_user_habits(self, user_id, active=True):
        """Get active habits for user"""
        try:
            habits = self.habits.find({'user_id': user_id, 'active': active})
            return list(habits)
        except Exception as e:
            print(f"Error getting habits: {e}")
            return []
    
    def mark_habit_completed(self, user_id, habit_id, date=None):
        """Mark a habit as completed for a specific date"""
        try:
            if not date:
                date = datetime.now().strftime('%Y-%m-%d')
                
            tracking_data = {
                'user_id': user_id,
                'habit_id': habit_id,
                'date': date,
                'completed': True,
                'created_at': datetime.now()
            }
            
            # Check if already completed
            existing = self.habit_tracking.find_one({
                'user_id': user_id,
                'habit_id': habit_id,
                'date': date
            })
            
            if existing:
                return False
                
            inserted = self.habit_tracking.insert_one(tracking_data)
            
            # Update habit's last completed date
            self.habits.update_one(
                {'_id': ObjectId(habit_id), 'user_id': user_id},
                {'$set': {'last_completed': date}}
            )
            
            return True
        except Exception as e:
            print(f"Error marking habit completed: {e}")
            return False
    
    def get_habit_streak(self, user_id, habit_id):
        """Calculate habit streak for a user"""
        try:
            # Get all completed dates for this habit
            tracking = list(self.habit_tracking.find({
                'user_id': user_id,
                'habit_id': habit_id,
                'completed': True
            }).sort('date', -1))
            
            if not tracking:
                return 0
                
            # Calculate streak
            streak = 0
            today = datetime.now()
            
            for entry in tracking:
                entry_date = datetime.strptime(entry['date'], '%Y-%m-%d')
                days_diff = (today - entry_date).days
                
                if days_diff == streak:
                    streak += 1
                else:
                    break
                    
            return streak
        except Exception as e:
            print(f"Error calculating habit streak: {e}")
            return 0
    
    # Expense Management
    def add_expense(self, user_id, amount, category, description=None, date=None):
        """Add a new expense"""
        try:
            if not date:
                date = datetime.now().strftime('%Y-%m-%d')
                
            expense_data = {
                'user_id': user_id,
                'amount': float(amount),
                'category': category,
                'description': description,
                'date': date,
                'created_at': datetime.now()
            }
            
            inserted = self.expenses.insert_one(expense_data)
            return str(inserted.inserted_id)
        except Exception as e:
            print(f"Error adding expense: {e}")
            return None
    
    def get_expenses_by_date_range(self, user_id, start_date, end_date):
        """Get expenses for a date range"""
        try:
            expenses = self.expenses.find({
                'user_id': user_id,
                'date': {'$gte': start_date, '$lte': end_date}
            }).sort('date', 1)
            
            return list(expenses)
        except Exception as e:
            print(f"Error getting expenses: {e}")
            return []
    
    def get_today_expenses(self, user_id):
        """Get today's expenses"""
        today = datetime.now().strftime('%Y-%m-%d')
        return self.get_expenses_by_date_range(user_id, today, today)
    
    def get_week_expenses(self, user_id):
        """Get last 7 days expenses"""
        today = datetime.now()
        week_ago = (today - timedelta(days=6)).strftime('%Y-%m-%d')
        today_str = today.strftime('%Y-%m-%d')
        
        return self.get_expenses_by_date_range(user_id, week_ago, today_str)
    
    def get_month_expenses(self, user_id):
        """Get current month expenses"""
        today = datetime.now()
        first_day = datetime(today.year, today.month, 1).strftime('%Y-%m-%d')
        last_day = datetime(today.year, today.month + 1, 1) - timedelta(days=1)
        last_day_str = last_day.strftime('%Y-%m-%d')
        
        return self.get_expenses_by_date_range(user_id, first_day, last_day_str)
    
    def get_category_expenses(self, user_id):
        """Get total expenses by category"""
        try:
            pipeline = [
                {'$match': {'user_id': user_id}},
                {
                    '$group': {
                        '_id': '$category',
                        'total': {'$sum': '$amount'},
                        'count': {'$sum': 1}
                    }
                }
            ]
            
            results = list(self.expenses.aggregate(pipeline))
            category_totals = {}
            
            for result in results:
                category_totals[result['_id']] = {
                    'total': result['total'],
                    'count': result['count']
                }
                
            return category_totals
        except Exception as e:
            print(f"Error getting category expenses: {e}")
            return {}
    
    # User Statistics
    def update_user_stats(self, user_id):
        """Update user statistics"""
        try:
            # Calculate task stats
            total_tasks = self.tasks.count_documents({'user_id': user_id})
            completed_tasks = self.tasks.count_documents({
                'user_id': user_id,
                'completed': True
            })
            
            # Calculate expense stats
            total_expenses = self.expenses.count_documents({'user_id': user_id})
            
            # Calculate habit stats
            habits = self.get_user_habits(user_id)
            if habits:
                current_streaks = []
                for habit in habits:
                    streak = self.get_habit_streak(user_id, str(habit['_id']))
                    current_streaks.append(streak)
                
                current_habit_streak = max(current_streaks) if current_streaks else 0
            else:
                current_habit_streak = 0
                
            # Calculate discipline score
            if total_tasks > 0:
                completion_rate = (completed_tasks / total_tasks) * 100
            else:
                completion_rate = 0
                
            discipline_score = int(completion_rate + current_habit_streak)
            
            # Update user profile
            self.users.update_one(
                {'user_id': user_id},
                {
                    '$set': {
                        'discipline_score': discipline_score
                    }
                }
            )
            
            # Update user stats
            self.user_stats.update_one(
                {'user_id': user_id},
                {
                    '$set': {
                        'total_tasks': total_tasks,
                        'completed_tasks': completed_tasks,
                        'total_expenses': total_expenses,
                        'current_habit_streak': current_habit_streak,
                        'discipline_score': discipline_score
                    }
                }
            )
            
            return True
        except Exception as e:
            print(f"Error updating user stats: {e}")
            return False
    
    # XP and Level System
    def add_xp(self, user_id, xp_amount):
        """Add XP to user"""
        try:
            user = self.users.find_one({'user_id': user_id})
            if not user:
                return False
                
            current_xp = user.get('xp', 0)
            current_level = user.get('level', 1)
            
            new_xp = current_xp + xp_amount
            
            # Calculate level (each level requires 100 XP)
            new_level = 1 + (new_xp // 100)
            
            self.users.update_one(
                {'user_id': user_id},
                {
                    '$set': {
                        'xp': new_xp,
                        'level': new_level
                    }
                }
            )
            
            return True
        except Exception as e:
            print(f"Error adding XP: {e}")
            return False
    
    # Cleanup Methods
    def cleanup_old_data(self, days=30):
        """Clean up old data older than specified days"""
        try:
            from datetime import timedelta
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            # Cleanup old tasks
            self.tasks.delete_many({'date': {'$lt': cutoff_date}})
            
            # Cleanup old habits tracking
            self.habit_tracking.delete_many({'date': {'$lt': cutoff_date}})
            
            # Cleanup old expenses
            self.expenses.delete_many({'date': {'$lt': cutoff_date}})
            
            print(f"Cleaned up data older than {days} days")
            return True
        except Exception as e:
            print(f"Cleanup error: {e}")
            return False
    
    def close_connection(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            print("MongoDB connection closed")


# Singleton instance
db_manager = None

def get_db_manager():
    """Get or create database manager instance"""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
    return db_manager
