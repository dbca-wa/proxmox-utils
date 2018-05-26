#!/usr/bin/env python3
import subprocess
from datetime import datetime, timedelta
from collections import namedtuple

# Needs to be run on a cluster, goes through each node and snapshots vms
nodes = [row.split()[2] for row in subprocess.check_output(["pvecm",  "nodes"]).decode("utf-8").strip().split("\n")[3:]]

for node in nodes:
    vms = subprocess.check_output(["ssh", node, "qm", "list"]).decode("utf-8").strip().split("\n")
    VMInfo = namedtuple("vminfo", vms[0].strip().replace("(", "_").replace(")", "").split())
    Snap = namedtuple("Snap", ["name", "parent", "desc", "date"])
    # date followed by 24hr time, with minutes truncated to disallow multiple snaps per hour
    timeformat = "auto_%Y%m%d_%H00" 
    now = datetime.now()
    maxage = timedelta(days=30)

    for vm in vms[1:]:
        vm = VMInfo(*vm.strip().split())
        if vm.STATUS == "running":
            try:
                subprocess.check_call(["ssh", node, "qm", "snapshot", vm.VMID, now.strftime(timeformat)])
            except Exception as e:
                print(e)
        snapshots = subprocess.check_output(["ssh", node, "qm", "listsnapshot", vm.VMID]).decode("utf-8").strip().split("\n")
        if snapshots and len(snapshots) > 1:
            snapshots.sort()
            for snap in snapshots:
                snap = Snap(*snap.strip().split(), None) 
                try: snap.date = datetime.strptime(snap.name, timeformat)
                except: continue # If name doesn't parse, it wasn't an automated snapshot, so just skip to next
                if now - snap.date > maxage: # delete snapshots older than maxage
                    try:
                        subprocess.check_call(["ssh", node, "qm", "delsnapshot", vm.VMID, snap.name])
                    except Exception as e:
                        print(e)
        print("{} ({}) snapshots:".format(vm.NAME, vm.VMID))
        subprocess.check_call(["ssh", node, "qm", "listsnapshot", vm.VMID])




