#!/bin/bash

# RADHEY AI LIFE OS - Startup Script
# This script simplifies running and managing the bot

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"
REQUIREMENTS="$PROJECT_DIR/requirements.txt"
MAIN_SCRIPT="$PROJECT_DIR/bot/main.py"
ENV_FILE="$PROJECT_DIR/.env"
ENV_EXAMPLE="$PROJECT_DIR/.env.example"

# Function to print messages
print_message() {
    local color="$1"
    local message="$2"
    echo -e "${color}${message}${NC}"
}

# Function to check command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python_version() {
    local python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    if (( $(awk -v num="$python_version" 'BEGIN{print(num < 3.8 ? 1 : 0)}') )); then
        print_message "$RED" "Error: Python 3.8 or higher is required. Current version: $python_version"
        exit 1
    fi
    print_message "$GREEN" "✅ Python version: $python_version"
}

# Function to set up virtual environment
setup_venv() {
    print_message "$YELLOW" "Setting up virtual environment..."
    
    if [ ! -d "$VENV_DIR" ]; then
        python3 -m venv "$VENV_DIR"
        print_message "$GREEN" "✅ Virtual environment created"
    else
        print_message "$YELLOW" "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
}

# Function to install/update dependencies
install_dependencies() {
    print_message "$YELLOW" "Installing dependencies..."
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    pip install -r "$REQUIREMENTS"
    
    print_message "$GREEN" "✅ Dependencies installed"
}

