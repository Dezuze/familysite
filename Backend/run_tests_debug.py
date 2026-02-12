import subprocess
import os

def run_tests():
    cmd = ["py", "manage.py", "test", "families.tests.FamiliesTests"]
    cwd = r"c:\Users\wesly\OneDrive\Documents\Coding\Project\Backend"
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        with open(os.path.join(cwd, "test_final_log.txt"), "w") as f:
            f.write("STDOUT:\n")
            f.write(result.stdout)
            f.write("\nSTDERR:\n")
            f.write(result.stderr)
            f.write(f"\nEXIT CODE: {result.returncode}")
        print("Test log written to test_final_log.txt")
    except Exception as e:
        print(f"Error running tests: {e}")

if __name__ == "__main__":
    run_tests()
