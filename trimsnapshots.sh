#!/bin/bash
qm listsnapshot $1 | cut -f1 -d' ' | grep auto | xargs -n 1 qm delsnapshot $1
