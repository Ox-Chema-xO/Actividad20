import os, json, subprocess

LEGACY_DIR = "legacy"
TF_DIR     = os.path.join(LEGACY_DIR, "tf_env")

CONFIG_FILE = os.path.join(LEGACY_DIR, "config.cfg")
RUN_FILE    = os.path.join(LEGACY_DIR, "run.sh")

# leer config.cfg
config = {}
with open(CONFIG_FILE) as f:
    for line in f:
        if "=" in line and not line.strip().startswith("#"):
            k,v = line.strip().split("=",1)
            config[k] = v

port = config.get("PORT", "8080")

# leer run.sh
message = ""
with open(RUN_FILE) as f:
    for line in f:
        if line.strip().startswith("echo "):
            msg = line.strip().split("echo",1)[1].strip()
            message = msg.replace("$PORT", "${var.port}")
            break

os.makedirs(TF_DIR, exist_ok=True)

# generar network.tf.json
network = {
    "variable": [
        {
            "port": [
                {
                    "type": "string",
                    "default": port,
                    "description": "Puerto del servidor legacy"
                }
            ]
        }
    ]
}
with open(f"{TF_DIR}/network.tf.json","w") as f:
    json.dump(network, f, indent=4, sort_keys=True)

# generar main.tf.json
main = {
    "resource": [
        {
            "null_resource": [
                {
                    "legacy-server": [
                        {
                            "triggers": {"port": "${var.port}"},
                            "provisioner": [
                                {
                                    "local-exec": {
                                        "command": f"echo {message}"
                                    }
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    ]
}
with open(f"{TF_DIR}/main.tf.json","w") as f:
    json.dump(main, f, indent=4, sort_keys=True)

# terraform init y plan
print("==> terraform init")
subprocess.run(["terraform","init"], cwd=TF_DIR, check=True)
print("\n==> terraform plan")
subprocess.run(["terraform","plan"], cwd=TF_DIR, check=True)

print(f"\nConfiguracion terraform generada en '{TF_DIR}/'")
