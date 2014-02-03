import subprocess

def main():
    args = ["python", "changes.py", "http://localhost:5984", "prufa"]
    changes = subprocess.Popen(args,
                   stdout=subprocess.PIPE,
                   )
    for response in iter(changes.stdout.readline, ''):
        print(response)

if __name__ == "__main__":
    main()
