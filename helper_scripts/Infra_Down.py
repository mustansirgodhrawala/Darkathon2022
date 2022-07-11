import docker

client = docker.from_env()

try:
    client.containers.get("torone").remove(force=True)
except Exception:
    pass
try:
    client.containers.get("balancer_container").remove(force=True)
except Exception:
    pass
