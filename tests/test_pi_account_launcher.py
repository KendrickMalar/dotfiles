import unittest, tempfile, pathlib, os, subprocess, json
SCRIPT=pathlib.Path(__file__).resolve().parents[1]/"dot_local/bin/executable_pi-account"
class AccountLauncher(unittest.TestCase):
 def test_three_accounts_keep_auth_dir_and_argv_with_explicit_bypass(self):
  for account in ("kuno","muu","rbx"):
   for bypass in (False,True):
    with self.subTest(account=account,bypass=bypass), tempfile.TemporaryDirectory(prefix="account-launch-") as directory:
     root=pathlib.Path(directory);bin=root/"bin";bin.mkdir();agent=root/".pi/agent";agent.mkdir(parents=True);(agent/"settings.json").write_text("{}")
     log=root/"called"
     for name in ("pi","pi-profile","pi-extension-deps-patch","pi-hermes-realpath-patch"):
      file=bin/name
      if name.startswith("pi-") and name.endswith("-patch"):file.write_text("#!/bin/sh\nexit 0\n")
      else:file.write_text("#!/bin/sh\nprintf '%s\\n' "+name+" \"$@\" > "+str(log)+"\nprintf '%s' \"$PI_CODING_AGENT_DIR\" > "+str(root/"agent-used")+"\n")
      file.chmod(0o755)
     env={"HOME":str(root),"PATH":str(bin)+":/usr/bin:/bin"}
     if bypass:env["PI_PROFILE_LAUNCHER"]="0"
     result=subprocess.run(["bash",str(SCRIPT),account,"--model","value with space","--","日本語"],env=env,capture_output=True,text=True)
     self.assertEqual(result.returncode,0,result.stderr)
     calls=log.read_text().splitlines()
     self.assertEqual(calls[0],"pi" if bypass else "pi-profile")
     self.assertEqual(calls[1:],["--model","value with space","--","日本語"] if bypass else ["launch","--","--model","value with space","--","日本語"])
     used=(root/"agent-used").read_text()
     self.assertEqual(used,"" if account=="kuno" else str(root/(".pi/agent-"+account)))
if __name__=="__main__":unittest.main()
