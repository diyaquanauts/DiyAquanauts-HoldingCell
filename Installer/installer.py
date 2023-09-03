import subprocess


def _reportOut(msg):
    print("~ " * 30)
    print(msg)


def _installPackage(cmd, packageName):
    try:
        _reportOut(f"EXECUTING: \n    {cmd}")
        subprocess.run(cmd, check=True, shell=True)

        _reportOut(f"    ---> {packageName} installed successfully. <---")

    except subprocess.CalledProcessError as e:
        _reportOut(f"ERROR INSTALLING {packageName}!!!\n", e)


def aptUpdate():
    cmdArgs = "sudo apt-get update"
    _installPackage(cmdArgs, "system update")



def aptUpgrade():
    cmdArgs = "sudo apt-get upgrade"
    _installPackage(cmdArgs, "system upgrade")


def installPackage(packageName):
    cmdArgs = f"sudo apt-get install {packageName}"
    _installPackage(cmdArgs, packageName)


def installPipPackages(pipPackage):
    cmdArgs = f"sudo pip3 install {pipPackage}"
    _installPackage(cmdArgs, pipPackage)


def execRawFromTemplate(templateFilePath, tokenAndSubstDictionary, exitOnFailure=True):
    with open(templateFilePath, "r") as file:
        lines = file.readlines()

    _reportOut("Source template:")

    for line in lines:
        print(f"    {line}")

    breakLoop = False

    for token, subst in tokenAndSubstDictionary.items():
        for line in lines:
            rawCmd = line.replace(token, subst)
            results = execRawCmd(rawCmd)
            if not results[0] == False and exitOnFailure:
                breakLoop = True
                break
        if breakLoop:
            break


def execRawCmd(cmd):
    successful = False

    output = []

    try:
        print(f"  ---> Executing: '{cmd}'")

        result = subprocess.run(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )

        if result.stdout:
            output.append(result.stdout)
        if result.stderr:
            output.append(result.stderr)

        msg = "\n".join(output)

        if(len(msg) > 1):
            print(msg)

        print("Execution successful.")
        successful = True

    except subprocess.CalledProcessError as e:
        _reportOut("Execution failure!")
        print(f"    -{e.stderr}")
        output.append(e.stderr)

    return [successful, output]
