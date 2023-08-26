import argparse
import subprocess

def addUserToSudoGroup(username):
    try:
        subprocess.run(["sudo", "usermod", "-aG", "sudo", username], check=True)
        print(f"User {username} added to the sudo group successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error adding user {username} to the sudo group: {e}")

def grantSudoPrivilegesWithoutPassword(username):
    try:
        configFile = f"/etc/sudoers.d/allow{username.capitalize()}"
        with open(configFile, "w") as file:
            file.write(f"{username} ALL=(ALL) NOPASSWD:ALL\n")
        print(f"Sudo privileges granted to {username} without password successfully.")
    except Exception as e:
        print(f"Error granting sudo privileges to {username}: {e}")

def main():
    parser = argparse.ArgumentParser(description="User Sudo Privileges Script")
    parser.add_argument("--username", type=str, help="Username to grant sudo privileges")
    args = parser.parse_args()

    if args.username:
        addUserToSudoGroup(args.username)
        grantSudoPrivilegesWithoutPassword(args.username)
    else:
        username = input("Enter the username: ")
        addUserToSudoGroup(username)
        grantSudoPrivilegesWithoutPassword(username)

if __name__ == "__main__":
    main()
