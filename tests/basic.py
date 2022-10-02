from src import NamedNumber

if __name__ == "__main__":
    x = NamedNumber(50)
    assert x == NamedNumber(str(x)), "not reversible"

    y = NamedNumber(72, "%adjective% %animal% %20%")
    z = NamedNumber(34, "%emotion% %animal%", emotion=["happy", "sad", "angry", "hungry", "sleepy"])
