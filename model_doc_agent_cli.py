#!/usr/bin/env python3

print("[DEBUG] Script starting...") # Early debug print

try:
    import os
    import subprocess
    import sys
    import re
    import time
    import json
    import threading
    from datetime import datetime
    print("[DEBUG] Imports successful.") # Debug print after imports
except Exception as e:
    print(f"[ERROR] Early import failed: {e}", file=sys.stderr)
    sys.exit(1)

# Configuration
VENV_DIR = "ModelDocumentation/model-doc-agent/venv"  # Path to virtual environment directory
DEFAULT_TEMPLATE_PATH = "templates/bmo_model_documentation_template.json"
KNOWN_NON_CODEBASE_DIRS = [
    "venv", "output", "src", "templates", ".git", "ModelDocumentation", 
    "__pycache__", ".DS_Store", "node_modules", "dist", "build"
]
CODEBASES_PARENT_DIR = "Data" # New configuration for parent directory of codebases

# Tracking variables
current_output_dir = None
monitored_files = {}
monitor_running = False
monitor_thread = None
show_file_summaries = True  # Set to True to display file summaries

def list_potential_codebases(base_path=CODEBASES_PARENT_DIR):
    """Scans the base_path for potential codebase directories."""
    potential_codebases = []
    
    # Ensure the CODEBASES_PARENT_DIR exists
    if not os.path.isdir(base_path):
        print(f"Error: The specified codebase parent directory '{base_path}' does not exist.", file=sys.stderr)
        return []

    for item in os.listdir(base_path):
        item_path = os.path.join(base_path, item)
        if os.path.isdir(item_path):
            # We are now looking inside CODEBASES_PARENT_DIR, so the KNOWN_NON_CODEBASE_DIRS 
            # check is less critical for items directly inside it, unless they are also named that way.
            # However, keeping it for general hygiene is fine.
            if item not in KNOWN_NON_CODEBASE_DIRS and not item.startswith("."):
                potential_codebases.append(item)
    return sorted(list(set(potential_codebases)))

def prompt_user_for_codebase_selection(codebases):
    """Prompt the user to select a codebase from the provided list."""
    print("\nAvailable codebases:")
    for idx, codebase in enumerate(codebases, 1):
        print(f"{idx}. {codebase}")
    
    selection = input("\nEnter the number of the codebase you want to document: ")
    try:
        selection_idx = int(selection) - 1
        if 0 <= selection_idx < len(codebases):
            return codebases[selection_idx]
        else:
            print("Invalid selection number. Please try again.")
            return None
    except ValueError:
        print("Please enter a valid number.")
        return None

def get_python_executable():
    """Returns the appropriate Python executable path for the environment."""
    # Check if we're in a virtual environment
    if os.path.isdir(VENV_DIR):
        # Construct path to the Python executable in the virtual environment
        if sys.platform == "win32":  # Windows
            return os.path.join(VENV_DIR, "Scripts", "python.exe")
        else:  # Unix-based (Linux/Mac)
            return os.path.join(VENV_DIR, "bin", "python")
    else:
        # Fallback to system Python
        return "python3"

def run_command(command, cwd=None, env=None):
    """Run a command and stream output in real-time."""
    global current_output_dir
    
    print(f"\nRunning: {' '.join(command)}")
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            cwd=cwd,
            env=env
        )
        
        # Stream output in real-time
        for line in iter(process.stdout.readline, ''):
            line = line.rstrip()
            print(line)
            
            # Look for output directory in the log using a more precise regex pattern
            output_dir_match = re.search(r"Output will be saved to:\s+(output/summarization_test_\d+_\d+)", line)
            if output_dir_match:
                current_output_dir = output_dir_match.group(1)
                print(f"\n[MONITOR] 📁 Located output directory: {current_output_dir}")
                print("[MONITOR] 🔍 Will display content as files are generated...\n")
                
                # Start monitoring the output directory in a separate thread
                start_monitoring_output()
            
            # Also try the simpler split method as a fallback
            elif "Output will be saved to:" in line:
                parts = line.split("Output will be saved to:")
                if len(parts) > 1:
                    path = parts[1].strip()
                    # Ensure we have a complete path
                    if path.startswith("output/summarization_test_") and "_" in path:
                        current_output_dir = path
                        print(f"\n[MONITOR] 📁 Located output directory (fallback): {current_output_dir}")
                        print("[MONITOR] 🔍 Will display content as files are generated...\n")
                        
                        # Start monitoring the output directory in a separate thread
                        start_monitoring_output()
        
        process.stdout.close()
        return_code = process.wait()
        
        if return_code != 0:
            print(f"Command failed with return code {return_code}")
            return False
        return True
    except Exception as e:
        print(f"Error executing command: {e}")
        return False

def read_file_content(file_path):
    """Read and return the content of a file."""
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