# Function to check environment variables
check_environment() {
    print_message "$YELLOW" "Checking environment configuration..."
    
    if [ ! -f "$ENV_FILE" ]; then
        print_message "$RED" "Error: .env file not found"
        
        if [ -f "$ENV_EXAMPLE" ]; then
            print_message "$YELLOW" "Creating .env file from .env.example..."
            cp "$ENV_EXAMPLE" "$ENV_FILE"
            print_message "$YELLOW" "Please edit .env file with your configuration"
        else
            print_message "$RED" "Error: .env.example file not found"
            exit 1
        fi
    else
        print_message "$GREEN" "✅ Environment file found"
        
        # Check required variables
        local missing_vars=()
        
        # Required variables
        while IFS= read -r line; do
            if [[ $line =~ ^[A-Z_]+= ]]; then
                local key=$(echo "$line" | cut -d'=' -f1)
                local value=$(grep -E "^${key}=" "$ENV_FILE" | cut -d'=' -f2)
                
                if [ -z "$value" ] || [ "$value" == "your-*" ] || [ "$value" == "localhost" ] || [ "$value" == "True" ]; then
                    if [ "$key" != "DEBUG" ] && [ "$key" != "PORT" ]; then
                        missing_vars+=("$key")
                    fi
                fi
            fi
        done < "$ENV_EXAMPLE"
        
        if [ ${#missing_vars[@]} -gt 0 ]; then
            print_message "$RED" "Error: Missing environment variables:"
            for var in "${missing_vars[@]}"; do
                echo "  - $var"
            done
            print_message "$YELLOW" "Please update .env file"
            exit 1
        fi
    fi
}

# Function to check Tesseract installation
check_tesseract() {
    print_message "$YELLOW" "Checking Tesseract installation..."
    
    if command_exists tesseract; then
        local tesseract_version=$(tesseract --version | head -n1)
        print_message "$GREEN" "✅ Tesseract: $tesseract_version"
        
        # Check if Hindi language pack is installed
        if tesseract --list-langs 2>/dev/null | grep -q 'hin'; then
            print_message "$GREEN" "✅ Hindi language pack installed"
        else
            print_message "$RED" "Error: Hindi language pack not found"
            print_message "$YELLOW" "Please install tesseract-ocr-hin package"
            exit 1
        fi
    else
        print_message "$RED" "Error: Tesseract OCR not found"
        print_message "$YELLOW" "Please install Tesseract OCR"
        exit 1
    fi
}

# Function to check MongoDB connection
check_mongodb() {
    print_message "$YELLOW" "Checking MongoDB connection..."
    
    local mongodb_uri=$(grep -E "^MONGODB_URI=" "$ENV_FILE" | cut -d'=' -f2)
    
    if command_exists mongo; then
        if mongo "$mongodb_uri" --eval "db.adminCommand('ping')" 2>&1 | grep -q 'ok'; then
            print_message "$GREEN" "✅ MongoDB connection successful"
        else
            print_message "$RED" "Error: MongoDB connection failed"
            exit 1
        fi
    else
        print_message "$YELLOW" "MongoDB client not found, skipping connection check"
        print_message "$YELLOW" "Bot will attempt connection during startup"
    fi
}

# Function to start the bot in development mode
start_development() {
    print_message "$YELLOW" "Starting bot in development mode..."
    
    source "$VENV_DIR/bin/activate"
    
    # Start bot
    python3 "$MAIN_SCRIPT"
}

# Function to start the bot in background mode
start_background() {
    print_message "$YELLOW" "Starting bot in background mode..."
    
    source "$VENV_DIR/bin/activate"
    
    # Create log directory if it doesn't exist
    LOG_DIR="$PROJECT_DIR/logs"
    mkdir -p "$LOG_DIR"
    
    # Start bot with nohup
    nohup python3 "$MAIN_SCRIPT" > "$LOG_DIR/bot.log" 2>&1 &
    PID=$!
    
    # Save PID
    echo $PID > "$PROJECT_DIR/bot.pid"
    
    print_message "$GREEN" "✅ Bot started with PID: $PID"
    print_message "$YELLOW" "Logs: tail -f $LOG_DIR/bot.log"
}

# Function to stop the bot
stop_bot() {
    print_message "$YELLOW" "Stopping bot..."
    
    if [ -f "$PROJECT_DIR/bot.pid" ]; then
        PID=$(cat "$PROJECT_DIR/bot.pid")
        
        if kill -0 $PID 2>/dev/null; then
            kill $PID
            rm "$PROJECT_DIR/bot.pid"
            print_message "$GREEN" "✅ Bot stopped"
        else
            print_message "$YELLOW" "Bot not running"
            rm "$PROJECT_DIR/bot.pid"
        fi
    else
        print_message "$YELLOW" "Bot PID file not found"
        
        # Try to find PID by process name
        PID=$(pgrep -f "python.*bot/main.py" 2>/dev/null)
        
        if [ -n "$PID" ]; then
            kill $PID
            print_message "$GREEN" "✅ Bot stopped with PID: $PID"
        else
            print_message "$YELLOW" "Bot not running"
        fi
    fi
}

# Function to check bot status
check_status() {
    if [ -f "$PROJECT_DIR/bot.pid" ]; then
        PID=$(cat "$PROJECT_DIR/bot.pid")
        
        if kill -0 $PID 2>/dev/null; then
            print_message "$GREEN" "Bot is running with PID: $PID"
        else
            print_message "$RED" "PID file exists but process not running"
            rm "$PROJECT_DIR/bot.pid"
        fi
    else
        # Check if bot is running without PID file
        PID=$(pgrep -f "python.*bot/main.py" 2>/dev/null)
        
        if [ -n "$PID" ]; then
            print_message "$GREEN" "Bot is running with PID: $PID"
        else
            print_message "$RED" "Bot is not running"
        fi
    fi
}

# Function to view logs
view_logs() {
    LOG_DIR="$PROJECT_DIR/logs"
    
    if [ -f "$LOG_DIR/bot.log" ]; then
        tail -f "$LOG_DIR/bot.log"
    else
        print_message "$RED" "Log file not found: $LOG_DIR/bot.log"
    fi
}

# Function to clean up old logs and temporary files
cleanup() {
    print_message "$YELLOW" "Cleaning up..."
    
    LOG_DIR="$PROJECT_DIR/logs"
    
    # Clean up old log files (keep last 3 days)
    if [ -d "$LOG_DIR" ]; then
        find "$LOG_DIR" -name "*.log" -type f -mtime +3 -delete
    fi
    
    # Clean up temporary files
    rm -f "$PROJECT_DIR/tmp/*.png" 2>/dev/null || true
    rm -f "$PROJECT_DIR/tmp/*.pdf" 2>/dev/null || true
    
    print_message "$GREEN" "✅ Cleanup complete"
}

# Function to run tests
run_tests() {
    print_message "$YELLOW" "Running tests..."
    
    source "$VENV_DIR/bin/activate"
    
    if [ -f "$PROJECT_DIR/test_ocr_engine.py" ]; then
        python3 "$PROJECT_DIR/test_ocr_engine.py"
    else
        print_message "$YELLOW" "No test files found"
    fi
}

# Main function to display help
display_help() {
    echo "RADHEY AI LIFE OS - Telegram Bot"
    echo "================================="
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  install        Install dependencies and configure"
    echo "  run            Start bot in development mode"
    echo "  start          Start bot in background"
    echo "  stop           Stop bot"
    echo "  status         Check bot status"
    echo "  logs           View bot logs"
    echo "  cleanup        Clean up temporary files"
    echo "  test           Run tests"
    echo "  help           Display this help"
    echo ""
    echo "Example:"
    echo "  $0 install     # Install everything"
    echo "  $0 run         # Run in development mode"
    echo "  $0 start       # Start in background"
    echo "  $0 logs        # View real-time logs"
}

# Main script execution
case "${1:-help}" in
    install)
        check_python_version
        setup_venv
        install_dependencies
        check_environment
        check_tesseract
        check_mongodb
        print_message "$GREEN" "✅ Installation complete!"
        print_message "$YELLOW" "Please edit .env file with your configuration"
        ;;
    run)
        source "$VENV_DIR/bin/activate"
        start_development
        ;;
    start)
        check_environment
        start_background
        ;;
    stop)
        stop_bot
        ;;
    status)
        check_status
        ;;
    logs)
        view_logs
        ;;
    cleanup)
        cleanup
        ;;
    test)
        run_tests
        ;;
    help|--help|-h)
        display_help
        ;;
    *)
        echo "Error: Invalid command"
        display_help
        exit 1
        ;;
esac
