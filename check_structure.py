import os

# Print current working directory
print(f"Current working directory: {os.getcwd()}")

# List all files and directories in the current directory
print("\nFiles and directories in current directory:")
for item in os.listdir():
    print(f"- {item}")

# Check if app directory exists
if os.path.exists("app"):
    print("\napp directory exists")
    print("\nContents of app directory:")
    for item in os.listdir("app"):
        print(f"- {item}")
else:
    print("\napp directory does NOT exist") 