def display_file_content(file_path, file_name):
    """Display the content of a file with formatting."""
    content = read_file_content(file_path)
    file_type = os.path.splitext(file_path)[1].lower()
    
    # Get terminal width for the banner
    try:
        term_width = os.get_terminal_size().columns
    except:
        term_width = 80
        
    # Special formatting for draft section files
    is_draft = False
    if "draft_section_" in file_name or "draft_subsection_" in file_name:
        is_draft = True
        banner = f"{'=' * term_width}"
        print(f"\n{banner}")
        print(f"🔄 GENERATING DOCUMENTATION: {file_name}")
        if "draft_subsection_" in file_name:
            print(f"📑 SUBSECTION DRAFT")
        else:
            print(f"📋 SECTION DRAFT")
        print(f"{banner}\n")
    else:
        banner = f"{'=' * term_width}"
        print(f"\n{banner}")
        print(f"📄 FILE: {file_name}")
        print(f"{banner}\n")
    
    # Format JSON nicely if possible
    if file_type == ".json":
        try:
            content_obj = json.loads(content)
            content = json.dumps(content_obj, indent=2)
        except:
            # If JSON parsing fails, just use the raw content
            pass
    
    print(content)
    print(f"\n{banner}")
    print(f"[MONITOR] ⏱ {datetime.now().strftime('%H:%M:%S')} - Displayed: {file_name}\n")

def monitor_output_directory():
    """Monitor the output directory for new or changed files and display their content."""
    global monitor_running, monitored_files, current_output_dir, show_file_summaries
    
    print(f"\n[MONITOR] 🔍 Starting real-time monitoring of: {current_output_dir}")
    print(f"[MONITOR] 📊 Show file summaries: {show_file_summaries}")
    print(f"[MONITOR] 📑 Section drafts will be displayed as they are generated")
    
    # For debug purposes, print all variables
    print(f"[MONITOR] 🔧 Current directory exists: {os.path.exists(current_output_dir) if current_output_dir else False}")
    
    ignore_patterns = ["__pycache__", ".DS_Store", ".git"]
    check_interval = 1.0  # Check every second instead of 2 for more responsiveness
    
    # Add a small delay to let the directory be created
    time.sleep(0.5)
    
    while monitor_running and current_output_dir:
        try:
            # Only proceed if the directory exists
            if not os.path.exists(current_output_dir):
                print(f"[MONITOR] ⚠️ Waiting for directory to be created: {current_output_dir}")
                time.sleep(check_interval)
                continue
                
            # Walk through the directory structure
            for root, dirs, files in os.walk(current_output_dir):
                # Skip ignored directories
                dirs[:] = [d for d in dirs if not any(pattern in d for pattern in ignore_patterns)]
                
                for file in files:
                    if any(pattern in file for pattern in ignore_patterns):
                        continue
                        
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, current_output_dir)
                    
                    # Get file modification time
                    try:
                        mtime = os.path.getmtime(file_path)
                    except:
                        continue
                    
                    # If file is new or has been updated
                    if rel_path not in monitored_files or monitored_files[rel_path] < mtime:
                        # For files in 02_file_summaries, respect the show_file_summaries flag
                        is_summary_file = "02_file_summaries" in rel_path and rel_path != "02_file_summaries"
                        
                        # Special priority for draft section files - always display these
                        is_draft_file = "draft_section_" in rel_path or "draft_subsection_" in rel_path
                        
                        # Store the modification time regardless
                        monitored_files[rel_path] = mtime
                        
                        # Skip displaying content for summary files if flag is False
                        if is_summary_file and not show_file_summaries and not is_draft_file:
                            print(f"[MONITOR] 📝 Updated file summary: {rel_path}")
                            continue
                        
                        # For other files, display their content
                        display_file_content(file_path, rel_path)
            
            # Sleep to avoid high CPU usage
            time.sleep(check_interval)
            
        except Exception as e:
            print(f"[MONITOR] ❌ Error in monitoring thread: {e}")
            time.sleep(check_interval * 2)  # Wait a bit longer after an error
    
    print(f"\n[MONITOR] 🛑 Stopped monitoring {current_output_dir}")

def start_monitoring_output():
    """Start the monitoring thread."""
    global monitor_running, monitor_thread, current_output_dir
    
    if not current_output_dir:
        print("[MONITOR] ⚠️ No output directory set, cannot start monitoring")
        return
        
    # Stop any existing monitor
    stop_monitoring_output()
    
    # Start a new monitoring thread
    monitor_running = True
    monitor_thread = threading.Thread(target=monitor_output_directory)
    monitor_thread.daemon = True
    monitor_thread.start()
    print(f"[MONITOR] 🚀 Started monitoring thread for {current_output_dir}")

