import os, subprocess, sys, tempfile, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import todo_age


def run(*a, cwd):
    subprocess.run(a, cwd=cwd, check=True, capture_output=True)


class T(unittest.TestCase):
    def test_collect(self):
        with tempfile.TemporaryDirectory() as d:
            run("git", "init", "-q", cwd=d)
            run("git", "config", "user.email", "a@b.c", cwd=d)
            run("git", "config", "user.name", "Ann", cwd=d)
            open(os.path.join(d, "x.py"), "w").write("a = 1\n# TODO: fix me\n# FIXME(bob) later\n")
            run("git", "add", ".", cwd=d)
            run("git", "commit", "-qm", "init", cwd=d)
            items = todo_age.collect(d)
            self.assertEqual([(i["tag"], i["line"], i["author"]) for i in items],
                             [("TODO", 2, "Ann"), ("FIXME", 3, "Ann")])
            self.assertEqual(items[0]["text"], "fix me")


if __name__ == "__main__":
    unittest.main()