def stop_monitoring_output():
    """Stop the monitoring thread."""
    global monitor_running, monitor_thread
    
    if monitor_thread and monitor_thread.is_alive():
        print("[MONITOR] 🔄 Stopping previous monitoring thread...")
        monitor_running = False
        monitor_thread.join(timeout=5)
        print("[MONITOR] ✅ Previous monitoring thread stopped")

def main():
    global current_output_dir, show_file_summaries
    
    print("Welcome to the BMO Model Documentation Agent!")
    print("I can help you generate professional documentation for your codebases.")
    print("Let's get started!\n")

    # Get available codebases
    codebases = list_potential_codebases()
    if not codebases:
        print(f"Could not find any potential codebase directories in '{CODEBASES_PARENT_DIR}'.")
        print("Please ensure your codebase folders (e.g., MonteCarloPFE, test_codebase) are inside the 'Data' directory.")
        return 1
    
    # Let user select a codebase
    selected_codebase = None
    while not selected_codebase:
        selected_codebase = prompt_user_for_codebase_selection(codebases)
    
    print(f"\nProcessing codebase: {selected_codebase}")
    
    # Construct the full path to the selected codebase
    codebase_abs_path = os.path.abspath(os.path.join(CODEBASES_PARENT_DIR, selected_codebase)) 
    template_abs_path = os.path.abspath(DEFAULT_TEMPLATE_PATH)
    
    # Set up environment variables for subprocess
    env = os.environ.copy()
    
    # Get the appropriate Python executable
    python_executable = get_python_executable()
    print(f"Using Python executable: {python_executable}")
    
    # Ask if user wants to see file summaries 
    show_summaries = input("Do you want to see individual file summaries? (y/n, default=n): ").lower()
    show_file_summaries = show_summaries.startswith('y')
    print(f"Individual file summaries will be {'displayed' if show_file_summaries else 'hidden'}")
    
    try:
        # Step 1: Run test_end_to_end_summarization.py
        print("\n--- Step 1: Generating Code Summaries and Documentation Draft ---")
        summarization_success = run_command(
            [
                python_executable, "test_end_to_end_summarization.py",
                "--codebase-dir", codebase_abs_path,
                "--template-path", template_abs_path
            ],
            env=env
        )
        
        if not summarization_success:
            print("Failed to complete the documentation summarization process.")
            return 1
        
        # Step 2: Get the latest output directory if not already set by monitoring
        if not current_output_dir:
            print("\n--- Step 2: Locating Generated Documentation ---")
            output_dirs = [d for d in os.listdir("output") if d.startswith("summarization_test_")]
            if not output_dirs:
                print("Could not find any summarization output directories.")
                return 1
            
            latest_output_dir = max(output_dirs)
            latest_output_path = os.path.join("output", latest_output_dir)
            print(f"Found latest output directory: {latest_output_path}")
            
            # Set the current_output_dir for the monitor
            current_output_dir = latest_output_path
            
            # Start monitoring for the found directory
            start_monitoring_output()
        else:
            latest_output_path = current_output_dir
        
        # Step 3: Run generate_final_documentation.py
        print("\n--- Step 3: Generating Final Markdown Documentation ---")
        markdown_success = run_command(
            [
                python_executable, "generate_final_documentation.py",
                "--json-input-dir", latest_output_path,
                "--template-path", template_abs_path
            ],
            env=env
        )
        
        if not markdown_success:
            print("Failed to generate final Markdown documentation.")
            return 1
        
        # Step 4: Show completion message with output location
        final_doc_path = os.path.join(latest_output_path, "final_documentation.md")
        
        # Display the final documentation
        if os.path.exists(final_doc_path):
            display_file_content(final_doc_path, "final_documentation.md")
        
        print("\n--- Documentation Generation Complete! ---")
        print(f"Your documentation has been generated at: {final_doc_path}")
        
        # Open the documentation file for the user if possible
        try:
            if sys.platform == "darwin":  # macOS
                subprocess.run(["open", final_doc_path])
            elif sys.platform == "win32":  # Windows
                os.startfile(os.path.normpath(final_doc_path))
            elif sys.platform.startswith("linux"):  # Linux
                subprocess.run(["xdg-open", final_doc_path])
        except Exception as e:
            print(f"Note: Couldn't automatically open the documentation file: {e}")
            print("Please open it manually using your preferred editor.")
        
        return 0
    finally:
        # Ensure monitoring is stopped when the main function exits
        stop_monitoring_output()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Script execution was interrupted by user")
        stop_monitoring_output()
        sys.exit(0)
    except Exception as e:
        print(f"[ERROR] Unhandled exception in main execution block: {e}", file=sys.stderr)
        import traceback
        print(traceback.format_exc(), file=sys.stderr)
        
        # Ensure monitoring is stopped when the script exits with an error
        stop_monitoring_output()
        
        sys.exit(1)